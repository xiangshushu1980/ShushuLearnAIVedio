# H3 SelfLift + Ref2VA 在 RTX 4090 上的证据边界

> 调查日期：2026-09-20
> 关联任务：T-comfy-ops-42

## 结论

RTX 4090 跑 H3 Ref2VA 本身已有公开、可复核的单卡证据；但截至本次调查，没有找到“同一张 4090、Ref2VA conditioning、SelfLift 渐进采样”同时成立，并附带视频、日志或 A/B 质量数据的公开案例。因此不能把“Ref2VA 能跑”和“Ref2VA + SelfLift 已被 4090 证明可用”混为一谈。

基于证据密度，本项目暂不继续 SelfLift 前沿实测；资源转给 41 号任务的 TaoMate-3step、HyperFlow 与 PDD 对照。若未来恢复，最低验收门槛应是同一 4090 上的三张参考图、SelfLift 开关 A/B、显存峰值、采样/端到端耗时和成片产物。

## 证据核查

| 来源 | 能证明什么 | 不能证明什么 |
|---|---|---|
| [comfyui-SelfLift](https://github.com/facok/comfyui-SelfLift) | 提供实验性的 H3 音视频节点；H3 reference 通过 conditioning 传递，R2V references 在高分辨率阶段保持完整；README 给出 H3 单 seed 的 `rho=0.6` 等伪影缓解观察 | 论文没有评估 H3；没有 Ref2VA + SelfLift 的系统质量/速度验证；`SelfLift-rich` 仍需训练 |
| [X-MinimaxH3](https://github.com/PullMyBoots/X-MinimaxH3) 的 [VALIDATION](https://github.com/PullMyBoots/X-MinimaxH3/blob/main/VALIDATION.md) | 以 RTX 4090/SM89 为校准平台，并有 Ref2VA 4-step 的实际生成与资源矩阵 | 功能清单同时写 Ref2VA/SelfLift，不等于二者在同一推理中被验证 |
| [X-MinimaxH3 SelfLift 文档](https://github.com/PullMyBoots/X-MinimaxH3/blob/main/docs/SELFLIFT_PROGRESSIVE_GENERATION.md) | SelfLift 当前 API 的渐进生成约束和可运行路线 | 当前约束是 H3 Base/Larry、text-to-video、单一物理生成窗口；没有 Ref2VA conditioning 路线 |
| [AIMixer Director](https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director/blob/main/README_EN.md) | 工作流接口可同时暴露 `r2v/ref2va` 与 SelfLift，SelfLift 结构为低清前缀 + 3D latent lift + 高清收尾 | README 明确部分桥接/蒸馏组件来自 FL2VA，对 r2v 属于 forced-compat / use with care；没有 4090 质量数据 |
| [Ref2VA-VSA](https://github.com/Kablex/ComfyUI-Ref2VA-VSA) | 4090 上报告 1344×768、5 秒级 Ref2VA 运行数据 | 只证明 Ref2VA，不包含 SelfLift |
| [H3 SelfLift 2K workflow 归档](https://civitaiarchive.com/models/2937121?modelVersionId=3324892) | 社区已有混合 FL2VA/Ref2VA UNET、latent upscaler、native audio 的打包工作流 | 没有 Ref2VA 分支 A/B、显存日志或 4090 复核数据 |

## 对本地 4090 的判断

- **Ref2VA：可行。** 本机已有 Ref2VA 生产基线；外部 4090 证据也覆盖 4-step、1344×768 和约 24GB 卡的运行边界。
- **SelfLift：工程上可能接通。** 社区节点/工作流存在接口或封装，但主要是实验适配或 FL2VA/文本生视频路径。
- **Ref2VA + SelfLift：未证明。** 缺少直接的 4090 paired run，尤其缺少参考图身份保持、音频口型和伪影的对照结果。

所以当前不值得为“可能节省空间计算”继续消耗本地测试资源；除非出现新的直接复核样本，或用户明确恢复 42 号路线。

