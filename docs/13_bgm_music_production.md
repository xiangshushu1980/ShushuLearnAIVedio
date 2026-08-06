# 13. 背景音乐制作（MusicGen 本地 + ACE-Step/ComfyUI）

> 视频背景音乐（BGM）制作的两条路径。2026-08-05 实战。
> 相关文件在 `.pi/agents/speech-video/`。

## 1. 两条路径

| 路径 | 模型 | 位置 | 质量/速度 |
|------|------|------|-----------|
| **A. 本地 MusicGen-small** | `facebook/musicgen-small` | transformers CPU，模型已缓存 | 好，30s≈3min |
| **B. ComfyUI ACE-Step 1.5** | `ace_step_1.5_ComfyUI_files` | ComfyUI generate_audio | 更高，需4个模型 |

## 2. 路径 A：本地 MusicGen-small（本次实际用的）

- 模型在 HF 缓存：`~/.cache/huggingface/hub/models--facebook--musicgen-small/`
  （来源：hyperframe 项目曾用 MusicGen 生成 BGM，模型已缓存）
- 脚本：`gen_bgm.py`（transformers + CPU，**不依赖 scipy**，用标准库 `wave` 写 wav）
- MusicGen **50 tokens/秒**；`max_new_tokens = 时长×50`；15s=760 tokens
- 输出：32kHz mono wav
- 用法：`python3 gen_bgm.py "prompt" 30 out.wav`

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
processor = AutoProcessor.from_pretrained("facebook/musicgen-small", local_files_only=True)
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small", local_files_only=True)
audio = model.generate(**inputs, max_new_tokens=1500)[0,0].cpu().numpy()  # 30s
```

- 生成了 3 段不同氛围对应环节：舒缓(立论)/紧凑(质询)/温暖(总结)，各 25-30s
- ⚠️ `scipy` 未装，写 wav 用标准库 `wave`，别用 scipy.io.wavfile

## 3. 路径 B：ComfyUI ACE-Step 1.5

- 工具：`comfyui_generate_audio`（model_family="ace_step_1.5"）
- 模型 4 个（`Comfy-Org/ace_step_1.5_ComfyUI_files`，放 `models/` 对应目录）：
  - `acestep_v1.5_xl_turbo_bf16.safetensors` → diffusion_models/ (~10GB)
  - `ace_1.5_vae.safetensors` → vae/ (337MB)
  - `qwen_0.6b_ace15.safetensors` → text_encoders/ (~922MB) —— **最容易下载损坏**
  - `qwen_4b_ace15.safetensors` → text_encoders/ (~8.4GB)
- qwen 0.6b=音乐主干编码，qwen 4b=细节/歌词/复杂结构

## 4. ACE-Step 下载踩坑（Xet 仓库）

- **HF CLI 连不上 hf-mirror 拉 Xet 仓库（401）**：hf-mirror 只做签名 HTTP 重定向，HF CLI 的 Xet 客户端走 xet-auth 授权流代理不了 → 401
- **正确做法**：`wget -c --tries=0 --timeout=30 --waitretry=5` 跟随 GET 重定向直接下签名 CDN 字节（实测 11-18MB/s）
- 或设 `HF_HUB_DISABLE_XET=1` 走经典 HTTP
- **断点续传可能产生损坏文件**：文件大小看着对但 safetensors header 不完整。**必须校验**：`python -c "import safetensors.torch as st; st.load_file('文件')"` 能过才算完整
- hf-mirror.com 某时段 DNS 解析到日本 IP 且国内直连不通 → 换 huggingface.co 直连（官方直连时 HF CLI/wget 正常）

## 5. 混音（ffmpeg）

```bash
# BGM 随人声闪避（sidechain，关键参数）
[bgm][narr]sidechaincompress=threshold=0.1:ratio=4:attack=20:release=500[bgmduck]
# BGM 音量 0.5~0.6（太小听不见，太大盖人声）
[narr][bgmduck][sfx]amix=inputs=3:normalize=0,alimiter=limit=0.95
```

- ⚠️ **sidechain 阈值别设太低**（如 threshold=0.03 会让 BGM 全程被压到听不见）；0.1 + ratio 4 较好
- BGM 分段（对应环节）交叉淡入淡出：`acrossfade=d=1`

## 6. 音效合成（ffmpeg，免下载）

| 音效 | 生成 | 要点 |
|------|------|------|
| 转场"咻" | `aevalsrc=sin(2*PI*(800+3200*t/0.4)*t)` 扫频 | 300-800Hz 基频会闷，用 800→4000Hz 更清脆 |
| ding | `sine=f=1800` + 衰减 | 1200Hz 偏闷 |
| gavel | `sine=f=120` + 衰减 | 低频敲击 |
| applause | 白噪声 + lowpass | 近似 |

- 摆放：`adelay=Ns:all=1` + `amix=normalize=0`
- ⚠️ 转场 whoosh **别每个帧切换都放**（会变成持续噪声），只在**大环节切换**放 3 处

## 7. 降噪

- 旁白间隙底噪先测：`ffmpeg ... -af volumedetect` 看 max_volume
- 实测：间隙 RMS -39.8dB（挺干净），-19dB 是瞬时瞬态（咂嘴/咔哒），**FFT 降噪降不掉瞬态**，重降噪无意义
- 只做轻量 `highpass=f=80` + `afftdn=nf=-45` 去低频隆隆
