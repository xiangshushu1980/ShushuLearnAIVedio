# H3 character reference organization test

## 当前状态

- Task Center T-ID: `remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196`
- 已完成：T0、T1、T2 五 seed、T3 两 seed、T4 数量消融。
- 当前阶段：证据精简与收尾，等待用户验收；未自行修改 Task Center 完成状态。

## 新增项目级 skill

- 已创建：`.pi/skills/reference-asset-organization/`
- 用途：设定图的 `design → generate → organize same-object package → select per-shot H3 inputs` 四阶段规则。
- 覆盖：人物、场景、法术、物品的最小/扩展参考包、同一对象合并边界、生成配方、H3 选择矩阵、manifest/QC 记录。
- 自审：已运行 `skill-creator` 的 `quick_validate.py`，无 TODO 占位符；已确认总板仅为辅助/负对照，不作为默认 H3 identity reference；已声明当前实测边界。

## 下一轮测试计划调整

- 已在 `docs/41_h3_character_reference_test_plan.md` 增加 T5：职责分离、有效像素与视角触发。
- T5 不比较 3 视图/6 视图总数；比较 `face_identity`、`wardrobe_full`、`wardrobe_body`、3/4、严格侧面、背面各自是否承担独立职责。
- 核心假设：全身图减少正脸信息、保留后脑/发型后侧/颈肩，可能降低脸部冲突；转身镜头再按需加入 3/4/侧面/背面图。该假设尚未成为 skill 定论。

## T5 执行进度（2026-09-24）

