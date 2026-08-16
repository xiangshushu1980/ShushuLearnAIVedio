# ViMax 阶段2：一致性与参考资产层深入拆解

> 任务线：T-20260814-02（vimax-dissect）｜执行：flash-worker（2026-08-15）
> 数据来源：/tmp/vimax（HKUDS/ViMax，commit 05a4894，浅克隆只读）
> 范围：references / first frames / continuity 相关实现（agents + interfaces + pipeline）

---

## 一、数据建模摘录（文件路径 + 行号 + 关键字段）

### 1. 角色模型 — static/dynamic 特征分离 + 跨场身份映射

**`interfaces/character.py:8-38` `CharacterInScene`**（场景内角色）：
- `idx`（场景内角色索引，从 0 起）
- `identifier_in_scene`（本场景内角色标识，如 "Alice"）
- `is_visible`（本场景是否可见）
- `static_features`（**静态特征**：脸型、五官、身形等不变量）
- `dynamic_features`（**动态特征**：服装、配饰、随身物品等可变项）

**`interfaces/character.py:47-90` `CharacterInEvent` / `CharacterInNovel`**（跨场/跨事件身份）：
- `active_scenes: Dict[int, str]`（场景索引 → 该场景中的角色名映射，处理同一角色在不同场景用不同称呼）
- `static_features`（跨场共享的不变特征，动态特征**不进**此层）

### 2. 镜头模型 — 首/尾帧双锚点 + 可见角色索引 + 变化量级

**`interfaces/shot_description.py:79-172` `ShotDescription`**（分镜→可执行镜头规格）：
- `cam_idx`（机位索引）、`visual_desc`（整镜视觉描述，角色用 `<Alice>` 尖括号标注）
- `variation_type: Literal["large","medium","small"]`（**镜内首尾帧变化量级**）+ `variation_reason`
- `ff_desc`（**首帧静态描述**：构图/机位/站位/光照，纯快照无动作）+ `ff_vis_char_idxs`（**首帧可见角色索引列表**）
- `lf_desc`（**尾帧静态描述**）+ `lf_vis_char_idxs`
- `motion_desc`（首尾帧之间的运动：机位运动 + 画面内元素运动，角色须用外观特征指代）
- `audio_desc`

### 3. 机位模型 — 相机树（父镜头→子镜头依赖声明）

**`interfaces/camera.py:6-42` `Camera`**：
- `idx`、`active_shot_idxs`（该机位拍的镜头序列）
- `parent_cam_idx` / `parent_shot_idx`（**父机位/父镜头**：父镜头的画面内容包含子镜头）
- `is_parent_fully_covers_child`（父镜头是否**完全覆盖**子镜头内容）
- `missing_info`（子镜头缺失的信息，如 "The frontal view of Alice"）

### 4. 帧模型 — 镜头 × 帧类型的可见角色

**`interfaces/frame.py:1-23` `Frame`**：`shot_idx`、`frame_type: Literal["first","last"]`、`cam_idx`、`vis_char_idxs`（帧内可见角色）。

### 5. 参考图选择输出 — 索引 + 元素级绑定提示

**`agents/reference_image_selector.py:157-186` `RefImageIndicesAndTextPrompt`**：
- `ref_image_indices: List[int]`（从候选池选出的参考图索引，≤8 张）
- `text_prompt: str`（**元素级引用绑定**："The man should reference Image 0. The landscape should reference Image 1."，索引指 ref_image_indices 列表内位置）

### 6. 参考资产落盘结构（JSON 契约）

- `characters.json`：`List[CharacterInScene]`
- `character_portraits_registry.json`：`{identifier_in_scene: {"front": {"path","description"}, "side": {...}, "back": {...}}}`（**每角色三视图肖像库**，见 `pipelines/script2video_pipeline.py:497-514`）
- `shots/<idx>/shot_description.json`、`first_frame.png`、`last_frame.png`、`video.mp4`、`first_frame_selector_output.json`（每镜头独立目录，全部可断点恢复）
- `camera_tree.json`、`storyboard.json`

---

## 二、机制说明

### 1. 参考资产如何生成（前置顺序，全在渲染前完成）

```
角色提取 CharacterExtractor        → characters.json（static/dynamic 分离）
  ↓
角色三视图肖像 CharacterPortraitsGenerator → character_portraits_registry.json
  （front 直接文生图；side/back 以 front.png 为参考图生成，保证同一角色多视角一致，
    见 agents/character_portraits_generator.py:47-86）
  ↓
分镜 StoryboardArtist              → storyboard.json（镜头序列 + 机位索引）
  ↓
镜头视觉分解 decompose_visual_description → shots/<idx>/shot_description.json
  （visual_desc → ff_desc/lf_desc/motion_desc + ff/lf_vis_char_idxs + variation_type，
    见 agents/storyboard_artist.py:214-274）
  ↓
相机树构建 CameraImageGenerator.construct_camera_tree → camera_tree.json
  （LLM 分析各机位镜头描述，输出父子依赖 + missing_info，见 agents/camera_image_generator.py:170-231）
```

