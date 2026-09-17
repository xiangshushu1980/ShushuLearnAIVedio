# 作品包工具分工

这个目录是 `wow-mage-survival` 的 comfy-ops 适配包，不是世界观真相源。

| 任务线 | 负责内容 | 交付 |
|---|---|---|
| Plugin | 作品专属节点、编辑器控制和资源管线 | `plugins/` |
| Workflow | ANIMA/KREA/H3 工作流模板和输入契约 | `workflows/` |
| Profile | 模型、LoRA、权重、尺寸、显存和输出策略 | `profiles/` |
| Fixture | 从作品母库导入的角色/任务/法术测试夹具 | `fixtures/` |
| Experiment | 风格、模型兼容性、参数和批量测试 | `experiments/` |
| QC | 生成物质量、身份、法术可读性、视频继承和性能 | `artifacts/` |

## 提升规则

- 只为本作品服务的代码留在本目录。
- 经两个以上项目验证、接口稳定的能力，才提议提升到 comfy-ops 共享插件层。
- 任何提升都要保留兼容性说明和回归夹具。
- 作品母库确认的设定通过 `exports/comfy-ops/` 输入；实验结论通过 manifest 回链，不直接覆盖 canon。
