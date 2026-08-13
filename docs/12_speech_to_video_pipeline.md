# 12. 音频+文字 → 生成视频管线（辩论讲解视频实战）

> 目标：把一段**音频旁白 + 演讲文字**制作成"插画分镜 + 逐帧动画 + 字幕 + 背景音乐/音效"的视频。
> 2026-08-05 实战（comfy-ops，辩论结构讲解 133s）。所有脚本在 `.pi/tasks/speech-video/`。
> 2026-08-11 并入原 docs/13（BGM/音效/混音/降噪）→ 本章 §10-§13。

## 1. 全流程概览

```
音频(m4a) + 文字
   │ ① whisper 转写 → 时间轴 + SRT
   ▼
分镜脚本(内容对齐)   ← 每帧=一个讲解主题的时间窗，非固定时长
   │ ② KREA 扁平插画生图 (1024×576)
   ▼
22 张分镜图
   │ ③ Wan2.2 I2V Lightning 逐帧动画（上下文运动）
   ▼
22 条动画片段 (~4.5s/条)
   │ ④ ffmpeg setpts 拉伸对齐帧时长 → 拼接
   ▼
完整视频(静态或动画) + 字幕烧录 + 文字层叠加
   │ ⑤ 音频混音：降噪旁白 + 分段BGM + 音效
   ▼
成品
```

## 2. 关键脚本（都在 `.pi/tasks/speech-video/`）

| 脚本 | 用途 |
|------|------|
| `gen_scenes.py` | 读 scenes JSON → 批量调 ComfyUI KREA 生图（1024×576） |
| `assemble_video.py` | 读 scenes JSON → 静态/微动切段 → 拼接 → 混音频 → 烧字幕 |
| `animate_frame.py` | 单帧 Wan2.2 I2V Lightning 动画（图→上下文运动视频） |
| `animate_batch.py` | 批量动画全部帧 |
| `gen_bgm.py` | 本地 MusicGen-small 生成背景音乐（见 §10） |
| 数据文件 | `transcript.json` `subtitles.srt` `subtitles_hms.srt` `scenes_v3.json` `motion_map.json` `animation_plan.md` `storyboard.md` |

## 3. 步骤一：whisper 转写（faster-whisper-small）

```bash
# m4a 先转 16k 单声道（m4a 直接转写可能 0 段）
ffmpeg -i 音频.m4a -ac 1 -ar 16000 narr.wav
python3 - <<'EOF'
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
seg, _ = model.transcribe("narr.wav", beam_size=5, language="en")
# 输出 {start,end,text} → 手工对回演讲原文（转写有误差）
EOF
```

- ⚠️ **SRT 时间戳必须 `HH:MM:SS,mmm` 全格式**，`MM:SS,mmm` 会让 ffmpeg 报 `Invalid data`（字幕滤镜打不开文件多半是 SRT 格式问题，不是路径问题）
- 转写文本有 ASR 误差，**用用户提供的原文为准**，时间轴借转写的

## 4. 步骤二：分镜脚本（内容对齐，关键）

- **帧边界 = 旁白停顿点**，每帧只在该句被讲的时间窗内显示，时长随内容浮动（2.2~11.6s）
- 不要硬凑"每帧5s"——会导致画面和旁白长时间错位
- 粒度：讲解是逐句讲规则/概念的，适合一句/一帧；短句相邻合并
- 产物：`scenes_v3.json`（id/s/e/prompt），`storyboard.md`（可读表）

## 5. 步骤三：KREA 生图（1024×576 扁平插画）

```bash
python3 gen_scenes.py scenes_v3.json --prefix img_debate4
```

- 模型：`krea2_turbo_fp8` + `qwen3vl_4b_fp8_scaled` + `qwen_image_vae`，8步/er_sde/cfg1
- **⚠️ 关键踩坑：prompt 禁用 "speaker" 一词** —— 会被画成**音箱**！用 `debater`/`panelist`/`person`
- 负面词必加：`loudspeaker, audio speaker, speaker device, megaphone, no devices`
- 风格前缀：`flat design, minimalist vector illustration, smooth clean shapes, muted warm palette, 16:9, no text, no watermark`

## 6. 步骤四：逐帧动画（Wan2.2 I2V Lightning，最快管线）

- **模型**：GGUF Q4 高/低噪 UNet + lightx2v 4步 LoRA + umt5-xxl 编码器 + wan_2.1_vae
- **参数**：832×480，16fps，73帧(~4.56s)，steps 6（两段 KSamplerAdvanced 各3步）
- **生成速度**：~1.5-2min/条（CPU 推理），22帧 ~40min
- **动画提示词 = 上下文运动**（`motion_map.json` / `animation_plan.md`）：讲"攻击"就射箭、讲"轮流"就拨开关、讲"看钟"就转指针。人物一律是辩论者
- 工作流连接要点（易错）：
  - `WanImageToVideo` 输出**3 路**：`[0]positive [1]negative [2]latent`
  - `KSamplerAdvanced` 的 positive/negative 从 `[12,0]/[12,1]`，latent 从 `[12,2]`
  - `SaveVideo` 输入是 **`video`**（不是 images），来自 `CreateVideo`
- 每帧可多出几版备选（换 seed / 换运动措辞）

## 7. 步骤五：合成

- 每条动画 4.56s，需按内容对齐帧时长调整：`setpts=PTS*(帧时长/4.56)`（拉伸=慢动作/缩短=加速），`-t 帧时长`
- concat 拼接（concat filter 重编码）→ 总时长 133s 与音频同步
- 字幕烧录：`subtitles=SRT:force_style=...`（需绝对路径）
- 文字层：ffmpeg drawtext（辩题卡/环节徽标/片尾），`enable='between(t,a,b)'` 控时间

