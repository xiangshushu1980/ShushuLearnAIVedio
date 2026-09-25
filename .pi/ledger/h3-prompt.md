# H3 提示词/风格/增强结论谱系

## 2026-09-24 T5 reference role conflict（阶段性，未定论）

- 资产候选：`F_face_identity` + `W_wardrobe_full` 对照 `F_face_identity` + `WB_wardrobe_body`；WB 为去掉正脸的前身服装/体态裁图，背面/后脑另由 `B_view_back` 提供。
- 运行：768×448、124 帧、普通 Ref2VA、无 LoRA、20 steps、res_multistep；A/B 各 3 seed（20260924–20260926），6 条均成功。
- 阶段性目视：WB 组未见明显身份交换或额外人物；部分样本主体/服装细节更大更清楚，但尚无法排除构图和主体占比 confound。不得据此升级为正式 skill 规则。
- 证据：ComfyUI output `sean_h3_character_reference_test/t5_reference_roles/`、`t5_A_F_W_s*`、`t5_B_F_WB_s*`、`t5_ab_quality_frames/`。
- 工程备注：本批 runner 未自动申请 GPU lease；后续批量前补资源租约登记，避免共享资源状态与实际运行脱节。
- D/E 视角补充阶段：`F+WB+S`（严格侧面）与 `F+WB+B`（背面）各 3 seed、20 steps 共 6 条全部成功；终点抽帧能达到对应侧面/背面，未见明显身份漂移。该结果只证明可行性，尚未证明相对无 S/B 的收益，需 D0/E0 对照。

> 提示词定论演进史。规则见 README.md。append-only。

## 条目索引

| C-ID | 主题 | 状态 | 备注 |
|---|---|---|---|
| C-20260816-15 | 渲染风格词主导 | ✅现行 | V7 混合风 |
| C-20260816-16 | 画面内文字控制（六块矩阵） | ✅现行 | 块5 必要条件 |
| C-20260816-17 | Seedance 7 条经验 H3 适用性 | ✅现行 | 适用 2.5/7 |
| C-20260816-18 | 提示词增强在线 IR API 选型 | ✅现行 | 在线胜出 |
| C-20260816-19 | turnaround LoRA 适用域 | ✅现行 | 仅动漫/风格化 |
| C-20260918-01 | 多 Subject 技能参考绑定与双人物一致性 | 🟡待验证 | 拆分绑定优于整图 |
| C-20260923-01 | H3 Ref2VA 多对象 reference 组织 | ✅现行 | A/D 候选，E 负对照 |
| C-20260923-02 | H3 Ref2VA reference 数量消融与 prompt 泄漏边界 | 🟡待验证 | 数量收益已测，盲评分待补 |

---

### C-20260816-15 | 渲染风格词主导
- 状态：✅现行（valid_from 2026-08-12）
- 现行值：i2v 快车道下 **prompt 风格词决定渲染风格**，首帧只锚定身份/构图——`Live-action, cinematic` → 真人写实（同首帧 aliya_1024）；`Anime style, cinematic` → 真实光照/真人质感 + 卡通渲染动漫角色（V7 混合风）；纯 2D 动漫 → 动漫首帧 + 不写人物描述（风格完全跟随首帧）
- 时间线：
  - 2026-08-12 提出：V7 对照实测（同首帧仅风格词差异；1024 写实怀疑系测试 prompt 自带 Live-action 模板开头，非分辨率问题；来源任务 T-20260812-07）
- 证据锚：params.md §提示词控制技巧（渲染风格词主导）/ .pi/tasks/comfyui-032-verify/progress.md（V7 风格发现）