- 资产阶段：已从已验收 T0/T1 素材派生 `F_face_identity`、`W_wardrobe_full`、`WB_wardrobe_body`、`S_view_side`、`B_view_back`；未重新生成人物身份。
- 资产 QC：初版 WB 顶部露出下巴/前发，判无效并修正；当前 WB 为去掉正脸的前身服装/体态裁图，背面/后脑信息由 B 独立提供。
- 冒烟：T5-A `F+W` 与 T5-B `F+WB`，768×448、124 帧、8 steps、seed 20260924，均成功。
- 正式第一批：T5-A/T5-B 各 3 seed（20260924–20260926）、768×448、124 帧、20 steps，共 6 条，全部成功、无工作流错误。
- 阶段性目视观察：B 未见明显身份交换或额外人物；部分 B 样本主体更大、服装细节更清楚，但尚不能区分是 WB 职责收益还是构图/主体占比差异；未形成正式结论。
- 证据：ComfyUI output `t5_reference_roles/`、`t5_smoke_*`、`t5_A_F_W_s*`、`t5_B_F_WB_s*` 和 `t5_ab_quality_frames/`；runner 结果为 `t5_ab_quality_cases.json.results.json`。
- 资源：运行期间 GPU 正常工作，观测到约 21.3GB 显存占用；本次 runner 未自动登记 GPU lease，已记录为工程改进项，未启动并行任务。
- 下一步：先补齐匿名首/中/末帧复核和评分，再测试 T5-C `F+WB+Q`、T5-D `F+WB+S`；不要把当前 B 观察直接写入 skill。
- T5-D/E 视角阶段：D=`F+WB+S` 严格侧面、E=`F+WB+B` 背面，各 3 seed、768×448、124 帧、20 steps，共 6 条全部成功；冒烟和终点抽帧均通过，未见明显身份漂移。
- D/E 当前只能证明“专门视角图可支持对应转身终点”，不能证明相对无视角图更好；下一步补 D0/E0（去掉 S/B、保持 prompt/镜头一致）做因果对照。
- T5-D0/E0 正式对照已完成：D0=`F+WB`、prompt 要求严格侧面但无 S；E0=`F+WB`、prompt 要求背面但无 B；各 3 seed，768×448、124 帧、20 steps，共 6 条全部成功。
- D0/E0 终点抽帧：D0 均能到达合理严格侧脸，E0 均能到达合理正背面；seed 间构图/主体大小有波动，但未见明显身份或服装失败。该结果只说明在本次低动作、缓慢转身条件下，专用侧/背参考图尚未显示为必要条件。
- T5 阶段性解释：D/E 证明专用视角图“可用”，D0/E0 说明本场景中“可能不必用”；不能据此删除视角素材规则。困难姿态、遮挡、动态动作、精确侧/背配饰仍需专用图，T5-C 真正 3/4 资产测试尚未完成。
- 证据：`t5_d0e0_quality_cases.json.results.json`、`t5_d0e0_quality_frames/`；结果已写入外部 manifest 的 `no_view_ablation_phase`。
- T5-C Q 素材准备：尝试用本地 Krea2 Identity Edit 从已验收正面图派生 `Q_view_three_quarter`；生成成功但 QC 不通过，输出仍接近正面，未形成约 45° 3/4 视图。因此未进入 H3，对照批次不启动，避免把无效 Q 当成有效视角证据。
- 该失败记录为工程观察：当前 Krea2 参考编辑 profile 对“改变视角为 3/4”的执行不可靠；后续需使用可控的视角生成/已有真实 3/4 素材，不能仅靠重复同一 prompt 继续消耗 H3 批次。
- 修正后取得合格 `Q_view_three_quarter`（独立图像生成，约 45°、全身、单人、身份/服装可辨），并完成 T5-C：`F+WB+Q` 对 `F+WB`，各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- T5-C 终点 QC：Q 组各 seed 均明显向侧面收敛，未稳定保持目标约 45° 3/4；无 Q 组同样向侧面收敛，部分近裁。Q 未显示稳定的终点角度控制收益，但未见明显身份/服装破坏。
- 阶段结论：Q 参考“可用但非必要/非充分”；本批不把 3/4 图升级为默认必选规则，也不宣称 Q 能控制 H3 终点角度。证据为 `t5_q_quality_cases.json.results.json` 与 `t5_q_quality_frames/`。
- T5-F 已完成：`F+W+Q`（普通全身图保留正脸信息，再加入 Q）3 seed、768×448、124 帧、20 steps，3/3 成功。
- T5-F 末帧观察：加入 W 后没有相对 `F+WB+Q` 显示清晰的 3/4 终点、身份或服装收益；仍属于同类的角度收敛表现。暂不保留重复正脸作为默认增强项。
- T5 当前阶段性结论：`face_identity + wardrobe_body` 是更干净的基础组合；额外侧/背/3/4 或普通全身图没有在本次慢转身中显示稳定提升。复杂动作、遮挡、近景和精确配饰仍未覆盖。
- T5 近景阶段已完成：`F+W` 与 `F+WB` 各 3 seed，768×448、124 帧、20 steps，共 6 条全部成功；prompt 明确为单人近景、无对白，不引入未核对台词。
- 近景首/中/末帧抽查：两组脸部身份、眼睛、鼻口、发际线和尖耳稳定性非常接近，未见明显 `WB` 退化，也未观察到明确提升。结论暂记为“近景无显著差异”，最终排名仍需匿名评分。
- 证据：`t5_closeup_quality_cases.json.results.json`、`t5_closeup_quality_frames/`；结果已写入 manifest 的 `closeup_face_phase`。
- T5 匿名评分已完成初评：所有已完成 T5 cell 的首/中/末帧先按匿名 ID 复核，再揭示条件；评分表为 `t5_anonymous_scoring.json`。抽查范围覆盖 A/B/C/C0/D/D0/E/E0/F 及近景 A/B，共 11 个匿名 cell、33 条视频样本，无硬失败。
- 匿名汇总：全身场景中 WB 偶尔提高主体占比/服装可读性，但没有明确身份优势；近景 `F+W` 与 `F+WB` 基本持平；Q/S/B 及重复 W 均未显示慢转身的稳定收益。
- T5 当前暂定结论：`F+WB` 是职责分离意义上的默认候选，不是已证明的质量优胜者；视角图不是默认叠加项。评分为单人手工序数评分，不能当总体统计定论；后续若要升级 skill，需第二评审者或困难动作/遮挡验证。

## T6 困难动作/自遮挡验证（2026-09-24）

