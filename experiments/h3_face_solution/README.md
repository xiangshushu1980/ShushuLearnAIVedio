# H3 远处小脸修复实验

日期：2026-09-20。目标：在本地 RTX 4090 / ComfyUI H3 上验证远处人物脸糊的可用方案。

## 当前结论

当前已验证一条可用基线：单人场景使用 YOLO 最大脸检测/平滑轨迹，512 方形 crop，H3 局部重采样 `crop_factor=3.0`、`denoise=0.35`，再 `face_only` stitch 回原视频。5 个时间点视觉检查中脸部细节更清楚，眼睛、鼻口、胡须和轮廓稳定，完整视频无明显贴回边缘或身份漂移。多视图/Contact Sheet 参考图路线可以稳定身份和侧面结构，但单独使用没有明显锐度增益；全画面二次采样和直接 1024 输出均能生成，但仍偏软。

## 已研究/下载

- [ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine)：逐帧裁脸、H3 重采样、贴回原视频；本地已有节点。
- [ComfyUI-MiniMax-H3-Studio](https://github.com/thaakeno/ComfyUI-MiniMax-H3-Studio)：单帧 Face Refine/YOLO/SAM，已下载到 `/tmp/h3-face-research`，未装入共享实例。
- [ComfyUI-MiniMaxH3_LatentUpscaler](https://github.com/Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler)：H3 两阶段之间的 2x latent upscale，已下载，未装入共享实例。
- [H3_HD_2K_Detailer](https://huggingface.co/zuanfilm/H3_HD_2K_Detailer)：latent upscale + RES4LYF 低步数二采，已下载，缺额外节点/模型，未装入共享实例。
- 本地 H3 ContactSheet 节点和 `minimax_h3_five_view_512_s1500.safetensors` 已可运行。

## 本地对照

| 实验 | 结果 | 资源/备注 |
|---|---|---|
| ContactSheet 五视图生成 | 成功；五视图身份一致 | 512，约 40 秒 |
| Ref2VA：单身份图 / Contact Sheet / 五视图 | 三条均成功 | 768×448、124 帧、约 155 秒/条，峰值约 23.0–23.1GB |
| 全画面二采 denoise 0.20 | 成功但锐度提升不明显 | 1024×576，约 275 秒，峰值约 23GB |
| 直接 1024 Ref2VA | 成功；局部观感略好但仍偏软 | 1024×576，约 245 秒，峰值约 23.1GB |
| FaceRefine 单人 crop_factor 2.0 / 512 / denoise 0.25 | 未完成 | CPU 身份跟踪超过 12 分钟，显存约 21.8GB，无 OOM；已中断 |
| FaceRefine 快速轨迹 crop_factor 2.0 / denoise 0.25 | 可生成，锐度增益有限 | 124 帧，约 80 秒，峰值约 23GB |
| **FaceRefine 快速轨迹 crop_factor 3.0 / denoise 0.35** | **通过当前基线** | 768×448、124 帧、约 75 秒，峰值约 23GB；5 个时间点检查稳定 |

## 结论边界

社区共识是“头部在画面中的像素占比”比输出分辨率更关键；超分不能凭空恢复未生成的身份细节。当前推荐的本地路线是：单人时用普通 YOLO 最大脸检测得到平滑轨迹，再每帧 crop → H3 低去噪重采样 → face-only stitch；默认参数为 512 canvas、crop_factor 3.0、denoise 0.35、20 steps。避免对 124 帧逐帧运行 InsightFace 身份匹配。多人、快速转头、遮挡和大幅运动仍需单独验证。通用 ESRGAN/4x-ClearReality 不作为主方案。

资源约束：H3 共享实例串行运行；4090 25.8GB 总显存，以上完整 H3 实验未 OOM。`hive-resource` 守护命令本轮超时，因此以 ComfyUI `/system_stats`、`/queue` 和 `nvidia-smi` 做直接观测。

## 证据

- [H3 官方讨论：wide shot 脸问题](https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30)
- [B 站：远景防崩脸](https://www.bilibili.com/video/BV1HdgV6BEyM/)
- [B 站：Self-lift 双采样](https://www.bilibili.com/video/BV1aLe76REZE/)
- [B 站：潜空间二次采样修复远景小脸](https://www.bilibili.com/video/BV1GR8i6TEjT/)

## 第二阶段：768 动态 denoise / 多人 / 动态侧脸

根据 [X 社区方案](https://x.com/sunbaolong_2001/status/2098316708515917961)，把本地节点升级为：

```text
H3FaceSelect 或 H3FaceTrackCrop
→ 768×768 crop
→ H3InjectVideoLatent
→ H3PerFrameDenoise
→ H3 采样
→ face-only H3FaceStitch
```

`H3PerFrameDenoise` 使用源视频脸高动态调节强度：小脸 multiplier=1.0，大脸 multiplier=0.35，脸高 30–120px 插值，`smooth_frames=9`。本地 4090 上 768 canvas、base denoise 0.40、8 steps、124 帧约 100 秒，峰值约 23.1GB，无 OOM。

验证结果：

- 单人动态侧脸：新增正面→三分之二侧脸→近侧面→回正素材；768 动态修复成功，抽查五个时间点身份、耳朵、鼻梁、下颌和胡须连续，跟踪 preview 框连续移动，无明显抖动/丢脸，贴回自然。输出：`/home/sean/projects/ComfyUI/output/face_solution/dynamic_side_refined_768_c3_s08_00001_.mp4`。
- 多人：对既有双人素材按人物分别串行处理，每人使用自己的参考图；两遍均成功，抽查首帧/中段/末帧未串脸，未破坏另一人。输出：`/home/sean/projects/ComfyUI/output/face_solution/two_person_subject0_then_subject1_dynamic_00001_.mp4`。
- VOSR2：X 方案确认其可作为最后的 1x 细节增强，但本机没有本地 VOSR2 节点/模型；本次以 H3 局部 768 重采样作为本地等效增强，未使用云端 VOSR2。

## 2026-09-21：reference 职责分离复测

- 修订了单人希尔瓦娜斯拉远提示词：`<Subject>` 只做角色/环境绑定，`<Picture>` 明确声明为对应视觉 reference 的唯一权威；不在镜头描述中重复人物外观。
- 发现 FaceRefine 的跟踪 reference 与 H3 重绘 reference 必须分开：脸部裁图只接 `CLIP Vision identity_reference`，完整人物图接 H3 局部重绘的 `ref_images.ref_image_0`。
- 修订后的母片：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_solo_pullback_source_768_00005_.mp4`；分离 reference refine：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_solo_pullback_refined_separated_refs_00001_.mp4`。
- 分离 reference refine 成功，124 帧约 110 秒；母片与 refine 平均 PSNR 约 44.0，首/中/尾帧未见背景或人物整体被重新改写。该结果支持“脸部跟踪 reference 与 H3 object reference 分离”的实现方向；远景脸的细节增益仍需逐帧局部放大对照。

## 最终边界

当前流程已验证单人动态侧脸和稳定双人场景。仍不保证快速转头、严重遮挡、硬切镜头、多人交叉遮挡；这些场景应启用 identity_track/身份参考或分镜切段。多人必须每人单独跑一遍并串行累积 stitch，不能用一个最大脸节点同时处理所有人。768 比 512 更清晰但显存接近 23GB，4090 上应保持串行，8 steps 是当前安全基线。

## 远景复测结论（2026-09-20）

用严格远景生成样本复测：两人全身、环境主导、源脸约 30–50px。普通最大脸选择会漏掉兜帽角色并选中英雄；改为 `H3FaceTrackCrop` 的 `closest_to_xy` 初始坐标锚点 + 时间平滑后，左右人物均可分别锁定。两人的 768 局部精修都能稳定贴回，但对这种极小源脸，视觉细节增益几乎不可见。当前本地 H3 流程的可靠结论是“解决跟踪/贴回”，不是“从极少像素恢复身份细节”；要真正改善需 VOSR2/专用 1x 细节模型，或在生成阶段提高头部像素占比。

## 1344 中景→远景复测

用单镜头连续慢速 pull-back 重新测试，输出 1344×768：开头为可读中景，中段转为宽景，末尾头部约 40–60px 的远景。8 steps 母片和 768 局部动态 refine 均在 RTX 4090 上完成；母片约 230 秒、局部 refine 约 106 秒，均无 OOM。对比显示中景阶段有轻微 refine 增益，进入远景后增益迅速消失；1344 让对比更容易观察，但不能突破源脸像素信息上限。

追加小步移动/转头测试：两人各做一步小位移并从正面转向自然三分之二侧脸，同时继续拉远。8 steps 母片和 Sylvanas 局部 refine 均成功，1344×768 输出保持稳定；抽查首/中/末帧未见跳脸、明显融脸或贴回抖动。该动态量级在当前链路内可通过，但远景细节恢复上限不变。此前 `pullback_1344_probe` 为 4 steps 资源探测版，不能与 8 steps 正式结果比较画质。

追加 8 秒大幅回望测试：英雄从正面开始，头部和上半身明显转向后方，随后保持背向并继续拉远；192 帧、1344×768、8 steps 母片及英雄局部 refine 均成功。正脸→大角度转头→后脑/背向过程中没有跳脸或明显融化，背向阶段也没有错误生成一张新脸。时长增加使最终景别进一步拉远，但远景细节恢复仍受源像素限制。

追加 10 秒动作/远景测试：开头即宽景，英雄先摇头，再转为完整背面并继续完成 360° 旋转，同时镜头大幅拉远到真正远景。240 帧、1344×768、8 steps 母片和英雄局部 refine 均成功；这次景别变化明显，动作过程可见。远景末段 refine 仍主要负责稳定跟踪与贴回，不能从极小脸源像素中恢复新细节。

追加西瓦抬头/低头/转身测试：10 秒、240 帧、1344×768、8 steps 母片中，西瓦依次抬头、低头并转向背面，同时镜头拉到远景；Sylvanas 局部 refine 保持了三段动作和稳定贴回。母片出现的蓝色能量与黑色粒子是 H3 自带生成效果，不属于 refine。
