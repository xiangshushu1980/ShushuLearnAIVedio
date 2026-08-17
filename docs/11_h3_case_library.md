# 11 H3 提示词案例库（持续生成，2026-08-04 起）

> 定位：H3 输出控制的**三维度**之一（提示词）。配套：数值参数 → skill params.md `### 关键参数`；参考图 → params.md `### 参考图准备规范` + `### Ref2VA 参考`。三维度协作决定输出，详见 params.md `### 提示词控制技巧`。
> 依据：A 提示词强度测试结论（镜头语言最强、动作中等、约束部分有效、双图融合可用）+ B 参考强度测试。参考图来自底图库 `input/ref_lib/`。全部 ref2va int8 20步（除非注明），review 目录可目测。

## 批 1（写实人物 × 镜头/动作/约束/声音升级，bikini_beach 参考）
| 案例 | 变体 | 耗时 | 目录 |
|------|------|------|------|
| C01 | 拉远大幅慢速 + 强风 + 海鸥 + 海浪声 | 152s | video/h3_cases/C01 |
| C02 | 环绕镜头 + 转身看海 | 147s | video/h3_cases/C02 |
| C03 | 奔跑 + 跟踪镜头 + 溅水 + 脚步声 | 147s | video/h3_cases/C03 |
| C04 | 坐下 + 推近 + 保脸/服装约束 + 音乐 | 142s | video/h3_cases/C04 |
| C05 | 静态 + 轻微抖动 + 紧张氛围 | 146s | video/h3_cases/C05 |
| C06 | **双图**（bikini+森林）+ 触树 + 森林鸟声 | 155s | video/h3_cases/C06 |

## 批 2（写实双图融合 + 文化特色）
| 案例 | 变体 | 耗时 | 目录 |
|------|------|------|------|
| C07 | 双图 bikini+霓虹夜景 + 雨声 | 153s | video/h3_cases/C07 |
| C08 | 双图 hanfu+灯笼街 + 鞭炮声 | 153s | video/h3_cases/C08 |
| C09 | qipao 单图 + 老上海复古 + 爵士乐 | 145s | video/h3_cases/C09 |
| C10 | bikini+水墨意境融合（partially）| 153s | video/h3_cases/C10 |
| C11 | tibetan + 经幡 + 强风 | 152s | video/h3_cases/C11 |
| C12 | fisherman **10s** + 船体晃动 + 海鸥声 | ~600s | video/h3_cases/C12 |
| C13 | 剑士拔剑 + 环绕快移 + 魔法声 | 320s(含加载) | video/h3_cases/C13 |
| C14 | 双图 剑士+蘑菇森林 + 萤火虫 | 295s(含加载) | video/h3_cases/C14 |
| C15 | hanfu 少女跳舞 + 古琴声 | 162s | video/h3_cases/C15 |
| C16 | 泳装少女玩水 + 笑声 | 157s | video/h3_cases/C16 |
| C17 | 双图 剑士+浮岛 + 史诗拉远 | 166s | video/h3_cases/C17 |
| C18 | 中国龙穿云 + 跟踪镜头 + 雷鸣 | ~600s | video/h3_cases/C18 |
| C19 | **三图** bikini+森林+水墨 过渡变换 | 174s | video/h3_cases/C19 |
| C20 | **六段式完整格式**（subject_definitions/retention/detailed/soundscape/music）| 159s | video/h3_cases/C20 |
| C21 | **抽卡管线验证**（768×448 + 14步 + MC）| 315s(含加载)⚠️脏数据（真实快速档见 09 补测批 D：~75-90s）| video/h3_cases/C21 |
| C22 | 森林人像 + **loud birdsong 强声音指令** | 281s(含加载) | video/h3_cases/C22 |
| C23 | **三图** hanfu+灯笼+水墨 文化融合 | 191s | video/h3_cases/C23 |
| C24 | **15s** 霓虹男多动作序列（走/停/看/打车）| ~1500s | video/h3_cases/C24 |

## 阶段总结（24 案例全完成，review/L_cases/）
- **镜头语言**：全案例带明确镜头（拉远/环绕/跟踪/推近/弧线），A 测试已证有效
- **双图/三图融合**：C06/C07/C08/C10/C14/C17/C19/C23 共 8 个多图案例（人物+场景/风格/文化）
- **声音指令**：海浪/鞭炮/古琴/鸟鸣/雷鸣等全带上；C22 强指令待听
- **六段式**：C20 完整官方格式对照
- **管线验证**：C21 抽卡档、C24 15s 复杂动作
- 速度稳定：单图 5s ≈ 145-175s；多图同档；10s ≈ 600s；15s ≈ 1500s

