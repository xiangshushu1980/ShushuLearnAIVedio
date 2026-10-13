# 任务进度：T-comfy-ops-47

> 目标：在本地 RTX 4090 / ComfyUI-H3-FaceRefine 环境中，专项研究并验证 H3 中景、远景小脸的 FaceRefine 防劣化方案。
>
> 边界：本任务不负责 T-comfy-ops-46 的全局 latent 二采；只研究脸部身份稳定、脸部不漂移、不面具化，以及远景小脸的可接受防劣化。VOSR2/普通超分只作为可选对照，不作为主要目标。

## 任务交接

- 创建日期：2026-09-21。
- 当前状态：已启动，尚未占用 GPU；等待新会话读取本文件后继续。
- 任务线：`comfy-ops_facerefine`。
- 任务 ID：`T-comfy-ops-47`。
- 用户要求：新对话重新读取上下文后继续，不依赖上一轮聊天记忆。

## 2026-09-26：单物体高清统一流程收敛

- 用户明确当前优先级不是五对象并行，而是先完成单物体：高清唯一正脸、高清全身、H3 全人物侧/背/回正统一性，以及之后的 S/Q/B 高清化方法选择。
- 回查 `docs/39_h3_latent_upscale_face_research.md`、`docs/40_h3_far_face_second_pass_strategy.md`、`docs/40_krea2_prompt_and_identity_pipeline.md`、`docs/41_h3_character_reference_test_plan.md`、`docs/42_h3_face_preanalysis_external_research.md`、`docs/43_h3_facerefine_current_state.md` 和 `docs/45_ref_asset_handbook.md` 后，确认旧手册“F/W/WB/S/Q/B 全部从低清 H3 抽帧”过于粗糙，不能满足高清细节目标。
- 当前采用职责分离：`F0` 为高清唯一正脸真值；`W0` 为同一身份源的高清全身真值；`WB` 从 `W0` 去脸/去头；H3 只输入 `W0`，负责侧面、背面、回正和服装一致性；S/Q/B 从通过审查的 H3 帧开始，先直接图像超分，再按需做低 denoise 图像 latent 二采。
- 完整视频 latent 二采保留为整体视频结构/时序慢车道，不作为 reference 默认路径；本地研究已显示它不能承诺恢复远景小脸身份细节。FaceRefine 同样只对近景/中景或明确需要的短片段启用。
- 已更新权威手册：`docs/45_ref_asset_handbook.md` v1.1；新增决策记录：`experiments/h3_reference_pipeline/t47_1_reference_batch_v1/SINGLE_OBJECT_HD_WORKFLOW_DECISION_20260926.md`；manifest 已记录 `single_object_hd_consistency_v1.1`。
- 本次未生成新图、未抽帧、未合成、未启动 ComfyUI、未占用 GPU。Character A 现有 H3 smoke 仍处于 `awaiting_h3_review_character_a`，只等待用户检查。

## 2026-09-26：Character A 高清静帧候选

- Sean 已确认 Character A H3 turnaround 的统一性通过；清晰度不足由后续高清静帧与视角高清化阶段覆盖，不作为 H3 review 否决项。
- 按单物体流程生成两张待审查候选，均以 `/home/sean/projects/ComfyUI/input/sean_t47_1_ref_v1_character_a.png` 为唯一输入：`F0` 1344×1344、identity_portrait、seed=4701202、prompt_id=`8ed468e6-ece6-48d4-9b61-ec2f715dbe90`；`W0` 1024×1536、wardrobe_full_reference、seed=4701203、prompt_id=`f20949ea-35e4-4843-915d-3d917c288f39`。
- 产物分别为 `/home/sean/projects/ComfyUI/output/sean_t47_1_hd_stills_20260926/character_a/F0_front_hd_00001_.png` 与 `/home/sean/projects/ComfyUI/output/sean_t47_1_hd_stills_20260926/character_a/W0_full_body_hd_00001_.png`；参数、hash 和路径已写入批次 manifest。
- 初步检查：F0 面部细节清楚；W0 全身、服装、披风、装备和靴子可读。当前状态改为 `awaiting_still_review_character_a`，未生成 WB、S/Q/B、组合图；GPU 租约已释放。

## 2026-09-26：Krea2 正面锚点→背面一致性 v2

- 用户要求验证“先生成正面，再仅依靠正面图和背面提示词生成背面”，并扩大到多种角色、服装、饰物、发型和怪物，同时保持统一风格。
- 新增参数化 Krea2 流程：`tools/krea2_prompt_profiles.py` 支持统一风格模板 + `--character-spec`；`scripts/krea2_front_back_consistency_batch.py` 串行执行 front → case-local input staging → back，避免跨角色 reference 污染。
- v2 生成 8 组 front/back，共 16 张 `1344×1536`：6 个人形角色 + 2 个怪物。原始输出保留在 `/home/sean/projects/ComfyUI/output/sean_krea2_front_back_consistency_20260926_v2/`，归档和 QC 位于 `experiments/krea2_front_back_consistency_20260926_v2/`。
- 初步 QC：6 个人形角色背面真正转身，主色、服装、发型后侧和主要装备大体统一；2 个怪物背面仍基本正面朝向，判定失败，不得作为背面 canonical。
- 发现并修复两项流程问题：ComfyUI SaveImage 的 prefix 实际落在 case 目录而非 `front/` 子目录；Krea2 LoadImage 不能直接读取 output 路径，已加入 input staging 复制契约。
- 当前只保存实验结果和失败边界，未进入 H3 turnaround、未生成 canonical reference；GPU 租约已释放，等待 Sean 检查成对 contact sheet 和 QC notes。

## 2026-09-26：一次性正反面 turnaround sheet 对照

- 针对“正面图单独生成背面会复制正面/不转身”的问题，新增 `turnaround_sheet` Krea2 prompt mode：一次画布生成左正面、右背面，要求同一角色、互补背部结构、禁止复制正面专属元素。
- 使用 Character A 高清 W0 作为唯一输入，生成 `1536×1024` 双视图 sheet；prompt_id=`9be5b71d-76cd-486a-a4c0-29f72b4e7144`，seed=`4712201`。
- 结果显示真实背面成立：后脑头发、披风后幅、箭袋、背部弓套和靴子后侧形成互补结构，未见明显正脸复制；该路线比“正面→单独背面”更有希望。
- 产物归档：`experiments/krea2_turnaround_sheet_test_20260926/`；仍是 experimental 双视图板，不能直接当两张 canonical reference。GPU 租约已释放。

## 2026-09-26：8角色高分辨率 turnaround sheet 批量测速

- 按用户确认的“一次生成同画布正面+背面”方案，复用 8 个角色/怪物的正面锚点，串行生成 `1728×1152`（约 1.99 MP）turnaround sheet；实验记录：`experiments/krea2_turnaround_sheet_batch_20260926_v1/`。
- 8/8 成功，串行总耗时约 268.9 秒，平均 33.6 秒/张，范围 30.3–36.1 秒/张。GPU 租约已释放。
- 严格两视图 QC 仅 4/8 通过：红法师、东方女剑士、矮人工程师、蜥蜴怪通过；精灵弓手、沙漠游侠、白骑士、冰狼出现重复正面主体。高分辨率提升了细节，但没有解决“第三主体/重复正面”布局不稳定。
- 一次性正反面模式对蜥蜴怪有效，解决上一轮单独生成 back 时不转身的问题；当前批次全部仍是实验图，不进入 canonical reference。下一步如需生产 reference，必须增加严格两主体 QC，并针对失败角色重试布局或采用拆分视图路线。

## 新会话必读

按以下顺序读取：

1. 项目 `AGENTS.md`。
2. `docs/INDEX.md`。
3. `.pi/skills/h3-prompt-writing/SKILL.md` 及 Ref2VA 对应参考文件。
4. `docs/17_h3_prompt_writing_rules.md`。
5. `docs/39_h3_latent_upscale_face_research.md`。
6. `.pi/tasks/T-comfy-ops-43/progress.md` 和 `.pi/tasks/T-comfy-ops-44/progress.md`。
7. `experiments/h3_face_solution/README.md`、当前 canonical prompt 和 runner。
8. Mem0 `comfy-ops` 池中关于 FaceRefine、reference 职责分离、Clip Vision 和远景小脸的记忆。

## 已有事实与基线

### 已验证可用

- T43：单人 YOLO 最大脸轨迹 + 512 crop + H3 局部重采样，`crop_factor=3.0`、`denoise=0.35`，4090 无 OOM；中景脸有改善。
- T44：768 crop、`crop_factor=3.0`、H3 Per-Frame Denoise、base denoise `0.40`、8 steps；单人动态侧脸、双人串行和动作跟踪均已通过基础验证。
- 当前更稳的身份路径：非真人/3D/插画角色使用本地 `clip_vision_h.safetensors`，不要强行依赖 InsightFace；InsightFace 在 Sylvanas 类角色上的置信度过低。
- 最新职责分离实验：
  - H3 生成 reference：完整人物/object reference，负责角色身份、脸、服装、轮廓和总体外观；
  - 环境 reference：负责环境；
  - FaceRefine identity reference：仅用于跟踪“是哪一个人”；
  - H3 局部 refine 的输入 latent：来自原视频当前脸部 crop，负责当前帧动作、角度、表情、光照和时间位置。
- 最新母片/结果：
  - 母片：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_solo_pullback_source_768_00005_.mp4`
  - 精修：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_solo_pullback_refined_separated_refs_00001_.mp4`
  - 124 帧，精修约 110 秒，PSNR 约 44.0；首/中/尾检查没有明显整体角色或背景重写。
- 远景 30–50px 小脸的已知上限：局部 crop→H3 重采样→stitch 能防止串脸、跳脸和抖动，但无法凭空恢复源视频中不存在的新身份细节；远景阶段视觉清晰度增益很小。

### 已确认的提示词规则

- “short 不描述外观”不等于删除 reference 绑定。
- 必须显式保留 `<Subject 1>` ↔ `<Picture 1>` 的唯一权威关系，但 short/detailed 只写动作、表情、镜头和主体运动。
- 不要把 face-only identity reference 同时当作 H3 全局人物 reference；这是此前“脸稳定但整个人物/背景错”的主要原因。
- 四项生成前检查：
  1. 每个 Subject 只有一个明确 Picture/object reference；
  2. short/detailed 只引用 Subject 并描述动作/镜头，不重写外观；
  3. H3 生成、脸部跟踪、H3 局部 refine 的 reference 职责分离；
  4. 非真人/3D/插画角色优先 Clip Vision/CCIP，先验证跟踪置信度。
- 不使用负面提示词作为当前主路径；重点靠正向 reference authority、源 latent 约束、低且平滑的局部 denoise 和正确跟踪。

## 待验证矩阵

1. 同一人物、同一母片：中景→远景连续拉远，比较不处理 / 当前 768 FaceRefine / reference 分离版。
2. 远景小脸 30–40px：重点评价身份漂移、面具化、脸型跳变，而不是“是否高清”。
3. 动态侧脸、抬头低头、转身：验证跟踪丢失、错误补正和贴回边界。
4. 多人：每人独立人物 reference，串行或可控并行处理；验证不串脸。
5. 对照变量：Clip Vision identity、crop_factor、768 crop、per-frame denoise；每次只改一个关键变量。
6. 可选后处理：本地 VOSR2/普通超分只测星光、锐化和身份漂移副作用，不把它当成身份修复方案。

## 验收标准

- 中景：脸部细节改善或至少不劣化，人物整体身份和背景不被改写。
- 远景：不要求高清，但脸不应明显变成面具、跳脸、融脸或错误正脸；动作、角度、表情、光照和时间连续性保持。
- 多人：每个人的脸只对应自己的 reference，不串脸；一人处理不得破坏其他人。
- 资源：记录分辨率、帧数、steps、denoise、显存峰值、耗时和是否 OOM。
- 提示词：遵守 H3 skill 六段式和 `docs/17` 的 Subject↔Picture 绑定规则，不能为追求短而删掉 reference authority。

