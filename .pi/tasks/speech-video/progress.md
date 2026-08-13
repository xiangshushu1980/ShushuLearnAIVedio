# 任务进度：speech-video（辩论结构演讲稿 → 视频）

## 任务
- 目标：把 08-05-2026 23.04.m4a（133s 辩论结构讲解）做成视频 ✅
- 当前状态：✅ 完成
- 交付物：`comfy-ops/debate_video_final.mp4`（1024×576, 30fps, 133.3s, h264+aac, 8MB）
- ComfyUI 可查看副本：`ComfyUI/output/video/debate_structure_video.mp4`（Output 浏览器可见）

## 方案（用户决策 2026-08-07）
- 画面：KREA 扁平插画风 + 横屏 16:9 + 烧英文字幕
- 结构：7 分镜（开场标题/第一辩/第二辩/质询总览/质询规则/质询轮换/总结辩），每段 zoompan 微动
- H3/数字人未用：H3 只能生成自带语音的画面，无法同步用户固定音频；本机无口型模型
- 补充信息做成画面文字层：开场叠加辩题卡、各环节加时间徽标(2.5/2.5/3/4min)、片尾投票收束

## 产物文件（.pi/tasks/speech-video/）
- transcript.json（whisper 时间轴 31 段）、subtitles.srt + subtitles_hms.srt（烧录用，须 HH:MM:SS 格式）
- narr.wav（音频 16k 单声道转写副本）
- anima_sample.png / krea_sample.png（风格小样）
- segments/ 7 段 zoompan 无声片段 + silent_full.mp4
- ovl/ 文字层（topic/badges/closing）

## 踩坑（2026-08-07）
- ffmpeg SRT 解析：时间戳必须 HH:MM:SS,mmm 全格式，MM:SS,mmm 会报 Invalid data
- 字幕滤镜打不开文件多半是 SRT 格式问题，不是路径
- 声音在 comfy-ops 根目录，脚本要用绝对路径

## 下一步
- 用户审片：可调整文字层位置/字号、微动幅度、加转场、换封面
- 文档沉淀：`docs/12_speech_to_video_pipeline.md`（视频管线）+ `docs/13_bgm_music_production.md`（音乐制作）已建，待新对话复用
- ACE-Step BGM：**4 个模型全部下载完成且 safetensors 校验通过**（2026-08-07 复核）：diffusion_models 9.3G + vae 322M + qwen_0.6b 1.2G + qwen_4b 7.9G，无 wget 进程残留。可随时对比重出 ACE-Step 版 BGM

## BGM 重做进展（2026-08-07 执行）

### V1（已废弃）
- ACE-Step 1.5 版 6 段 BGM，acrossfade 1s 拼接 → `bgm_full_ace.wav`，对比版 `debate_final_acebgm.mp4`
- 用户反馈：**衔接不紧密（质询内部 57.7/82.2s 拍脑袋拆段）+ 音乐复杂抢占说话空间**

### V2（当前）
- **重生成简单风**：prompt 改 minimal/ambient（sparse/very simple/low-key/去复杂声部），质询段一次 60s 长生成成功（ACE-Step 支持 60s+），接缝只剩 4 个且全部对齐环节边界（6/37.8/97.8/114s）
- **环节边界修正**：立论 6-37.8s（非 33.2）、质询 37.8-114s（非 102.4）、总结 114-133.3s（F20 才是 SUMMARY 标题卡）
- **混音三改**：BGM 音量 0.55→0.4；sidechain 加强 threshold 0.07/ratio 6/attack 15/release 600；BGM 加 highpass 50 + equalizer 2.5kHz -4dB 让中频
- **对比版**：`assets/debate_final_acebgm_v2.mp4` + ComfyUI 副本 `output/video/debate_final_acebgm_v2.mp4`
- 待用户试听对比（旧 MusicGen 版 / V1 / V2）

## 关键约束（用户决策 2026-08-07，后续必须遵守）
- 这是**辩论**演讲，画面里的 speaker = **辩论者**（1辩/2辩/3辩，正方/反方），不是普通演讲者
- 图片转视频时，**每帧动画必须由对话上下文驱动**（见 `animation_plan.md`）：讲攻击就射箭、讲轮流就拨开关、讲看钟就转指针，动作贴合该句语义
- 27 帧新分镜（~5s/帧）已生成：`img_debate3/`，成品 `debate_v2_27frames.mp4`
- BGM：方案A，ACE-Step 1.5 下载中（huggingface.co 直连；hf-mirror 的 SSL 当前不通已换源）

## BGM 重做 runbook（新对话接续用）

**状态**：ACE-Step 1.5 **4 模型全部就绪且校验通过**（无 wget 残留，复核 2026-08-07）：
- `diffusion_models/acestep_v1.5_xl_turbo_bf16.safetensors` (9.97G)
- `vae/ace_1.5_vae.safetensors` (337M)
- `text_encoders/qwen_0.6b_ace15.safetensors` (1.19G，曾损坏已修好)
- `text_encoders/qwen_4b_ace15.safetensors` (8.38G)

**步骤**（只重做音乐时不必重做画面）：
1. 读手册 `docs/13_bgm_music_production.md`（ACE-Step 用法/混音参数/音效合成）+ `docs/12` 合成节
2. 路径选择：A) ComfyUI `generate_audio` ACE-Step 1.5（模型就绪，质量高）；B) 本地 MusicGen `experiments/speech-video/scripts/gen_bgm.py`（快但质量低一档）
3. 生成分段 BGM 对应环节（开场/立论/质询/总结），acrossfade 拼接成 bgm_full.wav
4. 混音：`narr_denoised.wav` + 新 BGM + SFX → sidechaincompress（threshold≈0.1-0.12, ratio 3-4）→ amix → final_audio.wav
5. 换音轨：`ffmpeg -i 成品视频 -i final_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac`（不动画面只换音频）
6. 对比试听后选版；收尾更新本文件 + [STATE] + git commit

**现有素材**：`experiments/speech-video/assets/`（narr_denoised.wav 旁白、sfx_*.wav 音效、bgm_seg1/2/3.wav 旧 MusicGen 版）
