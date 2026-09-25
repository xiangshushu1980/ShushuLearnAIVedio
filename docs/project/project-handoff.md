# Comfy-Ops 项目交接文档

更新时间：2026-09-04

## 1. 项目定位

Comfy-Ops 是围绕 ComfyUI 的本地视频生成研究与工具化项目，重点验证三类能力：

1. 剧本和拍摄本驱动的视频生成流程；
2. 插画、动作、音频、字幕和音乐的成片合成；
3. 以 H3 为主线的粤语音频驱动数字人，以及 LongCat、DUIX 等外部方案评估。

项目主要面向本地 RTX 4090 环境。模型权重、ComfyUI 运行目录和视频输出通常位于项目外部，不属于本仓库的轻量交接包。

## 2. 调研工作简要总结

### 2.1 环境、模型与基础设施

- 建立了 ComfyUI 本地运行、API 调用、工作流提交和输出检查方式。
- 梳理了 H3、Wan2.2、KREA、ANIMA、Bernini、Music3/ACE-Step 等模型和工作流。
- 记录了模型下载、显存、CPU/RAM、量化、低显存启动和常见节点连接问题。
- 建立了脚本化跑批、结果检查、视频拼接和音频处理工具。

入口文档：[`docs/01_environment.md`](../01_environment.md)、[`docs/02_models.md`](../02_models.md)。

### 2.2 H3 提示词、IR 和拍摄本

- 研究了 H3 官方提示词结构、IR（中间表示）和参考图/参考音频的约束方式。
- 将剧本转换为导演拍摄本，再转换为 H3 三核心段或 Ref2VA 六段式提示词。
- 研究了角色卡、实体、参考图、镜头主体、声音和 BGM 描述的结构化注入。
- 形成了提示词校验、引用标色和拍摄本验收规则。

相关文档：[`docs/08_h3_prompt_agent.md`](../08_h3_prompt_agent.md)、[`docs/16_prompt_generator_plan.md`](../16_prompt_generator_plan.md)、[`docs/17_h3_prompt_writing_rules.md`](../17_h3_prompt_writing_rules.md)、[`docs/21_pipeline_acceptance.md`](../21_pipeline_acceptance.md)。

### 2.3 速度、连续性和画质优化

- 对 H3 的采样步数、量化、EasyCache、CondCache、Spectrum、Sage/注意力优化等进行了对比。
- 验证了不同参考路径、长段生成、Motion Context 续接、FaceRefine 和 latent 放大等方案。
- 当前结论是：Spectrum 的推荐范围是标准 20 步档；数字人生产候选优先采用稳定的 H3 FL2VA/PDD + MC 链，而不是把所有加速插件默认叠加。
- 对连续生成中的亮帧、身份漂移、音画错位、重复 context 和错误音频时间窗进行了专项排查。

相关文档：[`docs/09_h3_test_plan.md`](../09_h3_test_plan.md)、[`docs/10_h3_batch_optimization.md`](../10_h3_batch_optimization.md)、[`docs/h3-digital-human-research/`](../h3-digital-human-research/)。

### 2.4 音频与成片

- 研究了 Whisper/faster-whisper 转写、SRT 时间轴、旁白降噪、BGM、音效、sidechain ducking 和最终混音。
- 对本地 MusicGen-small 与 ComfyUI ACE-Step 1.5 进行了比较。
- 结论和参数均以实验记录为准，不能把单次样片直接视为生产保证。

相关文档：[`docs/12_speech_to_video_pipeline.md`](../12_speech_to_video_pipeline.md)、[`docs/26_music3_audio_quality.md`](../26_music3_audio_quality.md)。

## 3. 视频生成工作流

### 3.1 剧本 → 拍摄本 → H3 提示词 → 渲染输入

这是项目中最接近产品化的一条工作流，由 `web-shotlist/` 实现：

```text
剧本/世界观/参数头
        ↓
实体抽取、角色卡和参考图
        ↓
工具 A：生成导演拍摄本
        ↓
人工编辑镜头、主体、连续性和时间轴
        ↓
工具 B：生成 H3 提示词
        ↓
引用校验、输入源展示、导出渲染参数
        ↓
ComfyUI H3 / Ref2VA / FL2VA 工作流
```

主要代码：

