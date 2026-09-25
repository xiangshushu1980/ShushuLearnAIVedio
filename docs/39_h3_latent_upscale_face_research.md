# H3 远景人脸：像素局部修复与完整视频 latent 二采复核

> 记录日期：2026-09-20
> 任务：T-comfy-ops-45

## 当前结论

社区存在两条不同路线：

1. **像素裁脸 → 局部视频 latent → H3 二采 → 贴回**：`ComfyUI-H3-FaceRefine` 的路线。它逐帧检测、跟踪并裁切人脸，再把连续脸部视频送回 H3，适合只处理指定人脸和多人串行处理。当前 comfy-ops 已验证该路线在 4090 上可用，但 30–50px 远景脸的细节增益有限。
2. **完整视频 latent 直接放大 → H3 二采**：社区已有 MiniMax H3 latent upscaler 节点和权重。它绕过 `latent → VAE → 像素放大 → VAE → latent` 的往返，适合一采低分辨率、二采高分辨率的全视频流程；默认作用于完整视频 latent，不是只作用于人脸 ROI。

目前没有找到成熟、主流、专门用于 MiniMax H3 的“人脸 latent ROI 局部二采后再合并”的公开标准工作流。因此本任务第一优先级采用社区已有的**完整视频 latent 两阶段**路线测试，不把它误称为局部人脸 latent refine。

## 为什么测试完整 latent 二采

- 保留一采 latent 中的运动和时序信息，减少像素解码/重新编码损失；
- 验证远景脸是否能在不单独重画脸的情况下改善或至少保持稳定；
- 与当前 FaceRefine 结果做同一源视频对照；
- 如果全视频 latent 二采仍导致远景脸漂移，则说明问题来自 H3 二采本身，而不是 FaceRefine 的像素裁切往返。

## 社区证据

