# 14. Skill 治理框架（多 skill 维护纪律）

> 跨试验项目组织 skill 与记忆的规则。2026-08-05 确立（speech-video 首个试验项目后沉淀）。
> 适用范围：comfy-ops 项目级。**当实验项目扩展到其他目录/多项目统一时，升级到用户级 AGENTS.md。**

## 1. 核心原则（一句话）

**原始证据进 experiments，当前基线进 docs/skill，结论演进进 ledger，动态经验进 Mem0；稳定契约由单一 skill 持有，用例 skill 只组装核心能力。**

## 2. Skill 三层结构

```
共享层（跨所有 skill）           ← 只放"稳定契约"，不写入业务使用逻辑
  · ComfyUI API 调用 / ffmpeg 基础 / mem0 用法 / 网络检索
  · 内容只写一份，其他 skill 引用（绝不复制）

核心能力 skill                  ← 框架层/地基
  · comfyui：安装 + 理解框架 + 节点/API + 通用工作流 + 学习路径

特定用例 skill（N 个）           ← 业务层，组装核心能力
  · speech-to-video：whisper→分镜→生图→动画→合成→混音
  · 未来 xxx 用例
```

## 3. 划分纪律

- **按"触发场景/能力"分，不按工具/模型分**
- 一个 skill 一个**单一写者**主题，别塞太多
- 大 skill 内部用 `references/` 分册细化，不拆散
- **共享内容只写一份，跨 skill 用引用/路径，不用拷贝**（拷贝=必然分叉）
- 粒度适中：核心 1 个 + 特定用例各 1 个
- 每个 skill 标明宿主能力边界；依赖 canvas、choice cards、`hub_*` 等专有能力的 skill 不得承诺在普通 Pi/Codex 中完成生成和合成
- frontmatter 只使用当前校验器支持的字段；兼容性和自定义检索词放入 `metadata` 或正文。目录名必须与 `name` 一致

## 4. 经验与知识的流动（防污染）

```
mem0（动态经验层）               skill（稳定契约层）
  · 通用经验 → global 池           · 共享 skill：只放稳定 how-to
  · 业务经验 → comfy-ops 池+标签    · 用例 skill：业务稳定管线
  · 实测值/踩坑/偏好               · 单一写者，主动维护
        │ 验证稳定、跨场景通用后蒸馏
        └────────────────→ skill 参数表/引用
```

**铁律**：
1. 原始实验输入、输出和测量记录 → `experiments/`；当前有效参数/步骤/契约 → docs 或 skill
2. 结论的历史版本、覆盖关系与证据锚 → ledger；易变踩坑、个人偏好和语义检索型经验 → Mem0
3. Mem0 可以引用 docs/skill/ledger 的位置，但不复制权威正文
4. 只有被验证稳定、适用条件明确的经验才蒸馏成 docs/skill 的当前基线；蒸馏后历史留在 ledger

## 5. 新项目怎么办

| 新项目类型 | 动作 |
|-----------|------|
| **新框架**（新工具/技术栈） | 先建**核心 skill**：安装 + 跑通 + 理解节点/API/参数 + 学习路径（像 comfyui skill 干的事） |
| **新用例**（复用已有核心） | 建**用例 skill** + `experiments/<项目名>/` 试验文件夹 |

每个试验项目：
1. 试验产物 → `experiments/<项目名>/`（assets/scripts/data/README）
2. 经验 → mem0（先落动态层）
3. 验证成熟 → 蒸馏成用例 skill + 更新核心 skill 的共享引用

## 6. skill 与 mem0 分工

| | skill | mem0 |
|---|-------|------|
| 内容 | 怎么做及当前有效基线（稳定过程/参数/步骤） | 易变踩坑、偏好、待蒸馏结论（动态） |
| 读取 | 任务匹配时显式加载 | 开工时 recall 检索 |
| 更新 | 单一写者，主动维护 | 零协调，随时 retain |

## 7. 与 skill-creator 的关系

- **skill-creator** = 格式工具（怎么写 SKILL.md：结构/脚本/references）
- **本框架** = 战略（何时建、建核心还是用例、经验放哪、共享怎么处理）
- 流程：生成 skill 前，agent **先读本框架**决定"建哪种/哪些进 mem0/共享怎么处理"，**再调 skill-creator** 写文件

## 8. 升级路径

- 本框架先在 comfy-ops 项目级验证（当前阶段）
- 当出现任一情况升级到用户级（~/.pi/agent/AGENTS.md + docs/）：
  1. 在 comfy-ops 之外目录做实验项目
  2. 多项目需要统一 skill 组织方法
- 先例：多 PI Agent 协作纪律 = 先 comfy-ops 验证 → 后进 global
