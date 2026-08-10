# 17 H3 提示词写作规则手册（生成器知识底座，2026-08-08）

> 定位：提示词生成器（docs/16）合成环节的**规则输入**。来源 = 官方 h3-prompt-writing 指南（base-en/ref-en）+ 官方 README 示例 + 社区 benjiyaya skill 拆解 + IR 样本规律。
> 本手册是"可执行规则"，词汇库见 docs/18（待建，从 showcase 与 IR 样本蒸馏）。

## 一、模式与输出契约

| 模式 | 输入 | 输出结构 |
|---|---|---|
| T2VA | 纯文本 | 三核心段（无 instruction line） |
| I2VA | 文本+首帧图 | instruction line + 三核心段 |
| FL2VA | 文本+首尾帧 | instruction line + 三核心段 |
| L2VA | 文本+尾帧 | instruction line + 三核心段 |
| Ref2VA | 多模态参考 | 六段式 |

**铁律**：
- 只输出指定字段，无前言/解释/markdown fence/评论
- 全部英文（`<d>` 内对话与画面内文字保留原语言 verbatim）
- 时间戳 MM:SS.mmm 严格递增且在时长内；`[Shot 1]` 永不带时间戳
- 开场先 1-2 句整体风格，再 `[Shot 1]`（风格语句绝不放进 Shot 1 内部）

## 二、镜头规划（base 模式）

**时长→镜头数预算**：4-6s→1-2 镜；7-10s→2-3 镜；11-15s→3-5 镜；每镜至少 1.5-2s。
**切 vs 移**：切必须引入新信息（新主体/新空间/新状态/新视角/新时间）；仅距离/角度变化 → 用镜头运动，不切。
**一镜一动作**（硬约束）：一个镜头只有一个主导动作；连续动作拆到多个镜头。
**连续性**：每镜重复身份锚点（外形/服装/道具，换措辞但一致）；状态变化跨镜延续（湿了/脏了/破了就一直保持）；保持屏幕方向。

**镜头运动语法** = type + amplitude + speed（自然英语，非堆标签）：
- Type：Zoom In/Out、Push In/Pull Out、Pan L/R、Truck L/R、Tilt Up/Down、Pedestal Up/Down、Arc Shot、Tracking Shot、Static Shot、Shake Slightly/Strongly、POV、Roll CW/CCW
- Amplitude："with small amplitude"/"with large amplitude"（中等省略）
- Speed："at slow speed"/"at fast speed"（正常省略）
- 例：`The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.`