### C-20260816-16 | 画面内文字控制（六块矩阵）
- 状态：✅现行（valid_from 2026-08-15）
- 现行值：**块5 逐字打字 = 文字生成必要条件**（A 基准/C 块6 无字 vs B 块5/D 完整有字）；**块6 否定单用无效但组合质量最佳**（D 主文字清晰无杂散）；**位置控制弱**（写 "on the wall" 实际挂窗户上，需更具体定位或接受模型自选）；首帧无文字时模型会自选位置挂文字
- 时间线：
  - 2026-08-15 提出：同首帧同 seed 矩阵 A/B/C/D（换场景同首帧对照；来源任务 T-20260815-07）
- 证据锚：params.md §提示词控制技巧（画面内文字控制）/ output/video/text_ctrl3/ / .pi/tasks/h3-new-findings-test/progress.md

### C-20260816-17 | Seedance 7 条经验 H3 适用性
- 状态：✅现行（valid_from 2026-08-14；34 条收尾 2026-08-16）
- 现行值：**适用 2.5/7**——电影感 ✅（空洞词 motion 3164 vs 具体风格 606，用导演名/具体灯光）；空洞形容词 ✅（空洞词无效果 vs 具体名词被执行：打光/光晕）；长度 ⚠️ 部分（关键元素靠前写，尾部别放高信息量：366 字尾部白鸽丢失、193 字猫重排到开头、72 字也崩）。**不适用 4.5/7**——双镜头 ❌（并行合成不崩但执行不稳定：b 镜头静止；手持感描述运动量反而最大 6500）；负面词 ❌（负面/正向/无约束零差异 0.59/0.59/0.60）；快速 ❌（同条件 motion 140 vs 143 零差异，无效 token，速度靠肢体动作描述）；I2V 描述实体 ❌ **相反**（描述越多=强调，人脸更清晰；不冲突不漂移；必须写明确运动指令：无=自由发挥 3709、弱动作+静态=冻结 76）。H3 无高频抖动崩坏（osc_high≈0）
- 时间线：
  - 2026-08-14 提出：16 条首批（T4 初判"负面词有抑制"疑雨夜霓虹 confound；T2/T7 成立初证）
  - 2026-08-15 修正：二批 10 条（晴天黄昏去 confound + 镜头统一 + T7 近景）T4r 三条零差异 → 否定词无效果；T6 机制定位（描述+运动/只运动/只描述三档）
  - 2026-08-16 修正：三批 8 条（同跑法同服装控制变量）T5r2 零差异坐实；T6r2 梯度确认"描述越多=强调"；34 条（16+10+8）全部完成收尾（覆盖 08-14 初判；来源任务 seedance-h3-verify）
- 证据锚：.pi/tasks/seedance-h3-verify/progress.md（最终结论表）/ experiments/seedance_verify/（cases+analysis）/ ComfyUI/output/video/h3_seedance{1,2,3}/

### C-20260816-18 | 提示词增强在线 IR API 选型
- 状态：✅现行（valid_from 2026-08-08）
- 现行值：**在线 H3-Context-IR API 为主路径**——输出质量远超自写（"差别非常大"传闻初步验证：一句话输入→电影级分镜+声音层+BGM 建议）；25 元 ≈ 200+ 次调用（7500 tokens ≈ 0.1 元）；**本地视觉 LLM 关闭**（GPU 切换 3-6min/次对 2min/条生产线不可接受，且无 LM Studio 安装）；IR 会加戏（黑盒不可控再实证）；diegetic 音乐可入 soundscape；i2v 比 t2v 长 2-3 倍（图驱动细节）
- 时间线：
  - 2026-08-08 提出：架构决策用户拍板（在线 IR 为主、本地视觉 LLM 弃用；来源任务 h3-prompt-agent）
  - 2026-08-08 补充：IR 样本库 13 条建成、官方媒体格式 bug 修复、i2v/t2v 差异观察
- 证据锚：docs/08_h3_prompt_agent.md（接入落地节）/ docs/17_h3_prompt_writing_rules.md / docs/18_ir_sample_teardown.md / scripts/h3_ir_rewrite.py / .pi/tasks/h3-prompt-agent/progress.md

