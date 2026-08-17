# 任务进度：comfy-ops-awesome

## 任务
- 目标：吸收 BeatAPI/awesome-minimax-h3-prompts（301 条，108★）cinematic/ads/anime/UGC 提示词库：抽样 10-20 条分析结构规律 → 与 IR（docs/18）/六段式对比 → 有价值模式补进 docs/11 案例库（标注来源）
- 当前状态：🟡 分析完成，待落盘
- 我负责的文件区：docs/11_h3_case_library.md（新增社区模式分节）；本进度文件

## 进度日志（append-only）
### 2026-08-17
- 克隆仓库 /tmp/awesome-minimax-h3-prompts（301 条 JSON，分类：cinematic-story 76 / product-commercial 68 / music-video 47 / anime 21 / cinematic-travel 15 / fashion 14 / action 15 等；243 条 T2V，47 条 Ref2V，15s 232 条）
- 按任务四类分层抽样 24 条（cinematic 8 / ads 8 / anime 4 / ugc 4），全部精读，识别出 4 大结构族（详见下）
- 与 docs/18（IR 拆解）+ 六段式（ref-en.txt / C20）+ 本仓实测结论（seedance-h3-verify：T4 负面词零差异、空洞质量词存疑）对照完成
- 待办：把「社区模式库」分节写入 docs/11，标注来源；更新 mem0 [STATE] + retain 经验

## 抽样结构规律（24 条）

### A 族：时间分节式（最主流，~40%）
- `0–5 seconds: ... 5–10 seconds: ...` 或 `Scene N (Xs–Ys) – 标题` 或 `[0s-6s]` 前缀
- 每段 = 画面内容 + 镜头运动 + 2-4 个风格/质量词收尾；段数 3-5，15s 视频典型每段 3-5s
- 代表：nova-x TVC、wireless headphones（macro→hero→exploded-view→reconnect→hero 五段）、perfume 广告（五景）
- 变体：motion poster / paper-cut stop-motion 用「先空后满」渐进组装；教学片用循环 pattern

### B 族：字段式（LABELED FIELDS）
- `CAMERA/LOOK/STYLE/CHARACTER/SETTING`（vlog）；`Main Subject/Location/Visual Style/Camera Style/Timeline/Audio/Goal`（生活场景）；`[Core Concept]/[Character Identity]/[World Logic]/[Visual Language]/[Motion Rules]/[Restrictions]`（音乐 MV）
- Timeline 变体：`00:00–00:03 → 动作` 每 3s 一个 beat，台词写原文（含非英语）
- 分镜列表变体：`15s | 6 Cuts` + Propped/Handheld/Macro/Medium/Close/Selfie 每镜带台词

### C 族：单镜连续长句（one-take）
- 单段叙事长句 + 感官词 + 相机设备名（ARRI Alexa 35）+ 负面约束收尾（"No cyberpunk, no stylization"）
- 适合纪录片/真实感/UGC

### D 族：音乐驱动
- BPM/拍数 + beat 同步指令（"Every cut must land exactly on the beat"）+ 世界规则（kick 压缩时间线、snare 复制帧）
- 60s title sequence：开场稀疏→渐进加速→freeze-frame 硬切

### 通用惯例（跨族）
1. 角色引用标签 `@[char ref] / @[face ref] / @[body ref] / @[audio ref]`（Ref2VA 与官方 label 同构）
2. 一致性锚句："Preserve the exact identity ... Do not redesign" / "Same face, same bag, same world, held together across every cut"
3. 负面约束收尾：no hands / no text / no logos / no watermark
4. 空洞质量词高频：8K HDR / 4K / ultra-detailed / masterpiece
5. 相机/器材名：ARRI Alexa 35、DV camcorder、smartphone-shot look（反精致）

## 与 IR/六段式对照结论
- IR 用 `[Shot 1] At 00:02.650` 时间戳 + 镜头内描述层次（环境→主体→光→动作→物理细节）；社区用 `0–4s:` 段前缀更紧凑，无逐镜细节密度（IR 300-600 词/镜 vs 社区段 ~100-200 词）
- 六段式 subject_definitions/retention_analysis 官方独有；社区的 @[ref] 标签与"保留身份"句是同一思路的简化版（T2V 也能用，官方只有 Ref2V）
- 社区声音指令薄弱：多数无 overall_soundscape 段（只有个别带 "Soft ambient temple bells"）；IR 声音三层结构仍是本仓优势
- 冲突点（标注进 11）：① 负面约束词社区高频，但本仓 seedance-h3-verify 实测 T4 负面词零差异 → 标注"社区惯例 vs 本仓实测不支持"；② 空洞质量词（8K/ultra-detailed）社区高频，seedance 实测具体名词（打光/光晕）才被执行 → 建议用具体词
- 本仓可吸收（计划写入 11）：
  1. 产品片五段模板（macro→hero→exploded→reconnect→hero）
  2. 时间分节 + 每段风格词收尾（多段广告/15s）
  3. 字段式拍摄本模板（CAMERA/LOOK/STYLE/CHARACTER/SETTING）——与工具 B 拍摄本 schema 呼应
  4. 时间戳 beat 序列 + 台词原文（T2V 对话写法补充 docs/17）
  5. @[audio ref] 节奏参考（beat-sync MV）
  6. 「先空后满」渐进组装（产品 reveal / title sequence）
  7. UGC 反精致指令（smartphone-shot look, not overly retouched）

## 下一步
1. 写 docs/11 新分节「社区精选模式（BeatAPI awesome-minimax-h3-prompts）」
2. mem0 retain（吸收结论）+ 更新 [STATE]
3. 提交（scoped commit：docs/11 + 本进度文件）