### 2. 参考图如何绑定到每个镜头（两级筛选 + 动态候选池）

**`ReferenceImageSelector.select_reference_images_and_generate_prompt`**（`agents/reference_image_selector.py:190-237`）为**每一帧**（首帧+尾帧）独立运行：

- **候选池构建**（`pipelines/script2video_pipeline.py:294-298, 393-398`）：
  - 该帧 `ff_vis_char_idxs` 命中角色的**三视图肖像全部入池**（按 identifier_in_scene 从 registry 取）
  - 本机位第一镜头的首帧（`first_shot_ff_path_and_text_pair`）作为**场景/背景锚点**入池
  - 新机位时：父镜头的**过渡视频切帧图**（new_camera_image）入池
- **两级筛选**：候选 ≥8 张时先用**纯文本模型**（只读描述文字）粗筛到 ≤8 → 再用**多模态模型**（看图）精筛出最终 ref_image_indices
- **输出绑定提示**：LLM 生成 `text_prompt`，用 "Image N" 语法把生成图中的**每个元素**显式绑定到某张参考图（角色→肖像、场景→前序帧、缺失部位→补充说明）
- 筛选规则（prompt 内嵌，`reference_image_selector.py:17-95`）：同机位构图优先、**前序帧越近越优先**、同角色多视角只取 1 张（按朝向选）、避免冗余

### 3. 跨镜头连续性如何保证（三套机制）

**机制 A：相机树 + 过渡视频切帧（站位/场景连续性）**（`pipelines/script2video_pipeline.py:299-355` + `agents/camera_image_generator.py:233-273`）：
- 子机位首帧不直接文生图，而是先用**父镜头首帧 → 子镜头首帧**生成一段"过渡视频"（`generate_transition_video`，以父首帧为参考图）
- 用 PySceneDetect 场景检测切出**第二场景首帧**作为子机位基线图（new_camera_image）
- 若 `is_parent_fully_covers_child=True`：直接 `shutil.copy` 该帧作首帧（**站位/背景 100% 继承**）
- 否则：以 new_camera_image 为主参考 + "保持背景、把人物替换成三视图肖像、背景不变"的定向修复提示

**机制 B：变化量级分级（variation_type 决定锚点数量）**：
- `small`：只生成 first_frame，视频模型单帧驱动（表情/小动作）
- `medium/large`：生成 first+last 双帧，视频模型用 `frame_images`（首/尾帧两张，`tools/video_generator_openrouter_api.py:153-165`）约束起止状态
- 同机位后续镜头首帧**统一以本机位第一镜头首帧为参考**（同机位 = 同一空间基线）

**机制 C：事件驱动调度 + 中间件幂等落盘（顺序依赖 & 断点恢复）**：
- `frame_events[shot_idx]["first_frame"]` 等 `asyncio.Event`（`pipelines/script2video_pipeline.py:81-84`）：子机位等父机位首帧完成、视频生成等首帧（+尾帧）完成，依赖关系由 camera tree 声明
- 每个中间产物落盘即检查、存在即跳过（`if os.path.exists(...)`），全流程可断点续跑、可人工替换任一层

---

## 三、可吸收建议清单（对 comfy-ops 工具 A/B 的落地动作）

> 工具 A = 拍摄本（剧本→拍摄本）；工具 B = 六段式提示词（拍摄本→H3），H3 参考图用 `<Picture>/<Image>`。当前痛点：角色/场景跨段一致仅靠参考图+角色卡，无系统化设计。

### 建议 1：拍摄本镜头表增加「首帧/尾帧双锚点 + 可见角色索引」字段（对标 ff_desc/lf_desc + ff/lf_vis_char_idxs）
- **工具 A**：每镜头固定产出 `ff_desc`（静态快照，含构图/机位/角色站位/朝向/光照）、`lf_desc`、`ff_vis_char_idxs`（该镜首帧出现哪些角色）。此字段是纯文本，LLM 可生成，成本低
- **工具 B**：六段式的**首段直接消费 ff_desc**、**末段消费 lf_desc**（取代现在的"重新理解整镜"），`ff_vis_char_idxs` 决定该镜 `<Picture>` 注入哪些角色的参考图——角色参考图**按镜头显式绑定**而非全量塞入
- 价值：把"哪些角色出现在哪一帧、以什么朝向站位"从隐性提示词变成显式结构化字段，H3 参考图注入有据可依