### C-20260816-19 | turnaround LoRA 适用域
- 状态：✅现行（valid_from 2026-08-15）
- 现行值：**仅动漫/风格化可用**（45-50s 出 5 视图 + 拼接 strip，身份一致性好；512 档 45s / 1024 sweet spot 50s）；**写实 OOD 全崩**（用户目视）；必须用 ContactSheet 专用节点（ref2va 分区 + 五槽打包），普通 sampler 做不到且会降级运动
- 时间线：
  - 2026-08-14 提出：功能验证通过（动画域 512/1024 两档；来源任务 T-20260815-07）
  - 2026-08-15 修正：写实照片 OOD 验证失败 → 适用域限定动漫/风格化（覆盖 08-14 未限定版本）
- 证据锚：output/img_turnaround/ / workflows/turnaround_test.json / .pi/tasks/h3-new-findings-test/progress.md

### C-20260918-01 | 多 Subject 技能参考绑定与双人物一致性
- 状态：🟡待验证（valid_from 2026-09-18）
- 现行值：① **参考图拆分绑定优于整图**：把帽子裁成独立参考图，身份/帽子/服装/场景分别绑定为四个 Subject；帽子在 retention 与 detailed_description 中标记为 `fully_preserved` + `mandatory visible accessory`，保持效果最好；② 双人物场景「CC 在左、shushu 在右」五点抽帧**身份保持区分、无脸部混合**；③ **风险：身份源图背景会与场景竞争**——A 片首个抽样点短暂泄漏原始居家背景/动物，随后回到演播室，需强化场景排除或使用更干净的身份图；④ 外部音频锁定与五 Subject（身份/帽子/服装/场景/蓝色能量球）可同时提交 A/B 成功；⑤ 声音链路控制样本：因无 shushu 本人声音，使用既有数字人短语音 `audio_control_sample_s1.wav`，**明确不作 shushu 音色结论**
- 时间线：
  - 2026-09-18 提出：T-comfy-ops-38 双人物 A/B、四 Subject 绑定、五 Subject+外音锁定、声音链路控制样本同批实测（来源任务 T-comfy-ops-38）
- 证据锚：.pi/tasks/T-comfy-ops-38/progress.md / mem0 195e471b、9a722ee4、ead5f12c、2f144b9a

### C-20260923-01 | H3 Ref2VA 多对象 reference 组织
- 状态：✅现行（valid_from 2026-09-23；适用条件限定见下）
- 现行值：在普通 H3 Ref2VA、768×448、124 帧、无 LoRA、`res_multistep`、20 steps、低动作无对白双人物场景中，**A 独立多图**与**D 按人物语义簇混合**均稳定保持两个人物身份、左右站位、法术归属和物品归属；D 作为复杂双人物场景的默认候选，A 作为单人物/少对象基线；C 双人物构图板适合站位优先的镜头；E 一张总板只保留为负面对照，不作默认方案。
- 时间线：
  - 2026-09-23 提出并实测：T2 4 方案 × 5 seed × 20 steps 全部成功；A/C/D 无重复身份互换，E 语义分离最弱（来源任务 `remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196`）。
- 适用边界：本结论只覆盖低动作、无对白、768×448 的多对象绑定；不等同于复杂动作、近景脸部、1024×576 或长片结论。E 的总板不得作为默认 reference 组织。
- 证据锚：`/home/sean/projects/ComfyUI/output/sean_h3_character_reference_test/sean_h3_character_reference_manifest.json` 的 `t2_multiseed_quality` / `sean_t2_*_five_seed_mid_grid.png`；`docs/34_ref2va_generation_guide.md` §2026-09-23。

