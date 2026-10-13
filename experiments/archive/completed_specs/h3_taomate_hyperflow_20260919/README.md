# T-comfy-ops-41：TaoMate / HyperFlow / PDD 对照执行规格

本目录只放 41 号任务的测试规格与后续结果，不把官方 runtime、ComfyUI 转换 LoRA、diffusers HyperFlow 混写成同一实现。

## 当前可比边界

| 路线 | 后端 | 模式 | 步数契约 | 本机状态 |
|---|---|---|---:|---|
| PDD | ComfyUI | FL2VA | 8 | 已有本机基线 |
| TaoMate-3step | ComfyUI 转换 LoRA | FL2VA | 3 | 待宿主核查权重并跑最小样本 |
| HyperFlow | diffusers Modular Pipeline 专用 loader | FL2VA | 固定 8 NFE | 待安装/核查独立环境；4090 未验证 |

## 固定变量

- 第一阶段：FL2VA，5 秒，低分辨率 smoke test；通过后再进入 1024×576/124 帧正式短测。
- 同一首帧、英文 prompt、seed、帧数、输出格式和音频检查方法。
- ComfyUI 两臂统一 SageAttention；HyperFlow 先使用官方默认 dense SDPA，Sol-Attn 单独建臂。
- TaoMate 臂：LoRA strength 1.0、CFG 1.0、Euler、3 steps；禁止 PDD、Turbo 或其他采样加速叠加。
- HyperFlow 臂：必须使用 `load_hyperflow_lora` / `hyperflow-h3-fl2va`；不传 `num_inference_steps`，不使用普通 LoRA loader。

## 记录字段

每个结果至少记录：后端/版本、模型与 LoRA 文件及 hash、seed、prompt 文件、输入图 hash、宽高、实际帧数/时长、端到端时间、采样时间、VAE/编码时间、峰值 VRAM/RAM、音频采样率/声道、首块延迟（若可得）、失败原因，以及视频/音频人工 QC。

## 当前结论

在完成本机 smoke 前，不报告“三方同后端速度排名”。目前的决策是：

1. TaoMate 只做一次 4090/ComfyUI FL2VA smoke，验证是否比当前 PDD + Sage 有实际时间收益，以及动态运动/音频/prompt adherence 是否可接受。
2. HyperFlow 只使用带专用 `ComfyUI-HyperFlow` 节点的完整转换做 smoke；普通 LoRA loader 版缺少 endpoint conditioning，不作为正式结果。
3. 若目标只是速度，暂不扩大 HyperFlow；若目标是镜头控制、运动和材质质量，再决定是否进入正式 A/B。

当前社区证据不支持二者相对本机 PDD 已有“明显优势”：TaoMate 的速度收益伴随较强质量/音频风险，HyperFlow 的质量口碑尚缺 4090/PDD 同条件数据。
