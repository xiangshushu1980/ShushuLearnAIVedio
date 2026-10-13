# [Sean] H3 Reference 资产制作与选包手册

owner: Sean
status: v1.1 current workflow handbook
date: 2026-09-26

> **唯一正式链路**：`统一提示词 → 主图 → H3 全视角/视频 → 抽帧 → QC → manifest`。本手册是 Reference 资产的唯一当前操作入口；Krea2 只允许承担主图阶段，不能独立逐视角生成完整 F/W/WB/S/Q/B。

## 0. 固定生成链

Reference 资产的正式全视角生成器固定为 **H3 视频/ContactSheet 工作流**。当前可复用的 H3 参考图工作流是 [`workflows/h3_shushu_object_ref_probe.json`](../workflows/h3_shushu_object_ref_probe.json)，后续角色专用变体必须遵守同一输入/输出契约。

- 主图入口按角色任务选择 Krea2 主图工作流或既有 canonical 主图；
- 全视角入口：H3 ContactSheet / H3 视频工作流；
- Prompt 必须绑定同一主图和同一角色定义；
- 生成参数、主图、H3 workflow、seed、抽取帧号和输出 prefix 必须写入 manifest 或实验记录；
- 宿主 `image_gen`、其他在线生图服务和手工合成不得进入正式链路。

因此，本文后续所有“生成全视角”均指 H3 工作流生成；Krea2 只指主图阶段。WB 的抠脸/抠头是从 H3 结果中按职责整理，不能从另一张独立生图补齐。

本文是人物 Reference 资产的权威入口。实验结论仍以 `.pi/ledger/h3-prompt.md` 和对应实验记录为证据；本文只规定当前工程接口、命名、QC 和选包方法。

## 1. 目标

给定一个角色的 canonical source，工程化生成并登记：

- `F`：face identity，脸、发型、身份锚点；
- `W`：完整全身/服装图，保留脸，负责整体服装和体型；
- `WB`：wardrobe body，脸/头部竞争被移除，负责服装、体型、装备和肩颈连接；
- `S` / `Q` / `B`：侧面、3/4、背面视角补充；
- 场景、道具、法术等独立 object reference；
- 面向镜头的组合包和可复核 manifest。

组合图、contact sheet、total board 不是默认人物 identity。它们只能标记为辅助或负对照，不能替代职责分离的单图。

## 2. 资产层级

每个角色必须有一个 `character manifest`。每个资产必须带 `status`：

- `canonical`：通过人工 QC，可作为该职责的当前来源；
- `conditional`：只在指定景别/朝向/遮挡条件使用；
- `experimental`：有实验价值，但不能进入默认选包；
- `missing`：流程需要但尚未生成；
- `rejected`：有明确 QC 失败，不得引用。

推荐目录：

```text
reference_assets/<character_id>/
  manifest.json
  source/                 # 原始或用户确认的 source of truth
  canonical/              # F/W/WB 等已验收资产
  conditional/            # S/Q/B、镜头专用变体
  experimental/           # 失败或待验收版本
  composites/             # 仅用于辅助/负对照的组合图
  qc/                     # contact sheet、人工检查和机器报告
```

## 3. 制作顺序

### 3.1 建立 source of truth

先确认角色卡、服装、体型、发型、装备和风格。主图只建立一次，作为唯一视觉源；所有 F/W/WB/S/Q/B 必须从同一主图进入 H3 全视角链，不能从不同版本的脸、全身图各自生成。

### 3.2 从 H3 结果抽取 F

`F` 是从 H3 全视角结果中抽取的干净身份图，优先正面或稳定正脸/轻微 3/4，脸足够大，背景简单，不带其他角色。它只负责脸、发型、肤色、眼睛、耳朵和身份，不负责完整服装。

QC：脸部无遮挡、无多脸、无水印、发型与角色卡一致、没有场景/道具泄漏。

### 3.3 从 H3 结果抽取 W

`W` 是从同一 H3 结果中抽取的完整人物图，负责服装、体型、装备、发型与身体比例。它可以保留脸，适合需要完整外观语义的全身/中景，但与 `F` 同时使用时可能重复提供正脸。

### 3.4 生成 WB（全身抠脸/抠头）

`WB` 是从同一 H3 结果中按语义职责整理的 wardrobe body，不是另一张独立生图，也不是简单矩形裁剪或随意拼贴。目标是保留正面身体、服装、肩甲、衣领、手部和装备，同时移除会与 `F` 竞争的正脸/头部信息。