### C-20260923-02 | H3 Ref2VA reference 数量消融与 prompt 泄漏边界
- 状态：🟡待验证（valid_from 2026-09-23）
- 现行值：T4 以 7 个 cell、3 个 seed、20 steps 完成；仅身份、身份+服装、身份+服装+场景、角色板+脸部+场景以及复杂 D 的结果均可生成。单人物消融 prompt 若在通用保留句中提到未启用的第二人物，会诱导模型补出第二人物；该批必须判为 `invalid_prompt`，不能归因于 reference 数量。修正后 12 条单人物重跑通过；复杂 D/删除法术/删除物品 9 条初始结果有效。数量收益的最终质量排名仍待盲评分。
- 时间线：
  - 2026-09-23 提出并实测：初始 12 条因 Subject 2 prompt 泄漏作废；修正后重跑 12 条，另保留 9 条有效复杂 cell（来源任务 `remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196`）。
- 工程边界：ComfyUI output Asset Seeder 曾对约 400 个 output 文件做约 112 秒全量扫描；该扫描属于资产索引，不是 H3 推理。后续批量实验应关闭资产索引或隔离 output 根目录。
- 证据锚：manifest 的 `t4_reference_quantity_ablation`；`sean_t4_single_person_retry_mid_grid.png`；`docs/34_ref2va_generation_guide.md` §T4。

### C-20260924-03 | H3 T5 角色参考职责分离与视角触发（阶段性）
- 状态：🟡待验证（T5-D0/E0 已完成；T5-C 3/4 尚未完成）
- 现行观察：在低动作、缓慢转身、768×448、124 帧、20 steps 的本次条件下，`F_face_identity + WB_wardrobe_body` 在不提供专用侧/背图时，D0/E0 均能分别到达合理严格侧面/正背面终点（6/6 成功）。专用 S/B 图在 D/E 中也可支持对应终点，但尚未证明有因果质量收益。
- 解释边界：不能把“专用视角图不是必要条件”推广到所有镜头；困难姿态、遮挡、动态动作、精确侧/背配饰仍可能需要 S/B。3/4 需要真实 Q 资产单独测试，不能用严格侧面替代。
- 方法含义：reference 包按职责组织；`face_identity` 锚定脸，`wardrobe_body` 锚定服装/体态，视角图按镜头触发而不是按固定总张数加入。暂不升级 skill 默认基线，等待匿名评分和 T5-C。
- 证据锚：manifest `t5_reference_role_conflict.no_view_ablation_phase`；任务目录 `t5_d0e0_quality_cases.json.results.json`；`t5_d0e0_quality_frames/`。

### C-20260924-04 | T5-C 3/4 素材准备失败（不进入 H3 结论）
- 状态：🟡阻塞于合格 Q 资产（非任务阻塞）
- 观察：本地 Krea2 Identity Edit 以正面人物图和“约 45° 三视角”指令生成成功，但结果仍接近正面；未达到 `Q_view_three_quarter` 的 QC 条件。
- 处理：该图仅保留为失败证据，不作为 H3 reference，不启动 T5-C 对照；不能用严格侧面替代 3/4。
- 后续：寻找真实 3/4 定格素材或建立可控视角生成链路后再测试 `F+WB+Q` 对 `F+WB`。

### C-20260924-05 | T5-C 3/4 reference 对照（阶段性负结果）
- 状态：🟡待验证
- 运行：合格 `Q_view_three_quarter` 加入 `F_face_identity + WB_wardrobe_body`，对照无 Q；各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- 观察：Q 组和无 Q 组均向侧面终点收敛；Q 未稳定保持约 45° 3/4，未显示可归因于 Q 的终点角度控制收益。Q 组未见明显身份或服装破坏。
- 规则含义：3/4 图目前只能标记为可选视角提示，不能标记为必需输入，也不能承诺 H3 会按参考图保持目标角度。需要生产级 3/4 控制时，应另测更明确的镜头/端点设计。
- 证据锚：manifest `t5_reference_role_conflict.three_quarter_asset_phase`；任务目录 `t5_q_quality_cases.json.results.json`；`t5_q_quality_frames/`。

