# Reference 工作台实现证据

> Owner: Sean。演进与证据锚追加记录；当前操作与参数以 `reference-workspace/README.md` 和 catalog 为准。

## C-20261002-01 | 一期设定图片与概念图闭环

- 条件：Node 24.18.0、React 19.3、Vite 8.3.2，独立本地 API/SQLite；共享 ComfyUI 的 Qwen Image 2.1 int8 ConvRot、Qwen3-VL 8B int8、2.1 VAE，1536×1024、25 步、CFG1、Euler/simple。
- 实装验证：设定图当前目录多选导入；明确四图引用 → Qwen 概念图；概念图历史一图 → 下一轮；进行中重启工作台后恢复同一 `prompt_id`，无重复提交。三轮均成功回收，历史自动锁定，ComfyUI 本批输出清理完成。
- 保护语义验证：7 项测试全部通过，覆盖跨实体拒绝、幂等性、模板 hash、锁定与删除、被引用删除确认和墓碑；桌面与 390px 手机页面无横向溢出，最终浏览器控制台无错误。
- 限制：节点声明最多 16 图，本期只实跑四图与历史单图；不据此声称 16 图质量已验证。Krea 备选未纳入本期真实生成验收。ComfyUI 原生同次运行深链未验证，只提供实际提交图与 ID。主形象/三视图/声音及管理 UI 留后续。
- 证据：`experiments/sean_reference_workspace_phase1_20261002/manifest.json`、`QC.md`；任务 `remote-47938b21-ae2e-4c9c-b3ba-12d6696b3375`；代码 `reference-workspace/`。
