# 17 H3 提示词写作规则手册（生成器知识底座，2026-08-08）

> 定位：提示词生成器（docs/16）合成环节的**项目策略覆盖层**。官方 `base-en/ref-en` 负责字段、标签和格式；本文负责 comfy-ops 的默认策略、实测约束和用户偏好。两者冲突时，格式契约服从官方指南，策略默认服从本文。
> 本手册是"可执行规则"，词汇库见 docs/18（待建，从 showcase 与 IR 样本蒸馏）。
> 2026-08-17 对比 1038lab Promptor + T8 enhancer 后强化（原始抽样见 `experiments/archive/promptor_compare/`，吸收记录见 docs/11 工具对比节）。

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
- 总提示词时间线必须匹配目标视频时长；官方 H3 skill 当前提示范围为 4–15 秒
- `<Picture N>` / `<Video N>` / `<Audio N>` 标签在所有段落中保持稳定；优先写可验证的画面/声音事实，不用空泛的“cinematic/beautiful”替代细节
- I2VA / FL2VA / L2VA 必须明确首帧、尾帧如何接入时间线；这属于官方结果约束，不是可选修辞

## 二、镜头规划（base 模式）

**时长→镜头数预算**：4-6s→1-2 镜；7-10s→2-3 镜；11-15s→3-5 镜；每镜至少 1.5-2s。
**切 vs 移**：切必须引入新信息（新主体/新空间/新状态/新视角/新时间）；仅距离/角度变化 → 用镜头运动，不切。
**模式专属（2026-08-17 吸收，1038lab Promptor 模板 + T8 官方契约交叉验证）**：
- FL2VA：强烈偏好**单镜连续运镜（无硬切）**，保证首尾帧平滑插值；必须切时按普通切规则（✅ 2026-08-17 P1 视频实测成立：单镜版无切镜、多镜版 2.5s 精确切镜；尾帧对齐单镜/多镜无差异，原始证据见 `experiments/archive/promptor_compare/p1_video/`）
- I2V/L2VA：[Shot 1] 严格对齐首帧的光/构图/姿态；**不得引入首帧中不可见的角色**
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
- **不虚构未请求的对话/歌词/台词**（2026-08-17 实测暴露：base-en 契约下 LLM 自动编了 (S1) 台词；T8 契约有显式禁止句）——用户没给的台词一律不写，宁可静默
- 画外音：用精确短语 "says in an off-screen voiceover" + 立即声明嘴唇闭合 "while his lips remain completely closed."
- 对话跨切：两端加 `<scenetrans>` + 连续性声明；视频截断说话：`<cutoff>`
- 画面内文字：英文双引号 verbatim（如 A red neon sign reading "营业中"）
- **音乐策略（用户决策 2026-08-10）**：默认不主动设计 BGM。`non_diegetic_music` 写 `N/A`，soundscape 保持中性、避免音乐词；若交付物必须无音乐，生成后使用分离/替换流程，不能只依赖 prompt。需要连续配乐时走后期独立配乐（本地 MusicGen/ACE-Step 管线，docs/12 §10）
- **prompt 级去音乐不可靠（2026-08-10 四写法实测）**：N/A、显式 no music、全静音指令、极端否定描述仍可能产出音乐谐波（87/174/349Hz 泛音序列 + 440Hz），因此这些写法只表达意图，不构成交付保证
- **音乐两分**：角色能听到的音乐（收音机/现场演出）→ 写进镜头描述（diegetic）；若用户显式要求生成配乐才写 `non_diegetic_music`（配器/速度/节奏/力度，不写情绪词）
- **正向控制有效（2026-08-12 实测，T-20260812-02）**：负向禁音乐无效，但显式音乐指令可**正向触发/控制**——① 单镜头无音乐区 + `non_diegetic_music` 配器描述（慢速/稀疏/轻力度）= 触发钢琴（P1 实测 4s 出钢琴）；② 多镜头中性区 + 显式配乐 = 触发（P4，对照 C2 无音乐）；③ diegetic 写法（soundscape 写“远处海滩酒吧钢琴”）产出“场景内感”音乐，与配乐层听感有区分（P2）；④ 时间 cue 半可控：开始时间近似响应（要求 4s 实际 2.5s），动态变化（“6s 变强”）不可控（P3）
  - 生产含义：要音乐 → 显式写配器描述（不写情绪词）；不要音乐 → 维持单镜头中性 / 多镜头中性客观描述（2026-08-11 定论），不要写音乐相关词
