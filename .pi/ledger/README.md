# 结论谱系（Conclusion Ledger）

> 定位：**结论的「身份证 + 家谱」**——记录「定论/参数/技术判断」的演进史、覆盖链、证据锚。
> 它不是证据的副本，而是指向 docs/mem0/git 中证据的索引 + 结论的版本史。
> 唯一 append-only 的层：**永不覆盖、永不删除**，只追加时间线 + 改状态。

---

## 〇、条目索引（全量，2026-08-16 回填）

| C-ID | 主题 | 状态 | 所在文件 |
|---|---|---|---|
| C-20260816-01 | H3 管线三档 + 15s 长档 | ✅现行 | h3-speed.md |
| C-20260816-02 | TE/DiT 模型加载时间（80s→~11s） | ✅现行 | h3-speed.md |
| C-20260816-03 | SageAttention 加速 | ✅现行 | h3-speed.md |
| C-20260816-04 | Sol-Attn 弃用 | ✅现行 | h3-speed.md |
| C-20260816-05 | MotionCache 适用域 | ✅现行 | h3-speed.md |
| C-20260816-06 | H3 两阶段流水线（cond 缓存） | ✅现行 | h3-speed.md |
| C-20260816-07 | ComfyUI 0.32.0 修复验证 | ✅现行 | h3-speed.md |
| C-20260816-08 | fl2v Turbo LoRA 代际定案 | ✅现行 | h3-speed.md |
| C-20260816-09 | Ref2VA Turbo 4 步速度 | ✅现行 | h3-speed.md |
| C-20260816-10 | Ref2VA ref_image_size 策略 | ✅现行 | h3-speed.md |
| C-20260816-11 | H3 BGM 触发条件 | ✅现行 | h3-audio.md |
| C-20260816-12 | 音乐先验恒定 + 去 BGM 工具（demucs） | ✅现行 | h3-audio.md |
| C-20260816-13 | Ref2VA 纯音频参考可用 | ✅现行 | h3-audio.md |
| C-20260816-14 | 音频劣化归因（sage/MC） | ✅现行 | h3-audio.md |
| C-20260816-15 | 渲染风格词主导 | ✅现行 | h3-prompt.md |
| C-20260816-16 | 画面内文字控制（六块矩阵） | ✅现行 | h3-prompt.md |
| C-20260816-17 | Seedance 7 条经验 H3 适用性 | ✅现行 | h3-prompt.md |
| C-20260816-18 | 提示词增强在线 IR API 选型 | ✅现行 | h3-prompt.md |
| C-20260816-19 | turnaround LoRA 适用域 | ✅现行 | h3-prompt.md |
| C-20260816-20 | Hybrid b25-49（fl2va+ref2va） | 🟡待验证 | h3-models.md |
| C-20260816-21 | 防 OOM flags 全退 | ✅现行 | h3-models.md |
| C-20260816-22 | SageAttention v2 无需 patch | ✅现行 | h3-models.md |
| C-20260816-23 | Sol Engine 未开源 | ✅现行 | h3-models.md |
| C-20260816-24 | fal H3 定价 | ✅现行 | h3-models.md |
| C-20260816-25 | FaceRefine 精修参数铁律 | ✅现行 | h3-models.md |
| C-20260816-26 | Cache-DiT 加速（官方宣称） | 🟡待验证 | h3-models.md |
| C-20260816-27 | H3 能力边界（固定音频同步） | ✅现行 | h3-models.md |
| C-20260827-01 | OCR 文字流压缩范式与参数定论 | ✅现行 | va-ocr.md |
| C-20260828-01 | Spectrum 跳 transformer 加速适用域 | ✅现行 | h3-speed.md |
| C-20260827-02 | P1 OCR 合并逻辑失效（数据实证） | ✅现行 | va-ocr.md |
| C-20260902-01 | FL2VA PDD 8-step 长段可行性 | ✅现行 | h3-speed.md |
| C-20260902-02 | NVIDIA H3 Super Acceleration 架构边界 | ✅现行 | h3-speed.md |
| C-20260905-01 | SageAttention post6 H3 一致性 | ✅现行 | h3-speed.md |
| C-20260906-01 | H3 20 步 Sage 开关动作差异 | ✅现行 | h3-speed.md |
| C-20260914-01 | VDN Ref2VA 1024×576 双角色 NativeAudioLock 时长基线 | ✅现行 | h3-speed.md |
| C-20260914-02 | 普通 Ref2VA Turbo LoRA 1024×576 双角色长时基线 | ✅现行 | h3-speed.md |
| C-20260915-01 | Ref2VA PDD 8-step 与标准 20-step 5 秒同参对照 | ✅现行 | h3-speed.md |
| C-20260920-02 | H3 完整视频 latent 两阶段放大远景脸 smoke/5s 验证 | 🟡待验证 | h3-models.md |
| C-20260922-02 | VOSR2 本地安装与图像/短批次 smoke | 🟡待验证 | h3-models.md |