### C-20260924-06 | T5-F 普通全身图 + 3/4 图对照（阶段性）
- 状态：🟡待验证
- 运行：`F_face_identity + W_wardrobe_full + Q_view_three_quarter`，3 seed、768×448、124 帧、20 steps，3/3 成功；与同条件的 `F+WB+Q` 结果比较。
- 观察：保留普通全身图的重复正脸信息，没有显示稳定的 3/4 终点、身份或服装收益；仍未证明加入更多视角/重复脸部参考能提升慢转身。
- 方法含义：当前人物基础参考包优先使用职责分离的 `F+WB`；视角图和普通全身图按镜头特殊需求尝试，不作为默认叠加。
- 证据锚：manifest `t5_reference_role_conflict.full_wardrobe_plus_three_quarter_phase`；任务目录 `t5_f_quality_cases.json.results.json`；`t5_f_quality_frames/`。

### C-20260924-07 | T5 近景 F+W 对 F+WB（阶段性）
- 状态：🟡待匿名评分
- 运行：单人近景、无对白、无外部音频；`F_face_identity + W_wardrobe_full` 对 `F_face_identity + WB_wardrobe_body`，各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- 观察：抽查首/中/末帧后，两组脸部身份、眼睛、鼻口、发际线和尖耳稳定性非常接近；没有明显 WB 退化，也没有明确提升。
- 方法含义：目前没有证据要求在近景中额外保留普通全身图；`F+WB` 仍是更干净的默认候选，但正式定论需要匿名评分。
- 证据锚：manifest `t5_reference_role_conflict.closeup_face_phase`；任务目录 `t5_closeup_quality_cases.json.results.json`；`t5_closeup_quality_frames/`。

### C-20260924-08 | T5 全样本匿名评分汇总（阶段性）
- 状态：🟡待最终验收/第二评审
- 范围：已完成 T5 的 A/B/C/C0/D/D0/E/E0/F 与近景 A/B，共 11 个匿名 cell、33 条视频；首/中/末帧先匿名复核再揭示条件。
- 结果：本次复核样本无硬失败；WB 在部分全身样本中提高主体占比/服装可读性，但未显示明确身份优胜；近景 F+W 与 F+WB 基本持平；Q/S/B 及重复 W 未显示慢转身稳定收益。
- 暂定方法结论：`F+WB` 作为职责分离的默认候选合理，但还不是“质量已证明显著更好”的定论；视角 reference 不默认叠加。
- 限制：单评审者手工序数评分，不是总体统计结论；若需要升级 skill 正式基线，应增加第二评审者或进入困难动作/遮挡验证。
- 证据锚：manifest `t5_reference_role_conflict.anonymous_scoring_phase`；任务目录 `t5_anonymous_scoring.json`；output `t5_anonymous_review/`。

### C-20260924-09 | T6 拉弓自遮挡与侧面参考（阶段性）
- 状态：🟡待继续验证
- 运行：`F+WB` 对 `F+WB+S`；单人抬弓、约 45° 转向、前臂/弓短暂自遮挡脸部下缘和胸甲；各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- 观察：两组都能执行动作；S 没有带来更稳定的动作、身份恢复或终点表现，部分 B 样本主体更小、构图更弱。
- 方法含义：即使进入一次困难动作，侧面图仍不应默认叠加；仅在精确侧面配饰、极端遮挡或更高动作复杂度需求时继续专项验证。
- 证据锚：manifest `t5_reference_role_conflict.t6_difficult_action_phase`；任务目录 `t6_action_quality_cases.json.results.json`；`t6_action_quality_frames/`。

### C-20260924-10 | T7 首批 prompt 泄漏作废
- 状态：`invalid_prompt`，不进入结论
- 原因：同一 prompt 同时写入 Q/S/B 三种终点，只做局部替换，未删除未启用的终点要求；S0 出现背面，证明条件污染。
- 处理：遵守 T4 已确认的 prompt 泄漏纪律，改用 Q/S/B 三份完全独立 prompt 后重跑；首批 6 条只保留为工程失败证据。

