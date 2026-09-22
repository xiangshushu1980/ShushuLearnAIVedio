# wow-mage-survival Comfy-ops 适配包

这是一个轻量的作品相关实验包，不代表正式启动小说/短剧生产。当前只服务风格探索、人物 Ref 和相关技术验证。

故事讨论边界见 [`references/story_constraints_v1.md`](references/story_constraints_v1.md)：只借用 WOW 的任务功能和世界结构，不直接使用任何现有 NPC，也不直接复制标志性视觉元素。当前北郡任务映射见 [`references/northshire_task_map_v1.md`](references/northshire_task_map_v1.md)。

## 目录分工

- `plugins/`：当前概念需要的专属 ComfyUI 节点或控制逻辑。
- `workflows/`：人物 Ref、风格探针和后续必要的 H3 测试模板。
- `profiles/`：模型、LoRA、权重、尺寸和输出策略。
- `fixtures/`：少量与题材相关的测试输入。
- `experiments/`：候选风格、模型兼容性和参数实验。
- `artifacts/`：结果索引和 QC，不是正式美术资产库。

专属插件先放在这里；只有确认可复用于其他项目后，才提升到 comfy-ops 共享层。作品概念资料位于 `/home/sean/projects/wow-mage-survival`，但 comfy-ops 不依赖其未来的正式剧情结构。