## 2026-09-21：专项研究收束

- 已按要求重新读取项目 AGENTS、`docs/INDEX.md`、H3 prompt skill/ref-en、docs/17、docs/39、T43/T44 进度和实验目录。
- 只读检查确认共享 ComfyUI 当前未监听 `127.0.0.1:8188`；遵守项目权限边界，本会话未启动/重启 ComfyUI，未占用 GPU，未触碰 T46。
- 将现有正式结果整理为 `experiments/h3_face_solution/T47_face_refine_research.md`，包含推荐链路、职责分离、参数资源、单人远景、动态侧脸和多人验收矩阵及边界。
- 最终推荐：完整人物 reference 给 H3；face-only reference 只给 CLIP Vision/跟踪；源视频当前 crop latent 注入 H3；768×768、crop_factor 3.0、base denoise 0.40、8 steps、per-frame denoise（30–120px、small 1.0、large 0.35、smooth 9）；`face_only` stitch；多人逐人串行。
- 结论：中景可获得轻微细节收益；30–50px 真远景主要验证“不跳脸、不串脸、不面具化、不错误正脸”，不能承诺从源像素恢复新身份细节；动态侧脸/抬头低头/转身在已测动作量级通过；复杂遮挡、快速旋转、硬切和多人交叉遮挡仍为边界。

## 交付

- 研究记录：`experiments/h3_face_solution/T47_face_refine_research.md`
- 现有可验收视频路径见研究记录末节；资源和耗时来自 T43/T44/T47 已完成正式运行记录。

## 2026-09-21：本次会话重新启动

- 已通过 `hive-task start T-comfy-ops-47 --executor codex --project comfy-ops` 重新认领并开始执行，任务线为 `comfy-ops_facerefine`，Codex task `cx-mub2js3z-xm93`。
- 共享 ComfyUI 当前监听 `127.0.0.1:8188`，RTX 4090 读数约 384 MiB / 24564 MiB、GPU 利用率 0%；未见其他 H3 作业占用。`hive-resource status` 本次调用未返回，已记录为资源中心观测异常，未据此声称 GPU 可长期独占。
- 已复核 T47 必读材料、Ref2VA 六段式规则、FaceRefine 职责分离结论和 `comfy-ops` Mem0 记忆。
- 对现有同一 124 帧母片做了三路同帧抽查（0、30、62、93、123 帧）：原片 `sylvanas_solo_pullback_source_768_00005_.mp4`、分离 reference 结果 `sylvanas_solo_pullback_refined_separated_refs_00001_.mp4`、旧候选 `sylvanas_solo_pullback_refined_clipvision_v2_00001_.mp4` 均为 768×448、24 fps、5.167 s。分离 reference 版与母片保持同构图和连续拉远，未见明显背景重写、贴回边缘或跳脸；clipvision_v2 在抽查帧中出现更明显的姿态/视觉状态变化，暂不作为默认基线。
- 当前判断：分离职责链（face-only → identity tracking；完整人物图 → H3 局部 object reference；源 crop latent → 动作/角度/光照/时序）仍是首选候选。下一步继续用既有动态侧脸和双人串行结果做验收抽查，必要时再占用 GPU 补跑单变量实验。

## 2026-09-21：本次执行复核收束

- 已复核 `experiments/h3_face_solution/T47_face_refine_research.md`、README、实验结果 metadata 及全部列出的可验收视频路径；研究记录覆盖中景→远景、30–50px 真远景、动态侧脸/抬头低头/转身、多人串行和 reference 职责分离。
- 本次未新增 GPU 运行：现有 T43/T44/T47 正式结果已覆盖待验证矩阵；沙箱对共享 ComfyUI/GPU 的直接观测受权限限制，且项目边界禁止在未授权状态下启动、重启或操作共享实例。
- 结论保持不变：推荐 768×768、crop_factor 3.0、base denoise 0.40、8 steps、H3PerFrameDenoise（30–120px，small 1.0 / large 0.35，smooth 9）、face_only stitch；完整人物 reference 给 H3，face-only reference 只给 CLIP Vision/跟踪，源 crop latent 保留动作/角度/光照/时序，多人逐人串行。
- 已向用户明确汇报：中景有轻微细节收益；30–50px 远景主要验收不跳脸、不串脸、不面具化、不错误正脸，不能承诺凭空恢复身份细节；快速旋转、严重遮挡、硬切和多人交叉遮挡仍未覆盖。

## 2026-09-21：新会话执行启动与产物核验

- 已重新读取任务描述、项目索引、H3 Ref2VA skill/ref-en、docs/17、docs/39、T43/T44、本任务进度、FaceRefine README/研究记录，并 recall `comfy-ops` Mem0 中的职责分离结论。
- 远程任务仍为 `claimed`，generation=2，当前 lease 至 18:35（上海时间）；本次未启动 ComfyUI、未占用 GPU。
- 只读检查确认研究记录与 metadata 的参数/资源结论一致；其中 README/研究记录列出的旧动态侧脸和双人输出文件名当前在输出目录不存在，需在最终交付前改用实际存在的替代产物或补测后重新登记，不能直接引用失效路径。

## 2026-09-22：专项交付复核

- 完成任务要求的上下文复核：项目 AGENTS、`docs/INDEX.md`、H3 prompt skill 与 `ref-en.txt`、`docs/17`、`docs/39`、T43/T44、本任务进度、FaceRefine README/实现说明和实验 metadata 均已读取。
- 代码级核对确认 `identity_reference` 只服务 FaceRefine 跟踪，`identity_model=clip_vision` 需要单独的 `CLIP_VISION` 输入；H3 局部重绘仍应接完整人物/object reference，源 crop latent 负责当前帧动作、角度、表情、光照和时序。该职责分离不是提示词措辞，而是工作流连接约束。
- 专项结论保持：768×768、crop_factor 3.0、base denoise 0.40、8 steps、H3PerFrameDenoise（30–120px，small 1.0 / large 0.35，smooth 9）、face_only stitch、多人逐人串行是当前 4090 安全基线。中景有轻微细节收益；30–50px 远景主要验收不跳脸/不串脸/不面具化/不错误正脸，不承诺恢复源像素不存在的新身份细节。
- 动态侧脸、抬头低头、背转/360° 和稳定双人串行已有正式结果支撑；快速旋转中的长丢脸、严重遮挡、硬切、多人交叉遮挡仍是未覆盖边界。
- 产物一致性复核发现研究记录中 4 个旧文件名已不在当前输出目录：`sylvanas_solo_pullback_refined_separated_refs_00001_.mp4`、`dynamic_side_refined_768_c3_s08_00001_.mp4`、`two_person_768_subject0_then_subject1_dynamic_00001_.mp4` 及其关联历史条目。当前可直接验收的替代输出包括 `sylvanas_hero_pullback_1344_final8_sylvanas_refined_00001_.mp4`、`sylvanas_hero_wide_headshake_turn_360_hero_refined_00001_.mp4`、`sylvanas_hero_wide_head_up_down_turn_sylvanas_refined_00001_.mp4`、`sylvanas_hero_pullback_1344_motion_turn_sylvanas_refined_00001_.mp4`；未将缺失路径冒充现存交付物。
- 本次未启动/重启共享 ComfyUI，未新增 GPU 运行，未修改 Hive 完成状态；任务结果在当前上下文汇报。

## 2026-09-21：hybrid resources 更新后的补测

- `hive-resource` daemon 正常；补测前 `gpu:0` 空闲（384 MiB/24 GiB、0% util），活跃租约为 0，已为 `T-comfy-ops-47` 申请独占租约 `fa81d53b-ec38-4086-84eb-12a988f54d94`，完成后释放。
- 使用当前仍存在的 Sylvanas 单人 124 帧母片 + face-only identity reference + 完整人物 H3 object reference，提交 ComfyUI prompt `0e203412-3c30-46bc-83f8-627f8ffe4ba4`。
- 参数：768×768 crop、crop_factor=3.0、`res_multistep` 8 steps、base denoise=0.40、H3PerFrameDenoise（30–120px，小脸 1.0 / 大脸 0.35 / smooth 9）、CLIP Vision identity tracking、face_only stitch。
- 结果成功，124 帧、输出 768×448 / 24fps / 5.167s，耗时 145.2s，无 OOM；产物：`/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_clipvision_separated_20260921_00001_.mp4`。资源观测 ID：`1f28f32c-412e-4152-9624-7cd3a24b0c47`；本次观测没有运行中显存采样，因此 `peakVramMb` 保留 null，不用基线值冒充本次实测。
- 与母片全视频客观差异：PSNR average 43.997 dB，SSIM All 0.989103；首/中/末帧目视确认构图、拉远、背景和人物位置保持，未见跳脸、错误正脸、融脸或贴回边缘。中景脸有轻微局部重绘，进入远景后细节增益迅速消失，符合既有结论。
- 本次补测只覆盖“单人连续拉远 + 职责分离 + CLIP Vision”路线，不能替代动态侧脸和多人串行验收；旧记录中失效的动态/多人产物路径仍需后续补齐或改指向实际产物。
- 补测完成后已释放 GPU lease；资源中心确认活跃租约为 0。ComfyUI 保留模型缓存，释放后观测到 VRAM 21.2G/24.0G、系统内存 50.3G/57.9G；未擅自重启或清理共享服务。

## 2026-09-21：问题复核——prompt 绑定与远景丢脸机制

- 用户指出当前补测中主角/背景关系异常。复核确认：`sylvanas_crop_prompt.txt` 虽有六个字段，但不是正确的 reference authority 版本；`subject_definitions` 没有 `<Picture N>`/`<Video N>` 定义，`detailed_description`/`[Shot 1]` 没有引用 reference label，且把局部 crop 说成包含原始环境、把局部 refine 描述成 medium-wide two-person shot。当前补测的 H3 object ref 实际是完整 `sylvanas_style.png`，与 prompt 的引用语义不一致。
- 已新增修正版 `experiments/h3_face_solution/t47_sylvanas_pullback_edit_prompt.txt`：完整六段式；`<Video 1>` 权威负责源构图/动作/光照/时序，face-only `<Picture 1>` 只负责身份跟踪，完整人物 `<Picture 2>` 只负责 H3 object appearance，`<Audio 1>` 原音轨复用，并在 `[Shot 1]` 内显式引用。
- 代码复核确认远景不是单一“识别失败”分支：FaceTrackCrop 在多候选冲突时才调用身份 embedding；单人/连续且只有一个候选时主要靠几何 continuity（nodes.py:1642-1674），所以 CLIP 不会每帧强锁脸。YOLO 无脸或候选超出 reach 时标记 unresolved，检测权重渐隐并保留源像素（nodes.py:1635-1641、1875-1883、H3FaceStitch 2218-2223）。若远景仍检出一个低质量 face box，则会继续 refine，不会因“太远”自动停止。
- `H3PerFrameDenoise` 的 `face_px_small=30` 只是 denoise 曲线阈值，不是识别截止线；当前小脸 multiplier=1.0 会给 30px 以下脸完整 base denoise=0.40，最容易产生 H3 重绘的“面具/一坨”（nodes.py:2618-2646）。因此远景异常可能是低质量检测仍被接受 + 小脸高 denoise，而不是 identity embedding 主动放弃。
- 当前判断：人脸晃动主要由旧 prompt 的 reference/shot 语义错误、逐帧 H3 局部重绘和 crop/size 变化共同造成；远景则需区分“无检测→应保留源像素”和“低质量检测仍通过→继续重绘”两种路径。下一轮应使用修正版 prompt，并增加 FaceTrackCrop report/最小脸高 gate 的诊断后再调 denoise。

## 2026-09-21：正确 prompt + 跟踪框标记复测

