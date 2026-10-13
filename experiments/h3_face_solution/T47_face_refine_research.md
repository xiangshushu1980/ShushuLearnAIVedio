# T-comfy-ops-47：H3 远景/中景小脸 FaceRefine 防劣化研究

日期：2026-09-21  
执行环境：RTX 4090 24GB 级共享 ComfyUI-H3-FaceRefine 节点  
范围：脸部身份稳定、跟踪不串脸、局部重采样不面具化；不包含 T-46 全局 latent 二采。

## 最终推荐链路

```text
H3 生成：完整人物/object reference + 环境 reference
        ↓
源视频当前帧：H3FaceTrackCrop（平滑轨迹，必要时 closest_to_xy）
        ↓
脸部 identity：CLIP Vision identity reference（仅负责“是哪一个人”）
        ↓
局部 H3：原视频 crop 注入 latent，完整人物 reference 作为 H3 ref_image
        ↓
H3PerFrameDenoise → 768×768 crop → H3 8-step sampling
        ↓
H3FaceStitch（face_only，feather 6，串行多人）
```

职责必须分离：face-only 图只给跟踪/身份比较；完整人物图给 H3 局部重绘；原视频局部 latent 保留当前帧的姿态、角度、表情、光照和时间位置。不能把 face-only 图同时当作 H3 唯一 object reference，否则容易出现脸稳定但服装、头部造型或整体人物关系漂移。

## 已验证参数与资源

| 项目 | 当前安全基线 | 证据 |
|---|---|---|
| crop canvas | 768×768 | T44 动态侧脸、双人串行、远景复测 |
| crop factor | 3.0 | T43/T44 多轮成功 |
| sampler | `res_multistep`，8 steps | T44/T47 既有结果 |
| base denoise | 0.40 | T44 动态 per-frame 路线 |
| per-frame denoise | 小脸 1.0、大脸 0.35，30–120px，smooth 9 | T44 |
| stitch | `face_only`，feather 6，mask dilation 16 | T43/T44 |
| 追踪 | 单人平滑轨迹；多人每人独立轨迹；远景用 `closest_to_xy` 坐标锚点 | T43/T44 |
| 身份模型 | 3D/插画/游戏角色优先 CLIP Vision；不强行使用 InsightFace | T47 复测结论 |
| 资源 | 768 局部 124 帧约 100–115 秒，峰值约 23.0–23.1GB，无 OOM | T44/T47 |

768 路线必须串行运行。多人不可用“最大脸”一次处理所有人；每人独立 reference、独立 crop/refine/stitch，第二人以第一遍输出为输入。

## 验证矩阵与结论

### 1. 单人中景→远景连续拉远：通过（稳定性），部分通过（清晰度）

1344×768、8 steps 的连续 pull-back 母片上，768 局部 refine 在中景阶段有轻微清晰度和轮廓收益；进入头部约 40–60px 后收益快速下降。首/中/尾未见背景重写、跳脸、明显融脸或贴回抖动。结论：FaceRefine 能防劣化和稳定贴回，但不能突破源像素信息上限。

### 2. 真正 30–50px 远景小脸：通过（不漂移/不串脸），不通过（凭空恢复细节）

普通最大脸选择会漏掉兜帽角色并选中另一人；`closest_to_xy` 初始坐标锚点 + 时间平滑可以分别锁定左右人物。两人局部精修均可稳定贴回，视觉身份细节增益几乎不可见。验收标准应以“没有面具化、错误正脸、跳脸、融脸”为主，而不是要求高清。

### 3. 动态侧脸/抬头低头/转身：通过（当前覆盖动作量级）

正面→三分之二侧脸→近侧面→回正、抬头→低头→背向、正面→大角度转头→背向，以及 360° 转身+拉远均完成。抽查身份、耳朵、鼻梁、下颌、胡须和跟踪框连续，无明显丢脸、跳脸、错误补正或贴回边缘。完全遮挡、快速旋转中的长丢脸段仍不视为通过。

### 4. 双人：通过（稳定双人/分别处理）

两人分别使用自己的 reference 串行处理；首/中/尾检查未串脸，第一人的 refine 不破坏第二人。复杂交叉遮挡、同时大幅运动、硬切镜头仍需按镜头切段或人工锁定，不在本结论覆盖范围内。

## 生产前硬检查

1. H3 的 `<Subject N>` 与完整人物 `<Picture N>`/object reference 一一绑定；环境单独绑定。
2. `summary`/`detailed_description` 只引用 Subject、动作、表情和镜头，不重复发明外观描述；仍保留唯一权威 reference 句。
3. FaceRefine 跟踪 reference、H3 局部 refine reference、源视频 crop latent 三者职责分离。
4. 游戏/3D/插画角色先用 CLIP Vision 或 CCIP 检查跟踪置信度；InsightFace 只作为真人路线候选。
5. 远景人物先做坐标锚点/预览，确认目标框不跳到其他人；多人按人串行。
6. 检查源脸像素高度：30–50px 只承诺稳定与不劣化；若必须恢复身份细节，应回到生成阶段增大头部占比或另接专用 1x/VOSR2 路线。

## 可验收产物

以下路径按当前共享输出目录复核过，使用这些现存文件作为验收入口：

- 中景→远景母片：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_00001_.mp4`
- 中景→远景局部 refine：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_sylvanas_refined_00001_.mp4`
- 动态转头/360°远景 refine：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_headshake_turn_360_hero_refined_00001_.mp4`
- 抬头→低头→转身 refine：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_head_up_down_turn_sylvanas_refined_00001_.mp4`
- 8 秒回望/拉远 refine：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_long_pullback_lookback_hero_refined_00001_.mp4`
- 1344 tracking-gate 左右对照：`/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_start94_tracking_gate_comparison_20260922_00001_.mp4`
- 768 双人转头/拉远的目标选择与像素阈值静态证据：`/home/sean/projects/ComfyUI/output/face_solution/t47_turn_pixel_threshold_contact_sylvanas_20260923.jpg`

旧版研究日志中曾列出的 `sylvanas_solo_pullback_refined_separated_refs_00001_.mp4`、`dynamic_side_refined_768_c3_s08_00001_.mp4` 和双人旧输出已不在当前输出目录，不再作为现存交付物引用。

## 2026-09-23：远景误框门控收束

在 768 级别的另一条双人转头/拉远片上，使用 Sylvanas 的 CLIP Vision identity target，768 crop、crop factor 3、8 steps、base denoise 0.28、PerFrame 0.65/0.25、smooth 15、`undetected_frames=skip`，124 帧成功，约 301.1 秒，无 OOM；运行期间约 98% GPU、18.7 GB 显存、64°C。输出见上方 tracking-gate 对照。

关键规则更新：`face_h / frame_h` 只能作为启动 refine 的候选信号，不能单独作为停止/继续重绘的依据；当真实 face tracking 丢失时必须硬停止并保留源像素。低质量误框若继续送入 H3，会把背景纹理或非目标区域当脸重绘，产生面具化/一坨。`0.088` 是当前内容的启动候选比例，不是跨人物、跨后端的硬阈值；应先以 tracking preview/identity gate 确认目标框。

本会话未重复启动共享 ComfyUI；以上资源来自已完成的 T47/T43/T44 正式运行记录，未修改 T46，也未修改 Hive 任务完成状态。
