# 结论谱系（Conclusion Ledger）

> 定位：**结论的「身份证 + 家谱」**——记录「定论/参数/技术判断」的演进史、覆盖链、证据锚。
> 它不是证据的副本，而是指向 docs/mem0/git 中证据的索引 + 结论的版本史。
> 唯一 append-only 的层：**永不覆盖、永不删除**，只追加时间线 + 改状态。

---

## 〇、按主题查账本

每个主题文件维护自己的条目索引；本页只索引主题文件和解决旧 ID 冲突，避免复制一份容易过期的全量条目表。

| 主题 | 账本 |
|---|---|
| H3 速度、采样与生成管线 | [h3-speed.md](h3-speed.md) |
| H3 模型、可行性与 FaceRefine | [h3-models.md](h3-models.md) |
| H3 音频与 Breeze TTS | [h3-audio.md](h3-audio.md) |
| H3 提示词与 Reference 测试 | [h3-prompt.md](h3-prompt.md) |
| Motion Booster | [h3-motion-booster.md](h3-motion-booster.md) |
| 视频分析与 OCR | [va-ocr.md](va-ocr.md) |
| 多 Agent 协作治理 | [collab-governance.md](collab-governance.md) |
| Qwen 数据图表 | [qwen-charts.md](qwen-charts.md) |
| Qwen 图像节点与预览 | [qwen-nodes.md](qwen-nodes.md) |
| Reference Agent | [reference-agent.md](reference-agent.md) |
| Reference 工作区 | [reference-workspace.md](reference-workspace.md) |

## 〇-A、历史重复 ID 的无歧义映射

历史条目保持原样。引用下列结论时使用“规范 ID”；旧 ID 仅在对应账本文件内有效。新结论统一采用 `C-<DOMAIN>-YYYYMMDD-NN`，DOMAIN 使用稳定主题缩写。

| 旧 ID（仅文件内有效） | 规范 ID | 条目 | 文件 |
|---|---|---|---|
| `C-20260907-01` | `C-COLLAB-20260907-01` | Conductor Worker 失败回报与重试契约 | [collab-governance.md](collab-governance.md) |
| `C-20260907-01` | `C-H3MODELS-20260907-01` | Ref2VA 中文口型测试必须接 NativeAudioLock | [h3-models.md](h3-models.md) |
| `C-20260917-01` | `C-H3AUDIO-20260917-01` | Breeze TTS 2 标准流程与运行模式 | [h3-audio.md](h3-audio.md) |
| `C-20260917-01` | `C-H3MODELS-20260917-01` | VDN Ref2VA 1024×576/20s + NativeAudioLock 验收基线 | [h3-models.md](h3-models.md) |
| `C-20260926-01` | `C-H3PROMPT-20260926-01` | 角色 Reference 生成链统一为主图→H3全视角→抽帧 | [h3-prompt.md](h3-prompt.md) |
| `C-20260926-01` | `C-H3MODELS-20260926-01` | FaceRefine 分段慢车道与目标锁定边界 | [h3-models.md](h3-models.md) |

---

## 一、与现有机制的分工（不冲突、不重复）

| 机制 | 存什么 | 覆盖/删除时旧值去哪 |
|---|---|---|
| docs | 现行手册/参数（**最新态**，可留上一版 fallback） | 旧值靠 git 兜底 + **本谱系记演进** |
| mem0 | 经验/踩坑/偏好（**检索式**） | update/delete，旧值不留 |
| 远程 Task Center | 任务状态、控制权、checkpoint 与验收 | 按远程生命周期保留事件；本地文档和 Mem0 不承载当前任务状态 |
| progress | 任务私有日志 | git 保留 |
| **本谱系** | **定论的演进史（C-ID）** | **只追加，永不覆盖** |

**核心分工**：docs 保存当前可执行手册，谱系保存结论如何演进，Mem0 保存可检索经验线索。发生冲突时不能用记忆直接覆盖现行手册；先核对证据、条件和替代关系。

