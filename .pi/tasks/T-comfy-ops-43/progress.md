# 任务进度：T-comfy-ops-43

> 目标：寻找并在本地 RTX 4090 的 MiniMax H3 环境中测试通过远处人物脸糊解决方案。

## 2026-09-20

- 调研渠道：Bocha/Exa/Tavily 搜索、B 站搜索元数据、GitHub/Hugging Face 仓库 README 与官方讨论。重点覆盖 FaceRefine、Contact Sheet/多视图参考、H3 latent 二采、RES4LYF 二采、H3 Studio。
- 下载研究仓库到 `/tmp/h3-face-research/`：`ComfyUI-MiniMax-H3-Studio`、`ComfyUI-MiniMaxH3_LatentUpscaler`、`H3_HD_2K_Detailer`。未安装到共享 ComfyUI，避免无授权重启共享实例。
- 本地 ContactSheet 五视图生成成功；Ref2VA 单身份图、Contact Sheet、五视图三路均成功生成 768×448/124 帧视频，但五视图没有明显提升中远景脸部锐度，主要改善身份/侧面结构条件。
- 全画面二采 denoise 0.20 成功生成 1024×576 视频，面部没有决定性改善；直接 1024 Ref2VA 成功，局部略好但仍偏软。
- 尝试单人 FaceRefine：512 crop、crop_factor 2.0、denoise 0.25、身份参考 + InsightFace 逐帧跟踪。显存稳定约 21.8GB、无 OOM，但 CPU 预处理超过 12 分钟仍未出结果，已中断并确认共享队列清空。
- 改为单人 YOLO 最大脸 + 平滑轨迹，关闭逐帧身份跟踪后，`crop_factor=2.0, denoise=0.25` 成功完成 124 帧，约 80 秒，显存约 23GB；锐度增益有限。
- 参数优化为 `crop_factor=3.0, denoise=0.35` 后成功完成 124 帧、768×448，约 75 秒，峰值约 23GB。抽查首帧/1.25s/2.5s/3.75s/末帧：脸部细节更清楚，眼睛、鼻口、胡须和轮廓稳定，无明显贴回边缘或身份漂移。
- 阶段结论：当前 4090 的可用基线为“单人 YOLO 最大脸轨迹 + 512 crop + H3 denoise 0.35 + face-only stitch”。适用单人、固定或缓慢运动；多人、遮挡、快速转头仍需另测。输出：`/home/sean/projects/ComfyUI/output/face_solution/face_crop_refine_fast_c3_d035_00001_.mp4`。