- **场景驱动判断（2026-08-10 对比 IR 补充）**：表演/演出类场景（舞台/演唱会/街头艺人/收音机）音乐本身是 diegetic 主体，`non_diegetic_music` 可写 `N/A`；纯氛围场景仍遵守“默认不主动设计 BGM”，只有用户明确要求或任务方案选定配乐时才写背景配乐

## 四、Ref2VA 六段式要点

1. **subject_definitions**：四类 label——`<Subject N>`（可见可复用内容：人/物/场景/服装/风格，可合并多素材）、`<Picture N>`（仅当图本身是帧锚点）、`<Video N>`（整视频关系：编辑源/续写源/运镜节奏提供者）、`<Audio N>`（音频角色：拷贝/风格/音色参考）。视频与音频独立编号。
2. **summary**：方括号任务类型前缀（keyframe completion / reference generation / video editing / video continuation / audio reuse / audio reference，可 `+` 组合不可重复）
3. **retention_analysis**：视觉用 fully_preserved / partially_preserved / attribute_transfer / weak_reference；音频用 fully_copy / partially_copy / reference / weak_reference；每 label 一行
4. **detailed_description**：350-500 词；风格开场→`[Shot N]` 时间线；label 首现处插入引用
5. **overall_soundscape**：1-4 句：环境音+物理动作声+非语言人声；无对话/唱/配乐
6. **non_diegetic_music**：1-3 句：配器/速度/节奏/动态

**补充防误判（2026-08-17 吸收，T8 冻结官方契约 093f3129）**：
- retention 标记只限 4 种（fully_preserved / partially_preserved / attribute_transfer / weak_reference）；**新请求的动作或背景不构成 partially_preserved 的证据**
- summary 任务前缀按**实际关系推断去重**，不按接了哪些输入端口臆断
- 音频标签独立编号；视频内嵌的普通声音**不自动创建 `<Audio N>` 角色**
- `<Subject N>` 可合并多素材定义；`<Picture N>` 仅当图本身是帧锚点（见 §四.1）

**常见错误**：把角色参考图当帧锚点（角色卡是 `<Subject>` 不是 `<Picture>`）；发明 label（只能引用已定义）；`(Sx)` 出现在 retention_analysis。

## 五、动态生成中的 reference 绑定与最小提示词

### 5.1 Reference 的三种职责必须分开

在 Ref2VA 和 FaceRefine 组合流程中，reference 不是“接上图片就自动生效”，必须在提示词和工作流中分别声明职责：

- **H3 角色/object reference**：提供角色身份、脸、服装、轮廓和总体外观；提示词只需把 `<Subject N>` 绑定到对应 `<Picture N>`，不要再次罗列外观细节。
- **场景/environment reference**：提供环境建筑、布局、光照和整体空间；同样用 `<Subject N>` 绑定到 `<Picture N>`。
- **FaceRefine identity reference**：用于检测/跟踪“是哪一个人”；游戏、3D、插画角色优先使用 `CLIP Vision`，不要默认使用 InsightFace。

推荐的最小绑定句式：

```text
<Subject 1> is the character defined by <Picture 1>.
<Picture 1> is the authoritative reference for this subject's identity and visual appearance.
<Subject 2> is the environment defined by <Picture 2>.
<Picture 2> is the authoritative reference for the environment's layout and lighting.
```