## 二、什么进谱系 vs 什么进 mem0（判定）

- **进谱系**：实测得出的「定论」——参数值、加速比、可行性判断、选型结论（"是什么"，会随技术更新而演进）
- **进 mem0**：经验/踩坑/技巧/偏好（"怎么用"，检索式触发，不强调演进）
- **边界**：一条结论若同时是定论又是经验，定论部分进谱系、经验部分进 mem0，谱系条目里互指（证据锚写 mem0 id）

> 收尾时替换现有「收尾四步」第①步：结论提炼时按上表**分流**——定论 → 谱系（+ docs 现行值）；经验 → mem0。

## 三、条目模板

```
### C-<DOMAIN>-YYYYMMDD-NN | <主题一句话>
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

## 五、ID 与溯源（与远程任务 ID 区分）

- 新结论 ID：`C-<DOMAIN>-YYYYMMDD-NN`；DOMAIN 使用账本主题缩写（如 `H3MODELS`、`H3AUDIO`、`COLLAB`），保证跨文件唯一。已有无主题前缀的 ID 作为 legacy ID 保留；重复项按本 README 的迁移表解析。
- 任务 ID：`T-YYYYMMDD-NN`。引用结论时使用规范 ID；引用尚未迁移的唯一 legacy ID 时同时给出账本文件路径。
- 每条结论**引用来源任务 T-ID**（谁得出它）+ 覆盖时引用覆盖来源任务 T-ID
- 溯源链：`结论 C-XXX ← 任务 T-AAA（提出）← 任务 T-BBB（覆盖）`，Git 与远程任务事件都能顺着查

## 六、git 提交粒度

**ledger 变更独立 commit；有既有混合改动时保留工作树，不强行整文件提交**，message 格式：

```
[结论] C-20260816-02 覆盖：TE 80s→11s（swap 污染排除）
```

- 一次收尾登记/覆盖 N 条结论 = 一次 ledger commit（message 列出所有 C-ID）
- 效果：`git log --grep="[结论] C-XXX"` 可追一条结论的完整演进——补上「git 按 commit 组织、不可按结论检索」的短板
- 任务收尾的其他文件（progress/docs/远程 checkpoint）照旧 scoped commit，与 ledger commit 分开

## 七、写入纪律

1. **append-only**：只追加时间线、改状态，不覆盖/删除历史版本
2. **写前 read 最新 + `git status`**（共享文件，同现有纪律）
3. **独立 commit**（见上节，`[结论]` 前缀）
4. **证据删了回来改锚**：docs 归档/mem0 delete 后，回来把证据锚标「已删，历史见 git」，不让指针悬空

## 八、文件组织

- 本 README = 规则 + 模板 + 索引（索引见〇节）
- 条目按主题拆文件，单文件起步，超 ~500 行再拆；每文件顶部放本文件索引表
- 当前账本文件列表只维护在顶部「按主题查账本」；不再维护第二份文件/条目范围清单。初始回填范围与旧目录结构可从 Git 历史追溯。

## 九、设计对标（2026-08-16 调研）

本设计不是闭门造车，对标三个成熟范本：

- **ADR（Architecture Decision Records）**：状态机 + `superseded by` + append-only 纪律——本谱系的「已修正/已推翻」≈ ADR 的「superseded」
- **Temporal Knowledge Graph（时态知识图谱）**：`valid_from/valid_to` 时间语义 + 非破坏性保留（标 inactive 而非删除）
- **Event Sourcing（事件溯源）**：不可变事件序列 + 可重建任意时点状态

**决策**：采用 ADR 的方法论（格式/状态机/superseded 链）+ TKG 的时间语义（valid_from），**不引入 adr-tools 等 CLI 工具**——语义不匹配（ADR 管「决策」、本谱系管「定论」）、agent 工作流用纯 markdown 更轻（read/edit/grep + git 即可）。