## 批 5（8s 指令遵循度：动画 vs 真人，2026-08-04）
| 案例 | 变体 | 耗时 | 目录 |
|------|------|------|------|
| D01 动画剑士 8s | 拔剑→挥砍×2→收剑 + 环绕镜头 | 264s | video/h3_cases/D01 |
| D02 动画泳装 8s | 跑→停水边→转身挥手 + 跟踪转推近 | 511s(含加载) | video/h3_cases/D02 |
| D03 动画龙 8s | 穿云→俯冲→升空吐火 + 动态跟踪 | 382s | video/h3_cases/D03 |
| D04 真人 8s | 走→停→挥手→转身离开 + 横摇 | 355s | video/h3_cases/D04 |
| D05 真人汉服舞 8s | 舞蹈→转圈×2→下跪收尾 + 弧线镜头 | 513s | video/h3_cases/D05 |
| D06 真人霓虹 8s | 走→拉领→回望→继续走 + 跟拍 | 待填 | video/h3_cases/D06 |

**观察点**：动画（D01-D03）多动作遵循 vs 真人（D04-D06）哪里崩（动作衔接/身体变形/脸部）

## 批 6（真人崩点定位梯度 + 动画 9s）
| 案例 | 变体 | 耗时 |
|------|------|------|
| E01 真人 8s | **单动作**：只走路 | 264s |
| E02 真人 8s | **双动作**：走+停看海 | 278s |
| E03 真人 8s | **三动作**：走+停+挥手 | 247s |
| E04 动画 9s | 双图 剑士战斗（闪避+挥砍×2）+ 镜头震动 | 278s |
| E05 动画 9s | 长镜头（走→涉水→转身笑）| 269s |
| E06 真人汉服 8s | **单动作**：转圈 | ~300s |

**崩点定位逻辑**：E01→E02→E03 动作数递增，对照 D04（四动作）看真人崩在哪个动作数/哪种动作

---

## 社区精选模式（来源：BeatAPI/awesome-minimax-h3-prompts，2026-08-17 吸收）

> 来源仓库：https://github.com/BeatAPI/awesome-minimax-h3-prompts （301 条社区精选，T2V 243 / Ref2V 47，15s 232 条）。
> 抽样 24 条精读（cinematic 8 / ads 8 / anime 4 / ugc 4），与 IR 拆解（docs/18）+ 六段式 + 本仓实测对照。**标注说明**：✔=模式与 IR/六段式同构或本仓实测支持；⚠=社区高频但与本仓实测冲突，慎用。

### 模式 1：时间分节式（社区最主流，15s 标准骨架）

结构：`0–4s: 内容 + 镜头运动 + 风格词收尾`（或 `Scene N (Xs–Ys) – 标题`、`[0s-6s]` 前缀），3-5 段，每段 3-5s。

```
0–5 seconds: Extreme close-up ... Cinematic camera push-in, macro product details, realistic reflections.
5–10 seconds: The phone activates ... Dynamic camera movement, premium commercial aesthetic.
10–15 seconds: Hero product shot ... Cinematic lighting, high-end TV commercial quality, photorealistic, ultra-detailed, 4K.
```

- 与 IR 对比：IR 用 `[Shot 1] At 00:02.650` 时间戳 + 每镜 300-600 词细节密度；社区段前缀更紧凑（每段 ~100-200 词），**适合产品片/多段广告/15s 标准片**（本仓 C24 15s 多动作序列可对照）
- 本仓应用：C20 六段式之外的 T2V 平铺写法，多段商业片可直接照此模板
- 段落数建议：15s 用 3-5 段，每段一个明确动作节点

### 模式 2：产品片五段模板（ads 类精品，✔）

无线耳机展示（15s 五段，可复用的完整结构）：

```
0–4s: 极微距 tracking 扫材质（耳垫/金属铰链/控制键）→ 4–8s: 拉远到 hero 三视角，产品慢转 →
8–12s: exploded-view 拆解展示（内部结构逐层分离 + 光波脉冲）→ 12–15s: 组件重组归位 + 微距推近收尾
```

- 变体（nova-x 手机 TVC）：极微距 → 使用场景（界面激活/人机互动）→ hero 立姿 + **logo 口号收尾**（`"NOVA X — The Future in Your Hands."`）
- 通用逻辑：**材质细节开场 → 功能/场景展示 → 拆解或变形 → 归位 hero 收尾**，与香水五景（揭晓→微距→粒子变形→环境转场→hero 终景）同构
- 每段末尾固定追加质量词收尾（cinematic lighting / photorealistic / 4K），社区惯例，见模式 8 警示

### 模式 3：字段式拍摄本模板（✔ 与工具 B 拍摄本 schema 呼应）

把控制维度拆成大写字段，避免长句混写。三套已验证模板：

```
A. vlog 版（CAMERA/LOOK/STYLE/CHARACTER/SETTING）
CAMERA: DV 16mm tape camcorder POV ... natural handheld shake, imperfect framing, clumsy zooms
LOOK: Soft blurry tape aesthetic, faint tape noise, bloomed gym lights
STYLE: Calm post-workout gym vlog ... Slow pacing, natural laughs
CHARACTER: CHASE, Korean idol (20s) ... towel around neck, no jewelry
SETTING: Quiet evening gym ... soft lighting, mostly empty

B. 生活场景版（Main Subject/Location/Visual Style/Camera Style/Timeline/Audio/Goal）
Timeline (30 sec):
00:00–00:03 → She climbs into the hammock carefully
00:03–00:06 → She picks up a book ...（每 3s 一个 beat，台词写原文，如韩语对话直接嵌入）

C. 音乐 MV 版（[Core Concept]/[Character Identity]/[World Logic]/[Visual Language]/[Motion Rules]/[Restrictions]）
[Core Concept] 15s, 160 BPM, 4/4, 40 beats ...
[World Logic] Each kick compresses the timeline toward the dancer. Each snare duplicates previous movements ...
```