### 建议 2：参考图选择前置为「候选池 + 两级筛选 + Image N 元素绑定」
- **工具 A**：为每个镜头预生成 `_selector_output.json` 式中间件——候选池 = 该镜可见角色肖像 + **上一段尾帧**（场景锚点），由 LLM 选出 ≤8 张并输出元素级绑定（"人物用 <Image N>，场景沿用上一段画面"）
- **工具 B**：把绑定结果直接翻译成 H3 的 `<Image>` 多参考图语法，**每元素声明引用来源**，而不是六段式里把参考图当背景板
- 价值：参考图从"凭感觉挑"变为"每镜头的显式消费清单"，且候选池规则（前序帧优先、同角色单视角）可直接复用 ViMax prompt 经验

### 建议 3：跨段锚点链 = 上段尾帧作为下段首帧的构图基线（对标相机树/前序帧优先）
- **工具 A**：镜头表增加 `depends_on_shot` 字段（本镜首帧的构图继承自哪一镜），同场景段落自动链成锚点链
- **工具 B**：段落首镜的六段式首段显式写"延续 <Picture 上一段尾帧> 的构图与场景，人物按角色参考图替换/延续站位"——与 ViMax 的"new_camera_image + 换角色提示"同构，但用 H3 的参考图机制实现
- 价值：直接解决 seg2 台词瞬间海浪变轻这类**场景连续性问题**——把"背景"显式锚定到上一段画面，而非靠提示词描述

### 建议 4：角色卡升级为三视图资产（front/side/back），静态/动态特征分离落地为「肖像库 + 描述注册表」
- **工具 A**：沿用 T-20260812-03 设定图体系，但按 `character_portraits_registry.json` 的结构落盘——每个角色一个目录（front.png/side.png/back.png + 每张的 description），side/back 用 front 为参考图生成（对齐 ViMax `character_portraits_generator.py:47-86` 的级联生成法）
- **工具 B**：H3 提示词中角色出场按"该镜朝向"选对应视角参考图（侧面出场用 side 图），不再只用一张正脸图硬撑所有镜头
- 价值：角色一致性从"单视角参考"升到"多视角参考"，H3 侧身/背面镜头不再依赖模型脑补

### 建议 5：连续性依赖显式声明 + 中间件幂等落盘（断点恢复 & 局部重跑）
- **工具 A**：拍摄本落盘为可回看 JSON（镜头 idx / cam_idx / depends_on_shot / ff·lf_desc / 参考图清单），与 ViMax 的 storyboard.json / shot_description.json 同构；改造时**只改镜头表结构，不改六段式生成器**（工具 B 只消费新字段）
- **工具 B/渲染侧**：产物命名沿用 `output/video/h3_r2v/`，每段目录内落 `selector_output.json`（参考图选择+绑定提示，可人工检查替换），存在即跳过
- 价值：对齐阶段1对标点 6/7（局部修订 + 断点恢复），跨段重跑时只有依赖链上的镜头重生成，其余跳过

---

## 附：关键实现位置速查

| 关注点 | 文件:行号 |
|---|---|
| 角色 static/dynamic 建模 | interfaces/character.py:8-38 |
| 跨场身份映射 | interfaces/character.py:47-90 |
| 首/尾帧 + 可见角色索引 + variation_type | interfaces/shot_description.py:79-172 |
| 相机树父子依赖 + missing_info | interfaces/camera.py:6-42 |
| 三视图肖像生成（front→side/back 级联） | agents/character_portraits_generator.py:22-86 |
| 参考图两级筛选 + Image N 绑定 | agents/reference_image_selector.py:157-237 |
| 相机树构建（LLM 分析父子关系） | agents/camera_image_generator.py:170-231 |
| 过渡视频→切帧→新机位基线图 | agents/camera_image_generator.py:233-273 |
| 镜头视觉分解（ff/lf/motion 拆分） | agents/storyboard_artist.py:214-274 |
| 候选池构建 + 首帧生成编排 | pipelines/script2video_pipeline.py:285-355 |
| 帧生成 + 参考图选择调用 | pipelines/script2video_pipeline.py:360-437 |
| 事件驱动依赖（frame_events） | pipelines/script2video_pipeline.py:81-84, 636-647 |
| 视频模型首/尾帧双参考 | tools/video_generator_openrouter_api.py:153-165 |
| 角色肖像注册表落盘结构 | pipelines/script2video_pipeline.py:497-514 |
