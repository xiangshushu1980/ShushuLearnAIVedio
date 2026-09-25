# 认知架构 v3 定稿：最简版（ledger + incdoc + mentor(refs) + mem0）

> 状态：设计定稿 v3（2026-08-22，用户拍板"确认"）
> 前序：v1（../archive/dev/cognition-architecture-design.md）→ v2（../archive/dev/cognition-architecture-v2.md，吸收 codex）
> v3 变化：**做减法**——砍掉所有中间层（kresolve/catalog/refs.sqlite/mem0 语义索引池/hive-ledger CLI），
> 回到"两个现存系统 + 一个 refs 指针 + 两条纪律"。零新增基础设施。

---

## 〇、核心结论

- **ledger 与 mentor 数据不合并**：主角不同（结论 vs 用户），物理合并会破坏 ledger 的 append-only 本质
- **连接层薄到只有 refs 指针 + incdoc**：mentor 概念条存 `refs: [{kind, query}]`，复习时 incdoc grep 取本体
- **写入靠两条既有纪律的强制点**，不新增 CLI
- **incdoc 是防上下文过长的机制**（已有工具），不是新增

---

## 一、系统清单（全部现存，零新增）

| 系统 | 角色 | 状态 |
|---|---|---|
| **ledger** | 定论真相源（append-only 文本） | 已有 |
| **incdoc** | append-only 档案的条目级检索（防膨胀） | 已有 |
| **mem0** | 经验层（坑/偏好/检索） | 已有 |
| **mentor** | 认知状态层（掌握度/复习计划） | 已有，加 refs 字段 |

**唯一新增**：mentor concepts 条目加 `refs` 字段 + 两条纪律。

---

## 二、数据流（写入 + 读取）

```
写入链路（强制点①）：任务收尾 → 收尾五步（补"定论 append ledger"）
写入链路（强制点②）：日常对话 → 会话结束 mem0 retain 打标[定论候选] → 统一转 ledger
读取链路：mentor 复习 → refs 指针 → incdoc grep → 取 ledger 现行值出题
```

- **强制点②借既有纪律**：AGENTS 已有"会话结束 retain 落盘"，在此判断"是定论→打标→转 ledger"
- **可选强化**：mentor 登记新概念时反向检查 ledger 是否有对应条目，无则提示沉淀

---

## 三、mentor 数据模型（最小改动）

```json
{
  "concept": "H3 VAE 选型",
  "level": 2,
  "streak": 3,
  "next_review": "2026-08-24",
  "refs": [{"kind": "ledger", "query": "VAE"}]
}
```

- 只加 `refs` 数组（指针，非本体）
- 砍掉 v2 的 sources 五类三维分级（authority/freshness）、concept_id/k_ids 命名体系

---

## 四、已砍清单（v2 → v3）

| 砍掉 | 理由 |
|---|---|
| kresolve / catalog 注册表 | 条目标题即稳定锚点，mentor 用 incdoc grep 即可达 |
| refs.sqlite 倒排索引 | incdoc 毫秒级关键词检索已覆盖 |
| mem0 ledger 专用语义索引池 | mentor 是概念条驱动（确定性取内容），非随机语义查询 |
| hive-ledger CLI | 低频、单作者、git 兜底；强制靠纪律 |
| authority/freshness 三维分级 | 单用户场景防御性设计，用不上 |

---

## 五、实施清单（待用户拍板启动）

1. **AGENTS 加两条纪律**：
   - 收尾四步 → 五步（补"任务定论 append ledger"）
   - 对话定论判据 + retain 打标转 ledger
2. **mentor concepts.json 加 refs 字段**（试点 3 条：H3 VAE / nvfp4 / Hybrid）
3. **试点验证**：mentor 复习一条概念 → refs → incdoc grep → 取到 ledger 现行值

---

## 六、验收标准

- 会话检索 ledger 知识：incdoc grep，O(命中)，不读全量
- 日常对话产生的定论：会话结束 retain 打标 → 有落点，不漏
- mentor 复习：能沿 refs 取到 ledger 现行值出题
