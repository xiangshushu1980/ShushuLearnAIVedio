# HyperFlow 在 RTX 4090 上的 Ref2VA 可行性研究

> 研究任务：T-comfy-ops-41  
> 核查日期：2026-09-20  
> 目标：判断 HyperFlow 是否能基于现有 RTX 4090/24GB + pruned Ref2VA 基座进入生产。

## 结论

当前不建议把 HyperFlow 作为本机 Ref2VA 生产路线。

原因不是“完全不能运行”，而是两条可行路线都各有硬伤：

1. 完整 HyperFlow 需要带 `time_embedder` 的非 pruned Ref2VA 基座，约 34GB，不能完整驻留 RTX 4090 的 24GB 显存；通过 CPU offload 理论上可能运行，但目前没有 RTX 4090 的完整 HyperFlow Ref2VA 验证，预计速度不适合生产。
2. 社区提供了 pruned 版本，可以配合现有约 21GB 的 pruned Ref2VA 基座运行，但该版本只有 backbone LoRA，缺少 HyperFlow 的第二个 endpoint time embedder，属于 single-time/off-recipe 变体，不能等同于完整 HyperFlow，也不应作为正式生产基线。

因此，当前生产主线仍是 **PDD + SageAttention + pruned Ref2VA**。HyperFlow 只保留为实验性旁支：若需要确认“4090 能否出片”，可以跑一次明确标记为 `experimental_pruned_backbone_only` 的 smoke，但结果不能与 PDD 做正式质量/速度排名。

## HyperFlow 的算法契约

官方 HyperFlow 不是普通 8-step LoRA。它包含：

- 8-step 固定 sigma grid；
- video shift 12、audio shift 3；
- TwoTimeEmbedder；
- 每一步的 endpoint 条件 `r = 1 - sigma_next`；
- Ref2VA 的参考图、参考音频行保持 `r = t`。

完整路线必须使用专用 loader/节点和非 pruned 基座，不能用普通 LoRA loader 或手工改 steps 代替。[Video Rebirth 官方说明](https://github.com/Video-Rebirth/hyperflow)

## 社区 ComfyUI 路线

### 完整节点路线

`Addis-Pulse-Studio/ComfyUI-HyperFlow` 能把官方 HyperFlow 的 endpoint conditioning 映射到 ComfyUI，并提供 Ref2VA 示例：

```text
非 pruned Ref2VA H3
  → HyperFlow LoRA Loader
  → HyperFlow Sigmas
  → Euler / CFG 1.0
  → MiniMax H3 Reference to Video
```

其公开验证环境为 RTX 5090/32GB、ComfyUI 0.36。Ref2VA 使用参考图 + 参考音频，124 帧/5.167 秒成功；音频包络相关系数 0.980、0ms lag、无漂移。首次加载包含约 5 分钟模型初始化、解量化、打补丁和重新量化成本。[节点验证记录](https://raw.githubusercontent.com/Addis-Pulse-Studio/ComfyUI-HyperFlow/main/docs/VERIFICATION.md)

该节点明确拒绝 `*_pruned_*` 曲线基座，因为 pruned 模型没有运行时 `time_embedder`。

### pruned 社区路线

`Saganaki22/ComfyUI-Hyperflow` 提供 pruned/curve 版本的约 3.64GiB 权重，并能根据当前模型自动选择 pruned build。它理论上可连接现有：

```text
minimax_h3_ref2va_pruned_int8_convrot.safetensors
```

但作者明确标注 pruned build 为：

- backbone LoRA only；
- single-time；
- off-recipe；
- 不安装第二个 endpoint time embedder。

普通 stock LoRA 转换版也有同样限制。它可以作为低成本实验，但不能代表官方 HyperFlow 的 Ref2VA 算法。[Saganaki 社区节点](https://github.com/Saganaki22/ComfyUI-Hyperflow)、[节点源码](https://raw.githubusercontent.com/Saganaki22/ComfyUI-Hyperflow/main/hyperflow_h3/nodes.py)

## RTX 4090 硬件判断

本机环境：RTX 4090/24GB、约 62GB 系统内存。

| 项目 | 完整 HyperFlow | pruned 社区版 |
|---|---:|---:|
| Ref2VA 基座 | 非 pruned，约 34GB | 现有 pruned，约 21GB |
| 显存驻留 | 不可能完整驻留 | 适合现有 24GB 档 |
| CPU offload | 理论可行，但预计很慢 | 已是当前 ComfyUI 常规路线 |
| endpoint conditioning | 完整 | 缺失 |
| RTX 4090 Ref2VA 公开实测 | 未找到 | 未找到正式生产实测 |
| 生产可信度 | 低：速度未知且高内存压力 | 低：算法已偏离官方 |

社区量化资料确认 pruned INT8 ConvRot Ref2VA 是 24GB RTX 30/40 卡的常规选择，并有 RTX 4090 loader 通过记录；这只证明基座适配，不证明 HyperFlow pruned 变体的生成质量或稳定性。[社区量化记录](https://huggingface.co/DmitryDB/MiniMax-H3-ComfyUI-Quants/blob/main/README.md)

## 与当前 PDD 的关系

本项目已有 PDD + SageAttention 的 Ref2VA 基线：

- 1024×576/15 秒约 235 秒；
- 1024×576/20 秒约 335–342 秒；
- 生产路线使用 pruned Ref2VA，已在本机验证。

HyperFlow 同样是少步采样替换项，不应与 PDD、Turbo 或 TaoMate 叠加。当前没有 RTX 4090、同分辨率、同 seed、同参考图/音频条件下证明 HyperFlow pruned 版优于 PDD 的证据。

## 后续实验门槛

只有在需要验证社区版本是否“能跑”时，才做一次最小实验：

- 路线标记：`experimental_pruned_backbone_only`；
- 5 秒、低分辨率、单角色；
- 保留参考图和参考音频；
- 不与 PDD 叠加；
- 只检查：节点加载、参考条件是否生效、视频是否可解码、音频是否存在、显存/耗时；
- 不把结果写入正式 PDD 质量/速度矩阵；
- 若出现身份丢失、口型失配、音频损坏或明显运动退化，立即停止。

在没有完整 non-pruned 4090 实测前，不应把 HyperFlow 写入本项目生产推荐。