### C-20260924-11 | T7 修正版 seed 20260924 隐藏视角观察
- 状态：🟡待多 seed 验证
- 运行：Q/S/B 各比较无专用图与专用图，使用完全独立的视角 prompt；6/6 成功。
- 观察：背面 B0/B1 广义轮廓相近，但箭筒/配件显现和主体尺度不同；Q0 偏侧面，Q1 也未稳定达到约 45°。初步支持“背面隐藏细节的自由补全差异更大”，但不能以单 seed 定论。
- 下一步：扩展相同 Q/S/B 对照到 seed 20260925–26，再判断专用视角图是否提高跨视频隐藏细节一致性。

### C-20260924-12 | T7 侧面 S 跨视频一致性初步信号
- 状态：🟡待 Q/B 完成
- 运行：修正版独立侧面 prompt；S0=`F+WB` 对 S1=`F+WB+S`，3 个 seed 配对，6 条有效视频。
- 观察：无 S 的侧面终点在裁切和弓的位置/形态上变化较大；有 S 的结果更稳定接近严格侧面，弓与身体关系更收敛，但主体占比常变小。
- 方法含义：S 可能对侧面隐藏结构有帮助，但收益与构图代价同时出现；不能把它简化为“加 S 必然更好”。
- 证据锚：manifest `t5_reference_role_conflict.t7_hidden_view_consistency_phase.s_consistency_extension`；任务目录 `t7_s_consistency_cases_25_26.json.results.json`；`t7_s_consistency_frames/`。

### C-20260924-13 | T7 3/4 Q 跨视频一致性初步信号
- 状态：🟡待 B 完成
- 运行：修正版独立 3/4 prompt；Q0=`F+WB` 对 Q1=`F+WB+Q`，3 个 seed 配对，6 条有效视频。
- 观察：无 Q 的终点角度在正面/3/4/侧面间波动；有 Q 更倾向侧向轮廓，但不能稳定复现约 45° 3/4。弓具和服装大身份保持，主体占比和构图改变。
- 方法含义：Q 可能有“方向/侧向趋势约束”而非“精确角度锁定”作用；不能宣称 Q 提升了 3/4 目标一致性。
- 证据锚：manifest `t5_reference_role_conflict.t7_hidden_view_consistency_phase.q_consistency_extension`；任务目录 `t7_q_consistency_cases_25_26.json.results.json`；`t7_q_consistency_frames/`。

### C-20260924-14 | T7 背面 B 跨视频隐藏细节一致性正向信号
- 状态：🟡阶段性现行候选，仍需生产镜头复核
- 运行：修正版独立背面 prompt；B0=`F+WB` 对 B1=`F+WB+B`，3 个 seed 配对，6 条有效视频。
- 观察：无 B 时箭筒/箭、后发型、配件显现和裁切在不同视频间自由变化；有 B 时三条视频趋向同一套披风、后脑、弓和背部配置。弓的位置仍可随动作/透视变化，不视为一致性失败。
- 方法含义：B 的价值不是帮助角色“第一次转到背面”，而是约束不可见背面细节和物品绑定，使不同视频更像同一套背面设定。B 可作为“需要严格背面设定/背部配饰一致”镜头的条件输入。
- 总结：B 正向信号最强；S 为较弱的侧面结构/弓绑定信号并有主体占比代价；Q 未锁定 45°，主要影响转向趋势。
- 证据锚：manifest `t5_reference_role_conflict.t7_hidden_view_consistency_phase.b_consistency_extension`；任务目录 `t7_b_consistency_cases_25_26.json.results.json`；`t7_b_consistency_frames/`。