- `tools/h3_face_crop_refine_runner.py` 已增加可选 `--tracking-preview-prefix`；preview 框颜色：绿色=真实 face detection，黄色=body fallback，红色=interpolated/dropout。
- 使用修正版六段式 prompt `experiments/h3_face_solution/t47_sylvanas_pullback_edit_prompt.txt`，其余参数/seed 与上一轮保持一致：768 crop、crop_factor=3.0、8 steps、base denoise=0.40、per-frame denoise、CLIP Vision identity tracking。
- ComfyUI prompt `f01a3295-ebe4-4ae8-9c23-64260daaba55` 成功，耗时 120.0s，无 OOM。成片：`/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_correct_prompt_20260921_00001_.mp4`；标记 preview：`/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_correct_prompt_tracking_20260921_00001_.mp4`。资源观测 ID：`20e87bcb-eb6b-4ff5-a82b-c7835325f194`，本次峰值未采样，`peakVramMb=null`。
- 标记 preview 证据：约前 4 秒为绿色框且框在角色脸上；进入更远景后出现红框，红框先漂到右侧建筑；末段又出现绿色框但框在建筑窗户而不是角色脸上。说明机制是“真实脸检测丢失/不可达 → 插值 dropout”，随后背景纹理被 YOLO 当成候选且在单候选 continuity 路径中被接受；CLIP identity 没有每帧强制否决它。
- 因此远景“一坨”根因已从推测收敛为：脸过小导致真实 face detection 失效，同时低质量/误检框没有最小脸高或 identity 强门控，H3 仍对该 crop 重绘。下一步应在 FaceTrackCrop 后加最小脸高/检测框可信度 gate：失去真实脸后直接保持源像素，禁止误框继续进入 H3 refine。

## 2026-09-21：v2/v3 prompt 对照与旧稳定结果复核

- 对照旧 `sylvanas_solo_pullback_refined_separated_refs_00001_.mp4` 与 `sylvanas_solo_pullback_refined_clipvision_v2_00001_.mp4` 后确认：旧结果脸部稳定；本轮 v1/v2/v3 使用同一母片、相同采样参数但 prompt 语义更强，脸部状态变化更明显。
- v2 纠正了 `<Picture 1>`/`<Video 1>` 绑定，但仍将 prompt 语义写得过重；v3 已收缩到旧稳定 `far_face_edit_prompt` 的结构，只声明实际送入 H3 的完整人物图为唯一 `<Picture 1>`，face-only 图只留给 CLIP tracker。
- v3 prompt：`experiments/h3_face_solution/t47_sylvanas_pullback_edit_prompt_v3.txt`；ComfyUI prompt `266fb56a-a0fa-4b7c-83bf-a42e83a7d966`，耗时 100.0s，无 OOM。成片：`/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_correct_prompt_v3_20260921_00001_.mp4`；tracking preview：`/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_correct_prompt_v3_tracking_20260921_00001_.mp4`；资源观测 ID：`69343ba3-3982-4222-9038-c67069dc3b8f`。
- v3 tracking preview 与 v1/v2 在同一末段出现相同轨迹：前段绿色框在脸上，远景先红色 dropout，随后绿色误框到建筑窗户。由此确认框漂移主要是 FaceTrackCrop/检测门控问题，与 prompt 不是同一层；即使换回旧式 prompt，远景误框仍存在。
- 背景边界：FaceRefine 最终 `face_only` stitch 应保留源视频城堡背景；`sylvanas_style.png` 是灰背景完整人物 object reference，不能作为本地 refine 的整幅背景替换目标。若要求参考图同时决定角色和背景，应另做多 reference 的 Ref2VA 母片生成，不是 FaceRefine 局部修复。
## 2026-09-21 standalone reference-isolation rerun