## 8. 最终成品

- 静态+声音：`debate_final_sound.mp4`
- 动画+声音：`debate_final_animated.mp4`（832×480）
- ComfyUI Output 可看：`video/debate_final_*.mp4`

## 9. 目录/命名规范

- 分镜图：`ComfyUI/output/img_debate4/`（F01~F22）
- 动画片段：`ComfyUI/output/video/debate_anim/`
- 脚本产物：`.pi/tasks/speech-video/`

## 10. BGM 两条路径（本地 MusicGen / ComfyUI ACE-Step）

| 路径 | 模型 | 位置 | 质量/速度 |
|------|------|------|-----------|
| **A. 本地 MusicGen-small** | `facebook/musicgen-small` | transformers CPU，模型已缓存 | 好，30s≈3min |
| **B. ComfyUI ACE-Step 1.5** | `ace_step_1.5_ComfyUI_files` | ComfyUI generate_audio | 更高，需4个模型 |

### 路径 A：本地 MusicGen-small（实战用的）

- 模型在 HF 缓存：`~/.cache/huggingface/hub/models--facebook--musicgen-small/`（hyperframe 项目曾用，已缓存）
- 脚本：`gen_bgm.py`（transformers + CPU，**不依赖 scipy**，用标准库 `wave` 写 wav）
- MusicGen **50 tokens/秒**；`max_new_tokens = 时长×50`；15s=760 tokens；输出 32kHz mono wav
- 用法：`python3 gen_bgm.py "prompt" 30 out.wav`

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
processor = AutoProcessor.from_pretrained("facebook/musicgen-small", local_files_only=True)
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small", local_files_only=True)
audio = model.generate(**inputs, max_new_tokens=1500)[0,0].cpu().numpy()  # 30s
```

- 实战按环节分 3 段不同氛围（舒缓立论/紧凑质询/温暖总结），各 25-30s
- ⚠️ `scipy` 未装，写 wav 用标准库 `wave`，别用 scipy.io.wavfile

### 路径 B：ComfyUI ACE-Step 1.5

- 工具：`comfyui_generate_audio`（model_family="ace_step_1.5"）
- 模型 4 个（`Comfy-Org/ace_step_1.5_ComfyUI_files`，放 `models/` 对应目录，**已下载且校验通过 2026-08-07**）：
  - `acestep_v1.5_xl_turbo_bf16.safetensors` → diffusion_models/ (~10GB)
  - `ace_1.5_vae.safetensors` → vae/ (337MB)
  - `qwen_0.6b_ace15.safetensors` → text_encoders/ (~922MB) —— **最容易下载损坏**
  - `qwen_4b_ace15.safetensors` → text_encoders/ (~8.4GB)
- qwen 0.6b=音乐主干编码，qwen 4b=细节/歌词/复杂结构

**ACE-Step 下载踩坑（Xet 仓库）**：
- **HF CLI 连不上 hf-mirror 拉 Xet 仓库（401）**：hf-mirror 只做签名 HTTP 重定向，HF CLI 的 Xet 客户端走 xet-auth 授权流代理不了 → 401
- **正确做法**：`wget -c --tries=0 --timeout=30 --waitretry=5` 跟随 GET 重定向直接下签名 CDN 字节（实测 11-18MB/s）；或设 `HF_HUB_DISABLE_XET=1` 走经典 HTTP
- **断点续传可能产生损坏文件**：文件大小看着对但 safetensors header 不完整。**必须校验**：`python -c "import safetensors.torch as st; st.load_file('文件')"` 能过才算完整
- hf-mirror.com 某时段 DNS 解析到日本 IP 且国内直连不通 → 换 huggingface.co 直连（官方直连时 HF CLI/wget 正常）

## 11. 混音（ffmpeg）

```bash
# BGM 随人声闪避（sidechain，关键参数）
[bgm][narr]sidechaincompress=threshold=0.1:ratio=4:attack=20:release=500[bgmduck]
# BGM 音量 0.5~0.6（太小听不见，太大盖人声）
[narr][bgmduck][sfx]amix=inputs=3:normalize=0,alimiter=limit=0.95
```

- ⚠️ **sidechain 阈值别设太低**（如 threshold=0.03 会让 BGM 全程被压到听不见）；0.1 + ratio 4 较好
- BGM 分段（对应环节）交叉淡入淡出：`acrossfade=d=1`

## 12. 音效合成（ffmpeg，免下载）

| 音效 | 生成 | 要点 |
|------|------|------|
| 转场"咻" | `aevalsrc=sin(2*PI*(800+3200*t/0.4)*t)` 扫频 | 300-800Hz 基频会闷，用 800→4000Hz 更清脆 |
| ding | `sine=f=1800` + 衰减 | 1200Hz 偏闷 |
| gavel | `sine=f=120` + 衰减 | 低频敲击 |
| applause | 白噪声 + lowpass | 近似 |

- 摆放：`adelay=Ns:all=1` + `amix=normalize=0`
- ⚠️ 转场 whoosh **别每个帧切换都放**（会变成持续噪声），只在**大环节切换**放 3 处

## 13. 降噪

- 旁白间隙底噪先测：`ffmpeg ... -af volumedetect` 看 max_volume
- 实测：间隙 RMS -39.8dB（挺干净），-19dB 是瞬时瞬态（咂嘴/咔哒），**FFT 降噪降不掉瞬态**，重降噪无意义
- 只做轻量 `highpass=f=80` + `afftdn=nf=-45` 去低频隆隆