- [ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine)：逐帧跟踪、裁脸、H3 重生成、贴回；按源脸大小调整 denoise。
- [rockerBOO/h3-latent-upscaler](https://github.com/rockerBOO/h3-latent-upscaler)：MiniMax H3 视频 latent 在两次采样之间直接空间放大，并提供 Ref2VA/FL2VA 两阶段示例。
- [xmarre/Comfyui_Minimax_h3_latent_Upscaler-Plus](https://github.com/xmarre/Comfyui_Minimax_h3_latent_Upscaler-Plus)：学习型 3D latent upscaler，明确以绕过 VAE 解码/编码往返为目标，并支持放大后短 H3 refine。
- [社区远景脸 V2V 讨论](https://www.reddit.com/r/comfyui/comments/1vt47a6/minimax_h3_v2v_fixing_faces_at_distance/)：另一条实测路线是低分辨率视频再次 H3 V2V、低步数/低 denoise；报告同时指出对白时嘴部动作可能受损。

## 本地状态

- 本机原先没有 H3 latent upscaler 节点或权重。
- 已安装本地节点：`/home/sean/projects/ComfyUI/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler`。
- 权重下载目标：`/home/sean/projects/ComfyUI/models/latent_upscale_models/`。
- 4090 作为共享单实例资源使用；完整 latent 二采会显著增加目标分辨率下的 token 和显存，先做短片 smoke，再做正式对照。

## 验收重点

本测试不以远景“变清晰”为唯一成功标准，重点观察：

- 远景脸是否比原始视频更漂移或变形；
- 头部转动、表情和人物运动是否保留；
- 连续帧是否闪烁；
- 背景和身体是否被不必要地改变；
- 与当前 FaceRefine 相比，是否减少 VAE 往返造成的损失。

未来提示词继续使用正向描述，不使用负面提示词；本实验比较的是工作流，不通过提示词控制人脸修复。

## B 站第一轮复核（2026-09-20）

B 站检索命中说明，社区实际集中在四条路线：完整 latent 二采、latent upscaler 与 H3 节点组合、FaceRefine 局部重绘，以及 VOSR2/Flash VSR 一类生成后处理；另有 SLA 加速模型声称原生改善中远景小脸，但它应单独作为模型路线验证。

- [H3 远景人物脸部修复](https://www.bilibili.com/video/BV1wSbB6sEqQ)：简介明确组合 `Comfyui_Minimax_h3_latent_Upscaler` 与 `ComfyUI-YCNodes-MiniMax-H3`。
- [latent upscale 修复远景小脸](https://www.bilibili.com/video/BV1GR8i6TEjT)：简介给出 FL2VA、Ref2VA 的 latent-upscale 工作流入口。
- [H3 极速二采高清流](https://www.bilibili.com/video/BV1dMuQ6cEKM)：简介指向 T8 节点和 latent merge。
- [二次采样 vs Flash VSR](https://www.bilibili.com/video/BV12Auq6MEvk)：适合拆分“生成阶段二采”和“生成后超分”的效果边界。
- [SLA 加速模型与中远景小脸](https://www.bilibili.com/video/BV1g68264Ejn)：属于模型/采样加速路线，不能直接等同于脸部局部修复。
- [FaceRefine + VOSR2](https://www.bilibili.com/video/BV1oXYL6ZE9V)：属于局部重绘叠加后处理的组合，待确认本地可运行性和对 30–50px 远景脸的真实收益。

这些视频的标题和简介支持“社区确实在使用二采和 latent upscaler”，但 B 站评论接口本轮超时，尚未把视频内节点连线、参数和评论口碑视为已验证事实。当前脸部劣化研究线单独记录和验证这些局部人脸方案，不并入全局二采任务。

### 新发现：BV1uveq6CEo3

[MiniMax H3 小脸崩坏怎么修？ComfyUI 局部人脸重绘完整教程](https://www.bilibili.com/video/BV1uveq6CEo3) 展示的是局部人脸路线，不是纯全局 latent 二采：`H3 Face Track + Crop` 检测跟踪人脸，配合人物四视图/六视图 identity reference，把局部人脸视频送入 H3，并通过 `H3 Inject Video Latent` 保留原视频动作、角度、光照和时序；之后用 `H3 Face Frame Denoise` 重绘，再 `H3 Face Stitch Back` 融回全局视频，最后可接 `VOSR 2.0 Upscale` 做后处理。

这解释了它为什么可能比当前全局 latent 二采更能处理远景脸：它在脸部区域增加了独立身份条件，而不是只放大已经劣化的全局 latent。当前仅确认了视频画面中的节点链路，尚未确认 30–40px 多人转头场景的稳定收益；该路线作为 46 任务的对照，不改变 46 研究全局二采的目标。

## 本地 VOSR 2.0 smoke（2026-09-22）

- 安装完成：`/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-VOSR2`；VOSR2 1.4B DiT、Qwen-Image 2D VAE、DINOv2-L 均已落盘并被 ComfyUI object info 识别。
- 单图基线：输入 `1024x1024` Sylvanas face reference，`fp16`、`seed=42`、`color_alignment=wavelet`、DiT tile `512/64`、VAE tile `1024/128`。2x 成功约 13s，输出 `2048x2048`；4x 成功约 25s，输出 `4096x4096`；均无 OOM，目视未见明显 tile seam。
- seed 对照：相同输入 2x、seed 42/43 均成功，构图和身份保持，局部生成细节有轻微变化；因此不应把逐帧独立使用视为天然时序锁定。
- 视频批处理 smoke：取现有 H3 片段前 3 帧，先缩为 `512x288`，VOSR2 2x 输出 3 张 `1024x576` 图像，成功；这只证明 ComfyUI IMAGE batch 链路可用，**不等于已证明长视频时序稳定性**。
- 产物：`/home/sean/projects/ComfyUI/output/vosr2_quick_2x_00001_.png`、`vosr2_quick_4x_00001_.png`、`vosr2_quick_2x_seed43_00001_.png`、`vosr2_quick_clip_3frames_2x_00001_.png`–`00003_.png`。
- 当前定位：VOSR2 适合做生成后图像/短批次细节重建；对完整视频仍需另做长段帧间闪烁、身份漂移和动作保持验收，不能替代 H3 latent 二采或专门的时序视频超分结论。
