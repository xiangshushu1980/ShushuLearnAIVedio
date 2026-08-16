# 设定图体系设计（T-20260812-03，refimage-system）

> 产出：flash-worker（2026-08-16）｜输入：rolecards（alya_v1/yuki_v1）、ViMax stage2_consistency.md 建议2/4、H3 Ref2VA 机制（params.md/nodes.md）、web-shotlist-tool 实体系统现状、现有资产清单（ComfyUI/input/start/169/）
> 定位：设定图的**形态/主次/重点控制/自动推导**四维度设计，落地动作清单供工具 A（拍摄本）/ B（六段式）/ C（图需求推导器）吸收

---

## 〇、现状盘点与缺口（先看清家底）

### 现有资产（169/ 目录实测）
| 资产 | 内容 | 对应形态 |
|---|---|---|
| portrait/alya169_portrait_uniform | Alya 正脸 canon（白金夹克） | 角色正脸特写 ✓ |
| portrait/yuki169_portrait_uniform | Yuki 正脸 canon（白水手服） | 角色正脸特写 ✓ |
| portrait/yuki169_stand | Yuki 全身 | 角色全身正面 ✓ |
| beach/alya169_{tokidoki,ayra,roshidere} | Alya 海边 16:9 场景版 ×3 | 场景全景 ✓ |
| beach/yuki169_beach / night/yuki169_night / stage/yuki169_stage | Yuki 场景版 | 场景全景 ✓ |
| stage/alya169_stage | Alya 舞台版 | 场景全景 ✓ |
| multi/gen_2p_{leftright,talk} / gen_3p_group | 双人/三人站位图 | 双人互动（雏形）△ |
| wow_anime / wow_real | 风格对照产物 | 风格板（未组织）△ |
| 根目录 alya768_flat / alya_1024 / krea_alya_768 等 | 早期抽卡 | 废弃/备用 |

### 缺口清单（本设计的生成目标）
1. **全部角色缺 side/back**：无 3/4 侧脸、无背面图。Yuki 双马尾背面结构、Alya 单侧红丝带蝴蝶结背面全靠模型脑补 → 侧身/背面镜头必漂移
2. **缺佩饰特写**：Alya 红丝带蝴蝶结、Yuki 深色领巾无独立图（当前混在正脸/全身里，属"低分辨率细节"被 VAE 丢弃区）
3. **缺道具图**：无道具实体资产
4. **缺场景细节/光照板**：有全景无细节锚点（霓虹招牌/柜台/黄昏色调）
5. **缺变体图集**：换装/破损/状态图（用户决策 2026-08-12 已定方向未生成）
6. **风格板未资产化**：wow_anime/wow_real 是测试产物，未纳入实体库 style 资产
7. **双人图未入角色卡引用**：multi/ 三张存在但 rolecards 未声明

---

## 一、形态（维度 a）：四类设定图形态清单

> 图例：● 必要（core，星级 ≥4 必检）｜○ 可选（按剧情/镜头需求）｜级联 = 以 canon 为参考图生成，保证同人（对齐 ViMax `character_portraits_generator.py` front→side/back 级联法）

### A. 角色设定图（身份/外观锚定）
| 形态 | 必要性 | 锁定内容（大特征，VAE 上限内） | 生成方式 | 典型注入时机 |
|---|---|---|---|---|
| ① 正脸特写（face/identity） | ● core | 脸型/五官/发型/瞳色/发色 | anima t2i，canon 外观描述逐字 | 该角色所有镜头 |
| ② 全身正面（full body） | ● core（有中景及以下景别时） | 身高比例/服装轮廓/配色/鞋/标志道具 | anima t2i（可与①同外观描述） | 全景/中全景/全身出场镜头 |
| ③ 3/4 侧脸 | ○ | 脸侧面轮廓/发型侧面 | 级联自①（同人保证） | 侧身/转头/对话错位镜头 |
| ④ 背面 | ○ | 发型背面结构（双马尾/单侧蝴蝶结）/服装背面 | 级联自① | 背影/转身/跟拍镜头 |
| ⑤ 佩饰特写 | ○ 仅剧情关键道具 | 丝带/领巾/发饰/耳环形态与配色 | 级联自①或独立 t2i | 特写镜头/剧情点（接受被简化，params.md 经验） |
| ⑥ 变体图集（variant） | ○ 出现换装/破损/状态变化时 | 换装后服装/破损状态 | **级联自①**（canon 为参考图，禁文本微调，用户决策） | 变体活跃的段落 |
| ⑦ 双人/多人互动图（pair/group） | ○ ≥2 角色同镜且站位是剧情点时 | 相对站位/身高差/肢体关系 | t2i 双主体 | 双人对话/并肩镜头 |