当前变体定义：

- `WB_face_erased`：去脸但保留头型/后脑语义；若出现正面身体接后脑视角的混合，不通过 QC；
- `WB_head_removed`：去整头和头发，保留衣领/肩颈/身体；黑边、断颈和主体过小则失败；
- `WB_neck_only`：只保留中性颈部/衣领锚点，职责最干净，但仍需按角色重新验收；
- legacy rectangular crop：只保留历史对照，不得自动升级为 canonical。

WB 的最终 canonical 选择必须经过：肩颈接缝、头身比例、服装可读性、装备完整性、无正脸竞争和多 seed H3 复核。

### 3.5 从同一 H3 全视角结果抽取 S/Q/B

S/Q/B 必须来自同一主图驱动的 H3 全视角结果，不能单独调用 Krea2、Codex image 或其他模型生成，也不能把正面图和另一套服装图混合：

- `S`：严格侧面结构、耳朵、侧发、侧面装备；
- `Q`：约 3/4 视角；当前证据只支持“方向倾向”，不能承诺锁定 45°；
- `B`：后脑、披风、背部装备、箭筒等隐藏细节；在隐藏细节跨视频一致性上目前信号最强。

视角图按镜头触发，不默认全部加入。普通镜头先用 `F + WB`，否则多图会互相竞争。

## 4. 镜头选包

| 镜头需求 | 默认选包 | 备注 |
|---|---|---|
| 脸部近景/说话 | `F + W` 或 `F + WB` | 由脸/肩颈接缝和主体占比决定 |
| 普通中景 | `F + WB` | 当前默认候选 |
| 全身服装/装备 | `F + W` | W 保留完整外观语义 |
| 严格侧面 | `F + WB + S` | 只在朝向/侧面细节重要时加入 |
| 3/4 | `F + WB + Q` | Q 是条件提示，不保证精确角度 |
| 严格背面 | `F + WB + B` | 背部配饰一致性优先时加入 |
| 双人物 | 每个角色独立选包 + scene/object | 不用 pair/total board 替代两个角色包 |

同一角色同一镜头只加入一个同职责视角图；场景、道具、法术必须占独立 semantic slot。

## 5. 工程化契约

manifest 至少记录：角色 ID、canonical source、每个 role 的路径/status、生成来源、抠图方法、QC 状态、适用镜头、文件 hash 和失败原因。工具入口：

```bash
python3 tools/ref_asset_pipeline.py validate path/to/manifest.json
python3 tools/ref_asset_pipeline.py plan path/to/manifest.json --shot medium
```

第一版工具只做可审计的登记、校验和选包，不伪造缺失资产。生成结果必须来自 H3 主图→全视角链，先落 `experimental/` 或 `conditional`，通过人工 QC 与 H3 Ref2VA 下游验证后才提升为 `canonical`。工具允许登记 `experimental` 资产，但 `plan` 会将其视为不可用并阻止生产选包。

## 6. 当前迁移状态

- A（银发精灵）：已有 T5 资产和一批被拒绝的 direct-Krea2 对照图；正式包必须重新走 H3 主图→全视角→抽帧。
- B（红发女性）：已有一批被拒绝的 direct-Krea2 对照图；正式包必须重新走 H3 主图→全视角→抽帧。
- T47-1 现有 `sean_t2_*` Continuum 结果：保留为旧版 baseline，不作为标准 reference 验收。
- 下一阶段：建立 A/B 的 H3 主图和全视角产物；抽取并登记全部派生图，再做人工 QC、H3 Ref2VA smoke，最后重跑 T47-1。

## 7. 五对象批处理工作流（T47-1，2026-09-26）

T47-1 不是“把五个对象放进一个场景生成 reference”。正确含义是：同一批次建立五条彼此隔离的单对象流程。批次共享 runner、参数契约和 review 机制，但每个 job 只能有一个对象、一张主图和一个对象专属 prompt。

### 7.1 单对象 job 契约

每个 job 必须包含：

