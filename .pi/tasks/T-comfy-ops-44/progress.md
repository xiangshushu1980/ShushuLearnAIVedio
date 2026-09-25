# 任务进度：T-comfy-ops-44

> 目标：升级 H3 脸部修复为可复用的动态/多人流程。

## 2026-09-20

- 新目标来源：X 社区 768×768 crop、动态 per-frame denoise、VOSR2、feather stitch 方案。
- 待执行：复现 768 crop；实现按脸框大小动态且时间平滑 denoise；测试动态侧脸和多人；评估 VOSR2 或本地等效节点。
- X 原帖核验：[@sunbaolong_2001 的 H3 FaceRefine + VOSR2 方案](https://x.com/sunbaolong_2001/status/2098316708515917961)明确使用 YOLOv8-Face、768×768、动态逐帧 denoise、VOSR2 和 feather stitch；回复指出 crop jitter、identity drift、denoise 曲线需要平滑。
- 发现本地 `ComfyUI-H3-FaceRefine` 已内置 `H3PerFrameDenoise`：按源视频脸高在 30–120px 间插值，默认小脸 multiplier=1.0、大脸=0.35、smooth_frames=9；此前通过基线没有接入该节点。
- 已成功测试 512 动态 denoise：`crop_factor=3.0`、BasicScheduler base denoise=0.40、20 steps，124 帧约 70 秒，显存约 23GB。
- 已成功测试 768 动态 denoise：768 canvas、base denoise=0.40、8 steps，124 帧约 100 秒，显存约 23.1GB，无 OOM。输出：`/home/sean/projects/ComfyUI/output/face_solution/face_crop_dynamic_768_c3_base040_s08_00001_.mp4`。
- 已用既有两人视频验证串行多人链路：第 0 张脸处理后，再把第一遍输出作为第二遍输入处理第 1 张脸；两遍各约 80 秒，抽查双人脸未串脸、未破坏对方。输出：`/home/sean/projects/ComfyUI/output/face_solution/two_person_subject0_then_subject1_dynamic_00001_.mp4`。
- 当前仍缺动态侧脸/遮挡的专门输入；多人测试采用稳定双人站姿，证明了串行流程，不等同于复杂动态场景已通过。
- 已生成专门动态侧脸素材：正面→三分之二侧脸→近侧面→回正；原始 H3 768×448/124 帧约 155 秒、峰值 23.1GB。
- 用 768 canvas、crop_factor=3.0、base denoise=0.40、8 steps、H3PerFrameDenoise（small=1.0、large=0.35、30–120px、smooth=9）修复成功，约 100 秒、峰值 23.1GB。五个时间点检查身份、耳朵、鼻梁、下颌和胡须连续。
- 导出 FaceTrackCrop preview 检查跟踪框：正面→侧面→回正时框连续移动，无明显跳框、抖动或丢脸；贴回视频无明显边缘穿帮。输出：`/home/sean/projects/ComfyUI/output/face_solution/dynamic_side_refined_768_c3_s08_00001_.mp4`。
- 多人串行流程已验证：每人独立参考图、独立 crop/H3/face-only stitch，第二遍接第一遍输出；双人首帧/中段/末帧未串脸。VOSR2 本机无节点/模型，采用 H3 768 局部重采样作为本地等效增强。
- 最终边界：快速转头、严重遮挡、硬切和多人交叉遮挡仍未覆盖；768 canvas 4090 峰值约 23.1GB，必须串行，8 steps 为安全基线。
- 用户追问后补跑完整 768 多人串行版：第 0 张脸约 115 秒，第 1 张脸约 111 秒；两遍均 768 crop、base denoise=0.40、8 steps、per-frame denoise，最终 124 帧/768×448，峰值约 23GB，无 OOM。三处时间点抽查双人均保留且未串脸。输出：`/home/sean/projects/ComfyUI/output/face_solution/two_person_768_subject0_then_subject1_dynamic_00001_.mp4`。
- 本机搜索未发现 VOSR2 节点或模型；X 方案的 VOSR2 更像云端/RunningHub环节，不是当前 ComfyUI 中漏放的一个已知本地权重。当前本地等效方案仍是 H3 768 局部重采样。

### 远景真实性复测（2026-09-20）

- 为避免中景掩盖问题，按 H3 六段式写了简要远景生成提示词：`experiments/h3_face_solution/sylvanas_hero_far_prompt.txt`。两人全身、环境占主导、头部约 30–50 个源像素、明确禁止中近景；输出：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_far_wide_source_00001_.mp4`。
- 纠正本地精修提示词：`subject_definitions` 只定义 `<Subject 1>` 身份；`detailed_description` 只引用 `<Subject 1>` / `<Video 1>`，描述原位、动作、镜头与局部修复，不重复角色外观，不改景别。文件：`experiments/h3_face_solution/far_face_edit_prompt.txt`。
- 普通 H3FaceSelect 在远景中漏掉左侧兜帽角色，错误地把右侧英雄作为目标。新增 `tools/h3_face_crop_direct_runner.py`，使用 VHS 原视频帧 + `H3FaceTrackCrop` 的 `closest_to_xy` 坐标锚点和时间平滑跟踪；预览确认三处时间点均锁定左侧角色，没有跳到英雄。
- 远景英雄和左侧角色均完成 768 局部精修（base denoise 0.40、8 steps、crop_factor 3.0）。结果：构图、跟踪、贴回正常，但极小脸的可见身份细节提升几乎不可见。结论是本地 H3 crop→重采样→stitch 可以防止串脸和抖动，不能单独解决源脸仅 30–50px 时的信息缺失；需 VOSR2/专用超分细节模型或在生成阶段提高人物头部占比才能真正改善。
- 当前 ComfyUI 注册的 `fallback_detector` 列表没有人体分割模型，故本次采用低置信度脸检出 + 坐标锚点；远景兜帽角色预览已通过，但背身/完全遮脸仍需额外人体检测器或手工 ROI。

### 1344 中景→远景连续复测（2026-09-20）

- 新增简短 Ref2VA 提示词：`experiments/h3_face_solution/sylvanas_hero_pullback_1344_prompt.txt`。唯一主动作是同一镜头连续慢速 pull-back；开头中景可读，末尾远景，禁止切镜和重新描述角色外观。
- 1344×768、124 帧、8 steps 正式母片生成成功，约 230 秒，无 OOM：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_00001_.mp4`。抽查首/中/末帧确认景别连续拉远，不是直接开在极远景。
- 在该 1344 母片上用坐标锚点跟踪左侧角色，局部仍使用 768 canvas、crop_factor=3、base denoise=0.40、per-frame denoise、8 steps，最终输出保持 1344×768：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_sylvanas_refined_00001_.mp4`。
- 对比结论：中景阶段局部 refine 有轻微面部清晰度/轮廓改善；随着 pull-back 进入 40–60px 头部尺寸，增益快速减弱，远景阶段仍不能恢复新的身份细节。1344 提高了母片整体清晰度和对比可见性，但不改变“小脸源信息不足”的上限。

### 1344 小步移动 + 转头复测（2026-09-20）

- 新提示词：`experiments/h3_face_solution/sylvanas_hero_pullback_1344_motion_turn_prompt.txt`。在连续拉远同时加入每人一步小位移和从正面到自然三分之二侧脸的转头，仍保持单镜头和简短 Ref2VA 六段式。
- 8 steps、1344×768 母片生成成功：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_motion_turn_00001_.mp4`。
- 左侧 Sylvanas 使用坐标锚点 + 768 局部动态 refine，最终仍为 1344×768：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_motion_turn_sylvanas_refined_00001_.mp4`。
- 首/中/末帧检查：小步和转头被保留，跟踪未跳到英雄，无明显融脸、丢脸或贴回抖动；中景有轻微细节收益，拉远后收益仍快速降低。
- `sylvanas_hero_pullback_1344_probe_00001_` 明确标记为 4-step 资源探测版，不作为画质基线；正式画质对照使用 `final8` 和本次 `motion_turn` 8-step 结果。

### 8 秒大幅回望复测（2026-09-20）

- 为增加拉远距离，将时长扩展到 8 秒（192 帧），并新增提示词 `experiments/h3_face_solution/sylvanas_hero_long_pullback_lookback_prompt.txt`：英雄先正面出现，随后头部和上半身明显转向后方回望，保持回望姿态并继续慢速拉远。
- 1344×768、8 steps 母片成功，约 415 秒，无 OOM：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_long_pullback_lookback_00001_.mp4`。首/中/末帧确认正面→背向回望→更远景的过程成立。
- 以英雄参考图为目标做 768 局部动态 refine，输出仍为 1344×768：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_long_pullback_lookback_hero_refined_00001_.mp4`。正脸到大角度转头再到后脑/背向阶段均未跳脸、未明显融化；背向后没有虚构新脸。

### 10 秒摇头 + 背转 + 360° + 远景复测（2026-09-20）

- 针对上一版“视频变化不明显、景别仍近”的反馈，新增 `experiments/h3_face_solution/sylvanas_hero_wide_headshake_turn_360_prompt.txt`：开头即宽景，0–2 秒摇头，2–5 秒转至完整背面，5–9 秒完成一圈旋转，镜头全程大幅 pull-back，末帧头部目标 30–40px。
- 10 秒、240 帧、1344×768、8 steps 母片成功，约 595 秒，无 OOM：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_headshake_turn_360_00001_.mp4`。抽查 0/2/5/8/10 秒：宽景开场、明显背转、旋转过程和最终远景均可见，景别变化明显大于上一版。
- 英雄 768 局部动态 refine 成功：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_headshake_turn_360_hero_refined_00001_.mp4`。正面到背面、旋转及远景贴回稳定；远景末段脸部像素极少，refine 视觉增益几乎消失，但没有错误生成正脸或跳脸。

### 西瓦抬头 + 低头 + 转身复测（2026-09-20）

- 新提示词：`experiments/h3_face_solution/sylvanas_hero_wide_head_up_down_turn_prompt.txt`。西瓦按抬头、低头、身体转向三段动作执行，英雄仅作轻微反应，镜头继续大幅拉远。
- 10 秒、240 帧、1344×768、8 steps 母片成功：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_head_up_down_turn_00001_.mp4`。抽帧确认抬头、低头、转身和远景变化均可见；母片额外出现蓝色能量/黑色粒子效果，属于 H3 生成结果。
- 以 Sylvanas 为目标的 768 局部动态 refine 成功：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_head_up_down_turn_sylvanas_refined_00001_.mp4`。三段动作跟踪稳定，无跳脸、明显融化或错误补正；进入远景后仍主要体现稳定贴回，细节增益受源像素限制。