### C-20260924-15 | WB 头部去除方式修正（冒烟）
- 状态：🟡正式对照待完成
- 发现：旧 WB 是矩形裁剪，不是语义头部去除；会破坏肩颈/衣领连续性并可能保留正脸竞争。
- 新资产：`WB_face_erased` 与 `WB_head_removed`；前者保留后脑/耳朵/颈肩，后者去整头和头发但保留衣领/肩甲/身体。
- 冒烟观察：两种新资产均比旧矩形裁剪更少出现正脸泄漏；head_removed 分离更彻底，face_erased 上下文更完整。该批使用 built-in image edit 生成，只作资产候选，不等于已验证的 ComfyUI mask-node 生产链。
- 证据锚：manifest `t5_reference_role_conflict.wb_head_processing_phase`；任务目录 `wb_variant_smoke_cases.json.results.json`；output `t5_reference_roles/WB_face_erased.png`、`WB_head_removed.png`。

### C-20260924-16 | WB face-erased/head-removed 正式对照（阶段性）
- 状态：🟡不升级默认资产
- 运行：旧矩形 WB、`WB_face_erased`、`WB_head_removed`，各 3 seed，768×448、124 帧、20 steps，9/9 成功。
- 观察：H3 仍由 `F_face_identity` 提供输出脸；新 WB 的作用是减少服装图内部的重复正脸竞争，而不是让视频输出无头。两种新版本主体占比偏小；head_removed 有个别黑边/构图异常。
- 选择：下一候选优先 `WB_face_erased`（保留后脑/耳朵/颈肩语义更完整）；head_removed 暂作实验资产。没有证据证明新版本质量优于旧版，不能直接改 skill 默认基线。
- 证据锚：manifest `t5_reference_role_conflict.wb_head_processing_phase`；任务目录 `wb_variant_quality_cases.json.results.json`；output `wb_variant_quality_frames/`。

### C-20260924-17 | WB neck-only 对 face-erased（阶段性）
- 状态：🟡待细评分
- 运行：`F_face_identity + WB_face_erased` 对 `F_face_identity + WB_neck_only`，各 3 seed，768×448、124 帧、20 steps，6/6 成功。
- 观察：两组都能由 F 重新生成脸和头发并接回身体；抽查未见明显浮空头、头身比例崩坏或衣领连接失败。neck-only 没有因缺少完整头部而失败；face-erased 保留更多后脑上下文。
- 方法含义：WB 可以采用“中性脖子锚点”而不是完整后脑；但最终选择仍需按头身比例、接缝、发型连续性和跨 seed 一致性评分。
- 证据锚：manifest `t5_reference_role_conflict.wb_neck_anchor_phase`；任务目录 `wb_neck_vs_head_quality_cases.json.results.json`；output `wb_neck_quality_frames/`。

### C-20260924-18 | WB 头身比例/颈部重点评分（阶段性）
- 状态：🟡暂不选单一默认版本
- 指标：头身比例、脖子/衣领接缝、发型/肩颈连续性、跨 seed 稳定性；两变体各 3 seed，首/中/末帧复核。
- 结果：两者均无硬失败，评分基本持平。face_erased 保留更完整的后脑/耳朵/发型连接；neck_only 头部职责更干净，且未出现明显浮空头或比例崩坏。
- 使用建议：优先减少头部竞争时用 neck_only；需要后脑/发型连接语义时用 face_erased。两者都不能在当前证据下替换 skill 默认 WB。
- 证据锚：manifest `t5_reference_role_conflict.wb_neck_anchor_phase`；任务目录 `wb_neck_focus_scoring.json`；output `wb_neck_scoring_frames/`。

### C-20260924-19 | WB_face_erased 视角语义冲突修正
- 复核：`WB_face_erased` 不是合格的“正面去脸”素材，而是正面身体叠加后脑/后发的视角混合体。
- 影响：会与 F 的正脸身份图、以及 B 的背面参考互相竞争；此前将其描述为“保留后脑语义更完整”不成立，相关评分降级为工程观察，不用于生产选型。
- 当前结论：`WB_neck_only` 的职责更干净；若要测试保留头型的 WB，先重做正面头部轮廓去脸版本，再进行公平对照。
- 状态：已记录，未修改 skill 默认基线。
