# Reference 工作台实现证据

> Owner: Sean。演进与证据锚追加记录；当前操作与参数以 `reference-workspace/README.md` 和 catalog 为准。

## C-20261002-01 | 一期设定图片与概念图闭环

- 条件：Node 24.18.0、React 19.3、Vite 8.3.2，独立本地 API/SQLite；共享 ComfyUI 的 Qwen Image 2.1 int8 ConvRot、Qwen3-VL 8B int8、2.1 VAE，1536×1024、25 步、CFG1、Euler/simple。
- 实装验证：设定图当前目录多选导入；明确四图引用 → Qwen 概念图；概念图历史一图 → 下一轮；进行中重启工作台后恢复同一 `prompt_id`，无重复提交。三轮均成功回收，历史自动锁定，ComfyUI 本批输出清理完成。
- 保护语义验证：7 项测试全部通过，覆盖跨实体拒绝、幂等性、模板 hash、锁定与删除、被引用删除确认和墓碑；桌面与 390px 手机页面无横向溢出，最终浏览器控制台无错误。
- 限制：节点声明最多 16 图，本期只实跑四图与历史单图；不据此声称 16 图质量已验证。Krea 备选未纳入本期真实生成验收。ComfyUI 原生同次运行深链未验证，只提供实际提交图与 ID。主形象/三视图/声音及管理 UI 留后续。
- 证据：`experiments/sean_reference_workspace_phase1_20261002/manifest.json`、`QC.md`；任务 `remote-47938b21-ae2e-4c9c-b3ba-12d6696b3375`；代码 `reference-workspace/`。

## C-20261003-01 | 引用平等布局与历史输入恢复

- 用户反馈后，所有本轮 ref 使用同尺寸网格，来源库移入选择窗口；生成结果独立显示大图。历史记录点击恢复原输入、ref 顺序和原始工作流，后续运行保留来源 ID 并检查模板兼容。
- 页面复核：四图历史的提示词、模型、原始风格、1536×1024、seed 42、steps 25 恢复；四卡尺寸一致；选择取消保持 4 图、确认改为 3 图；390px 无横向溢出，console 无错误。构建成功，无新增 GPU 生成或单元测试执行。
- 早期没有模板 hash 的记录用完整提交图对比当前模板重建的原输入图，本期四图记录匹配；证据：`experiments/sean_reference_workspace_phase1_20261002/sean_review_20261003.md`。当前操作仍以 README 为准。

## C-20261003-02 | 主形象选择与 V3 Simple 多视图

- 用户已验收一期，二期直接从概念图选主形象，不再重复生成；PC 优先。主形象独立版本与来源 hash 持久保存，当前来源受保护；三／四视图绑定该版本，结果确认记录独立版本，旧图留历史。
- 接入用户提供的 V3 Simple 本地 int8 静态 API 图，1536×1024、25 步、CFG1、Euler/simple、seed6200605。三视图只保留正侧背；四视图按用户确认保留四特写表情栏。没有新增模型或依赖。
- 一个角色、每布局一次：三视图 run `d2fde352`、四视图 run `3547aa4f` 均成功。PC 页面选主形象、两轮触发／回收／确认、独立草稿重载、历史载入通过；7 类错误请求被拒绝，最终 console 无错误、GPU leases 为空。
- 质量限制：四视图布局完整，但没有严格输出喜悦表情；没有用户质量验收、H3 下游验证或 canonical 晋升。证据：`experiments/sean_reference_workspace_phase2_20261003/manifest.json`、`QC.md`。操作权威仍为 README。

## C-20261003-03 | Breeze 声音工作台接入

- Owner: Sean。当前操作基线见 `reference-workspace/README.md` 声音节，模板 `catalog/breeze-voice.v1.json`。
- 本机 Breeze ComfyUI BF16/CUDA/SDPA/cuda_graphs，经工作台实际生成并回收中文三段系统试听，24kHz 单声道 WAV，3.92/3.84/4.24 秒；端到端约31秒，仅此短样例，不作为性能基线。
- 证据：`experiments/sean_reference_workspace_voice_20261003/manifest.json`、`QC.md`。PC播放器、音源导入/转写确认、历史/草稿恢复可用；没有人工声音质量验收，真实录音克隆及英文生成待实跑，样例保持未定稿。

## C-20261003-04 固定基础音色与预制模板（Owner: Sean）

用户纠正：人物音色固定，不同情绪只展现同一音质。当前声音模板改 v2：design/clone 各中性一段；reference 全部共享同一基础音源/逐字转写，并保留 anchor ID/hash；情绪结果不能定稿或再作为基础引用。12 声音模板、8 特征、5 试听题材。v1 hash/历史原图保留，旧三段设计载入提示迁移、直接 retry 拒绝。PC 1440×1000 与构建检查通过；只读构图 evidence experiments/sean_reference_workspace_voice_20261003/sean_voice_v2_workflow_review.json（submitted=false），不构成声音质量定论。本轮未新增生成、单元测试或改变用户版本；真实跨情绪音色与克隆质量待试听。远程任务 remote-1eae8efb-cdeb-416b-8bee-7daf781801af generation 2。