- 一个 `object_id` 和唯一 `object_type`：`character`、`scene`、`prop` 或 `spell`；
- 一张已通过主图 review 的 `main_image`；
- 一个只描述该对象的 H3 turnaround prompt；
- 独立的 seed、H3 workflow 记录和输出 prefix；
- 独立的 `01_main`、`02_h3_turnaround`、`03_review_frames`、`04_reference_views`、`05_composites` 目录；
- 不允许把其他对象的图片作为输入，也不允许在单对象 H3 视频中出现其他对象。

五对象批次只是在调度层同时拥有五个 job，不改变单对象隔离契约：

```text
batch
├── character_a → one main image → one H3 turnaround video → refs/composites
├── character_b → one main image → one H3 turnaround video → refs/composites
├── scene       → one main image → one H3 turnaround video → refs/composites
├── prop        → one main image → one H3 turnaround video → refs/composites
└── spell       → one main image → one H3 turnaround video → refs/composites
```

### 7.2 三道 review gate

1. `main_review`：只检查五张主图。未通过的 job 不得进入 H3。
2. `h3_review`：检查每个单对象 H3 视频的身份/形态、视角覆盖、背景纯净度和错误对象泄漏。未通过的 job 不得抽帧。
3. `package_review`：检查抽出的每张 ref 和组合图，确认来源帧、职责、hash、QC 和 manifest 完整后，才可标记 `canonical`。

runner 默认只做 `plan` 和契约校验；执行 H3 必须显式提供对应 review gate 的批准标记。不得因为五个 job 在同一批次就跳过任一 gate。

### 7.3 从 H3 视频一次性打包

H3 turnaround 视频通过 `h3_review` 后，按 manifest 中的 `frame_map` 一次性抽取全部职责图，并生成同一对象的组合图。抽帧不是重新生成，组合图不是 canonical source。

- 角色：从同一 H3 视频抽取 `F/W/WB/S/Q/B`；不需要的视角标记为 `conditional` 或 `missing`；
- 场景：抽取正面建立视图、左右空间视图和镜头需要的结构视图；
- 道具：抽取正面、3/4、侧面、背面或细节视图；
- 技能：抽取主形态、角度和状态视图；技能 reference 只锁大形态，不承诺逐帧物理一致。

最终 H3 Ref2VA 场景测试发生在五个独立 package 都通过 `package_review` 之后。场景测试可以选择多个 object package，但不能反向污染任何单对象 package。

## 8. 单物体高清统一工作流（v1.1，当前优先级）

本节是当前角色单物体流程的优先定义；它对第 3 节中“所有职责图均从 H3 抽帧”的旧默认作收敛修正。目标不是让同一张低清视频帧同时承担身份、服装和多视角细节，而是把不同信息源的职责拆开：高清静帧负责细节真值，H3 视频负责统一性和视角变化。

### 8.1 角色资产职责

```text
高清唯一正脸 F0
        │
        ├── 高清全身 W0（同一角色源，服装/体态/装备真值）
        │       │
        │       └── WB（从 W0 去脸/去头，减少身份竞争）
        │
        └── H3 Ref2VA turnaround（只输入 W0；前→3/4→侧→背→侧→前）
                    │
                    ├── 通过视频审查的 S/Q/B 候选帧
                    └── 二采或图像超分后成为 conditional/experimental 视角图
```

- `F0` 是唯一高清正脸身份真值。它可以沿用已验收的正脸流程；如果角色的脸会与服装图竞争，生成/整理 `F` 时只保留脸、发型前侧和必要的耳形，不把整套衣服再带进来。
- `W0` 是唯一高清全身真值。它必须能读出服装层次、体态、主要装备、鞋和轮廓；不能用低清 H3 全身帧裁切来冒充高清 W0。
- `WB` 从 `W0` 派生，去掉脸或整头但保留肩颈/衣领、服装、装备和身体比例。`WB` 是控制输入，不是为了视觉展示而重新发明一个身体。
- `S/Q/B` 的第一来源是 H3 turnaround 的视角变化，因为这些视角必须与 `W0` 的衣服、体态和配饰统一。它们不是独立随机生图，也不是把五物体放进一个总板。
- H3 帧若细节不足，只能在保留原帧的前提下进入“二采/图像超分”阶段；处理后的图先标为 `experimental` 或 `conditional`，不能覆盖原始 H3 帧证据。

因此，角色的默认最小高清包不再是“从一段低清 H3 视频一次性抽出全部 F/W/WB/S/Q/B”，而是：