这不是重复描述人物外观，而是给 reference 分配权威职责。`summary` 和 `detailed_description` 只引用 `<Subject N>`，写动作、表情、镜头和主体移动；不要重新发明人物外观。

### 5.2 FaceRefine 的 reference 分离

对于远景脸防劣化，推荐：

```text
脸部裁图 → CLIP Vision identity tracking
完整人物 object/reference → H3 局部重绘
原视频局部 latent → 保留动作、角度、光照和时序
```

不要把 face-only reference 同时作为 H3 唯一 object reference。它可以稳定脸部，却会让 H3 缺少服装、头部造型和整体角色信息，导致“脸不劣化但人物不像原 reference”。

### 5.3 少检查的生成前清单

动态生成只做四项硬检查：

1. 每个 `<Subject N>` 是否绑定了唯一的 `<Picture N>` 或明确的对象 reference；
2. `summary`/`detailed_description` 是否只引用 Subject、动作和镜头，未重复外观；
3. 生成 reference、跟踪 reference、H3 refine reference 是否职责分离；
4. 游戏/3D/插画人物是否使用 CLIP Vision 或 CCIP，而非 InsightFace。

通过这四项后，不再逐句审查提示词，直接进行短片 smoke。

## 六、七维创作增强（benjiyaya 拆解，生成器"增强器"参考）

> T8 Creative DNA（`T8mars/minimax-h3-prompt-skill-T8`）是持续更新的案例机制库，不是新的官方 H3 格式。引用时只抽取已验证的镜头/节奏/声音机制，并回填本手册的字段、标签、时长和用户事实约束；不直接复制整套模板或让案例覆盖参考图事实。

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

## 七、高级 pattern（creative-showcase 提炼）

- **角色颜色锁定**（动作戏）：每个角色特效/轨迹/反射固定配色（BULLDOG=焦橙/锈红/金，VIPER=橄榄绿/黑/白）
- **环境反应**：世界回应角色（灯闪烁/地板开裂/尘埃飞溅）
- **镜头身份命名**：每镜有记忆点（"穿手特写"比 "Shot 3" 有效）
- **慢镜拍点**：关键帧短暂 slow-mo 再硬切回全速
- **叙事蒙太奇**：CAMERA/LOOK/STYLE 块开头 + 服装/地点跨时间推进 + 旁白承载情感
- **SeeDance→H3 转换**：合并时间戳段（7段→5镜），保留全部动作拍点；镜头语言换成 H3 语法

## 八、验证清单（合成后自检）

- [ ] 模式判定正确；只含规定字段
- [ ] 时间戳递增且在时长内；镜头数符合预算
- [ ] 一镜一动作；每镜有运动（含 Static Shot）
- [ ] 身份锚点跨镜一致；状态连续
- [ ] 对话 verbatim + `<d>` 格式正确；VO 有 lips-closed 声明
- [ ] diegetic 音乐在镜头内，non-diegetic 只在配乐段
- [ ] 无第三方 IP/名人/商标角色名
- [ ] 开场风格句在 `[Shot 1]` 之前
- [ ] 无用户未请求的对话/歌词/音乐（LLM 幻觉高发点）
- [ ] 声音信息完整：环境音+动作声在 soundscape，配乐在 non_diegetic_music（防跳段/防遗漏）

## 九、参考来源

- 官方：`.pi/skills/h3-prompt-writing/references/{base-en,ref-en}.txt`（格式宪法）
- 官方示例：`experiments/ir_samples/official_{t2va_10s,i2va_8s,ref2va_5s}.txt`（含 token 用量）
- 社区：vendor 外 /tmp/Minimax-H3-Prompt-AgentSkill（benjiyaya，53★）：SKILL.md + base-multishot-format.md + ref2va-format.md + creative-showcase.md（7 个完整 pattern）
- IR 实测样本：experiments/ir_samples/（本任务线收集，拆解见 docs/18）
