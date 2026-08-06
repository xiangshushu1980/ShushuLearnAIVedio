# 12. 音频+文字 → 生成视频管线（辩论讲解视频实战）

> 目标：把一段**音频旁白 + 演讲文字**制作成"插画分镜 + 逐帧动画 + 字幕 + 背景音乐/音效"的视频。
> 2026-08-05 实战（comfy-ops，辩论结构讲解 133s）。所有脚本在 `.pi/agents/speech-video/`。

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

## 2. 关键脚本（都在 `.pi/agents/speech-video/`）

| 脚本 | 用途 |
|------|------|
| `gen_scenes.py` | 读 scenes JSON → 批量调 ComfyUI KREA 生图（1024×576） |
| `assemble_video.py` | 读 scenes JSON → 静态/微动切段 → 拼接 → 混音频 → 烧字幕 |
| `animate_frame.py` | 单帧 Wan2.2 I2V Lightning 动画（图→上下文运动视频） |
| `animate_batch.py` | 批量动画全部帧 |
| `gen_bgm.py` | 本地 MusicGen-small 生成背景音乐 |
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
- 脚本产物：`.pi/agents/speech-video/`