- 字段式把「身份/环境/镜头/节奏」分开控制，与六段式 subject_definitions 思路同构，但 T2V 平铺可用（六段式是 Ref2V 专用）
- **时间戳 beat 序列 + 台词原文**：社区把对话直接写原文（非英语也写），对照 IR 的 `<d>[English] ...</d>` 标记——T2V 平铺可省标记直接写原文，参考 docs/17 对话写法
- 分镜列表变体：`15s | 6 Cuts` + 每镜一行（Propped medium: sits on mat, exhales. "Okay, cool-down time."），适合口播/UGC

### 模式 4：@[ref] 角色引用标签（✔ 与六段式 label 同构）

社区 Ref2V 通用语法：`@[face ref]` / `@[body ref]` / `@[audio ref]`（日文社区高频）：

```
@[face ref] をNEONの顔、ピンクのボブヘアの厳密な参照として使用します。
@[audio ref] は映像のリズム、カットの強弱、主要な音楽アクセントの参照として使用します。
Use @[char ref] as the sole character reference. Preserve the exact identity, face, body proportions, hairstyle, outfit ...
```

- 与本仓六段式 label 规则一致；**@[audio ref] 做节奏参考（beat-sync）**是本仓未用过的新用法：`Use the attached track for timing, every cut must land exactly on the beat`（Bond 片头 60s，开场稀疏→随鼓点加速→freeze-frame 硬切）
- 一致性锚句社区高频：`Same face, same bag, same world, held together across every cut` / `Do not redesign, simplify or replace any defining visual features` —— 即六段式 retention_analysis fully_preserved 的 T2V 版

### 模式 5：「先空后满」渐进组装（✔）

从空白/近空白开始，逐元素组装：motion poster（画框自绘→标题滑入→主体淡入→小字逐一 pop-in）、paper-cut stop-motion（0-2s 背景→2-4s 珊瑚逐片→6-8s 角色：身体先入头盔后装）、产品 exploded-view。

- 每段只进 1-2 个新元素，段落标题即该元素动作，天然规避长镜头多元素崩点
- 适合：标题序列 / 产品 reveal / 开场镜头

### 模式 6：单镜连续长句 + 设备名（one-take）

单段叙事长句（纪录片/街头/旅行/UGC）+ 相机器材名 + 感官词：`shot on ARRI Alexa 35 with spherical lens` / `DV camcorder, handheld` / `smartphone-shot look, candid lifestyle beauty content`。

- **UGC 反精致指令**：`smartphone-shot look ... not overly retouched` / `imperfect framing, delayed focus, clumsy zooms`——刻意写「不精致」反而增强真实感（本仓未测，可作 C/D 批对照）
- 负面词收尾高频：`no hands, no distortion, no onscreen text` / `No cyberpunk, no stylization` / `no text, no watermark`

### ⚠ 与实测冲突的社区惯例（慎用）

1. **负面约束词**（`no hands / no text / no logos`）：社区 40%+ 提示词收尾必带，但本仓 seedance-h3-verify 实测 **T4 负面词零差异**（34 条 AB 对比）——写不写无差别。如需排除元素，优先用正面描述替代（如"no text"→"clean minimalist frame"）
2. **空洞质量词**（8K / 4K HDR / ultra-detailed / masterpiece / blockbuster quality）：社区普遍堆叠，本仓实测具体名词（导演名/具体灯光/光晕）才被执行，空洞词效果存疑——用 `volumetric lighting` / `rim light` 等具体词替代
3. 社区声音指令整体薄弱（多数无 soundscape 段），IR 声音三层结构（docs/18 §二.5）仍是本仓优势，不降级模仿

### 社区 vs 本仓写法速查

| 维度 | 社区（BeatAPI） | 本仓现行（IR/六段式/17 号） | 取用建议 |
|------|----------------|--------------------------|---------|
| 时间戳 | `0–4s:` 段前缀 | `[Shot N] At 00:02.650` | 15s 商业片用段前缀，电影感用 IR 格式 |
| 身份保持 | @[ref] + 锚句 | subject_definitions/retention | Ref2V 用六段式，T2V 平铺用锚句 |
| 细节密度 | 每段 100-200 词 | 每镜 300-600 词（IR） | 保持本仓密度下限（<200 词不够电影级） |
| 声音 | 多数缺失 | 三层 soundscape 必写 | 不降级 |
| 负面词 | 高频收尾 | 实测零差异 | 用正面描述替代 |
| 质量词 | 8K/ultra-detailed 堆叠 | 具体名词 | 用具体灯光/材质词 |
| 对话 | 原文直接嵌入 | `<d>[English] ...</d>` | T2V 可省标记写原文 |
