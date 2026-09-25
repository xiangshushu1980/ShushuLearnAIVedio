# KREA 2 生图

> Krea2 人物身份、风格化脸和 H3/Ref2VA 前置参考图不在本页维护；唯一入口是 [docs/40_krea2_prompt_and_identity_pipeline.md](../../../../docs/40_krea2_prompt_and_identity_pipeline.md)，实际 Prompt 唯一来源是 [tools/krea2_prompt_profiles.py](../../../../tools/krea2_prompt_profiles.py)。

## 资源

- 扩散模型：`krea2_turbo_fp8.safetensors`
- 文本编码器：`qwen3vl_4b_fp8_scaled.safetensors`，`CLIPLoader type=krea2`
- VAE：`qwen_image_vae.safetensors`
- 基础工作流：[workflows/krea2_t2i_test.json](../../../../../workflows/krea2_t2i_test.json)

## 当前本地基线

- 8 steps
- CFG 1.0
- `er_sde` / `simple`
- 1024×1024 或 1024×576 作为研究起点
- 正向和负向 conditioning 可先使用同一文本，实验时再单独比较

完整参数与历史对比见旧版 [params.md KREA 2 小节](../params.md)。模型文件清单见 [docs/02_models.md](../../../../../docs/02_models.md)。

## KREA 专用实验节点

`ComfyUI-KJNodes` 中的 `Krea2PromptWeight` 可用于测试概念强调/抑制，属于 experimental；没有对照实验前不能当作默认流程。

## 研究边界

当前任务只验证提示词、风格约束、人物/场景/道具/法术概念和分辨率边界。正式 Object ref 生产工作流另行建立。