- 目标：验证侧面参考图是否只在复杂动作、自遮挡和 3/4 姿态中提供收益。
- 对照：T6-A `F+WB`；T6-B `F+WB+S`；同 prompt、同 3 seeds、768×448、124 帧、20 steps。
- 动作：抬弓、转向约 45°、拉弦；前臂/弓/弦短暂遮挡躯干并接近脸部，但不得遮住双眼；单人、无对白、无外部音频。
- 结果待执行；评分指标：身份、手臂/弓绑定、脸部遮挡后恢复、服装/配饰、肢体重复/融合、主体丢失、侧面终点。
- T6 正式批次已完成：A=`F+WB`、B=`F+WB+S`，各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- T6 终点/中帧抽查：两组均能执行抬弓、转向和自遮挡；加入 S 没有带来更稳定的动作或终点表现，B 部分样本主体更小、构图更弱；A 基线未出现明显身份或弓具灾难性错误。
- 阶段性结论：在本次拉弓自遮挡条件下，专用侧面参考仍未显示默认收益；不能据此排除极端遮挡、精确侧面配饰或更大动作幅度的需求。结果写入 manifest `t6_difficult_action_phase`。

## T7 隐藏视角跨视频一致性（2026-09-24）

- 新问题：T5/T6 证明“能转过去”不等于“不同视频的隐藏视角细节一致”。
- 假设：3/4 主要可由正面推断，侧面有中等隐藏细节，背面最依赖模型自由补全；专用 Q/S/B 可能约束跨视频差异，但尚未验证。
- 设计：Q、S、B 三种终点分别比较无专用图（`F+WB`）和带专用图（`F+WB+Q/S/B`）；同 prompt、768×448、124 帧、20 steps、同 seed。首批预注册 6 条 seed 20260924，若无基础设施问题再扩展至 20260925–26。
- 指标：终点类别稳定性、后脑/头发、肩甲、腰带、披风、弓具等隐藏细节的跨视频一致性；不把“成功转身”直接当作一致性通过。
- T7 首批 6 条已完成但判为 `invalid_prompt`：初版共用 prompt 同时写入 Q/S/B 三种终点，只做局部字符串替换，未删除其他终点条件；S0 出现背面即暴露 prompt 泄漏。该批不进入评分、不进入结论，需改为 Q/S/B 三份独立 prompt 后重跑。
- T7 修正版 seed 20260924 已完成：Q0/Q1、S0/S1、B0/B1 共 6 条，全部成功；每个视角使用独立六段式 prompt，未复用含其他视角条件的 prompt。
- 修正版初步观察：B0/B1 的背面大轮廓相近，但箭筒/配件可见性和主体尺度不同；Q0 更接近侧面，Q1 也未稳定保持约 45°；这支持“背面隐藏细节更容易自由发挥”的假设，但单 seed 不能定论。
- 下一步：保持同一修正版 prompt，扩展 seed 20260925、20260926，完成 Q/S/B 三组跨视频一致性比较后再评分。
- S 扩展已完成：seed 20260925、20260926 的 S0/S1 共 4 条成功；结合 seed 20260924，共 3 个 seed 配对。
- S 阶段观察：无 S 时侧面终点的裁切、弓的位置/形态变化较大；有 S 时更稳定接近严格侧面，弓与身体关系更收敛，但主体占比常变小。暂记为“侧面隐藏结构可能有帮助，但伴随构图代价”，尚非最终定论。
- 下一步：用同一独立 Q prompt 扩展 Q 的两个 seed，再补齐 B 的两个 seed。
- Q 扩展已完成：seed 20260925、20260926 的 Q0/Q1 共 4 条成功；结合 seed 20260924，共 3 个 seed 配对。
- Q 阶段观察：无 Q 的终点在正面、3/4、侧面之间变化较大；有 Q 后更稳定趋向侧向轮廓，但没有稳定复现约 45° 3/4；弓具/服装大身份保持，主体尺度和构图发生变化。
- 阶段解释：Q 可能约束转向方向/侧向趋势，但不能可靠锁定精确 3/4 角度。下一步补齐 B 的 seed 20260925–26，确认背面隐藏细节的跨视频差异。
- B 扩展已完成：seed 20260925、20260926 的 B0/B1 共 4 条成功；结合 seed 20260924，共 3 个 seed 配对。
- B 阶段结果：无 B 时三条视频会自由补全箭筒/箭、后发型和配件显现，位置与主体尺度变化较大；有 B 时三条视频趋向同一套披风、后脑、弓和背部配置。该结果是当前最明确的跨视频隐藏细节一致性正向信号。
- T7 阶段性总论：B 对“背面物品/服装身份与绑定一致性”有较强帮助；S 对侧面结构/弓绑定有较弱帮助但伴随主体缩小；Q 主要改变转向趋势，不能稳定锁定 45°。结果不等于固定姿态，弓仍可随动作变化。