- User clarified that the stable comparison is from before the current batch; therefore paused FaceRefine diagnosis and regenerated a standalone Ref2VA source first.
- New six-section prompt: `experiments/h3_face_solution/t47_sylvanas_standalone_reference_locked_prompt.txt`.
- Prompt explicitly binds `<Picture 1>` to Sylvanas identity/costume and `<Picture 2>` to the frozen fortress courtyard, repeats both bindings inside `[Shot 1]`, and forbids face refinement, replacement, extra characters, unrelated backgrounds, and cuts.
- Inputs: `ref2va_refs/vdn_dual_dialogue/sylvanas_style.png` + `ref2va_refs/vdn_dual_dialogue/ice_fortress_background.png`; 768x448, 124 frames, 8 steps, seed `2026092121`.
- Prompt ID `8187bac1-effd-4a0e-a459-7124f8b0925c`; ComfyUI success in 65.0s. Output: `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_reference_locked_20260921_00001_.mp4` (5.167s, 768x448, 124 frames).
- Contact-sheet check at frames 0/60/123: character is Sylvanas-like with the referenced hood, pale face, blue eyes, dark hair, red-black armor and bow/quiver; background follows the referenced icy courtyard, banners, arches, braziers, mountains and red-lit fortress skyline. This isolates the reference/prompt path as functioning for the standalone source. FaceRefine wobble is not evaluated in this run.
- Resource note: GPU lease `891d765e-2780-4f16-9a79-372f26281c1d` was acquired for the run. The resource daemon became unreachable after generation and could not confirm release; restart/status attempts also immediately reported it unreachable. ComfyUI generation itself completed and queue was empty before submission.
- 2026-09-21 follow-up on the confirmed-good standalone source: used `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_reference_locked_20260921_00001_.mp4` as the only source, with face-only identity `/home/sean/projects/ComfyUI/input/ref2va_refs/vdn_dual_dialogue/sylvanas_face_only_identity.png`, H3 object ref `sylvanas_style.png`, and `clip_vision` identity tracking. Baseline parameters: canvas 768, crop factor 3, denoise .40, 8 steps, per-frame denoise, small/large multipliers 1.0/.35, smooth 9. Prompt ID `57f56c89-37d9-43ef-9f7f-d6ce80123c3d`, success in 110s. Output: `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_clipvision_refine_20260921_00001_.mp4`; marked preview: `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_clipvision_refine_tracking_20260921_00001_.mp4`.
- Baseline tracking preview is green at frames 0/60/123 and remains locked on Sylvanas's face; no background false lock or dropout was observed. Source/refined contact sheets are visually nearly identical at the pull-back checkpoints.
- Conservative follow-up used the same source/tracker/reference path, only reducing denoise to .28, small/large multipliers to .65/.25, and smooth frames to 15. Prompt ID `15a1df70-f4f0-4bda-861c-6462458e1d90`, success in 80.3s. Output: `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_clipvision_conservative_20260921_00001_.mp4`; marked preview: `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_clipvision_conservative_tracking_20260921_00001_.mp4`. Preview remains green and correctly locked at the same checkpoints; the conservative result does not introduce visible face motion and is the safer candidate for the next comparison.
- Resource daemon intermittently dropped immediately after commands; the active lease remained visible until expiry. No competing GPU lease existed. Both ComfyUI jobs completed successfully.
- 2026-09-21 hive-resource protocol correction: the current hivemind working tree adds `occupancy` (real-time lease-only, no nvidia-smi), `resources --json [--refresh] [--processes 0]` (hardware snapshot with 1.5s cache), and separates lease arbitration from metric sampling. During the two recent FaceRefine waits I only sampled before/after and did not poll GPU utilization, so the UI gap cannot prove the GPU was idle; the 80–110s successful ComfyUI completions confirm the jobs were executing. The canonical hive-resource skill was updated with the new protocol and the rule to heartbeat during runs and record `observe` before release.
- 2026-09-21 1344 far standalone source: prompt `experiments/h3_face_solution/t47_sylvanas_standalone_1344_far_prompt.txt`, two refs (Sylvanas + frozen fortress), 1344x768, 124 frames, 8 steps, seed `2026092124`. Prompt ID `45f9a9b1-7516-4ae9-a3f9-663f38bb214c`; success in 202.1s. Output: `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_1344_far_20260921_00001_.mp4` (5.167s, 1344x768, 124 frames). GPU was actually observed during generation: 100% utilization, 23060 MiB / 24564 MiB, 78C; observation `e74d5ad0-4cb7-4f4e-b3f7-d4477fd6ed7f`. Contact frames 0/60/123 show the intended longer pull-back and stable referenced courtyard/character composition.
- The user asked about two older good outputs: `sylvanas_hero_pullback_1344_final8_sylvanas_refined_00001_.mp4` and `sylvanas_hero_pullback_1344_motion_turn_sylvanas_refined_00001_.mp4`. They are older T43/T44-style two-person 1344 source + local face refinement results, not direct Bilibili source-video reuse. Current route keeps the same broad crop -> H3 local resample -> face-only stitch idea, but uses separated references and ClipVision identity tracking; the new 1344 source is deliberately farther and single-person, so its final face has fewer source pixels than the old mid-shot portions.
- Resource protocol issue: lease `8944840a-543c-4fd5-95b6-97f8dbc4dbdb` was acquired with `--ttl 600000` and actual PID metadata, but server expiry remained about 60s; heartbeat after expiry failed. Generation completed successfully and occupancy is now empty. Treat this as an hivemind lease-TTL implementation issue, separate from GPU execution.
- 2026-09-22 continuation: ran local-only latent FaceRefine on the older good 1344 source `/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_00001_.mp4`, not global redraw. Used separated face identity + full Sylvanas H3 object reference, ClipVision tracking, canvas 768, crop factor 3, 8 steps, base denoise .28, per-frame .65/.25, smooth 15, marked preview. Prompt ID `fec67ce7-580e-46d9-a02f-bac517664e46`, success in 115s. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_old1344_sylvanas_clipvision_conservative_20260921_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_old1344_sylvanas_clipvision_conservative_tracking_20260921_00001_.mp4`.
- Preview checkpoints 0/60/123 stayed green and locked on Sylvanas; no background false lock/dropout. The 1344 composition, hero and courtyard remained unchanged in the contact-sheet comparison. This is the correct next baseline for stabilizing medium-to-normal-wide before testing the new farther 1344 source.
- Observation `d7c9c4d1-bdaf-4743-a854-d0c57782e540`; lease was no longer active by post-run check. Exact current-run peak VRAM was not sampled, so do not infer it from the idle post-run reading.
- 2026-09-22 long/far continuation: extended the standalone 1344 Ref2VA source to 10.042s / 241 frames with a 0-3s medium-wide, 3-7s wide, 7-10s far-wide pullback and final head target ~20-35px. Source prompt: `experiments/h3_face_solution/t47_sylvanas_standalone_1344_far_10s_prompt.txt`; output `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_1344_far_10s_20260922_00001_.mp4`; H3 prompt ID `7a5c9091-8442-473b-8993-e1368bcaefba`; generation completed in 555.6s.
- Updated `tools/h3_face_crop_refine_runner.py` to accept `--length` and pass it to H3FaceSelect `frame_load_cap` and MiniMaxH3ReferenceToVideo `length`; this prevents 10s sources from being silently truncated to 124 frames.
- Applied exactly the conservative local chain to all 241 frames: ClipVision, separated face/H3 references, canvas 768, crop factor 3, denoise .28, per-frame .65/.25, smooth 15, H3InjectVideoLatent + face-only stitch. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_far1344_10s_sylvanas_clipvision_conservative_20260922_00001_.mp4`; marked preview `/home/sean/projects/ComfyUI/output/face_solution/t47_far1344_10s_sylvanas_clipvision_conservative_tracking_20260922_00001_.mp4`; prompt ID `a22baca3-501f-4bc6-949c-5d2ec2f144aa`; success in 277.8s.
- Result: frames 0/60/120 remain green and correctly locked. At frames 180/210/240 the box turns red and sits above/away from the tiny character face: this is a real far-distance detector/tracker dropout with an interpolated stale box, not a background false lock. Thus the same parameters stabilize medium-to-normal-wide, but the 20-35px tail exceeds the current face detector gate; next work should target far-face gating/coordinate anchoring, not increase denoise.
- Observation `0faa3925-0a16-449b-a6c3-2d8c78f38f85`; occupancy was empty after completion.
- 2026-09-22 independent whole-person track experiment: downloaded `/home/sean/projects/ComfyUI/models/ultralytics/segm/person_yolov8m-seg.pt` (52.3MB); ComfyUI object info recognized registration name `segm/person_yolov8m-seg.pt` without restart. Extended `tools/h3_face_crop_refine_runner.py` with `--detector`, `--paste-region`, and existing `--length` support; the original face/ClipVision default remains unchanged.
- Added whole-person prompt `experiments/h3_face_solution/t47_sylvanas_person_crop_refine_prompt.txt`. Ran separate path on existing 1344 comparison video `/home/sean/projects/ComfyUI/output/face_solution/t47_far1344_sylvanas_clipvision_repeat_20260922_00001_.mp4`: `--detector segm/person_yolov8m-seg.pt --fast-detect --crop-factor 1.30 --canvas 768 --denoise .28 --steps 8 --per-frame .65/.25 --smooth 15`, still through `H3InjectVideoLatent`, person-box (`face_only` mask semantics) stitch. Prompt ID `e7cf1718-8316-4693-b94a-1dee562b71ec`, success in 115s.
- Output `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_persontrack_20260922_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_persontrack_tracking_20260922_00001_.mp4`. Green body boxes at frames 0/60/123 cover the whole Sylvanas body continuously; no far-face dropout. First person-box result is visually stable, but it is still rectangular person-box compositing, not a segmentation-mask stitch; a later mask pass is needed to remove possible background rectangle seams. Observation `20e93d9b-a688-47aa-8ebc-97fafc352dd0`; lease released.
- 2026-09-22 person rectangle follow-up: reran the independent person-detector route with `paste_region=full_crop` (complete rectangular crop), same source and conservative parameters, seed `2026092132`. Prompt ID `d1e7bbf2-5e42-4cb4-a7fb-27b6c31aea98`, success in 85.3s; GPU observed at 100% / 23036MiB / 62C during the run. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_fullcrop_rect_20260922_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_fullcrop_rect_tracking_20260922_00001_.mp4`.
- Tracking stayed green at frames 0/60/123. Full-crop rectangle result keeps the whole character stable and visually close to the person-box result; no obvious seam at contact-sheet scale, but this remains a rectangular composite and must be inspected at playback/full resolution before production use. Observation `53874555-d142-47c7-a585-5daf20c96d71`; lease released.
- 2026-09-22 extended rectangle stress test: used the longer 10.042s / 241-frame 1344 far-pullback source `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_1344_far_10s_20260922_00001_.mp4`, YOLOv8m-seg person detector, crop factor 1.30, canvas 768, denoise .28, H3PerFrameDenoise .65/.25, smooth 15, `paste_region=full_crop`, and the whole-person six-section prompt. Prompt ID `8a24a0a5-1262-4098-8e28-c60ae226c34c`; success in 277.9s; GPU observed during H3 at 100% utilization, ~23052MiB, 76C. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_fullcrop_rect_20260922_00001_.mp4`; marked preview `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_fullcrop_rect_tracking_20260922_00001_.mp4`; observation `59967e24-1ba7-4345-a9a5-9520b66f7c2c`; lease released.
- Far-tail inspection at frames 120/150/180/210/240 shows the person box remains green and follows the shrinking full body; no face-detector dropout because the person detector continues to see the character. At full-resolution far frames, no obvious rectangular seam, hard halo, or background patch boundary is visible; the character itself becomes naturally tiny/low-detail, so this confirms tracking continuity more strongly than detail recovery. This is still rectangular compositing, not a true segmentation-mask stitch; production acceptance should wait for a playback check and, if needed, a mask-based pass.
- 2026-09-22 face-vs-mask controlled rerun on the same 10.042s / 241-frame 1344 far-pullback source: face route used ClipVision identity tracking, face detector, crop factor 3.0, face-only stitch, denoise .28, per-frame .65/.25, smooth 15; prompt `8977f52f-6edf-47b4-a955-ea65a2fa3708`, 260.1s. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_clipvision_faceonly_20260922_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_clipvision_faceonly_tracking_20260922_00001_.mp4`; observation `e38ecab4-ca30-4edb-9b30-a9219c9b360e`.
- Added `--person-mask` to `tools/h3_face_crop_refine_runner.py`: it runs `AILab_YoloV8` with `segm/person_yolov8m-seg.pt` on each tracked crop and wires the resulting per-frame mask into `H3FaceStitch.masks`, overriding the rectangular `full_crop` mask. Same person-detector route and sampling parameters; prompt `778515c6-320c-469b-850f-e056aebabc61`, 270.1s. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_mask_20260922_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_mask_tracking_20260922_00001_.mp4`; observation `83cf95ac-1bda-4e97-bbf9-8eb3e739d7b7`.
- Inspection: face preview is green through close/medium frames but turns red at far frames 180/210/240, confirming the face detector cannot reliably see the tiny face; the face output therefore has no obvious far-face change to compare. Person-mask preview stays green on the whole character at the same far frames. Face-vs-mask PSNR is 41.87dB (different tracked/refined route), while rectangle-vs-mask PSNR is 43.40dB; contact sheets show no visually obvious rectangle seam in either person route. GPU reached 100% / ~23.0GB / 82–83C; lease released and occupancy is empty.
- 用户复核结论：此前 `fullcrop_rect` 确实经过 H3 全人物局部 refine；预览中的绿色框是 detector/tracker 的矩形框，不是 segmentation mask 可视化。当前所有 refine 结果比原片略软，说明锐度/细节恢复仍不足；但劣化开始后 refine 对抑制进一步崩坏明显有效。人物/脸小到阈值以下时，原片与 refine 都会发生较大视觉变化，暂未找到可靠的单一 refine 参数解决方案。
- 2026-09-22 native-resolution test: runner now accepts independent canvas dimensions. Face-only route used `1344x768` H3 canvas (same as source), otherwise same 10.042s/241-frame source and conservative ClipVision settings; prompt `d10c8f16-6a67-4c83-92de-5abfd696df26`, success in 616.0s, observed 100% GPU / ~23092MiB / 85C. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_native1344_faceonly_20260922_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_native1344_faceonly_tracking_20260922_00001_.mp4`; observation `7c191a9d-3343-4221-8819-7b4448769a43`.
- Native-resolution person-mask test initially exposed an implementation issue: basic `AILab_YoloV8` ignored the attempted `classes=0` filter, so its debug overlay selected horse/bicycle at the far tail. Those outputs are not accepted as valid mask evidence. Runner was corrected to use `AILab_YoloV8Adv` with `classes="0"` (person-only), and the corrected run succeeded in 106.0s with prompt `4c292a31-eefc-4faa-9252-3d5f043c2bce`; output `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_native1344_mask_personclass0_adv_20260922_00001_.mp4`, tracking `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_native1344_mask_personclass0_adv_tracking_20260922_00001_.mp4`, actual mask overlay `/home/sean/projects/ComfyUI/output/face_solution/t47_person1344_10s_native1344_mask_personclass0_adv_tracking_20260922_mask_overlay_00001_.mp4`; observation `ddecf5f8-9831-433f-8ca3-7701cf5b62b6`.
- Corrected mask overlay confirms person silhouette mask at close/medium frames; at the far tail the person-class detector returns no mask, so the stitch preserves the original far pixels rather than pasting a wrong object. This is the desired safe failure mode, but it also means the mask route does not recover ultra-far detail. All GPU leases released; occupancy empty.
- 2026-09-22 1024 face-only comparison: used the same 10.042s/241-frame source, ClipVision face route, face-only rectangular stitch, seed and conservative denoise as the 768 baseline, changing only H3 canvas to `1024x1024`. Prompt `bff35386-2176-48f2-9df5-c09d102ad12b`; success in 610.3s versus 260.1s for the prior 768 run; observed 100% GPU / ~23028MiB / 84C. Output `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_1024_faceonly_20260922_00001_.mp4`; preview `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_1024_faceonly_tracking_20260922_00001_.mp4`; observation `44d81994-5f20-4ee0-a958-54d324c4a71b`.
- Initial visual comparison at frame 60 shows 1024 is not obviously sharper than 768 at the final 1344 output scale; it is substantially slower (~2.35x). ROSE2 was not found in local ComfyUI object info, models, project docs, or local skills, so no unverified ROSE2 pass was run. Need exact ROSE2 model/workflow/path before chaining it.
- Tear-mark issue hypothesis: the H3 object reference contains hair/hood context, while the prompt does not bind the dark tear streaks as fixed facial paint/markings. The model can reinterpret them as thin hair strands. Preferred next fix is positive material/attachment wording plus a dedicated close face reference/crop; a negative prompt is not required initially. View-angle reference should be added only if the source angle is not covered.
- 2026-09-22 tear-mark prompt test at 768: added positive fixed-material semantics in `experiments/h3_face_solution/t47_sylvanas_pullback_edit_prompt_v4_tear_marks.txt` (tear streaks are skin-attached facial markings, not hair/fibers, never flutter or detach). Kept face-only rectangular stitch and all conservative parameters unchanged. Prompt `3d6ec6d7-1bf1-4454-96c6-3c61592df053`, success in 286.3s, observation `f505ba2c-89c3-4123-9e01-6fb9b5872e1b`; output `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_768_tearmarks_20260922_00001_.mp4`, tracking `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_768_tearmarks_tracking_20260922_00001_.mp4`.
- Current recommendation after the horse false-mask observation: use face-only rectangular stitch as the default. The earlier mask debug path could select non-person objects; the corrected person-class mask fails closed at the far tail, but still adds detector complexity and does not recover detail. A true face SAM mask can be tested later as a separate boundary experiment, not mixed into the resolution baseline.
- 用户反馈：v4 正向泪痕语义仍被 H3 解释成会飘动的头发，说明文字约束不足以覆盖当前完整人物 reference 的视觉先验。后续优先级调整为：使用明确可见泪痕的近脸 H3 reference/source crop，必要时用脸部 SAM/皮肤轮廓限制可贴回区域；不使用负面提示词。用户要求后续关闭 tracking preview；runner 不传 `--tracking-preview-prefix` 即可省去 preview CreateVideo/SaveVideo，保留最终视频。
- 2026-09-22 attempted Krea2 reference-sheet generation through the local `Krea2ImageNode`. The dynamic model input format was corrected on the second submission, but the node returned `Unauthorized: Please login first to use this node`; no image was generated and no local GPU was used. Intended prompt was a 3:2 three-panel sheet: face close-up with skin-attached dark tear markings, front view, and back view. Requires ComfyUI Partner/API login before resubmission.
- 2026-09-22 correction: local Krea2 weights were present and the project already had `tools/krea2_identity_edit_runner.py`; the API-node login error was unrelated. Added local Krea2 prompt modes `tear_mark_face`, `front_reference`, and `back_reference` to `tools/krea2_prompt_profiles.py`/runner. Generated with `krea2_raw_fp8_scaled.safetensors`, 1024x1024, ref_boost 4.0: face `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_krea2_tear_face_20260922_00001_.png`, front `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_krea2_front_20260922_00001_.png`, back `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_krea2_back_20260922_00001_.png`.
- The first Krea2 face output still mixed a dark facial line with hair. Cropped the original Sylvanas reference to `/home/sean/projects/ComfyUI/input/ref2va_refs/vdn_dual_dialogue/sylvanas_face_krea_input.png` and reran the positive tear-mark prompt with `ref_boost=8.0`; improved candidate `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_krea2_tear_face_crop_ref_20260922_00001_.png`. It shows the under-eye markings more clearly, though some hair still crosses the upper face; inspect before using as the sole H3 reference. Local Krea2 outputs completed; observation `d43f707c-4791-4d85-be3c-dc078f2aef28`; GPU lease released.

- 2026-09-22 VOSR2 local install/smoke: installed `/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-VOSR2`; downloaded the official VOSR2 1.4B DiT bundle, Qwen-Image 2D VAE and DINOv2-L under `/home/sean/projects/ComfyUI/models/vosr2/VOSR2/`; corrected `args.json` placement and converted `dinov2_vitl14_pretrain.pth` to `dinov2_vitl14.safetensors` locally. ComfyUI restarted with an empty queue and registered `VOSR2ModelLoader`/`VOSR2Upscale`.
- Smoke inputs: `vosr2_test_face.png` (1024x1024 face reference) and first 3 frames of `vosr2_test_clip.mp4` resized to 512x288. Settings: `dtype=fp16`, `seed=42`, `color_alignment=wavelet`, DiT tile `512`, overlap `64`, VAE tile `1024`, overlap `128`.
- Results: 2x single image succeeded in ~12.9s to 2048x2048; 4x succeeded in ~24.6s to 4096x4096; seed 43 2x succeeded in ~9.4s; 3-frame video batch 2x succeeded to three 1024x576 PNGs. No OOM; idle post-run GPU was 4.0–4.4GB, so do not infer peak VRAM from that reading.
- Outputs: `/home/sean/projects/ComfyUI/output/vosr2_quick_2x_00001_.png`, `vosr2_quick_4x_00001_.png`, `vosr2_quick_2x_seed43_00001_.png`, and `vosr2_quick_clip_3frames_2x_00001_.png`–`00003_.png`. Visual smoke: composition/identity preserved and no obvious tile seam; seed variation confirms generated detail is not strictly deterministic across seeds. This is an image/batch smoke only, not a long-video temporal-consistency acceptance.

- 2026-09-22 current-baseline + local VOSR2 A/B: reran the old 1344×768 / 124-frame source with the conservative face-only route and no tracking preview. Parameters: ClipVision, separated face/H3 references, crop 768, crop factor 3, 8 steps, denoise .28, per-frame .65/.25, smooth 15, seed `2026092201`; prompt `b942f751-df7b-41b3-b020-756bf85788dc`, elapsed 137.1s. Output: `/home/sean/projects/ComfyUI/output/face_solution/t47_old1344_faceonly_no_preview_20260922_00001_.mp4`.
- Added `--vosr2-upscale` and `--vosr2-seed` to `tools/h3_face_crop_refine_runner.py`. The VOSR2 branch runs after H3 local decode on each 768 crop, uses VOSR2 2× / seed 42 / wavelet alignment / 512 tile + 64 overlap / 1024 VAE tile + 128 overlap, then resizes back to 768 before `H3FaceStitch`; it does not super-resolve the background.
- VOSR2 A/B used the baseline video as input and kept every H3 parameter unchanged; prompt `1bd157ff-c73d-4b04-a772-b0b9146fa5d3`, elapsed 635.4s, no OOM. Output: `/home/sean/projects/ComfyUI/output/face_solution/t47_old1344_faceonly_vosr2_2x_no_preview_20260922_00001_.mp4`. Output remains 1344×768 / 124 frames / 5.167s. Observation `21ead8c8-03a6-41b4-ab91-db0b845742c4`, observed peak about 22.9GB / 100% / 71°C.
- Initial visual A/B at frames 0/60/123: local VOSR2 gives a small apparent increase in eye/edge sharpness in the medium shot, without obvious background or identity rewrite; it does not yet demonstrate far-small-face recovery. Cost is roughly 4.6× the H3-only baseline (635.4s vs 137.1s). Next useful test is a short far-tail crop/segment, not another full 124-frame run.
- 2026-09-22 far-tail VOSR2 test: extracted the last ~2.5s from the 10.042s 1344 far-pullback source (`/home/sean/projects/ComfyUI/input/t47_far_tail_2p5s_20260922.mp4`, 62 source frames). The face-only route failed before sampling at `H3FaceSelect`: `No face detected in any frame` with `face_yolov8m.pt`; this is direct evidence that the 20–35px tail is below the current face detector gate, not a VOSR2 failure.
- Retried the same tail with the validated whole-person detector route (`segm/person_yolov8m-seg.pt`, fast detect, crop factor 1.3, `full_crop` stitch) plus local VOSR2 2×. Prompt `0acc9943-dd6c-44e1-a794-f0c0d79a042f`, elapsed 480.2s, no OOM; output `/home/sean/projects/ComfyUI/output/face_solution/t47_far_tail_person_vosr2_20260922_00001_.mp4`, 1344×768 / 61 frames / 2.542s. Observation `ab73cedb-11aa-4690-9f38-1b15a096d357`, peak observed about 21.8GB / 100% / 71°C.
- Far-tail inspection: person detector preserves continuous tracking, but VOSR2 does not recover readable facial detail at this scale. Full rectangular person-crop stitching can expose background/rectangle artifacts when the character is tiny; therefore this is not a production default. Conclusion: VOSR2 is a mild medium-shot detail enhancer, not a solution for detector failure or 20–35px identity recovery. Further full-length VOSR2 runs are not justified; the next technical work, if continued, is detector-independent coordinate anchoring plus a true person/face mask or source-generation head-size increase.

## 2026-09-22：Refine 主线交接（Krea2 支线停止）

- 用户决定暂时放弃 Krea2 参考图支线；上述 Krea2 生成物均不纳入 H3/Refine 有效基线。原因是新图出现模糊、风格漂移、泪痕仍可能被解释为头发；不要用它们覆盖原有稳定参考。
- 当前有效主线基线：局部 latent FaceRefine，不做全局重绘；完整 Sylvanas 人物图只作为 H3 局部 object reference，face-only identity 图只给 ClipVision/跟踪，当前帧 crop latent 保留动作、角度、表情、光照和时序；H3InjectVideoLatent 后 face-only rectangular stitch。
- 推荐稳定参数：源视频同分辨率优先作为输出画布；但当前成本/效果基线仍为 `768x768` crop、`crop_factor=3.0`、8 steps、base denoise `0.28`、per-frame `0.65/.25`、smooth `15`、ClipVision。768 远景长片 241 帧耗时约 `260.1s`；1024x1024 约 `610.3s`，未见明显更清晰；native 1344x768 约 `616.0s`，同样未解决软化，因此暂不把更大画布作为默认值。
- 当前已验证结论：中景到正常远景，保守 FaceRefine 可明显减轻劣化并保持脸部稳定；源脸约 20–35px 后 face detector 会掉检，红框代表检测失败/插值旧框，不是背景误锁。全人物 YOLO/人物 mask 可以继续跟踪到远景，但只证明跟踪连续，不凭空恢复远景细节；person-class mask 在无检测时安全保留源像素。
- 当前默认选择：face-only rectangular stitch；人物矩形/人物 mask 作为单独的远景连续性实验，不与脸部锐度基线混合。当前所有 refine 比原片略软，但在劣化开始后抑制进一步崩坏明显有效；小于检测阈值后原片和 refine 都会显著变化，尚未找到单一参数解决方案。
- 后续最小测试：使用已确认稳定的旧 1344 中景母片，关闭 tracking preview（不传 `--tracking-preview-prefix`），只做一次 face-only conservative rerun 作为当前可复现基准；然后若用户继续，再单独测试“只在劣化开始后启用 refine”的门控，不再同时改变分辨率、mask、提示词和 reference。
- 资源状态：阈值统计使用临时 GPU 租约 `58fead10-ff82-4c51-a4eb-647a9eb83b56`，统计结束后释放；远程 Task Center `T-comfy-ops-47` 仍为 `running`，generation=3，未提交完成。

## 2026-09-22：VOSR2定位与人脸阈值初测

- 用户要求把 VOSR2 记录为当前最终生成优化手段，但继续验证其边界。现行定位：VOSR2 仅接在 H3 局部 decode 后，对已被 H3 refine 的 crop 做可选细节增强，再缩回 stitch 画布；不处理背景、不替代 FaceRefine、不解决人脸 detector 丢失。旧 1344 中景 A/B：H3-only 137.1s，H3+VOSR2 2x 635.4s（约 4.6x），中景眼缘/边缘略锐，未证明远景小脸恢复；远景尾段人物路线仍无可读脸细节。因此 VOSR2 是“当前可用的最终生成优化手段”，但尚未完成长时序/远景验收。
- 新增阈值诊断入口：`tools/h3_face_crop_refine_runner.py --report-only`，只执行 H3FaceSelect/FaceTrackCrop，不加载 H3 采样；`H3FaceTransformInfo` 已扩展为输出源脸高、检测状态、权重和丢检区间。未生成 tracking preview。
- 对 `/home/sean/projects/ComfyUI/output/face_solution/t47_sylvanas_standalone_1344_far_10s_20260922_00001_.mp4` 使用 `face_yolov8m.pt` 做原始检测统计（243 帧；视频实际比请求的 241 帧多 2 帧）：脸高约 35px 时置信度仍约 0.7；约 30px 仍可检测；约 25–27px 时置信度降到约 0.25–0.4；约 20px 时置信度主要约 0.08–0.22；约 15px 后几乎只剩低置信/误检；最终约 20–35px 尾段在默认 conf=0.25 下掉检。2.5s 尾段在 conf=0.20 已 0/62 帧检测到可靠人脸。
- 初始门控假设（待受控视频 A/B）：源脸高 `>35–40px` 不做 refine 或只用极低强度；`30–35px` 进入 FaceRefine；`25–30px` 仍可 refine 但需保守 denoise/连续检测确认；`<25px` 停止脸部 refine，保留原始像素；`<20px` 不再依赖脸部跟踪，必要时切人物框/人物 mask，仅保持人物位置，不承诺脸部细节。真正“停止计算”不能靠当前 `H3FaceStitch=fade_out`，需要在采样前按帧/连续区间做 gate；当前实现仍会让所有 kept crop 进入 H3，丢检后只是淡出贴回。
- 结构澄清：face rect、face mask、ClipVision 不是同一个东西。当前 face-only rect 与 ClipVision 共用 H3 人脸检测/跟踪上游，ClipVision 负责身份关联；当前 person-mask 是独立的 `person_yolov8m-seg.pt` 人物分割，仍依赖人物框路线，不是脸部 mask。矩形/人物 mask 可以共享人物 tracker，但不能据此认为与 ClipVision 人脸版本等价。

## 2026-09-22：按人脸跟踪状态门控的左右对照

- `tools/h3_face_crop_refine_runner.py` 新增 `--undetected-frames {fade_out,skip,composite_anyway}`。本轮使用 `skip`：人脸跟踪不到时最终 stitch 保留原始像素，不贴回 H3 refine；未启用 VOSR2，未生成 tracking preview。注意这版是输出合成门控，H3 仍对 kept crop 批量采样，后续若要省算力需做采样前 gate。
- 输入：`t47_sylvanas_standalone_1344_far_10s_20260922_00001_.mp4`，241帧/1344×768；ClipVision identity、face-only rect、crop 768/crop_factor 3、8 steps、denoise .28、PerFrame .65/.25、smooth 15、seed 2026092201。Prompt `30becaf2-beb6-46df-a0c5-acd9f4c27654`，耗时 204.1s；GPU 观测 `00cd4558-2d26-4cb0-880e-7c6f70e67ac4`，峰值约 22.8GB、100%、79°C，无 OOM。
- refine 输出：`/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_tracking_gate_skip_no_vosr2_20260922_00001_.mp4`。
- 左右标记对照工具：`tools/make_facerefine_comparison.py`；输出 `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_tracking_gate_comparison_20260922_00001_.mp4`，2688×768、241帧。左侧逐帧显示 `TRACKED -> REFINE`（绿框）或 `NOT TRACKED -> ORIGINAL`（红字）；右侧为门控结果。抽帧检查确认远景丢检段右侧回到原片，没有继续贴旧 refine crop。
- 用户指出首段在劣化前不应 refine；已将实际起始劣化点设为第 94 帧（0-based）。`tools/make_facerefine_comparison.py` 新增 `--start-refine-frame`，本轮 0–93 帧强制右侧使用原片，94 帧起才按人脸跟踪状态选择 refine/原片，远景丢检后仍保留原片。抽帧核对 80/93 帧左右一致，94 帧开始出现绿色 tracked/refine，远景红色 not tracked 后右侧回原片。
- 修正版左右对照：`/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_start94_tracking_gate_comparison_20260922_00001_.mp4`；纯结果：`/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_start94_gate_result_no_vosr2_20260922_00001_.mp4`。本次仅重合成，没有重新运行 H3/VOSR2；因此仍属于输出门控，后续可再做采样前 gate。
- 对源片做了独立尺寸扫描：`tools/analyze_face_threshold.py`，CSV=`experiments/h3_face_solution/t47_face_threshold_metrics_20260922.csv`。关键结果：用户观察的第94帧脸高约68px，原图VAE等效约8.50 latent px，confidence约0.821，仍是稳定跟踪；第120帧约45px/5.63 latent px；第145帧约30px/3.75 latent px；第150–155帧约26–27px/3.25–3.4 latent px且confidence降至约0.25–0.40；第156帧后默认conf=0.25基本无脸检测。
- 因此当前应保留两个阈值：`refine_start`（本片用户标定的开始劣化点约68px源脸高/8.5 latent px）与 `face_track_stop`（约26px源脸高/3.25 latent px）。前者不是人脸识别失败点，后者也不是画面首次劣化点。Laplacian清晰度不能单独当判据：脸变小后边缘方差反而升高，必须和源脸尺寸/身份连续性一起判断。
- 同一内容等比例缩放到 1344×768、960×548、768×438 后做三路扫描：第94帧脸高分别为 68/48/38px，对应脸高占画面高度约 8.85%/8.76%/8.68%；同一远景跟踪终点附近分别约 26/18/14px，占画面高度约 3.4%/3.3%/3.2%。初步说明跨分辨率应优先使用归一化脸高 `face_h / frame_height`，而不是固定源像素；原图 VAE latent px 会随分辨率缩放，不是跨分辨率的稳定阈值。CSV：`t47_threshold_1344.csv`、`t47_threshold_960.csv`、`t47_threshold_768.csv`。
- 暂定规则更新：`face_h/frame_h <= 0.088` 作为本片“开始劣化、启动 refine”的候选阈值；人脸跟踪失败作为硬停止条件，直接保留原始帧，不再 refine。该比例仍需在不同内容/真正不同分辨率生成片上复核，当前缩放扫描证明的是尺度归一化方向，不是最终模型质量定论。

## 2026-09-23：768级别多视频/多人物阈值扫描

- 新增 InsightFace 后端扫描工具：`tools/analyze_face_threshold_insight.py`。原因：`face_yolov8m` 对 Sage 风格画面全程漏检，但 InsightFace 能检测到两张脸；检测后端失败不能直接当作脸太小。
- Shushu（768×448，真人、基本固定中近景）：InsightFace 124/124 帧检测，脸高约 145–148px，占画面高度约 0.325–0.332，单脸稳定；这是大脸稳定对照，不跨越远景阈值。CSV：`experiments/h3_face_solution/threshold_insight_shushu.csv`。
- Sage（768×448，双人）：InsightFace 243/243 帧检测，每帧 2 张脸，最大脸约 96–106px，占画面高度约 0.215–0.237，全程稳定；不能直接用最大脸作为目标，后续需要 identity/位置选择。CSV：`experiments/h3_face_solution/threshold_insight_sage.csv`。
- Sylvanas 中景（1344×768、124帧）：InsightFace 124/124 帧检测，最大脸比例从约 0.142 降到约 0.064，仍未进入丢检区；说明 0.088 不能直接作为跨内容的“必须开始 refine”硬阈值。CSV：`experiments/h3_face_solution/threshold_insight_sylvanas_mid.csv`。
- Sylvanas 长转镜头（1344×768、243帧）：InsightFace 198/243 帧检测；脸比例从约 0.177 下降到约 0.018，约 0.024 以下开始间歇丢检，后段大量无检测。CSV：`experiments/h3_face_solution/threshold_insight_sylvanas_turn.csv`。
- 当前规则收敛：`face tracking lost` 是可靠的硬停止条件——停止 refine，保留原始像素；不同后端/人物/姿态下，脸大小只能作为候选启动信号，不能单独决定开始 refine。下一步 768 实际生成优先选 Sylvanas 长转镜头做“按检测状态停止”的门控对照，再用 Sage 做双人目标选择测试。
- 本轮启动点输出门控对照（基于已有 H3 结果，未重复采样）：同一长拉远片用 768 crop 分别测试脸高比例 0.14/0.11/0.088/0.064，对应第70/82/95/119帧开始。输出：`t47_start014_768_gate_comparison_20260923_00001_.mp4`、`t47_start011_768_gate_comparison_20260923_00001_.mp4`、`t47_start0088_768_gate_comparison_20260923_00001_.mp4`、`t47_start0064_768_gate_comparison_20260923_00001_.mp4`。
- `tools/make_facerefine_comparison.py` 新增 `--start-refine-frac`：按检测到的脸高/画面高比例首次达到阈值后锁存启动，避免把帧号硬编码到不同视频；丢失人脸仍沿用原始帧。下一步用真实不同视频的 768 H3 结果复核启动比例，而不是只做重合成对照。

## 2026-09-23：第二条 768 转头镜头实测

- 使用另一条双人转头/拉远源片 `/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_headshake_turn_360_00001_.mp4`，仍选 Sylvanas 为 ClipVision identity target；参数保持 768 crop、crop_factor 3、8 steps、denoise .28、PerFrame .65/.25、smooth 15、`undetected_frames=skip`，关闭 VOSR2。Prompt `25b6c5cf-bd63-450b-9cdc-59a261db2d30`，耗时 301.1s，无 OOM；GPU 运行期间约 98% 利用率、18.7GB、64°C（资源观测因 daemon 在结束时短暂掉线未成功写入，已恢复并释放租约）。
- refine 输出：`/home/sean/projects/ComfyUI/output/face_solution/t47_turn_768_tracking_gate_no_vosr2_20260923_00001_.mp4`。
- 按 `face_h/frame_h <= 0.088` 做自动启动门控并生成左右对照：`/home/sean/projects/ComfyUI/output/face_solution/t47_turn_768_sylvanas_start0088_gate_comparison_20260923_00001_.mp4`。抽帧确认标记框修正为左侧 Sylvanas；此前用最大脸生成的 `t47_turn_768_start0088_gate_comparison_20260923_00001_.mp4` 误标 Superman，不作为验收结果。
- 用户确认后续按源脸像素高测试，并要求清理测试视频。已生成静态像素阈值对比图：`/home/sean/projects/ComfyUI/output/face_solution/t47_pixel_threshold_contact_20260923.jpg`（长拉远片，70/60/50/40/30px，交叉帧92/101/119/133/145）；`/home/sean/projects/ComfyUI/output/face_solution/t47_turn_pixel_threshold_contact_sylvanas_20260923.jpg`（双人转头片，正确目标Sylvanas，交叉帧89/101/121/134/166）。
- 本轮阈值测试视频和缩放中间片未直接删除，而是可恢复移动到 `/tmp/t47_cleaned_20260923/`；原始母片及用户确认的第94帧基准对照保留。保留的静态图作为后续像素阈值判断依据。

## 2026-09-23：固定 70px 的 Hero 多镜头静态对照

- 用户复核结论：70px 比较合适；50px 已基本不可接受；40px 即使 refine 也开始丢失角色特征。后续对照固定测试 70px，不再生成 50/40px 启动视频。
- 已对四条已有 Hero 原片/Refine 成对视频生成静态 70px 对比图（不新增视频）：
  - `t47_hero_final8_pixel70_contact_20260923.jpg`，70px交叉帧28；
  - `t47_hero_motion_turn_pixel70_contact_20260923.jpg`，起始帧即低于70px，说明此镜头没有经过大脸阶段；
  - `t47_hero_updown_pixel70_contact_20260923.jpg`，起始帧即低于70px；
  - `t47_hero_headshake_pixel70_contact_20260923.jpg`，70px交叉帧89。
- 所有静态图位于 `/home/sean/projects/ComfyUI/output/face_solution/`。本轮只保留静态图和原始母片；相关阈值测试视频已可恢复移动到 `/tmp/t47_cleaned_20260923/`。

## 2026-09-23：本轮交付收束

- 校正文档 `experiments/h3_face_solution/T47_face_refine_research.md` 的验收入口，移除当前输出目录中已不存在的旧文件名，改列现存的 1344 pull-back、360°/转身、回望和最新 tracking-gate 视频。
- 将最新规则固化：`face_h/frame_h` 仅作启动 refine 的候选信号；真实 tracking lost 必须硬停止并保留源像素；低质量误框不得继续进入 H3，否则可能把背景纹理重绘成面具/一坨。`0.088` 只适用于当前内容的候选启动比例，不是跨内容硬阈值。
- 研究结论：完整人物 reference 给 H3 object/refine，face-only reference 只给 CLIP Vision identity tracking，源视频 crop latent 保留动作/角度/表情/光照/时序；768×768、crop factor 3、8 steps、动态 denoise、face-only stitch、多人逐人串行是当前 4090 安全基线。
- 本轮未新增 GPU 运行、未启动/重启 ComfyUI、未修改 Hive 完成状态；任务结果在当前任务上下文汇报。

## 2026-09-23：通用两阶段预分析首轮测试

- 用户要求将“人物/脸部识别”和“H3 refine”拆成通用两阶段管线。第一阶段只分析，不执行 H3；第二阶段读取已确认轨迹后再 refine。
- `tools/h3_face_crop_refine_runner.py` 新增 `--analysis-report-prefix`。在 `--report-only` 下通过 `SaveStringKJ` 将选脸报告和逐帧变换报告保存到 `ComfyUI/output/face_solution/analysis/`，避免分析结果只存在 ComfyUI 日志中。
- 对疑似骷髅误检的双人侧脸源片 `/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_00001_.mp4` 做自动预分析：124帧、1344×768，YOLO共248个候选检测，最多2脸/帧；ClipVision使用现有 face-only identity reference，自动选择1条Sylvanas轨迹，124/124帧保持检测，源脸高45.2–90px，无丢检。
- 报告：`/home/sean/projects/ComfyUI/output/face_solution/analysis/t47_auto_preanalysis_final8_20260923_selection_00001_.txt` 与对应 `_transform_00001_.txt`。当前结果说明身份选择能在该片中选中左侧Sylvanas，但报告还没有持久化每个候选框的身份分数/人物关联，因此尚不能证明骷髅候选已被明确标记为 `false_positive`。
- 另对长转头片 `/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_wide_headshake_turn_360_00001_.mp4` 做同样扫描：241帧、409个候选检测，ClipVision选择1条轨迹，228/241帧真实检测，丢检区间为181、188、215–225；报告为 `t47_auto_preanalysis_headshake_20260923_*`。
- 当前自动化首轮结论：通用预分析可行，且不需要信任第一帧；但要满足“缓存后第二阶段不重新猜测”的目标，还需把 `face_pick` 原始候选框、候选身份分数、人物框和最终 gate 状态写入结构化 JSON manifest，并增加 manifest loader。现阶段已先保存可审计文本报告，未运行 H3 refine。
- ClipVision 阈值 A/B：将同一侧脸双人片的身份阈值从旧基线 `0.20` 提高到建议值 `0.80` 后，真实 Sylvanas 候选最高分约 `0.768`，整条镜头被错误标记为 absent；说明通用管线不能硬编码 `0.80`。当前应使用全局/局部多视角 anchor + 候选间分数 margin + 时空连续性自适应判断，阈值只作为项目可校准参数。
- 已实现 `H3FaceManifestSave` 节点及 runner 参数 `--analysis-manifest-prefix` / `--refine-start-px`：manifest 设计包含源视频路径/哈希、尺寸帧数、检测器参数、身份模型/分数、原始候选框、选中轨迹、逐帧 face_px、检测状态和 refine/original gate。当前代码已通过 `py_compile`；共享 ComfyUI 未重启，因此新节点尚未在当前进程中加载，实际 manifest 写盘测试待下一次安全 reload 后进行。
- 外部方案检索：`face-finder` 已实现多张 reference、consensus/min-matches、连续片段、视频 hash/checkpoint、reference embedding 缓存和检测结果导出；与我们的“预分析/缓存/多视角身份库”方向高度相近。ComfyUI-H3-FaceRefine 上游已实现逐 shot 选脸、identity_reference、连续跟踪和一次检测后通过 face_pick 传递框，但未见我们要的完整结构化 manifest + 70px refine gate + 人物辅助关联闭环。FaceFusion/ComfyUI-facefusion 可按 reference_face_image 在多人视频中跟踪目标，并提供替换/换检测器路线，但目标是换脸，不是 H3 局部 latent refine。未发现一个现成项目完整覆盖“风格化角色、多视角 reference、骷髅误检排除、预分析缓存、第二阶段 H3 局部重绘”这一组合。
- 已下载研究副本到 `vendor/sean_source_research/`：`face-finder`、`comfyui-facefusion`、`h3-face-refine-upstream`；`ComfyUI-faceExtractor` 网页资料可见但 clone 地址返回 repository not found，未安装。已新增 `[Sean]` 研究文档 `docs/42_h3_face_preanalysis_external_research.md` 并更新 `docs/INDEX.md`；文档检查现已通过。
- 仓库同步检查（2026-09-23）：face-finder 本地/远程 HEAD 均为 2025-06-12；facefusion 本地/远程 HEAD 均为 2025-01-21；H3-FaceRefine 本地/远程 HEAD 均为 2026-09-12，当前研究副本未落后远程。
- 用户要求续开 T47；`hive-task start` 返回成功并生成 Codex task `cx-mudstcxk-7td`，但随后 `hive-task info` 仍显示旧 generation=3、旧过期 lease（与此前 Coordinator 状态投影问题一致），因此远程续开尚未得到可靠确认；本地仍以本 progress 作为恢复上下文，不据此伪造 checkpoint。
- 资源：预分析租约 `d1a7991a-c50e-49f4-8ee6-d3734a434869`；分析结束后尝试释放时 hive-resource daemon 短暂掉线，未能确认 release 响应，租约按TTL自然失效；未启动/重启 ComfyUI。

## 2026-09-23：预分析 manifest 续开实现

- 继续 T47 generation=4：围绕“第一阶段分析、第二阶段只消费缓存”补齐 manifest 消费路径。
- `H3FaceSelect` 新增可选 `analysis_manifest`：读取并校验 `h3_face_analysis_manifest` v1、源视频帧数/尺寸，然后直接复用 JSON 中的候选框、置信度、shot picks、检测和身份参数；manifest 路径不会加载 detector 或重新做 identity selection。
- `tools/h3_face_crop_refine_runner.py` 新增 `--analysis-manifest`，并在 manifest 模式下关闭 `H3FaceTrackCrop` 的二次 identity tracking；第二阶段仍走现有 H3 local latent refine/stitch。
- 验证：runner 与 ComfyUI 节点源码均通过 Python AST 静态校验；未 reload/重启共享 ComfyUI，未启动 GPU，尚未做真实 manifest 闭环运行。
- 下一步：获准安全 reload 后，用现有 `t47_auto_preanalysis_final8_20260923_*` 对应源片做一次 manifest 读取闭环；核对输出与预分析轨迹一致，再决定是否增加源哈希校验与结构化候选 identity/margin 字段。
- 2026-09-23 续接协议复核：[Sean] 确认前一轮只写入 checkpoint，没有设置新对话可接管标记；因此新对话的 start 在永久 controller 模式下正确拒绝了直接 claim，checkpoint 也因旧 worker/generation 被拒绝。Hivemind 已补充 `handoffReady`：当前对话 checkpoint 后，新对话 `hive-task start T-comfy-ops-47` 会先注册新 Worker，自动调用原子 handoff，再把 checkpoint.context 注入启动提示；旧对话只读。正式 Task Center 已部署并通过 27 项 Coordinator 回归测试，当前任务 generation=4、`handoffReady=true`。本机隧道 `hivemind-task-center-tunnel.service` 已 enabled/active，3191 健康检查返回 protocolVersion=2；此前日志中的 `Broken pipe` 已由 systemd 自动重启恢复，沙箱内无权限时可能出现假性 fetch failed。

## 2026-09-26：当前交接摘要

- 官方 `ComfyUI-H3-FaceRefine` v1.1.2 已完成升级回归；当前权威续开入口为 `docs/43_h3_facerefine_current_state.md`，本任务不再重复维护一套独立参数表。
- Continuum 4×8 实测：32 秒整段 FaceRefine 因主机内存压力主动中止；改用 8 秒/192 帧窗口后，红发角色 c1/c2 成功（228.2–275.1 秒/段），精灵 c2 因 `face-index=1` 误选红发角色而作废。
- 后续第一优先级是预分析 manifest/坐标 ROI/identity gate 的目标锁定闭环；错误目标输出不得进入成片。`face-index` 只能作候选排序，不能作为双人身份契约。
- 当前生产分流：latent 二采负责全片结构与分辨率；FaceRefine 只处理近中景或明确需要修脸的 8 秒以内片段；VOSR2 仅为可选末端锐化，不解决丢检或 20–35px 远景身份恢复。

## 2026-09-26：长度与资源基准

- 清缓存后，8 秒/192 帧、768 crop、8 steps、单脸 FaceRefine 成功，耗时 222.3 秒；采样阶段显存约 23.1GiB，系统可用内存最低约 375MiB。
- 直接扩展到 16 秒/384 帧后，显存约 22.9GiB、GPU 100%，系统可用内存降至约 300–500MiB并开始使用约 2.3–2.4GiB swap；为避免主机 OOM 主动中止，未继续 20/24 秒。
- 当前结论：8 秒是本机当前已验证安全分段；16 秒是风险边界而非稳定上限。下一步若要提升单次长度，先定位长序列系统内存占用/降低内存峰值，再复测 16 秒。
- 源长度对照已完成：FaceRefine 先完整解码源视频，再执行 `frame_load_cap`。5.17 秒源处理 124 帧耗时 125.1s；32 秒源只处理前 124 帧仍耗时 140.6s（慢约 12.4%），证明“只处理 0–8 秒”不能抵消长源文件的内存成本。物理裁成 8 秒后处理 192 帧成功，耗时 180.2s，未出现 16 秒测试的危险内存状态。后续流程应在 FaceRefine 前物理切段；当前 768 crop/8 steps 的 8 秒物理短源是安全基线。
- 详细记录：`experiments/h3_vae_upgrade/sean_facerefine_duration_benchmark_20260926.md`；资源观测 `a11a2151-5c91-4458-aecb-de525304920e`；本轮 GPU 租约已释放。

## 2026-09-26：Reference 生成链纠偏与新 Agent 续接入口

- 用户确认 Reference 正式链路必须是：`统一提示词 → 主图 → H3 全视角/视频 → 抽帧 → QC → manifest`。Krea2 只能作为主图阶段；Codex image、独立 Krea2 逐视角生成和其他模型不得进入正式 F/W/WB/S/Q/B 包。
- 本轮 A/B 的 direct-Krea2 v1 产物已判定为 rejected noncanonical：它们没有经过 H3 主图到全视角链，不能作为 T47-1 的 reference 验收依据。项目产物尚未删除，待用户确认新 Agent 接管后按精确清单清理。
- 文档已整理：`docs/45_ref_asset_handbook.md` 是唯一当前 Reference 手册；`docs/40_krea2_prompt_and_identity_pipeline.md` 只保留 Krea2 主图专题；旧 `docs/23_refimage_system.md` 标记为历史设计；重复的 46 已合并/移除。相关结论追加至 `.pi/ledger/h3-prompt.md` 的 `C-20260926-01`。
- 正确续接必须先读：项目 `AGENTS.md`、`docs/INDEX.md`、`docs/45_ref_asset_handbook.md`、`docs/40_krea2_prompt_and_identity_pipeline.md`、`docs/34_ref2va_generation_guide.md`、`docs/17_h3_prompt_writing_rules.md`、`workflows/h3_shushu_object_ref_probe.json`、本 progress 和 T5 reference 组织证据。
- 新 Agent 的第一阶段只做 H3 reference pipeline smoke，不做 FaceRefine 视频测试：确认主图输入、H3 ContactSheet/视频全视角输出、帧抽取、F/W/WB/S/Q/B manifest 写盘；通过人工检查后再进入 H3 Ref2VA smoke。
- 生成门禁：不得调用宿主 `image_gen`；不得使用 `tools/krea2_identity_edit_runner.py` 直接生成 S/Q/B；不得从不同角色版本拼接；每个资产必须记录 `source_main_image`、H3 workflow、prompt hash、seed、抽取帧号和 QC 状态。
- 当前远程 Task Center 状态核对：`T-comfy-ops-47` 已处于 `awaiting_acceptance`、无 controller、generation=6。由于当前 CLI 在 T-ID 后不支持 `--help` 形式，误将接口探查触发为实际 finish/awaiting_acceptance 操作；未继续执行任何远程写操作。新 Agent 接管前需按当前 Task Center 新接口执行 reopen/claim/handoff，不使用旧 `hive-task start`。

## 2026-09-26：严格双视图 prompt + 1536×1024 速度复测

- 用户指出上一批的三个确定问题：部分图出现两个正面一个背面；东方女剑士肩甲/肩胛前后不对应；红法师头发前后不一致。
- `tools/krea2_prompt_profiles.py` 的 turnaround prompt 已加强为：恰好两个主体、左正右背、同一中立姿势、同脚位/手臂/肩高、肩甲对应同一肩胛 landmark、发型颜色/长度/绑法保持一致、禁止第三主体和重复正面。
- 为恢复已保留的 8 个正面锚点，新增最小源清单 `experiments/krea2_front_back_consistency_20260926_v2_recovered/manifest.json`；未重新生成正面图。
- 新批次 `experiments/krea2_turnaround_sheet_batch_20260926_v2/` 使用 1536×1024（1.57 MP），8/8 成功，串行总耗时约 192.6 秒，平均 24.1 秒/张，相比上一批 1728×1152 的 33.6 秒/张快约 28.4%。
- QC：布局无第三主体 6/8；东方女剑士与冰狼仍出现两个正面一个背面。红法师布局通过但双侧编发/中央后辫仍不构成同一明确发型；东方女剑士背面肩甲结构仍未严格对应。全批次仍为实验产物，不进入 canonical reference。
- 相关 prompt 代码、manifest、原图、contact sheet、hash 和 QC notes 已归档；GPU 租约已释放。

## 2026-09-26：暂停生成，重新检索多视图统一性方案

- 按用户要求暂停生成，使用 sources 对 GitHub/Hugging Face/ComfyUI 相关资料重新检索，并回查本地 T-comfy-ops-38、T-comfy-ops-43 与 T-20260815-07 历史记录。
- 找回并确认此前主流程辅助候选：`ComfyUI-H3-ContactSheet` + `minimax_h3_five_view_512_s1500.safetensors`；本机节点和 LoRA 仍在，历史实测为风格化角色 512 约45秒、1024约50秒出5视图，写实旋转曾失败。
- 新增研究文档 `docs/46_multiview_consistency_research.md`。当前最值得恢复验证的是 OrbitSheets 的 H3 硬切 front/face/left/right/back + 内容聚类抽帧，其次比较 H3 ContactSheet 五槽和 H3 Edit 的 6/8 view decoder；静态 Krea2/Flux 多视图 LoRA 暂列对照，不进入正式 canonical。
- 本轮只检索和记录，没有安装新节点、下载新模型或生成图；GPU 无租约。

## 2026-09-26：CharacterSheet QuadView 八案例 smoke

- 按用户要求测试静态 CharacterSheet，不改变 canonical reference 流程。下载并安装 `QuadView_krea2_v1.safetensors` 到 ComfyUI LoRA 目录。
- 由于用户此前手动清理了恢复 manifest，重新建立最小测试清单 `experiments/krea2_charactersheet_test_20260926/manifest.json`；只引用仍保留的 8 张正面锚点，不使用旧 turnaround 作为输入。
- 新增批次 `experiments/krea2_charactersheet_quadview_20260926_v1/`，8/8 成功。配置为 1536×1024、10 steps、CFG 1、Euler/simple、ref boost 1；串行平均约 27.1 秒/张，总计约 216.6 秒。
- 结果为 face close-up + front full body + side full body + back full body 四栏。初检 8/8 均有四个不同视角，未见上一批的“两个正面一个背面”或明显重复正面；东方面剑士、红法师、冰狼和蜥蜴怪的服装/发型/身体结构转向关系也明显更好。
- QC 仍标为 `pass for review`，不是 canonical：单图四栏需要进一步裁切、放大和逐项检查，才能写入 F0/W0/WB/S/Q/B manifest。详见 `experiments/krea2_charactersheet_quadview_20260926_v1/qc/README.md`。
- GPU 租约已释放；未删除用户文件。

## 2026-09-26：实验 1，QuadView Krea2 严格三视图 prompt

- 官方仓库核对确认：没有 Krea2 专用 TripleView LoRA；只有 `QuadView_krea2_v1`。因此用同一东方女剑士正面锚点、同一 seed/参数，仅把 prompt 改为严格 `front + side + back full body only`。
- 结果成功：1536×1024 输出恰好三栏，没有脸部特写、hero、第四栏或额外角色。正面/严格侧面/背面清晰，马尾、肩甲、长外套、红腰带和武器保持统一。
- 结论：QuadView Krea2 可以通过 prompt 实现三视图，但这是 prompt-level 行为，不是独立 TripleView 模式；需要更多角色复测后才能作为稳定默认。产物：`experiments/krea2_quadview_threeview_test_20260926/`。

## 2026-09-26：QuadView 两种三栏布局 A/B

- 使用东方女剑士和冰狼两个角色，分别测试 `脸部特写 + 正面全身 + 背面全身` 与 `上半身正面 + 正面全身 + 背面全身`。
- 四张图均 1536×1024、10 steps、CFG 1、Euler/simple、ref boost 1；4/4 成功，均严格生成三栏，无侧面、第四栏或 Dynamic 额外区域。
- 两种布局都能保持发型/角/毛发、肩甲/披风、腰带、武器和背部轮廓。`face + front + back` 更适合脸部身份与前后服装；`upper-body + front + back` 更适合肩颈、胸前装备和上半身细节。
- 产物：`experiments/krea2_quadview_layout_ab_20260926/`，contact sheet 和 QC 见 `qc/README.md`。

## 2026-09-27：QuadView 加宽左脸栏复测

- 按 Sean 修正后的布局测试东方女剑士：前后保持原来的窄长全身矩形，左侧脸部栏加宽、脸部放大，整体改为 1792×1024，不留白。
- 结果符合预期：左侧脸部明显更大更清楚；中间正面和右侧背面仍保持完整竖长比例与一致高度。马尾、肩甲、长外套、红腰带、武器和靴子保持统一。
- 产物：`experiments/krea2_quadview_wide_face_test_20260927/`；当前建议先用该布局做两角色复测，再批量扩展。

## 2026-09-27：固定 QuadView 布局与四角色复测

- Sean 要求将多个已测试 prompt 和特征说明保留到同一目录，并固定生成流程。新目录：`experiments/krea2_quadview_fixed_layout_batch_20260927/`。
- 目录内保存 4 个 prompt 版本：严格三视图、脸部+正面+背面、上半身+正面+背面、当前生产候选的加宽左脸布局；manifest、脚本、原图和 QC 均在同一目录。
- 当前固定布局为 `1792×1024`：左侧加宽脸部+上半身栏，脸更大；中间正面全身、右侧背面全身保持原来窄长矩形；无留白。用东方女剑士、红法师、矮人工程师、冰狼分别测试，4/4 成功，平均约 27.4 秒/张。
- 初检四个角色均保持脸/发型、服装、装备和背部轮廓统一；状态为 `pass for review`，等待 Sean 人工检查。未删除之前目录。

## 2026-09-27：全部 QuadView 配置统一预览矩阵

- 按 Sean 要求，将已保存的 4 种 prompt 配置全部对同一批 4 个角色生成：严格三视图、脸部+正面+背面、上半身+正面+背面、加宽左脸布局。
- 共 16 张，16/16 成功；严格/脸部/上半身布局为 1536×1024，加宽左脸布局为 1792×1024。总输出和按角色/按布局预览均归档到 `experiments/krea2_quadview_fixed_layout_batch_20260927/all_layouts/`。
- 目录内 `README.md` 提供所有比较入口；当前只交付 Sean 人工比对，不提升任何配置为最终 canonical。

## 2026-09-26：DynamicCharacterSheet 结构化 prompt smoke

- 下载 `DynamicCharacterSheet_krea2_v1.safetensors`，按官方结构化 prompt 格式对同一批 8 个正面锚点测试；未使用旧 turnaround 作为输入。
- 官方推荐起点确认：1536×1024、10 steps、CFG 1、LCM sampler、simple scheduler、LoRA strength 1。实际 8/8 成功，平均约 27.1 秒/张。
- 输出包含 metadata、hero、front/side/back、action poses、silhouettes、expression/state study 和 detail crops。整体身份、服装、发型、装备和怪物结构保持得很好，内容丰富度明显超过 QuadView。
- 主要问题：Dynamic 的文字生成仍明显乱码/伪文字，部分 panel 标签错误；动作姿势和细节栏不能直接视为 canonical reference。定位为设计资料板和 QC 辅助，不替代 QuadView 或 H3。
- 产物：`experiments/krea2_dynamic_charactersheet_20260926_v1/`，详见其中 `qc/README.md` 和 `qc/contact_sheet.png`。GPU 租约已释放。

## 2026-09-27：收敛为两种 active 布局

- 社区方案复核后确认：半身/bust 应完整露出双肩、衣领和上躯干；若只服务脸部，则应改成 head-focused portrait，不能把“脸部特写”和“完整半身”混在同一 prompt。
- 当前只保存并激活两种配置：`face_front_back_focused_head` 与 `upper_front_back_full_upperbody`；两者均为 1792×1024、左 43% / 中右各 28.5%、无留白、正面/背面保持窄长全身矩形。
- `face_front_back_focused_head`：脸占主体，保留发际线、耳朵、颈部和双肩顶部；`upper_front_back_full_upperbody`：头到腰/中躯干，双肩、衣领、上胸、上臂和肩甲/袖子/背带完整可见。
- S/side 配置暂不加入。精确 prompt、特征和 active manifest 均在 `experiments/krea2_quadview_fixed_layout_batch_20260927/`。

## 2026-09-27：active QuadView 两布局四角色 preview

- 按当前 active 标准，对东方女剑士、红法师、矮人工程师、冰狼各生成一张 `face_front_back_focused_head` 和一张 `upper_front_back_full_upperbody`，共 8 张，8/8 成功。
- 两种布局均使用 `1792×1024`、`QuadView_krea2_v1.safetensors`、10 steps、CFG 1、Euler/simple、ref boost 1；单张约 30.1–30.8 秒。
- 结果统一归档在 `experiments/krea2_quadview_fixed_layout_batch_20260927/active_preview/`，总览、按角色和按版式 contact sheet 均已生成；GPU 租约已释放。
- 初检中，`face_front_back_focused_head` 四个角色均形成目标三栏；`upper_front_back_full_upperbody` 的东方女剑士、矮人工程师、冰狼通过初检，但红法师发生布局漂移，额外出现侧面栏，成为四栏，标记为 `layout drift / review`。等待 Sean 人工验收。
- 本批仍是静态预览，不进入 canonical；S/side 未生成，H3 turnaround 和 F/W/WB/S/Q/B manifest 未改变。

## 2026-09-27：face + front + back 加宽脸部布局 v2

- Sean 要求脸部栏继续加宽、正面/背面栏变窄，并指出此前矮人工程师出现两个背面。
- 已将 `face_front_back_focused_head` 调整为 `52% / 24% / 24%`，并在 prompt 中强化“恰好三栏、唯一正面、唯一背面、禁止第二背面/侧面/三四分之三视图”。
- 按要求只生成一张版式 preview，不再按人物批量生成：1/1 成功，约 30.4 秒。左侧脸部明显放大，正面/背面仍完整，未见重复背面。
- 结果：`experiments/krea2_quadview_fixed_layout_batch_20260927/active_preview_v2/`；等待 Sean 检查后再决定是否批量复测。

## 2026-09-27：基础 face + front + back 60/20/20 preview

- 按 Sean 要求先测试通用基础布局，不加入大头发、翅膀等人物特殊适配，也不按人物批量生成。
- 新建简洁通用 prompt：左脸部约 60%，中间正面约 20%，右侧背面约 20%；要求脸部突出、正反面完整、尽量减少空白，并禁止重复视图。
- 单张 preview 1/1 成功，约 30.5 秒。初检脸部更聚焦，正面/背面窄但完整，整体空白较少。
- 结果：`experiments/krea2_quadview_fixed_layout_batch_20260927/active_preview_base_60_20_20/`；等待 Sean 检查。

## 2026-09-27：CharacterSheet / QuadView 社区资料复核与当前结论

- Sean 要求核对社区对 `QuadView_krea2_v1` 的使用经验，重点确认视图数量、布局可控性、LoRA 强度和失败模式。
- 官方模型卡、官方 ComfyUI workflow、官方 demo、ComfyUI Wiki、Tensor.Art 和社区长文的共同信息：QuadView Krea2 的默认目标是“脸部特写 + 正面全身 + 侧面全身 + 背面全身”；推荐 `1536×1024`、10 steps、CFG 1、Euler/simple、LoRA strength 1.0。官方没有面板宽度参数，也没有 `60/20/20` 的布局控制。
- 已确认的可控范围：通过 prompt 可把四视图改成三视图，并改变第一栏内容（脸部/上半身等）；不能可靠改变三栏实际宽度。当前本地 `60/20/20` preview 仍生成接近等宽栏，证实 LoRA 的版式先验高于比例提示词。
- 官方限制与本地现象一致：不同视角可能出现脸、服装、配件和比例变化；侧面/背面可能需要重生成或手工修正；复杂配件和非人类角色更不稳定。矮人工程师重复背面、红法师额外侧面栏属于已知失败类型。
- 官方 workflow/demos 把 QuadView 当作固定多视图 reference-sheet 生成器；Dynamic 虽允许更自由的结构化 prompt，但属于实验模式，不用于当前基础布局结论。
- 当前工作结论：[定论候选] QuadView 的强项是视角数量/语义和身份关系，不是精确排版。基础流程应接受其近似等宽组合图，再进行脸部栏裁切/放大和正反面独立裁切合成；不要继续依赖 prompt 直接实现精确栏宽。
- 本轮只完成资料复核和总结，没有新增生成；GPU 空闲。续开入口：`experiments/krea2_quadview_fixed_layout_batch_20260927/active_preview_base_60_20_20/`，先由 Sean 检查基础版，再决定是否固定布局或测试后处理裁切。