### B. 场景设定图（环境锚定）
| 形态 | 必要性 | 锁定内容 | 生成方式 | 注入时机 |
|---|---|---|---|---|
| ① 场景全景（scene establishing） | ● core（每 distinct scene 1 张） | 空间布局/配色/光照基调/标志建筑，**16:9 匹配生成分辨率** | anima t2i（场景描述，无人/不含主角） | 该场景所有段落首镜 + 换场 |
| ② 场景细节/标志物 | ○ 标志物承担剧情功能时 | 霓虹招牌/柜台/道具级环境物 | t2i 特写 | 标志物出现镜头 |
| ③ 光照/氛围板 | ○ 特殊时段（黄昏/夜/雨） | 色调/光线方向/氛围 | t2i（或全景生成参数内并入） | 特殊时段段落 |

### C. 道具设定图（物件锚定）
| 形态 | 必要性 | 锁定内容 | 生成方式 | 注入时机 |
|---|---|---|---|---|
| ① 道具单体图（prop single） | ● 道具承担剧情功能时 | 造型/配色/材质，干净背景 | t2i 单体 | 道具出现镜头 |
| ② 道具手持/使用中图 | ○ 有道具-角色互动镜头时 | 拿法/背法/尺寸比例 | 级联（单体为参考）或 t2i | 互动镜头 |
| ③ 道具细节特写 | ○ 高辨识度道具 | 细节纹理 | 级联自① | 特写镜头 |

### D. 技能/风格设定图（效果与风格锚定）
| 形态 | 必要性 | 锁定内容 | 生成方式 | 注入时机 |
|---|---|---|---|---|
| ① 技能效果示范图 | ○ 技能/特效是核心卖点时 | 特效形态（魔法阵几何/粒子形态/变身结构） | t2i 效果示范 | 技能释放镜头 |
| ② 风格板（style board） | ● core（每项目 1 张） | 渲染风格/美术方向（2D 动漫/真实光照卡通渲染/写实） | t2i 风格示范 | 全局（prompt 风格词 + 可选独立 <Picture>） |
| ③ 光影/氛围参考 | ○ | 光影调性 | t2i | 特殊氛围段落 |

> ⚠️ 技能/特效类诚实边界：H3 对特效的控制主力是 prompt 文字（细节物理上限：VAE 8x 下采样，微细节编码阶段就丢）；技能参考图只锁**大形态**（几何结构/颜色分布），retention 用 partially_preserved，不承诺逐帧一致。

---

## 二、主次（维度 b）：主设定图与辅助图分工

### 分层定义
| 层 | 图 | 职责（一图一职责） | 注入纪律 |
|---|---|---|---|
| **主设定图（身份锚定）** | 角色正脸特写 | 锁**身份**：脸/发/瞳 | 该角色**所有**镜头必注入；**跨段复用同一张**（v3 验收：canon 基准图跨段复用 = 稳定一致） |
| | 角色全身正面 | 锁**服装/体型** | 全身相关景别注入；服装为 canon 唯一来源（**设定图 = source of truth**，用户原则） |
| **辅助图（环境/细节/风格）** | 场景全景 | 锁**环境**：布局/光照基调 | 按镜头 scene 匹配注入；与人物**分开喂独立 slot**（C06-C19 本地验证融合可用） |
| | 风格板 | 锁**美术风格** | 全局 1 张，低优先级（slot 紧张时可只用 prompt 风格词——渲染风格词主导，T-20260812-07 实测） |
| | 变体图 | 锁**服装/状态变体** | 仅变体活跃段落；retention 用 partially_preserved 声明 |
| | 侧/背面 | 锁**视角补全** | 仅对应朝向镜头注入（同角色多视角每镜头**只取 1 张按朝向选**，ViMax 筛选规则） |
| | 道具/佩饰/技能/双人 | 锁**单一剧情元素** | 仅该元素出现的镜头注入，其余镜头不占 slot |