```text
canonical: F0 + W0 + WB
conditional: S/Q/B（来自 H3，并通过高清化与一致性 QC）
evidence: H3 turnaround 原视频 + 原始抽帧 + 参数/seed/prompt manifest
```

### 8.2 单物体生成顺序与 review gate

必须按顺序停闸，任何一步未通过都不进入下一步：

1. **主图阶段**：确认 `F0` 与 `W0`。优先提高静帧生成分辨率和主体占比；`F0` 负责脸部唯一性，`W0` 负责全身细节。两者必须来自同一角色设定/身份源，并记录 source、模型、prompt、seed、尺寸和 QC。
2. **WB 阶段**：从已确认的 `W0` 生成/整理 `WB`。先做人眼检查，再做一小次 H3 语义复核；检查肩颈接缝、头身比例、服装和装备，不把脸部高清化任务混入 WB。
3. **H3 阶段**：只用一个对象、一个 `W0`、一个对象专属 prompt 生成完整人物 turnaround。视频目标是前/3-4/侧/背/回正和服装连续性；不把 H3 当作正脸高清器。当前测试应使用单人、慢速转身、无其他对象、4–15 秒范围内的短段。
4. **H3 review**：检查身份轮廓、服装/装备、侧面、背面、回正、背景纯净度和时序稳定；不检查“远景脸是否凭空变高清”作为通过条件。
5. **视角高清化阶段**：只挑 H3 review 通过的 S/Q/B 候选帧。先做直接图像超分作为低风险基线；仍缺细节时再做低 denoise 图像 latent 二采。两者都保留原始 H3 帧，记录放大模型、倍率、tile、seed、denoise 和输出尺寸。
6. **package review**：以 `F0/W0/WB` 为 canonical，以经过比较的 S/Q/B 为 conditional/experimental；确认同一衣服、装备、发型后，才允许提升状态或进入下游 H3 Ref2VA。

### 8.3 二采与图像超分的选择

| 路线 | 适用职责 | 一致性风险 | 当前定位 |
|---|---|---|---|
| 直接图像超分 | H3 已经正确、只是纹理/边缘不足的 S/Q/B | 可能产生逐图细节差异；不能补回不存在的脸部身份 | 第一优先对照 |
| 单帧图像 latent 二采 | H3 帧结构正确但服装/材质细节不足 | 可能改脸、改配饰、改服装；必须低 denoise 与原帧比对 | 第二优先、逐帧实验 |
| 完整视频 latent 二采 | 需要整体输出尺寸和时序连续 | 全局重绘可能改变身份/衣服；成本和显存高 | 不作为当前单物体 reference 默认 |
| H3 FaceRefine | 近景/中景脸部防劣化 | 远景 20–35px 不能凭空恢复新身份；需跟踪和分段 | 只在下游视频需要时启用 |

完整视频 latent 二采已有本地验证，主要价值是全片结构和时序保持，不等于能恢复小脸细节；因此不应把它插入当前 reference package 的默认生成链。只有当单帧高清化改变了 S/Q/B 的服装或身份，才回到同一 H3 帧和同一 `W0` 重做对照。

### 8.4 当前单物体验收指标

- `F0`：正脸唯一性、五官/发型/脸部标记清楚，无第二身份。
- `W0`：全身主体足够大，服装层次、装备、鞋、轮廓和体态在原尺寸可读。
- H3：前/侧/背/回正视角完整，服装和主要配饰不跳变，不出现第二对象或背景污染。
- S/Q/B：视角正确、与 `W0` 统一；高清化后不得出现“纹理更锐但身份/衣服被改写”。
- 一致性优先级固定为：身份与服装统一 > 视角覆盖 > 单帧锐度。锐度提升若破坏前两项，资产必须降级为 `experimental` 或拒绝。

### 8.5 当前测试状态

2026-09-26 已完成 Character A 的单物体 H3 turnaround smoke：输入一张主图、无其他 reference，`768×448`、192 帧、8 秒、20 steps、`res_multistep`、seed `4701201`。视频显示前/侧/背/回正和服装连续性基本成立，但画面偏软；该结果只证明 H3 统一性链路可继续，不是最终高清 reference package，也未抽取 `F/W/WB/S/Q/B`。

下一步必须先完成 `F0/W0` 高清主图方案和 H3 结果审查，再决定 S/Q/B 的直接超分与图像二采对照；在 Sean 审查前不得继续生成、抽帧或合成。
