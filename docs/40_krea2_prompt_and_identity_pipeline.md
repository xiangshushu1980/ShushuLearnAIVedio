# Krea2 提示词与人物身份管线

> 状态：研究基线，2026-09-21。本文区分官方 Krea2 能力、社区 Identity Edit 能力和本地实测；未实跑的 Raw 参数不视为本地定论。

## 目标

本项目使用 Krea2 为 H3/Ref2VA 视频准备人物参考图，目标不是单张好看的插画，而是：

```text
真人照片 → 身份保持的风格化脸 → 统一人物参考图 → H3 Ref2VA 视频
```

身份、删除显著元素和 Jibs 风格化必须分阶段，不能让一个 Turbo + Jibs prompt 同时承担三种任务。

## 证据分层

### 官方 Krea2

- [官方开源仓库](https://github.com/krea-ai/krea-2)：提供 Raw/Turbo 推理代码和基础 Prompting Guide。
- [官方 prompting.md](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md)：建议自然语言；详细 prompt 可以帮助构图和视觉方向，但没有人物身份锁定模板。
- [官方 expansion.txt](https://github.com/krea-ai/krea-2/blob/main/docs/expansion.txt)：强调忠实保留用户指定主体、动作、颜色和空间关系，不凭空添加输入未支持的细节。
- [官方 Style Transfer API](https://www.krea.ai/docs/developers/krea-2/style-transfer)：style reference 负责把参考图的风格应用到新主体，不等同于人物身份参考。

官方没有发现独立的“身份头像 Prompt Skill”。

### 社区 Identity Edit

主要依据：

- [ComfyUI-Krea2Edit](https://github.com/lbouaraba/comfyui-krea2edit)
- [Identity Edit v1.2 模型卡](https://huggingface.co/conradlocke/krea2-identity-edit)
- [官方示例 workflow](https://github.com/lbouaraba/comfyui-krea2edit/blob/main/workflows/krea2_identity_edit.json)

该社区项目使用 `Krea2EditModelPatch` + `Krea2EditGroundedEncode`：参考图同时进入 VAE 外观路径和 Qwen3-VL 图像语义路径。它要求 plain-English edit instruction，而不是重新描述整张图片。

社区可迁移结论：

- 人物身份不稳定时，可以追加“保持准确的面部身份”和来自原图的辨识特征；不要发明新的五官。
- `ref_boost≈4` 是 v1.2 强身份保真的起点；`>10` 可能使删除/替换失败。
- `fit_mode=fit` 是 v1.2 的推荐几何处理。
- 人物可尝试 `grounding_px=1024`；出现重复/分裂构图时降低它。
- Turbo 适合 restyle、re-stage、加元素：8–12 steps / CFG 1。
- 删除眼镜、衣服等显著内容使用 Raw：模型卡建议 20 steps / CFG 3；示例 workflow 另给出 40 steps / CFG 3–4 对照。
- CFG 大于 1 时，negative conditioning 仍使用同一张参考图和空 prompt；不要自行堆叠长负向词串。
- 输出先控制在约 1MP 且不超过 2MP；身份确认后再放大。

## 三个明确模式

runner：`tools/krea2_identity_edit_runner.py`；Prompt 唯一来源：`tools/krea2_prompt_profiles.py`。

本文只记录 Prompt 的用途和参数契约，不复制完整 Prompt 文本；修改 Prompt 时先改 `krea2_prompt_profiles.py`，再在本文件更新版本说明。

### 1. `identity_portrait`

用途：从真人照片建立统一的身份头像。当前本地可直接运行 Turbo，不加载 Jibs。

提示词 profile：`IDENTITY_PORTRAIT`，见 [`tools/krea2_prompt_profiles.py`](../tools/krea2_prompt_profiles.py)。语义要求是：正面 1:1 头像、保留原始身份锚点，只改变渲染，不加入新五官。

默认参数：

| 参数 | 默认值 |
|---|---:|
| UNET | 本地 `krea2_turbo_fp8.safetensors` |
| Identity LoRA | `krea2_identity_edit_v1_2.safetensors` / 1.0 |
| Jibs | 不加载 |
| steps / CFG | 10 / 1.0 |
| ref_boost | 4.0 |
| grounding_px | 1024 |
| 输出 | 1024×1024，约 1MP |
| fit_mode | fit |

### 2. `identity_remove`

用途：先去除眼镜、帽子、服装等显著元素，再进入风格化阶段。

提示词 profile：`IDENTITY_REMOVE`，见 [`tools/krea2_prompt_profiles.py`](../tools/krea2_prompt_profiles.py)。删除对象由 `--remove-item` 指定，默认是眼镜和所有眼部佩戴物；删除操作只在 Raw 模式验证。

默认参数：ComfyUI Raw FP8 scaled（`krea2_raw_fp8_scaled.safetensors`）/ 20 steps / CFG 3 / ref_boost 4 / grounding_px 1024。由于该 checkpoint 尚未下载到本机，该模式目前只接入配置和参数校验，不能标记为已实测。

### 3. `jibs_style_portrait`

用途：在已经确认的身份头像上应用 Jibs 风格。它不再负责去眼镜、换衣服或修复脸部结构。

提示词 profile：`JIBS_STYLE_PORTRAIT`，见 [`tools/krea2_prompt_profiles.py`](../tools/krea2_prompt_profiles.py)。语义要求是：只改变 Jibs 渲染方式，保留已经确认的身份头像，不负责删除眼镜、服装或修复五官。

默认参数：Turbo / 10 steps / CFG 1 / Jibs 1.0 / ref_boost 4 / grounding_px 1024 / 1024×1024。Jibs 强度 1.0 是本任务本地选择，不是 Krea 官方参数；0.6 与 1.5 仍属于对照实验档。

## 视频参考图阶段

身份头像和风格头像确认后，再生成统一人物参考图。构图 profile：`VIDEO_REFERENCE`，见 [`tools/krea2_prompt_profiles.py`](../tools/krea2_prompt_profiles.py)。它只控制统一景别、姿态和背景，不重新设计脸。

进入人物场景时，社区 workflow 的输入顺序固定为：场景图 image 1，人物图 image 2；不能交换。完成后再将人物参考图交给 H3 Ref2VA。

## 本地状态与限制

- 已有：Turbo、Qwen3-VL 4B、Qwen Image VAE、Identity Edit v1.2、Jibs LoRA。
- 未有：Krea2 Raw checkpoint；`identity_remove` 暂不能实跑。
- 当前本地 runner 已切换到三模式；negative 默认恢复为空 prompt，不再使用实验性的 `no clothing/no eyewear` 负向词串。
- 之前的 `style-only` + Jibs 1.0 结果不作为人物身份基线；它把身份锁定、显著内容删除和风格化混在一起，已被实验否定。