### 分工三原则
1. **每图一个职责**（rundiffusion/Runware 社区方案）：身份图不含服装变体，服装图不含场景，场景图不含主角——同维度冲突细节（光照/表情/角度不一致）→ 特征平均 → 身份漂移，是 H3 参考图第一大坑
2. **主图全镜头在场，辅图按镜头消费**：主设定图是"身份底线"，辅助图是"局部增强"。宁可少喂辅助图也不挤占主图 slot（甜点 2-4 张/镜）
3. **canon 唯一源**：正脸 canon 是所有级联图（side/back/变体）的生成基准；角色卡文本与设定图逐字对齐（v3 教训：参考图白 vs 文本深色 → 产物随机选边）

---

## 三、重点控制（维度 c）：如何用设定图控制生成重点

### 1. 身份/服装/场景/风格四维分开喂（H3 标签机制落地）
| 维度 | 喂法 | retention_analysis 写法 |
|---|---|---|
| 身份 | 正脸图 → `<Subject N>` | `Subject N identity (face, hair, eyes) fully preserved` |
| 服装 | 全身图 → `<Subject N>`（可与身份同一 N，多图定义同一 Subject） | `Subject N wardrobe fully preserved`；变体 → `partially_preserved` |
| 场景 | 场景全景 → `<Picture M>` | `Scene background fully referenced, keep spatial layout and lighting` |
| 风格 | 风格板 → `<Picture M>`（或仅 prompt 风格词） | `Style of Picture M applied globally` |

- `<Subject N>` = 身份/道具定义（subject_definitions 段逐图写清"这张图是谁/什么"）
- `<Picture N>` = 关键帧/构图锚点（场景/风格/站位）
- 同一实体多图（正脸+全身）：subject_definitions 里写 `<Subject 1> is Alya (face)`, `<Subject 2> is Alya (full body, same character)`——用描述绑定同人，不靠模型猜

### 2. 同维度冲突规避（四大铁律）
1. **同角色同视角只喂 1 张**（ViMax 两级筛选规则），杜绝双正脸光照不一致 → 特征平均
2. **同角色多图必须同光照同服装同表情基调**（甜点配置；canon 生成时用同一外观描述逐字驱动）
3. **场景图不含主角**（避免身份污染与场景图被当人物参考）
4. **禁文本微调获得变体**（用户决策 2026-08-12：参考图白 vs 文本深色实测漂移）——变体必须独立图

### 3. 数量控制（slot 预算）
| 场景 | 预算 | 说明 |
|---|---|---|
| 单人单场景 | 2-3 张 | 正脸 + 全身 + 场景 |
| 双人单场景 | 3-4 张 | 2×正脸 + 场景 +（全身 或 双人站位） |
| 双人多场景段落 | 4-6 张 | + 场景变体/光照板 |
| **单镜头注入上限** | **≤4 张** | 甜点 2-4；9 是模型上限不是目标 |
| 全局资产（每角色维度） | ≤9 张/角色 | 正脸/全身/side/back/佩饰/变体×N 的总预算 |

### 4. 跨段复用与锚点链
- **身份：跨段复用同一张 canon 正脸**（v3 验收过的机制），绝不在中段换新图
- **场景：跨段换场/场景延续** = 同一张场景全景 + 上一段尾帧作 `<Picture>` 构图锚点（ViMax 建议3 的前序帧优先，工具 B 段落首镜消费）
- **站位：双人互动图/全局站位约定**，不在每段靠文字描述（T-01 站位教训）

### 5. 细节边界（物理上限诚实声明）
- VAE 8x 下采样 + 480-576p：参考图只锁大特征（脸型/发型/服装轮廓/配色/标志道具），微细节靠 prompt 文字 + 后期超分（FaceRefine 管线）
- ref_image_size 用 `match`（训练一致）；`max`（2048 短边）仅对 >2048px 图有增益，身份保真优先时对 canon 正脸可用

---

## 四、自动推导（维度 d）：工具 C 图需求推导器

### 输入 / 输出
- 输入：剧本参数头（role_cards/style/scene）+ 角色卡（appearance 逐字）+ 工具 A 拍摄本（shots[].subject/framing/action/scene）
- 输出：`refimage_plan.json`（图需求清单：每张图的实体、形态、用途层、级联来源、注入时机、生成参数）