---

## 一、与现有机制的分工（不冲突、不重复）

| 机制 | 存什么 | 覆盖/删除时旧值去哪 |
|---|---|---|
| docs | 现行手册/参数（**最新态**，可留上一版 fallback） | 旧值靠 git 兜底 + **本谱系记演进** |
| mem0 | 经验/踩坑/偏好（**检索式**） | update/delete，旧值不留 |
| TODO | 任务待办（T-ID，四态机） | 完成移 ✅ 节 |
| [STATE] | 任务线共享状态（mem0） | 完成即删 |
| progress | 任务私有日志 | git 保留 |
| **本谱系** | **定论的演进史（C-ID）** | **只追加，永不覆盖** |

**核心分工一句话**：docs/mem0 存「当前是什么」，谱系存「它怎么变成这样的」。

## 二、什么进谱系 vs 什么进 mem0（判定）

- **进谱系**：实测得出的「定论」——参数值、加速比、可行性判断、选型结论（"是什么"，会随技术更新而演进）
- **进 mem0**：经验/踩坑/技巧/偏好（"怎么用"，检索式触发，不强调演进）
- **边界**：一条结论若同时是定论又是经验，定论部分进谱系、经验部分进 mem0，谱系条目里互指（证据锚写 mem0 id）

> 收尾时替换现有「收尾四步」第①步：结论提炼时按上表**分流**——定论 → 谱系（+ docs 现行值）；经验 → mem0。

## 三、条目模板

```
### C-YYYYMMDD-NN | <主题一句话>
- 状态：✅现行（valid_from YYYY-MM-DD）/ 🟡待验证 / 📝已修正（被 C-YYY 取代）/ ❌已推翻（被 C-YYY 取代，原因）
- 现行值：<一句话当前结论>
- 时间线（append-only，只追加不删）：
  - YYYY-MM-DD 提出：<值>（来源任务 T-XXX）
  - YYYY-MM-DD 修正：<新值>（原因：...；覆盖 YYYY-MM-DD 版本；来源任务 T-YYY）
- 证据锚：docs/X §Y / mem0 <id> / git <hash> / 产物 <path>
```

**示例（真实案例，正式登记见 C-20260816-02）**：

```
### C-20260816-02 | H3 TE 加载时间
- 状态：✅现行（valid_from 2026-08-16）
- 现行值：TE 冷 ~11s / 热 ~4s（健康态）
- 时间线：
  - 2026-08-05 提出：~80s/次（来源任务 T-20260815-06）
  - 2026-08-16 修正：~11s/4s（原因：80s 系 swap 污染数据；覆盖 2026-08-05 版本；来源任务 T-20260816-01）
- 证据锚：docs/10 §开销分析 / mem0 11eaa2d0 / git commit cond-cache-node
```

