# 任务进度：T-comfy-ops-45

> 目标：落盘 H3 远景人脸修复复核结论，并测试第一优先的完整视频 latent 两阶段放大方案。

## 2026-09-20

- 完成社区复核：确认已有两条公开路线。
  - `ComfyUI-H3-FaceRefine`：像素裁脸后形成局部视频 latent，再 H3 二采和贴回。
  - `rockerBOO/h3-latent-upscaler` / `xmarre/Comfyui_Minimax_h3_latent_Upscaler-Plus`：完整 H3 视频 latent 直接放大，再进行第二阶段 H3 refine。
- 修正此前表述：社区已有完整 latent 二采，但尚未找到成熟的 H3 人脸 latent ROI 局部二采标准工作流。
- 新增结论文档：`docs/39_h3_latent_upscale_face_research.md`。
- 检查本机：原先没有 latent upscaler 节点或模型；4090 当前约占 18GB、利用率 0%，ComfyUI 共享单实例仍在。
- 已克隆本地节点：`/home/sean/projects/ComfyUI/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler`。
- 已下载 `LBH-123-AI/Minimax_h3_latent_Upscaler` 本地 BF16 权重；已重载 ComfyUI 并完成节点注册。

## 2026-09-20 测试结果

- 已安装本地节点：`/home/sean/projects/ComfyUI/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler`。
- 已下载并注册 BF16 权重：`/home/sean/projects/ComfyUI/models/latent_upscale_models/minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors`。
- ComfyUI 注册节点：`MinimaxH3LatentUpscaler3D`、`MinimaxH3LatentUpscaler3DRefineHandoff`。
- 49 帧 smoke 成功：约 130.5 秒，输出 `sylvanas_hero_latent_two_pass_768_to_1344_smoke_00001_.mp4`，56 帧/2.33 秒，1376×800，音频正常。
- 同 seed、同正向提示词的一采源片成功：`sylvanas_hero_latent_two_pass_768_source_00002_.mp4`，768×448，56 帧/2.33 秒。
- 124 帧/5.17 秒正式测试成功：约 125.1 秒，输出 `sylvanas_hero_latent_two_pass_768_to_1344_full_00001_.mp4`，124 帧，1376×800，音频正常；显存观测约 22.9/24.6GiB，无 OOM。
- 视觉初判：完整 latent 二采保持远景构图和人物位置，未见明显跳脸、强制近景化或错误重画；远景脸仍然模糊，细节增益有限，符合“远景不追求清晰”的目标。需要与同源 5 秒的一采/当前 FaceRefine 做更严格的逐帧脸部局部对照后，才能确定是否比当前 FaceRefine 更稳定。
- 输出尺寸注意：请求 1344×768 时，当前节点/H3 对齐实际生成 1376×800；后续若生产需要 1344×768，应增加最终裁剪或调整目标网格，不能把这次输出标记为严格 1344×768。

## 待完成

- 确认权重文件完整、节点注册成功、现有 H3 Ref2VA 两阶段工作流可加载。
- 以现有远景拉远源片做短片 latent 二采 smoke。
- 抽帧/视频对比原片与当前 FaceRefine，记录脸部稳定性、动作保留、闪烁和显存峰值。
- 如测试通过，再做正式同源对照并补充结果。
