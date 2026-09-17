# ComfyUI 能力索引

本索引是 ComfyUI skill 的按需入口。先按“我要完成什么”定位，再只读取对应分册；不要默认全文读取所有 references。

## 按任务目的查找

| 任务 | 先读 | 然后按需读 |
|---|---|---|
| 了解本机环境、模型、启动/API | [core/environment.md](references/core/environment.md) | `docs/01_environment.md`、`docs/02_models.md` |
| 查通用节点含义和输入输出 | [core/nodes.md](references/core/nodes.md) | 旧版完整节点档案 [nodes.md](references/nodes.md) |
| KREA 2 / ANIMA 文生图 | [image/README.md](references/image/README.md) | [image/krea2.md](references/image/krea2.md)、[image/prompt-style.md](references/image/prompt-style.md) |
| 研究统一风格、Object ref | [image/prompt-style.md](references/image/prompt-style.md) | `experiments/` 与 `T-comfy-ops-40` progress |
| H3 文生视频/图生视频 | [video/README.md](references/video/README.md) | [video/h3.md](references/video/h3.md) |
| H3 Ref2VA / Object ref 接入视频 | [video/ref2va.md](references/video/ref2va.md) | `docs/34_ref2va_generation_guide.md`、`docs/33_h3_mc_engineering.md` |
| H3 提示词、视频生成或测试 | [h3-prompt-writing/SKILL.md](../h3-prompt-writing/SKILL.md) | 按模式读其参考文件和 `docs/17_h3_prompt_writing_rules.md`，再读对应视频分册 |
| 找可复用工作流 | [workflows/README.md](references/workflows/README.md) | 按意图打开具体 JSON 和档案 |
| 批量实验、对比、验收 | [workflows/batch-qc.md](references/workflows/batch-qc.md) | `scripts/`、`experiments/` |
| 排查报错、显存、队列、模型缺失 | [troubleshooting/README.md](references/troubleshooting/README.md) | 按类别读取旧版 [troubleshooting.md](references/troubleshooting.md) |

## 内容边界

- `core/`：跨图像/视频稳定通用的 ComfyUI 操作和契约。
- `image/`：生图能力、模型专项和提示词/风格实验。
- `video/`：视频能力、H3/Wan/Ref2VA 专项。
- `workflows/`：按工作流目的查找实际 JSON，而不是按模型堆放。
- `troubleshooting/`：按症状查经验；历史和易变踩坑仍保留在旧版档案/Mem0。
- 原始实验进 `experiments/`；稳定当前结论进入 docs 或对应分册；演进史进入 `.pi/ledger/`。

## 兼容说明

现有 `references/nodes.md`、`params.md`、`workflows.md`、`troubleshooting.md`、`learning.md` 暂作为完整旧档案保留。新任务优先从本索引进入；第二阶段再按索引迁移并收缩旧档案。
