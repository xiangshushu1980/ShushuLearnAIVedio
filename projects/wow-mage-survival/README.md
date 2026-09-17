# wow-mage-survival Comfy-ops 项目包

这是 `wow-mage-survival` 在 comfy-ops 中的专属工具包。当前承载该作品的插件、工作流、ComfyUI profiles、测试夹具、实验和生成产物索引。

## 目录分工

- `plugins/`：该作品专属的 ComfyUI 节点/插件源；稳定通用后再提升到共享插件层。
- `workflows/`：角色、场景、法术和 H3 的工作流模板。
- `profiles/`：模型、LoRA、权重、尺寸和输出策略。
- `fixtures/`：来自作品母库的版本化角色/任务/法术测试输入。
- `experiments/`：候选风格、模型兼容性和参数实验。
- `artifacts/`：生成结果 manifest、QC 和可追溯索引；正式 canon 仍回到作品项目。

当前项目包的第一项任务是 `T-comfy-ops-37`：使用第一集野狼任务验证总风格，而不是生成正式资产。