### 决策树（伪代码）
```
derive_refimage_plan(script, rolecards, shotlist) -> plan:
  # ── 1. 实体与场景收集 ─────────────────────────────
  entities = collect(script.role_cards) ∪ collect(shotlist.shots[].subject)   # 角色+道具
  scenes   = distinct(shotlist.shots[].scene)                                  # 场景枚举（工具 A 的 scene 字段）
  shots_by_entity = index(shotlist.shots, by subject)

  # ── 2. 角色图（每实体） ────────────────────────────
  for e in entities where type == character:
    plan.add(canon正脸, e, core, gen=t2i(e.appearance + 全局风格词))           # 身份图，必出
    if 存在 e 的 中景/中全景/全景 镜头 或 rolecard 有全身描述:
      plan.add(全身正面, e, core, gen=t2i(e.appearance))                       # 服装图
    if 存在 e 的 action 含 [侧,背,转身,回头,背影]:
      plan.add(3/4侧脸, e, aux, gen=级联(canon, 侧视角))                      # 级联保证同人
      plan.add(背面,   e, aux, gen=级联(canon, 背视角))
    for v in e.variants:                                                       # 换装/破损/状态
      plan.add(变体图, e+v, aux, gen=级联(canon, v.description))               # 禁文本微调原则
    if e.signature_prop 且 prop_in_plot(e):
      plan.add(佩饰特写, e, aux, gen=级联(canon, 特写))

  # ── 3. 场景图（每 distinct scene） ─────────────────
  for s in scenes:
    plan.add(场景全景, s, core, gen=t2i(场景描述, 16:9 匹配分辨率))            # 无人/不含主角
    if s 有标志物且标志物承担剧情:
      plan.add(场景细节, s, aux, gen=t2i(标志物))
    if s 时段 in {黄昏, 夜, 雨}:
      plan.add(光照氛围板, s, aux, gen=t2i(氛围))

  # ── 4. 道具图 ─────────────────────────────────────
  for p in entities where type == prop:
    if p 承担剧情功能:
      plan.add(道具单体, p, aux, gen=t2i(单体, 干净背景))
      if 存在 p 与角色互动镜头:
        plan.add(道具手持, p, aux, gen=级联(单体))

  # ── 5. 风格/技能图 ────────────────────────────────
  if script.style: plan.add(风格板, 项目级, core, gen=t2i(style 词))           # 每项目 1 张
  if 剧本含技能/特效语义 且 技能是卖点:
    plan.add(技能效果示范, skill, aux, gen=t2i(特效形态))

  # ── 6. 双人互动（可选） ────────────────────────────
  if 存在 shots(subjects ≥ 2) 且站位是剧情点:
    plan.add(双人互动图, subjects, aux, gen=t2i(双主体站位))

  # ── 7. 预算裁剪 ───────────────────────────────────
  plan = prune(plan,
    规则1: 单镜头注入 ≤4 张（正脸/全身/场景 优先，其余按镜头消费）
    规则2: 每角色总资产 ≤9 张
    规则3: 可选图按实体星级降序裁剪（≥4 星必检，web-shotlist-tool 星级体系）
  return plan
```

### 生成顺序（级联，对齐 ViMax character_portraits_generator）
```
风格板 → 角色 canon 正脸（全局风格词并入）→ side/back/变体/佩饰（以 canon 为参考图级联）
场景全景（独立 16:9）→ 场景细节/光照板（全景或独立）
道具单体 → 手持/细节（级联）
```
- 级联语义：生成时 canon 正脸进参考槽，prompt 写"same character, view from X"——保证同人（本地已有 anima t2i + 级联机制，web-shotlist-tool 设定图生成可扩展）
- 断点：plan 落盘 JSON，逐图生成状态可查（对齐 ViMax 幂等落盘：存在即跳过）

### 与工具 A/B 的契约
- **工具 A → 工具 C**：shotlist.yaml 的 subject/framing/action/scene 字段就是推导输入；建议工具 A 后续按 ViMax 建议1 增补 ff/lf_vis_char_idxs + 朝向字段（更精确触发 side/back）
- **工具 C → 工具 B**：`refimage_plan.json` 提供六段式注入所需的三件套——① 每镜可见角色 → 该角色对应视角图进 `<Subject N>`；② 镜头 scene → 场景全景进 `<Picture M>`；③ 变体角色 → retention 写 partially_preserved

