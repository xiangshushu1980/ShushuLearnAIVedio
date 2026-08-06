# 试验项目：speech-video（音频+文字 → 生成视频）

> 第一个 OP 试验项目（2026-08-05）。把一段**辩论讲解音频 + 演讲稿文字**制作成插画分镜 + 逐帧动画 + 字幕 + BGM/音效的视频。
> 详细手册见 `docs/12_speech_to_video_pipeline.md`、`docs/13_bgm_music_production.md`。

## 目录结构

```
experiments/speech-video/
├── assets/        # 成品视频 + 最终音频 + BGM分段 + 音效 + 风格样图
├── scripts/       # 管线脚本
│   ├── gen_scenes.py      # KREA 批量生图
│   ├── assemble_video.py  # 静态/微动切段+拼接+混音+烧字幕
│   ├── animate_frame.py   # Wan2.2 I2V 单帧动画
│   ├── animate_batch.py   # 批量动画
│   └── gen_bgm.py         # 本地 MusicGen 生成 BGM
└── data/          # 分镜/场景/运动映射/字幕/转写
    ├── scenes_v3.json     # 内容对齐分镜（22帧）
    ├── motion_map.json    # 每帧上下文运动提示词
    ├── animation_plan.md  # 逐帧动画设计
    ├── storyboard.md      # 分镜可读表
    ├── subtitles_hms.srt  # 烧录用字幕（HH:MM:SS格式）
    └── transcript.json    # whisper 转写时间轴
```

## 成品

- `assets/debate_final_animated.mp4` —— 动画版（22帧 I2V，832×480，133s）
- `assets/debate_final_sound.mp4` —— 静态+声音版
- 动画片段源：`ComfyUI/output/video/debate_anim/`
- 分镜图源：`ComfyUI/output/img_debate4/`

## 管线速览

```
whisper 转写 → 内容对齐分镜 → KREA 生图 → Wan2.2 I2V 逐帧动画 → ffmpeg 合成 → 字幕+文字层 → 混音(BGM+音效+降噪)
```

## 关键参数/坑

- 生图 prompt 禁 "speaker"（会画成音箱），用 debater
- SRT 时间戳必须 HH:MM:SS
- WanImageToVideo 输出3路，SaveVideo 用 video 输入
- sidechain 闪避阈值别设 0.03（BGM 被压没），用 0.1
- 转场 whoosh 只在环节切换放（3处），别每帧放
- BGM 本地 MusicGen（scipy 未装用 wave 写文件）；ACE-Step 可选
