# T-comfy-ops-46：H3 二采与远景脸防糊方案深度探索

## 目标

系统研究 H3 的二采方案，并以“远处脸部劣化”作为第一验收场景：比较不同二采方式如何影响远景脸的面具化、身份漂移、变形、闪烁、朝向和动作连续性。

任务范围仍包括二采的完整链路、latent 放大方式、二采采样参数、条件/reference 传递、不同 H3 模式以及必要的后处理对照；不把任务改成单独的人脸检测或局部修复研究。二采速度、显存、整体画质也继续记录，但远处脸部稳定性是首要质量指标。

## 已知基线（2026-09-20）

- 当前已验证路线：768×448 一采 latent → 本地 BF16 学习型 3D latent upscaler → H3 4-step 二采，`refine_denoise=0.40`，锁定音频。
- 124 帧正式样本约 125.1 秒，峰值约 22.9/24.6 GiB，无 OOM；请求 1344×768 时实际输出 1376×800（H3/VAE 对齐）。
- 相比此前直接 1344×768、8-step、约 230 秒的基线，约快 45%。
- 运动、构图和人物位置稳定，未见明显跳脸或强行近景重画；但远处约 30–50 px 的脸仍偏面具化，细节增益有限。
- 结论：完整视频 latent 二采主要解决速度、时序和 VAE 往返损失，不自动补足远景缺失的身份细节；一采已是面具状时，二采会继承这一结构。

## B 站第一轮线索

- [BV1wSbB6sEqQ](https://www.bilibili.com/video/BV1wSbB6sEqQ)：`Comfyui_Minimax_h3_latent_Upscaler` + `ComfyUI-YCNodes-MiniMax-H3`，宣称用于 H3 远景人脸修复。
- [BV1GR8i6TEjT](https://www.bilibili.com/video/BV1GR8i6TEjT)：介绍 latent upscale 修复远景小脸，并给出 FL2VA、Ref2VA 工作流线索。
- [BV1dMuQ6cEKM](https://www.bilibili.com/video/BV1dMuQ6cEKM)：H3 极速二采高清流，远景细节；简介指向 T8 节点和 latent merge。
- [BV12Auq6MEvk](https://www.bilibili.com/video/BV12Auq6MEvk)：对比二次采样与 Flash VSR，适合后续拆解“生成阶段修复”和“生成后超分”的差异。
- [BV1g68264Ejn](https://www.bilibili.com/video/BV1g68264Ejn)：SLA 加速模型，宣称原生中远景小脸不崩；需与真正的人脸修复路线分开验证。
- [BV1BSeJ6gE1C](https://www.bilibili.com/video/BV1BSeJ6gE1C)、[BV1Pw8H6jEUv](https://www.bilibili.com/video/BV1Pw8H6jEUv)、[BV1a3eS6mEJp](https://www.bilibili.com/video/BV1a3eS6mEJp)：FaceRefine 路线。
- [BV1oXYL6ZE9V](https://www.bilibili.com/video/BV1oXYL6ZE9V)：FaceRefine + VOSR2 两阶段超清重绘，需确认 VOSR2 是后处理超分而非 H3 生成阶段修复。

评论抓取当前因 B 站视频信息接口超时未完成；上述是标题、简介和已保存元数据线索，不把简介中的效果宣称当作已验证结论。

## 下一步验收矩阵（以远处脸为核心场景）

1. 同源同 seed，对比直接高分辨率 H3、完整 latent 二采、不同 latent upscaler/二采参数、latent upscaler + YCNodes-H3，并以 FaceRefine/后处理作为对照。
2. 统一记录远景脸的身份漂移、脸型塌陷、五官错位、面具化、闪烁、朝向连续性和动作保持，同时记录速度、显存和整体画质。
3. 固定测试 30–40 px 正脸、侧脸、转头、多人远景，区分“源 latent 已经劣化”和“二采阶段再次劣化”。
4. 研究二采如何传递源 latent、人物 reference、动作/光照条件，以及不同 denoise、步数和放大倍率对远景脸的影响；不把后处理锐化误判为二采解决方案。
5. 核查 B 站工作流能否落地本机；不在线调用 VOSR2 或 Flash VSR，除非找到本地模型和节点。
6. 所有 H3 提示词保持正向描述，不加入负面提示词。
