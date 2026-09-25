# 任务进度：h3-face-fix

> 任务：2026-08-14 修理脸崩——远处人物动作时脸崩坏（H3 通病：头部占画面比例小则脸崩，与分辨率无关，Comfy-Org discussions/30 确认）
> 队列占用：待跑批前声明

## 任务
- 目标：解决"远处人物动作脸崩"。候选方案：① 二阶采样工作流（B 站 BV1HdgV6BEyM：原模型一阶低像素→超分→LoRA 二阶 denoise 0.2→100 万像素）② 超分+FaceRefine 组合（超分后检测更稳）③ 1344×768 高分辨率直接生成（改善有限）④ 分镜规避（非修复）
- 当前状态：🟡 调研与方案确认中
- 我负责的文件区：`.pi/tasks/h3-face-fix/`、ComfyUI output/video/h3_r2v/、/tmp 工作流

## 进度日志（append-only，每条带日期）
### 2026-08-14
- **背景沉淀**：H3 脸崩=头部占比小（非分辨率问题，720p+ 依旧）；FaceRefine（Carasibana）官方参数在单人场景可用（T1d 干净 30s）但**双人场景检测乱飞+不稳定**（用户否决，暂停）
- **方案库**：① 二阶采样（B 站教程，一阶原模型 6 步→英伟达超分(4090 报 -12 换 fresr)→二阶 v1.0 LoRA denoise 0.2→100 万像素；结论=二阶>直接一阶 100 万像素；时间=编解码重复为主要开销；工作流：本地版夸克 pan.quark.cn/s/26f1caa9ee9、线上 runninghub.cn/post/2086816639672213505）② 超分+FaceRefine ③ 高分辨率 ④ 规避
- 参考：ComfyUI-H3-FaceRefine 已装；Florence-2 反推已装（场景级）；对比图统一放 ~/projects/ComfyUI/output/compare/

## 下一步
1. 抓 runninghub 线上工作流结构（节点+参数），本地复刻二阶采样
2. 测本地超分方案：fresr / 英伟达 VideoUpscaler（-12 错确认）
3. 跑对比：直接 1024 vs 二阶采样 vs 超分+FaceRefine，用户目视
4. 结论入 mem0 + skill 手册

## 关键链接
- B 站教程: https://www.bilibili.com/video/BV1HdgV6BEyM/（字幕 /tmp/bili_ref2v/text.txt）
- 线上工作流: https://www.runninghub.cn/post/2086816639672213505
- 本地工作流网盘: https://pan.quark.cn/s/26f1caa9ee9
- 官方讨论: https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30
- FaceRefine: https://github.com/Carasibana/ComfyUI-H3-FaceRefine
### 2026-08-14（挂起）
- **方案确认**：H3InjectVideoLatent（FaceRefine 仓库节点）= 通用 img2img 入口（docstring 确认"encodes real frames into the video stream → ordinary img2img"，denoise 用 BasicScheduler 控制）——二阶采样本地复刻路线已规划：一阶原模型 6 步@960×544 → ClearReality 4x 逐帧超分（本地已装 4x-ClearRealityV1）→ 缩放 1344×768（32 对齐）→ 注入 + v1.0 LoRA + denoise 0.2 → 采样
- **用户指示：之后再测试，现在先放着**（⏸ 挂起）
- 已跑：P1_pass1_960_6step（一阶产物，output/video/h3_r2v/，留作后续输入）
