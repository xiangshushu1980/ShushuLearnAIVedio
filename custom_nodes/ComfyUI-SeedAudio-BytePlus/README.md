# Seed Audio 1.0 (项目自有)

本目录是 comfy-ops 维护的 ComfyUI custom node，直接调用 Seed Audio 1.0 HTTP API；不依赖或安装官方节点包。节点可选择 BytePlus Seed Speech 或火山引擎豆包语音服务。

## 节点

`SeedAudioBytePlus`（显示名 `Seed Audio 1.0 (项目自有)`）输出 ComfyUI `AUDIO`、字幕 JSON、SRT、生成时长、计费时长、临时结果 URL、request ID 和服务端 log ID。把 `audio` 接到 `Preview Audio` 或 `Save Audio`。每次执行会向所选服务发起独立计费请求；服务端没有可复现的生成 seed。

## 凭据

节点的 `provider` 决定请求域名和读取的凭据变量：

| provider | 请求地址 | 本地凭据变量 |
|---|---|---|
| BytePlus Seed Speech | `https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/create` | `BYTEPLUS_SEED_SPEECH_API_KEY` |
| Volcengine Doubao Voice | `https://openspeech.bytedance.com/api/v3/tts/create` | `VOLCENGINE_DOUBAO_VOICE_API_KEY` |

随附的画布与 API workflow 默认选择 Volcengine Doubao Voice，因为当前使用的 key 来自火山引擎控制台。

将对应控制台签发的 API Key 写入 ComfyUI 用户目录 `.env` 或服务环境变量。当前安装对应的 `.env` 路径为 `/home/sean/projects/ComfyUI/user/.env`。两类凭据分别由 BytePlus 和火山引擎控制台签发，不应跨服务混用。ModelArk Ark API Key 不适用。代码不会把 key 写入节点输出、工作流或日志。

## 输入与约束

- `text_prompt`：必填，1–3000 字符；20 种语言；可用 `[5.5s:8.0s]` 一类时间提示。
- `reference_mode`：text only / audio reference / image reference / preset voice。
- 音频参考：最多 3 段，每段最长 30 秒、10 MB；prompt 按顺序使用 `@Audio1`–`@Audio3`。ComfyUI 音频会编码为单声道 16-bit WAV。每个槽也可填 `http(s)` 音频 URL 或 Seed Speech speaker ID。
- 图像参考：单张图或公开 HTTPS URL，不可和音频参考混用；本地图像必要时自动缩放到约 16 万至 2048×2048 像素范围，再转为 JPEG 内联发送，限制 10 MB。该模式下 prompt 应放要说的文本和台词，不使用 `@AudioN`。
- 预设音色：`preset_voice` 填 TTS 2.0 或克隆 speaker ID；此模式不使用 `@AudioN`。纯文本模式描述期望的声线，不要填写参考 source 字段。
- `sample_rate`：BytePlus 支持 8000/16000/24000/32000/44100/48000 Hz；火山引擎的 `wav/pcm` 还支持 40000 Hz，`mp3` 沿用其余采样率，`ogg_opus` 仅允许 48000 Hz。节点会拒绝不支持的 provider/format/rate 组合。
- `speech_rate`、`loudness_rate`：-50 至 100；`pitch_rate`：-12 至 12。
- `audio_format`：wav / mp3 / ogg_opus / pcm；响应解码为 ComfyUI AUDIO。
- `enable_subtitle` 开启后返回原始字幕 JSON 和由服务端时间戳转换的 SRT；关闭时这两个输出为空。
- 支持可听/元数据水印及水印标识字段。`generation_count` 可生成 1–16 条独立 take，每条分别计费；`seed` 只触发 ComfyUI 重算，不是服务端随机种子。官方 API 单次输出上限 120 秒。

## 安装与限制

项目源代码：`/home/sean/projects/comfy-ops/custom_nodes/ComfyUI-SeedAudio-BytePlus`。ComfyUI 扫描目录通过软链加载此目录。节点包中 `example_workflows/Seed Audio 1.0 - Text to Audio.json` 是画布模板，会在节点加载后进入模板列表。增加软链后需由 Hive0 的 ComfyUI 服务卡片安排重启，才会加载新节点和模板；Agent 不直接重启共享服务。在线请求还需先安全配置 Seed Speech API key，且需用户确认计费 smoke。

`workflows/seed_audio_byteplus_api.json` 是 ComfyUI API Prompt 格式，可交给 API runner 或 `POST /prompt` 执行；它不是用于画布直接导入的 UI 布局 JSON。

## 官方依据

- BytePlus Seed Speech Audio 1.0 API：`POST https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/create`；`X-Api-Key` 认证；API 接受 `model`、`text_prompt`、`references`、`audio_config`、`watermark`。
- [火山引擎豆包语音音频生成 API](https://docs.volcengine.com/docs/DoubaoVoice/audio-generation-http?lang=zh) 与 [BytePlus Seed Speech Audio 1.0 API](https://docs.byteplus.com/en/docs/byteplusvoice/seedaudio-01) 的模型名、路径、`X-Api-Key` 头及主要主体参数一致，但域名与控制台不同；节点按所选 provider 使用对应域名和独立 API Key。
- 参数上限、参考输入模式及输出字段按官方 API 文档和官方 ComfyUI 节点参考实现核对。