## 四、状态机

```
🟡待验证 ──实测通过──▶ ✅现行（valid_from = 通过日）
✅现行   ──重新实测──▶ 📝已修正（被 C-YYY 取代）
✅现行   ──证伪─────▶ ❌已推翻（被 C-YYY 取代，原因）
```

- 覆盖是**追加 + 改状态**，不是改正文：旧版本永远留在时间线里
- **取代关系内联在状态里**（学 ADR 的 `superseded by`）：旧条目标「被 C-YYY 取代」，新条目在时间线里写「覆盖 YYYY-MM-DD 版本」——双向可追
- **valid_from**（学 TKG 时间语义）：现行值标注生效日期；失效日期 = 被取代时的日期（不显式写 valid_to，由被取代时间推出）

## 五、ID 与溯源（和 TODO 不撞）

- 结论 ID：`C-YYYYMMDD-NN`；任务 ID：`T-YYYYMMDD-NN`——前缀区分，无冲突
- 每条结论**引用来源任务 T-ID**（谁得出它）+ 覆盖时引用覆盖来源任务 T-ID
- 溯源链：`结论 C-XXX ← 任务 T-AAA（提出）← 任务 T-BBB（覆盖）`，git/TODO 都能顺着查

## 六、git 提交粒度

**ledger 变更独立 commit，不混在任务收尾的其他文件里**，message 格式：

```
[结论] C-20260816-02 覆盖：TE 80s→11s（swap 污染排除）
```

- 一次收尾登记/覆盖 N 条结论 = 一次 ledger commit（message 列出所有 C-ID）
- 效果：`git log --grep="[结论] C-XXX"` 可追一条结论的完整演进——补上「git 按 commit 组织、不可按结论检索」的短板
- 任务收尾的其他文件（progress/docs/TODO）照旧 scoped commit，与 ledger commit 分开

## 七、写入纪律

1. **append-only**：只追加时间线、改状态，不覆盖/删除历史版本
2. **写前 read 最新 + `git status`**（共享文件，同现有纪律）
3. **独立 commit**（见上节，`[结论]` 前缀）
4. **证据删了回来改锚**：docs 归档/mem0 delete 后，回来把证据锚标「已删，历史见 git」，不让指针悬空

## 八、文件组织

- 本 README = 规则 + 模板 + 索引（索引见〇节）
- 条目按主题拆文件，单文件起步，超 ~500 行再拆；每文件顶部放本文件索引表
- 现状（2026-08-16 首轮回填）：
  - `h3-speed.md`（C-01~C-10）：速度/加速/管线
  - `h3-audio.md`（C-11~C-14）：音乐/音频
  - `h3-prompt.md`（C-15~C-19）：提示词/风格/增强
  - `h3-models.md`（C-20~C-27）：模型/可行性
  - `va-ocr.md`（C-20260827-01~02）：视频分析/OCR 压缩（fund-video-analysis）

  - `h3-speed.md`（C-20260920-01）：H3 Ref2VA + SelfLift 在 RTX 4090 上的证据边界

## 九、设计对标（2026-08-16 调研）

本设计不是闭门造车，对标三个成熟范本：

- **ADR（Architecture Decision Records）**：状态机 + `superseded by` + append-only 纪律——本谱系的「已修正/已推翻」≈ ADR 的「superseded」
- **Temporal Knowledge Graph（时态知识图谱）**：`valid_from/valid_to` 时间语义 + 非破坏性保留（标 inactive 而非删除）
- **Event Sourcing（事件溯源）**：不可变事件序列 + 可重建任意时点状态

**决策**：采用 ADR 的方法论（格式/状态机/superseded 链）+ TKG 的时间语义（valid_from），**不引入 adr-tools 等 CLI 工具**——语义不匹配（ADR 管「决策」、本谱系管「定论」）、agent 工作流用纯 markdown 更轻（read/edit/grep + git 即可）。