---

## 五、落地动作清单（工具 A/B/C + 资产补全）

### 工具 C（图需求推导器，新建）
- [ ] 1. 实现第四节决策树：输入 shotlist.yaml + rolecards → 输出 refimage_plan.json（含级联来源/注入时机/生成参数）
- [ ] 2. 生成方式对接：canon/辅助图 → anima t2i（复用 web-shotlist-tool 设定图生成的"外观描述 canon + 类型构图 + 全局风格词"配方）；级联图 → t2i + canon 参考图
- [ ] 3. 落盘幂等 + 逐图状态可查（存在即跳过）
- [ ] 4. 预算裁剪落地：单镜 ≤4 / 角色 ≤9 / 星级裁剪

### 工具 A（拍摄本）
- [ ] 1. subject 字段统一实体 id（含变体 `实体id:变体id`）
- [ ] 2. scene 字段枚举场景 + 时段（黄昏/夜/雨 → 触发光照板）
- [ ] 3. （后续）镜头表增 ff/lf_vis_char_idxs + 角色朝向字段（ViMax 建议1，让工具 C 精确触发 side/back）

### 工具 B（六段式）
- [ ] 1. subject_definitions：每镜注入该镜可见角色的**对应视角图**（按朝向选 side/back，不全量塞入）
- [ ] 2. retention_analysis 分维度写：身份 full / 服装 full / 变体 partially / 场景 background preserve（第三节表格）
- [ ] 3. 场景锚点 `<Picture>` 按镜头 scene 匹配 + 段落首镜延续上一段尾帧（ViMax 建议3）
- [ ] 4. 双人镜头：双人互动图进 `<Subject>` 或 `<Picture>`（站位锚点），prompt 不再单靠文字定站位

### 资产补全（按优先级，anima 生成，需宿主占坑跑批）
- [ ] P0：Alya/Yuki **背面图 + 3/4 侧脸**（级联自现有 canon）——解决侧身/背面镜头漂移
- [ ] P0：**风格板资产化**（wow_anime/wow_real 组织进实体库 style 资产，或按当前项目 style 重生成）
- [ ] P1：**佩饰特写**（Alya 红丝带蝴蝶结 / Yuki 深色领巾）
- [ ] P1：**双人互动图入角色卡引用**（multi/gen_2p_* 三张纳入实体引用）
- [ ] P2：变体图集首例（换装/破损）——验证级联生成同人度后铺开
- [ ] P2：道具图（等道具实体出现）

### 现有资产映射速查（可直接开用）
| 实体 | 正脸 canon | 全身 | 场景版 | 缺 |
|---|---|---|---|---|
| alya_v1 | portrait/alya169_portrait_uniform | alya768_flat（需验证） | beach/alya169_tokidoki、stage/alya169_stage | side/back、佩饰、变体 |
| yuki_v1 | portrait/yuki169_portrait_uniform | portrait/yuki169_stand | beach/yuki169_beach、night/yuki169_night、stage/yuki169_stage | side/back、佩饰、变体 |
| 双人 | — | — | multi/gen_2p_leftright/talk | 引用未入 rolecards |

---

## 附：设计依据速查
- H3 机制：≤9 图独立 slot 零速度惩罚；`<Subject N>` 身份/道具、`<Picture N>` 构图/场景锚点；retention_analysis 写保留关系（params.md:160-162、nodes.md:103-104）
- 甜点 2-4 张（正脸+全身+可选背面/佩饰），同光照同服装；九宫格必失败；同维度冲突→身份漂移；场景/风格独立图分开喂（params.md:101-106）
- ViMax：三视图级联生成（character_portraits_generator.py:47-86）；同角色多视角只取 1 张按朝向选、前序帧优先（reference_image_selector.py）；static/dynamic 分离（character.py:8-38）
- 用户决策：设定图=source of truth、禁文本微调变体、变体=独立图 partially_preserved（h3-prompt-agent progress 2026-08-12）
- 现有管线：Ref2VA 默认生产模式；跨段一致性三要素=服装（参考图统一+角色卡逐字）/屏幕方向（全局约定）/音色（同种子）
