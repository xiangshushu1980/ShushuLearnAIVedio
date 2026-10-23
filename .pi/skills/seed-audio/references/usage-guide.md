# Seed Audio 1.0 使用与提示词指南

本指南是日常使用入口，按官方文档提炼能力和限制。官方链接留作权威依据；普通调用不需要实时读取整篇 API 文档。官方规则、节点实现和提示词组织建议分开理解。

## 官方能力与限制

- 模型标识：`seed-audio-1.0`。这是非流式 HTTP 音频生成 API。一次 `text_prompt` 可组织多角色台词、语气、情绪节奏，以及音乐、环境和动作声效的一体化生成。
- `text_prompt` 最长 3000 字符。官方建议用于合成人声的文本控制在 400 字符以内；过长时模型可能加快语速以在时长限制内完成。
- 单次输出最长 120 秒。API 支持用自然语言描述整段时长和人声出现的时间段。官方没有定义 `[start:end]` 等固定时间码语法；可以把时间标记作为提示词中的自然语言辅助，但不能承诺其是严格解析规则。
- 官方页面对语种范围不一致：音频生成 API 页面列出多种语言，模型列表页对 Seed Audio 1.0 列出中文、英文并说明可演绎部分口音。未确认控制台当前开通范围前，不承诺较宽语言列表；纯方言输出也不能由“可演绎口音”推出。
- 支持纯文本、文本加音频参考、文本加图片参考。最多 3 条音频参考，每条最长 30 秒、10 MB；最多 1 张图片，最大 10 MB。图片参考不能与音频参考或 speaker 同次混用。
- 音频参考可使用音频数据、音频 URL 或 speaker ID；同一条参考不能同时给多个来源。API 文档列明 speaker 可使用豆包语音合成模型 2.0 或声音复刻音色。
- 输出格式：WAV、MP3、PCM、OGG Opus。火山引擎 WAV/PCM 支持 8/16/24/32/40/44.1/48 kHz，MP3 支持 8/16/24/32/44.1/48 kHz，OGG Opus 仅 48 kHz。BytePlus 的可选采样率以当前节点验证及其官方文档为准；本节点不向 BytePlus 传 40 kHz。
- `speech_rate` 与 `loudness_rate` 范围为 -50 到 100，0 表示不调整；`pitch_rate` 范围为 -12 到 12，0 表示不调整。节点也支持字幕、可听水印和元数据水印。
- API 没有独立“音质等级”或码率参数。格式和采样率是输出规格，不等同于提高模型本身的生成质量。不要把 ComfyUI `seed` 描述成模型可复现 seed；此节点用它影响 ComfyUI 重算，不会发送给音频模型。

## 节点输入速查

| 目的 | 节点输入 | 使用说明 |
|---|---|---|
| 选择服务 | `provider` | BytePlus 或火山引擎；只读取匹配服务的本地 key，不能跨服务混用。 |
| 场景和对白 | `text_prompt` | 1–3000 字符；写场景、角色、原文台词、声音表演和音效时序。 |
| 选择参考模式 | `reference_mode` | `text only`、`audio reference`、`image reference`、`preset voice`。 |
| 输出编码 | `audio_format`, `sample_rate` | 按服务与格式限制组合；一般要做后期选 WAV，需更小文件才考虑压缩格式。 |
| 表演微调 | `speech_rate`, `loudness_rate`, `pitch_rate` | 只调整整体对应数值；角色差异优先写在 prompt 或使用参考声源。 |
| 字幕和标识 | `enable_subtitle`, `audible_watermark`, `metadata_watermark`, `content_producer`, `produce_id`, `content_propagator`, `propagate_id` | 字幕开启后可返回字幕 JSON/SRT；水印字段按项目需要填写。 |
| 语音参考 | `reference_audio_1`–`reference_audio_3`, `ref_audio_1_source`–`ref_audio_3_source` | 选 `audio reference`。每个槽位使用已连接 ComfyUI 音频、HTTP(S) URL 或 speaker ID 中的一种。 |
| 图片参考 | `reference_image`, `ref_image_url` | 选 `image reference`；连接图片与填写 URL 二选一。URL 必须是公开 HTTPS 地址。 |
| 预设角色音色 | `preset_voice` | 选 `preset voice`，填写可用的 TTS 2.0 或克隆 speaker ID。当前预设模式是一个 voice ID 输入。 |
| take 与重算 | `generation_count`, `seed` | 每个 take 单独计费；seed 不是远端模型随机种子。 |

节点有 22 个必填参数，以及 3 个可选音频输入和 1 个可选图像输入。用户未要求多条 take 时保持 `generation_count=1`。请求成功后使用 `audio` 输出连接预览/保存；其他输出包括字幕 JSON、SRT、生成时长、计费时长、临时 URL、request ID 与服务端 log ID。

服务与凭据对应关系：

| provider | API endpoint | 本机凭据变量 |
|---|---|---|
| BytePlus Seed Speech | `https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/create` | `BYTEPLUS_SEED_SPEECH_API_KEY` |
| Volcengine Doubao Voice | `https://openspeech.bytedance.com/api/v3/tts/create` | `VOLCENGINE_DOUBAO_VOICE_API_KEY` |