- `web-shotlist/apps/web/`：剧本、拍摄本、时间轴、提示词和实体库界面；
- `web-shotlist/apps/server/src/tools/shotlistGen.ts`：剧本到导演拍摄本；
- `web-shotlist/apps/server/src/tools/promptStage2.ts`：拍摄本到 H3 提示词；
- `web-shotlist/apps/server/src/tools/templates.ts`：提示词模板；
- `web-shotlist/packages/shared/src/shotlistSchema.ts`、`promptSchema.ts`：共享校验结构；
- `web-shotlist/apps/server/src/store.ts`、`entities.ts`：项目和实体资源管理。

该工具已经完成多轮端到端验证，但仍属于项目内工具，不应描述为已经完成商业化产品。API schema、候选池、多视图参考图和部分 UI 收尾仍有后续空间。

### 3.2 音频/文字 → 分镜 → 动画 → 成片

该路线用于 2026-08-05 的辩论结构讲解视频，最终完成约 133 秒样片：

```text
旁白音频 + 演讲文字
        ↓ Whisper 转写和时间轴
分镜 JSON / storyboard
        ↓ KREA 生成扁平插画
多张分镜图
        ↓ Wan2.2 I2V Lightning
逐帧动画片段
        ↓ ffmpeg 按旁白时长调整、拼接
字幕 + 文字层 + BGM + 音效 + 旁白混音
        ↓
最终 MP4
```

原始任务记录：`.pi/tasks/speech-video/`。其中 `progress.md` 记录了 7 段版本、27 帧版本、BGM 重做和最终输出信息；完整方法说明见 [`docs/12_speech_to_video_pipeline.md`](../12_speech_to_video_pipeline.md)。

项目中可查询的相关脚本包括：

- `scripts/video_gallery.py`：视频结果查看/整理辅助；
- `scripts/h3_audio_sep.py`、`scripts/h3_demucs.py`：音频分离；
- `scripts/run_music3.py`：Music3 相关运行入口；
- `experiments/speech-video/`：该路线的实验归档和素材说明。

部分早期实战脚本在任务目录或实验归档中，交接时应以文档和实际存在的文件为准，不应假设所有历史脚本仍是可直接运行的产品入口。

### 3.3 5C+ 辩论视频简单工作流

项目中存在辩论样例工作流：

- `workflows/sample_krea_debate.json`；
- `workflows/sample_anima_debate.json`。

其思路是先用 KREA 或 ANIMA 生成辩论主题插画，再通过图生视频工作流生成简单运动，最后进行片段拼接、字幕和音频处理。它属于 5C+ 辩论内容的实验性样例，没有固化为独立产品管线，也没有完整的项目级自动编排入口。

辩论视频还可参考：

- `workflows/wan2.2_i2v_lightning_test.json`；
- `workflows/sample_krea_debate.json`；
- `workflows/sample_anima_debate.json`；
- `docs/11_h3_case_library.md`；
- `docs/12_speech_to_video_pipeline.md`。

### 3.4 其他视频生成方向

仓库还保留了 Wan2.1/Wan2.2、Bernini、ANIMA、KREA、H3、LongCat 等实验工作流。它们主要用于模型对比、画面编辑、图生视频、视频编辑、参考图一致性和动作测试，不应全部视为同一条正式产品流程。

## 4. 数字人生成方案

### 4.1 当前主线：H3 本地数字人

H3 是项目当前最完整的本地数字人研究主线。典型方案为：

```text
真人/角色参考图 + 外部粤语 TTS 母带
        ↓
H3 FL2VA 或 Ref2VA
        ↓ NativeAudioLock
锁定外部音频对应的音频 latent
        ↓ Motion Context
连续生成下一段
        ↓
按 context 帧数裁切并重新挂回原始母带
```

关键判断：

- 外部粤语音频是口型、停顿、语速和最终音轨的时间真值；
- NativeAudioLock 是外部音频约束机制，不能与 H3 原生参考音频混称；
- FL2VA 更适合作为当前主线，Ref2VA 保留给多参考身份/声音条件场景；
- PDD Acc 8-step 已验证可用，并有明显速度收益；
- MC 可以实现短段连续生成，但并不能自动消除亮帧、身份漂移或音画错位；
- 每个续段必须使用自己切点前的音频预滚，不能错误复用上一段音频窗口；
- context 的裁切、音频时间线和视频帧数必须统一，否则会出现口型延迟或音画不同步。

主要工作流：

