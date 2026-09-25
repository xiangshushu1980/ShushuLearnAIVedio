# 认知架构设计 v2（吸收 codex 复查意见 + incdoc 定位）

> 状态：设计草案 v2（2026-08-22），已吸收 codex 复查意见
> 上一版：v1（cognition-architecture-design.md，见同目录）
> 关键变化：①弃"用户级 ledger"，改"知识目录/解析器 kresolve" ②索引当可重建缓存 ③四步落地 ④incdoc 定位为 append-only 档案的防膨胀检索层

---

## 〇、设计原则（v2 确立）

1. **认知分层 + ID 互通**，不物理合并（保护 ledger 的 append-only 本质）
2. **正文不上移**：用户级只建"知识目录/解析器"，不复制正文、不存定论摘要
3. **索引当可重建缓存**：不做人工维护的反向表，由工具增量扫描生成
4. **契约先行**：先定 K-ID 粒度/命名/失效契约，再动数据
5. **防膨胀是显式设计目标**：incdoc 承担 append-only 档案的条目级检索

---

## 一、系统分层（不变，确认有效）

| 层 | 系统 | 主角 | 可变性 | 层级 |
|---|---|---|---|---|
| 认知状态层 | **mentor** concepts | 用户本人 | 可变（升档） | 用户级 |
| 知识本体层 | **ledger** / docs / skills | 结论 | ledger 不可变（append-only） | ledger 留项目级 |
| 经验层 | **mem0** | 经验片段 | 可变可删 | 用户级 |
| 行为层 | **TODO** / progress / git | 任务 | 可变 | 用户级 |
| **检索层** | **incdoc** + kresolve | 索引 | 可重建 | 用户级 |

> **incdoc 定位**：ledger/progress/done 等不断追加的文本档案，一律用 incdoc 条目级检索
> （`incdoc grep/find/show/scan`），禁止全量 read。实测：ledger 各文件已可直接 incdoc grep/scan，
> 命中条目原文 + 行号区间一次拿到，O(命中) 不读全量。→ 这就是"正文膨胀不拖累会话"的机制。

---

## 二、K-ID 契约（先定，防别名地狱）

- **命名**：命名空间式 `K:<域>:<子域>:<主题>`，如 `K:comfyui:h3:vae-selection`
- **粒度**：一个 K = 一个会跨任务/来源/项目复用、或需学习跟踪的**主题**（概念/参数/选型问题）
- **不可变**：canonical ID 不可改；改名只加 alias，保留旧 ID
- **一次性观察不建 K**：只有跨任务/来源/项目复用，或需学习跟踪才注册
- **淘汰**：已淘汰 K 只留 `alias → replacement` 映射，不参与默认检索

**身份与正文分离**：
- source 文件自身标注 K-ID（ledger 条目头 / docs 章节 / mem0 标签）
- 用户级只放 catalog（身份/别名/归属）+ alias 映射，无正文、无摘要

---

## 三、接口：kresolve 解析器（最小耦合）

```
K 注册表（catalog）→ 只负责身份/别名/归属
source 文件 → 自身标注 K-ID
工具增量扫描 → 生成 refs.sqlite 倒排索引（可重建缓存）
kresolve <query> → 只返回 ≤5 个短卡片 + locator
需深入时按层级加载：现行 claim → 文档段落 → 证据/经验
```

- **mentor 不持有 sources 数组**，改为通过 `kresolve` 查询（去取非推送）→ 消除三处人工双写漂移
- **验收标准**：未命中知识问题时读 0 个 catalog 分片；命中先返回短卡片；完整谱系只在明确追问时加载

---

## 四、mentor 数据模型（v2）

```json
{
  "concept_id": "M:comfyui:h3-vae-selection",
  "k_ids": ["K:comfyui:h3:vae-selection"],
  "level": 2,
  "confidence": "medium",
  "capability_gap": "能选用，不能解释适用条件",
  "misconceptions": [{
    "text": "认为 nvfp4 一律不可用",
    "status": "active",
    "observed_at": "2026-08-21"
  }],
  "last_assessed_at": "2026-08-21",
  "source_revision_seen": ["C-20260816-20"],
  "review": { "streak": 3, "next_review": "2026-08-24" }
}
```

- 独立 `concept_id` 为主键；`k_ids` 是关联
- `source_revision_seen`：核心结论被替换时标记"需重新校准"，不必同步全文

**来源 5 类拆三维**（v1 混合了载体/外部/常识三维度，v2 拆分）：

| 字段 | 取值 |
|---|---|
| `source_kind` | ledger / docs / mem0 / network / world |
| `authority` | 高（官方实测）/ 中（社区）/ 低（world 常识） |
| `freshness` | 按主题：价格/版本/政策短，论文/本地实测长；过期≠删除，是"用前复验" |

> `world` 只作 `unattributed-model-knowledge`，默认低可信，不当决策证据。
> `mem0` 是经验入口，不单独作为高风险结论的唯一证据。
> `network` 带抓取时间/发布日/再验证策略/快照 hash。

---

## 五、落地四步（v2，改自 v1 三小步）

1. **先定契约与校验器**：K/C/T/E 的粒度、命名、引用信封、失效与重定向规则；写 `kresolve`/lint 最小规范。
2. **本项目只读试点**：为 3 主题注册 K（`K:comfyui:h3:vae-selection` 等），给已有 C-ID 和 docs 加 K 标记，生成可重建索引；验证"查询 K → 精确找到当前 C 和正文"。验收 = 未命中读 0 分片 / 命中先短卡片。
3. **再接 mentor**：加 `concept_id/k_ids/source_revision_seen`，验证"知识更新后提示复习"（非 mentor 回写 ledger）。
4. **最后用户级聚合**：catalog/alias/resolver 放用户级；项目 ledger 正文不迁移，跨项目只增索引项。

---

## 六、高风险陷阱（codex 提 + v2 应对）

| 陷阱 | v2 应对 |
|---|---|
| K 粒度失控 → 重叠/别名地狱 | 先定粒度契约（二） |
| 三处人工双写漂移 | source 标注 + 工具生成索引收敛；mentor 用 kresolve 去查 |
| ledger"改状态"名实不符 | 明确"时间线不可变、状态字段是可变投影"；或状态由最新事件推导 |
| 隐私：mentor 用户级敏感档案 | 项目仓库不反向携带用户掌握状态；项目可见 K 与掌握状态分开 |
| 并发写全局 K 注册 | 单一 CLI/锁/原子写；禁多 agent 手编同一 JSON |
| TODO 完成 ≠ 沉淀知识 | 完成只产生候选信号；可复用的结论/证据/学习点才建 C/K |
| 全局文件膨胀拖累会话 | incdoc 条目级检索 + kresolve 惰性加载 + catalog 只存身份 |

---

## 七、待拍板

1. K-ID 用 `K:域:子域:主题` 命名空间式，OK？
2. 用户级叫"知识目录/解析器"（非"用户级 ledger"），ledger 正文留项目，OK？
3. incdoc 承担 ledger/progress/done 的检索层，是否纳入本次实施范围？
4. refs.sqlite 倒排索引 vs incdoc 重扫（毫秒级、文件即真相）：是否两者都要，还是先用 incdoc、索引后置？