密钥只从 ComfyUI 本地环境或 `user/.env` 读取；不要要求用户把 key 发到聊天，不要将 key 写入 prompt、workflow、日志或实验记录，也不要输出变量值。

## 从剧本写成一条场景 prompt

官方产品说明支持在单条 prompt 中说明多角色对白、语气与情绪节奏，并整合音乐、环境音效和人声。下面是便于 Agent 使用的组织顺序，不是官方固定语法：

1. **交付目标**：目标总时长、语言、场景氛围、整体写实/卡通/游戏化风格，是否需要音乐。
2. **角色声线**：每个角色用稳定的名称或标签，并描述必要的语言/口音、音域或音色、年龄感、情绪与说话方式。没有用户给定依据时不擅自锁定身份特征。
3. **对白**：保留剧本原句；标清说话人、语气、停顿、呼吸或笑/喊/耳语等表演。对白字数尽量控制在官方建议范围内。
4. **事件顺序**：按发生顺序写动作与转场；需要时用“开头/随后/最后”或自然语言时间区间，标明对白与动作、环境声之间的先后或重叠。
5. **声音层次**：说明持续背景（房间声、风雨、机器等）、前景动作（脚步、碰撞、物件）、远近移动、对白清晰度和收尾方式。

可用的提示词骨架：

```text
生成一段【时长】的【场景/类型】音频，包含【对白/环境/动作声/音乐要求】。
角色A（【声线与表演】）说：“【剧本原句】”。
角色B（【声线与表演】）回应：“【剧本原句】”。
随后【动作与音效顺序】，背景持续【环境声】；对白保持清晰，声音随【距离/运动】变化，最后【收尾】。
```

剧本已提供完整对白时，不改写台词；prompt 过长时先删重复形容，不删事件因果或角色台词。复杂动作场景要让时间、说话人、关键声效和结尾可辨认，避免在很短的时长里塞入过多对白。

## 角色音色与图片/人声的选择

- **没有指定音色参考**：`text only`，在 prompt 描述各角色声线和表演。官方产品概述支持多角色提示，但仅凭文字描述不能保证跨次生成的角色音色完全一致。
- **需要参考录音或固定 speaker ID**：用 `audio reference`，在 prompt 中清楚说明哪个角色对应哪个音频参考；对上传的参考音频按顺序使用 `@Audio1`、`@Audio2`、`@Audio3`。speaker ID 是音色来源，不是台词本身。
- **提供角色或场景图片**：用 `image reference`，在 prompt 明确希望声音从图片中借鉴什么，以及实际要生成的对白和声音。图片本身不能代替剧情信息或台词。
- **用户同时给人声和图片**：当前 API 不允许同一次请求混用两类参考。解释这一限制并询问哪种素材优先；若用户允许，可分成独立生成/后期合成方案，不能静默丢弃某类素材。
- **固定角色音色是核心要求**：说明 Seed Audio prompt 里的文字角色描述与固定 speaker ID 的区别。不要承诺参考图片会锁定音色，也不要承诺多角色 ID 的稳定分配超出本节点接口与实测证据。

## 生成和验收

- 仅在用户要求生成音频或授权生成时执行；免费额度与扣费状态以账号控制台为准，不能由 API 成功响应推断“免费”。多 take 会增加独立计费请求。
- 使用项目自有 `SeedAudioBytePlus` 节点，不把 provider API 当作常规执行入口。运行前查共享 ComfyUI 状态和队列，使用现有 ComfyUI API/runner 契约；不要创建第二实例或清理全局队列。
- 只提交一次；若 POST 超时或结果不确定，先按 prompt ID、队列与 history 查是否已运行，不能盲目重发。
- 完成后检查实际时长、输出可解码并试听。分别核对台词、角色区分、事件顺序、环境声存在与混音清晰度；接口成功不代表内容验收通过。归档音频和 request/result 记录到任务的 `experiments/` 目录，清理自己产生的 ComfyUI 临时输出。

## 官方依据

- [火山引擎音频生成 API](https://docs.volcengine.com/docs/DoubaoVoice/audio-generation-http?lang=zh)：请求结构、引用输入互斥、格式/采样率、时长控制与响应字段。
- [火山引擎产品概述](https://docs.volcengine.com/docs/DoubaoVoice/ProductOverview-9?lang=zh)：音频创作能力、多角色对白与一体化音轨等产品描述。
- [火山引擎模型列表](https://docs.volcengine.com/docs/DoubaoVoice/model-list?lang=zh)：语言、参考输入、字符和时长上限。
- [BytePlus Seed Audio 1.0 API](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01)：BytePlus 服务端的官方接口说明。
- [本项目自有节点说明](../../../../custom_nodes/ComfyUI-SeedAudio-BytePlus/README.md)：provider、节点输入、安装路径与项目实现约束；实现有变更时核对当前代码与 live schema。

## 后续经验

本指南当前只收录官方明示能力、当前节点实现和必要的操作流程。将来新增本地 prompt 或质量经验时，只将重复验证且适用条件明确的结论标为“本地实测”，并链接对应 `experiments/` 证据；不要把单次结果升级成官方规则。

官方页面最后核对日期：2026-10-23。