- `workflows/minimax_h3_i2v.json`；
- `workflows/minimax_h3_r2v.json`、`workflows/minimax_h3_ref2va_img_api.json`、`workflows/minimax_h3_ref2va_img_vid_api.json`；
- `workflows/h3v1_r2_audio_only.json`；
- `scripts/h3_fl_motion_context_runner.py`；
- `scripts/h3_mc_runner.py`；
- `scripts/h3_ref2v_runner.py`；
- `scripts/h3_facerefine_batch.py`。

详细研究资料：[`docs/h3-digital-human-research/README.md`](../h3-digital-human-research/README.md)、[`docs/27_DUIX_Avatar_数字人评估.md`](../27_DUIX_Avatar_数字人评估.md)。

### 4.2 LongCat 外部测试

LongCat 属于外部开源项目/独立测试方向。项目对其进行了方案和产能评估，结论是：生成式数字人效果具有参考价值，但在本机 4090 条件下速度和连续生产能力不适合作为当前主线。因此交接文档只保留评估结论、任务记录和对比定位，不复制 LongCat 源码。

可参考：`.pi/tasks/T-comf-01/`、`.pi/tasks/T-comfy-ops-27/` 及相关工作流文件。

### 4.3 DUIX 外部测试

DUIX-Avatar 是另一条路线：使用真人参考视频，通过音频驱动口型和脸部替换，属于低算力、接近实时的数字分身方案，不是 H3 式的生成式视频模型。它适合已有真人主播/演员的口播分身，和需要凭空生成虚拟角色的 H3 场景定位不同。

项目已有 DUIX 方案调研和评估文档：[`docs/27_DUIX_Avatar_数字人评估.md`](../27_DUIX_Avatar_数字人评估.md)、[`docs/28_数字人在线方案_对比与价位.md`](../28_数字人在线方案_对比与价位.md)。DUIX/LongCat 的开源工程代码不纳入本项目交接包。

## 5. 代码与资料索引

| 内容 | 位置 |
|---|---|
| 项目导航 | `docs/INDEX.md` |
| 环境与模型 | `docs/01_environment.md`、`docs/02_models.md` |
| H3 提示词与拍摄本 | `docs/08_h3_prompt_agent.md`、`docs/16_prompt_generator_plan.md`、`docs/22_shotlist_web_tool.md` |
| H3 工作流 | `workflows/minimax_h3_*.json`、`workflows/h3v1_*.json` |
| Wan/Bernini/ANIMA/KREA | `workflows/wan*`、`workflows/bernini*`、`workflows/anima*`、`workflows/krea*` |
| 视频与音频脚本 | `scripts/`、`experiments/speech-video/` |
| 拍摄本 Web 工具 | `web-shotlist/` |
| 数字人研究 | `docs/h3-digital-human-research/`、`docs/27_*`、`docs/28_*` |
| 任务进度与实验证据 | `.pi/tasks/`、`.pi/ledger/` |
| Git 全量记录 | [`git-history-handoff.md`](../archive/project/git-history-handoff.md) |

## 6. 打包建议

建议纳入：

- `docs/`、`scripts/`、`workflows/`、`web-shotlist/`；
- `experiments/` 中仍需查询的配置、JSON、说明和可复现实验记录；
- `.pi/tasks/` 中用于追溯结论的进度文件；
- Git 历史导出文件。

建议排除或单独存放：

- ComfyUI 模型权重、Hugging Face 缓存和 Docker 镜像；
- `/home/sean/projects/ComfyUI/output` 下的视频、图片和临时渲染结果；
- 外部 LongCat、DUIX 项目的源代码；
- API Key、登录信息、个人音频/视频原始素材和本机运行时状态；
- `web-shotlist/data/` 等本地项目数据（除非另行确认需要交付样例数据）。

## 7. 当前交接风险

- 当前分支 `main` 相对 `origin/main` 有本地提交，且工作树存在大量未提交、未跟踪和删除状态；打包前应先决定哪些实验要提交、哪些只归档。
- H3 数字人链路已多次成功，但连续长视频的亮帧、身份漂移、帧数尾差和音画同步仍需按最终验收标准复核。
- `docs/` 中部分内容是调研结论，部分内容是单次实验记录；交接时应以“事实/实测/推论”区分，不宜统一表述为生产承诺。
- Git 全量记录只反映提交历史，不包含未提交工作树内容；当前工作树状态已在 Git 导出文件中单独记录。