## WB 头部去除方式修正（2026-09-24）

- 发现：旧 `WB_wardrobe_body.png` 是矩形裁剪，错误地丢失头部边界并可能保留/诱导正脸信息；不符合“去脸/去头而保留完整服装身体”的目标。
- 新资产：`WB_face_erased`（去脸和前发、保留后脑/耳朵/颈肩）与 `WB_head_removed`（去整头和头发、保留衣领/肩甲/身体）。两者已落盘到 output/input 的 `t5_reference_roles/`。
- 冒烟：旧裁剪、face_erased、head_removed 各 1 条，768×448、124 帧、8 steps，3/3 成功；新两种都减少了明显正脸泄漏，head_removed 分离最彻底，face_erased 保留更多后脑结构。
- 暂不替换 skill 或正式 manifest 基线；下一步跑 20-step、3 seed 正式对照。
- 正式对照已完成：旧矩形 WB、`WB_face_erased`、`WB_head_removed` 各 3 seed，768×448、124 帧、20 steps，9/9 成功。
- 结果：H3 仍从 `F_face_identity` 生成脸，head_removed 不会让成片无头；两种新 WB 主要作用是减少第二张参考图的重复正脸竞争。新版本常使主体占比变小，head_removed 个别样本出现黑边/构图异常；尚未证明质量优于旧版。
- 当前资产建议：`WB_face_erased` 比 `WB_head_removed` 更适合作为下一候选，因为保留后脑/耳朵/颈肩上下文；但暂不替换 skill 默认资产，需先建立更干净的本地 mask/inpaint 版本。
- 颈部对照已完成：`WB_face_erased` vs `WB_neck_only`，各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- 结果：使用同一 `F_face_identity` 时，两种 WB 都能把脸/头发重新接回身体；抽查未见明显浮空头、头身比例崩坏或衣领连接失败。`WB_neck_only` 没有因缺少完整头部而失败；`WB_face_erased` 保留更多后脑上下文。
- 阶段结论：完全去头但保留中性脖子是可行候选；是否优于 face_erased，需继续评分头身比例、脖子/衣领接缝、发型连续性和跨 seed 一致性。
- WB 重点评分完成：首/中/末帧按头身比例、脖子/衣领接缝、发型/肩颈连续性、跨 seed 稳定性复核，评分表为 `wb_neck_focus_scoring.json`。
- 两种变体均无硬失败，当前评分基本持平：`WB_face_erased` 后脑/耳朵/发型上下文更完整；`WB_neck_only` 参考职责更干净，未出现明显头脸浮空或头身比例崩坏。
- 暂定选择：不能宣布单一版本胜出；需要减少头部竞争时优先 neck_only，需要保留后脑/发型连接语义时优先 face_erased。两者都暂不替换 skill 默认资产。

### WB 资产视角语义复核（2026-09-24）
- 复核发现：`WB_face_erased` 实际是“正面身体 + 后脑/后发”的混合视角，不是“正面头部轮廓去脸”。
- 这会与 `F_face_identity` 的正脸，以及独立 `B_view_back` 的后视参考产生语义冲突；因此此前 face_erased vs neck_only 的评分只能作为工程冒烟证据，不能作为公平选型结论。
- 当前更干净的候选是 `WB_neck_only`。后续若保留 WB 方案，必须重做“正面头部轮廓、去脸去前发、保留脖颈肩线”的资产，再与 neck_only 重新对照。