**instruction line 模板（逐字复制）**：
- i2va：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- fl2va：`How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- l2va：同 fl2va 单图版（`<Picture 1>` 对齐最终镜头 N 的 S.SS 秒）

## 三、对话/声音语法

- 发声者稳定 ID `(S1)`、`(S2)`…跨镜复用；不发声角色无 ID；群声 `(S1,S2)`
- 首次出现给身份锚点（类型/年龄/性别/屏内屏外/音高/音色/语速/口音）
- 格式：`识别短语 + ID + 语气`在 `<d>` 外，`<d>` 内只有语言标签+原词：`<d>[English] Wait for us!</d>`
- 对话 verbatim：永不翻译/改写用户原词
- 画外音：用精确短语 "says in an off-screen voiceover" + 立即声明嘴唇闭合 "while his lips remain completely closed."
- 对话跨切：两端加 `<scenetrans>` + 连续性声明；视频截断说话：`<cutoff>`
- 画面内文字：英文双引号 verbatim（如 A red neon sign reading "营业中"）
- **音乐两分**：角色能听到的音乐（收音机/现场演出）→ 写进镜头描述（diegetic）；背景配乐 → 只进 `non_diegetic_music`（配器/速度/节奏/力度，不写情绪词）
- **场景驱动判断（2026-08-10 对比 IR 补充）**：表演/演出类场景（舞台/演唱会/街头艺人/收音机）音乐本身是 diegetic 主体，`non_diegetic_music` 可写 `N/A` 省略（IR 舞台版实测行为）；反之纯氛围场景必须有背景配乐

## 四、Ref2VA 六段式要点

1. **subject_definitions**：四类 label——`<Subject N>`（可见可复用内容：人/物/场景/服装/风格，可合并多素材）、`<Picture N>`（仅当图本身是帧锚点）、`<Video N>`（整视频关系：编辑源/续写源/运镜节奏提供者）、`<Audio N>`（音频角色：拷贝/风格/音色参考）。视频与音频独立编号。
2. **summary**：方括号任务类型前缀（keyframe completion / reference generation / video editing / video continuation / audio reuse / audio reference，可 `+` 组合不可重复）
3. **retention_analysis**：视觉用 fully_preserved / partially_preserved / attribute_transfer / weak_reference；音频用 fully_copy / partially_copy / reference / weak_reference；每 label 一行
4. **detailed_description**：350-500 词；风格开场→`[Shot N]` 时间线；label 首现处插入引用
5. **overall_soundscape**：1-4 句：环境音+物理动作声+非语言人声；无对话/唱/配乐
6. **non_diegetic_music**：1-3 句：配器/速度/节奏/动态

**常见错误**：把角色参考图当帧锚点（角色卡是 `<Subject>` 不是 `<Picture>`）；发明 label（只能引用已定义）；`(Sx)` 出现在 retention_analysis。

## 五、七维创作增强（benjiyaya 拆解，生成器"增强器"参考）

| 维度 | 要点 |
|---|---|
| 1 Camera Identity | 物理型（handheld/tripod/drone/steadicam/POV/arc）+ 有意保留的瑕疵（抖动/对焦漂移/曝光波动）+ 格式质感（16mm/DV/anamorphic） |
| 2 Visual Texture | 颗粒/噪点/色彩科学/布光设计/跨镜头光线转换 |
| 3 Pacing Arc | 能量曲线命名（quiet→energetic / tense→release）+ 剪辑节奏（加速切/长hold/踩点） |
| 4 Character Detail | 外貌+服装（色/材质/纹理）+ 视觉签名（每镜可识别的固定元素，如红色围巾）+ 覆盖描述 |
| 5 Spatial Geography | 屏幕方向（Left→Right/Deep→Front）+ 关键动作拍点 2-3 个 + 环境布局 |
| 6 Continuity Progression | 物理状态累积（伤/汗/尘土）+ 环境变化 + 情绪递进 |
| 7 Sound Design | 环境音/动作音/配乐/环境内音乐/对话与旁白 五层全映射 |

**质量条**：每镜必须指定——构图（景别+角度）、镜头运动（type+幅度+速度）、单一主导动作、环境/光线、声音线索。

## 六、高级 pattern（creative-showcase 提炼）

- **角色颜色锁定**（动作戏）：每个角色特效/轨迹/反射固定配色（BULLDOG=焦橙/锈红/金，VIPER=橄榄绿/黑/白）
- **环境反应**：世界回应角色（灯闪烁/地板开裂/尘埃飞溅）
- **镜头身份命名**：每镜有记忆点（"穿手特写"比 "Shot 3" 有效）
- **慢镜拍点**：关键帧短暂 slow-mo 再硬切回全速
- **叙事蒙太奇**：CAMERA/LOOK/STYLE 块开头 + 服装/地点跨时间推进 + 旁白承载情感
- **SeeDance→H3 转换**：合并时间戳段（7段→5镜），保留全部动作拍点；镜头语言换成 H3 语法

## 七、验证清单（合成后自检）

- [ ] 模式判定正确；只含规定字段
- [ ] 时间戳递增且在时长内；镜头数符合预算
- [ ] 一镜一动作；每镜有运动（含 Static Shot）
- [ ] 身份锚点跨镜一致；状态连续
- [ ] 对话 verbatim + `<d>` 格式正确；VO 有 lips-closed 声明
- [ ] diegetic 音乐在镜头内，non-diegetic 只在配乐段
- [ ] 无第三方 IP/名人/商标角色名
- [ ] 开场风格句在 `[Shot 1]` 之前

## 八、参考来源

- 官方：`.pi/skills/h3-prompt-writing/references/{base-en,ref-en}.txt`（格式宪法）
- 官方示例：`experiments/ir_samples/official_{t2va_10s,i2va_8s,ref2va_5s}.txt`（含 token 用量）
- 社区：vendor 外 /tmp/Minimax-H3-Prompt-AgentSkill（benjiyaya，53★）：SKILL.md + base-multishot-format.md + ref2va-format.md + creative-showcase.md（7 个完整 pattern）
- IR 实测样本：experiments/ir_samples/（本任务线收集，拆解见 docs/18）