### WB_front_face_erased 重做（2026-09-24）
- 已使用内置图像编辑生成实验资产 `WB_front_face_erased.png`，并复制到 output/input 的 `t5_reference_roles/`。
- 初检通过：正面头部轮廓、无五官、无前发、无后脑/后发视角，脖颈和肩线保留；尚未进入 H3 质量结论。
- 下一步：以 `F+W`、`F+WB_neck_only`、`F+WB_front_face_erased` 做同 prompt、同 seed 的三组对照，测试普通转身、抬弓自遮挡和背面经过。

### WB 动态动作三组对照（2026-09-24）
- 设计：`F+W` 控制组、`F+WB_neck_only`、`F+WB_front_face_erased`；同一 Ref2VA 六段式动作 prompt、768×448、124 帧、20 steps、seed 20260924–26。
- 动作：抬弓、转入约 45°、拉弓、弓与前臂自遮挡、短暂背向经过；共 9 条，全部成功。
- 证据：`wb_dynamic_action_cases.json.results.json`；首/中/末帧目录 `output/sean_h3_character_reference_test/wb_dynamic_action_frames/`。
- 初看：三组均完成主要动作，未出现工作流错误；暂不据此宣布质量优胜。下一步按头身比例、脖颈/衣领接缝、发型连接、弓具自遮挡、背向阶段服装/配件一致性进行重点评分。

### 参考视角选择规则（2026-09-24）
- 阶段性规则：所有对象默认使用一个合格的主视/规范参考；只有当镜头或动作暴露隐藏表面时，才加入同一对象的侧面或背面参考。
- 该规则适用于人物、场景、法术和物品；视角图约束隐藏结构/身份，不等于固定姿势、相机角度或逐帧物理。
- 已更新 skill 的 `object-rules.md` 与 `selection-matrix.md`；人物部分仍保留当前实测边界，场景/物品的跨对象验证正在进行。

## 已保存结论

- T1：单人物独立多图 A 与角色板+独立脸部 B 在静态中景中均稳定。
- T2：A/D 均为候选；D 适合复杂双人物，A 适合单人物/少对象，C 适合站位优先，E 仅作负对照。
- T3：A/D/E 两 seed 完成；普通 Ref2VA 节点无独立 guide 输入，D-guide 标记为能力缺口。
- T4：7 cell × 3 seed × 20 steps；前 4 个单人物 cell 初始 prompt 曾泄漏 Subject 2，已判 invalid_prompt 并修正重跑；复杂 D、删除法术、删除物品 9 条有效，修正单人物 12 条有效。最终盲评分待后续需要时补。

## 权威记录与证据

- Manifest：`/home/sean/projects/ComfyUI/output/sean_h3_character_reference_test/sean_h3_character_reference_manifest.json`
- 现行手册：`docs/34_ref2va_generation_guide.md`
- 结论谱系：`.pi/ledger/h3-prompt.md`
- 代表性总览：manifest 中 `review_grid` / `comparison_grid` 字段对应文件。

## 工程注意

- 所有本任务产物均在 `/home/sean/projects/ComfyUI/output/sean_h3_character_reference_test`；ComfyUI input 副本在 `/home/sean/projects/ComfyUI/input/sean_t2_*`。
- ComfyUI Asset Seeder 会在每条输出后扫描 output 根目录；约 400 文件时曾出现约 112 秒扫描。未重启共享 ComfyUI，GPU lease 已释放。

## 清理策略

- 保留：manifest、源资产、T0/T1/T2/T3/T4 代表性总览图、少量代表性视频；输出目录清理后约 22MB。
- 删除：186 个重复/中间文件，包括重复 seed 视频、逐条首中末帧、初始 invalid_prompt 视频/帧、重复比较网格；同时删除 `_discarded_t2_invalid` 和 ComfyUI input 中 3 个重复 T0 副本。
