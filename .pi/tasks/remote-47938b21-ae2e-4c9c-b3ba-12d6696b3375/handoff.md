# Reference 工作台一期实现交接

Owner: Sean。更新：2026-10-03。

任务：`remote-47938b21-ae2e-4c9c-b3ba-12d6696b3375`。上游：`remote-3d1bfef4-93c7-4b19-93e8-1090a7405e04`。远程生命周期以 Task Center 为准，本文件只保存恢复上下文。

## 范围与冲突

用户明确要求查交接、查冲突、新建实现任务并开始实现；首阶段仅设定图片和概念图。远程列表没有重复代码实现任务。旧 `remote-c1320849-4f64-4781-9929-c7922a9d1ae5` 是 ComfyUI 原生画布方向的设计任务，仍 running/handoffReady；未修改它或 `docs/47`。独立应用架构按已验收 docs/49，产品细节按新的设计交接，不继承固定双图/Krea/主形象再次生图等旧假设。

初次实现为 generation 1；用户反馈后已 reopen 并重新 claim，controller `01a0fd18-7207-77e2-8e7f-197e9421ef93`、generation 2。写回前仍须重新查询当前 controller。

## 已落盘实现

- `reference-workspace/`：React 19.3 + Vite 8.3.2、Node 24 API、SQLite/独立图片目录、两面板 UI、能力 schema、版本化模板与草稿、不可变运行快照、真实 ComfyUI 适配器、状态/进度、一次性音效/glow、历史自动锁定/解锁/删除、来源墓碑、重试、运行重启恢复、GPU lease/观测。
- 首选 Qwen Image 2.1：用户提供了 `experiments/qwen_image_2_1_civitai_character_sheet_20261002` 与 `experiments/qwen_image_2_1_staged_character_reference_20261002` 的脚本与工作流；本期引用其本地配置，不使用 Qwen Image 3 Partner API。
- 运行说明：`reference-workspace/README.md`。证据：`experiments/sean_reference_workspace_phase1_20261002/manifest.json`、`QC.md`；ledger：`.pi/ledger/reference-workspace.md`。

## 验证与恢复

- `npm run build` 成功，`npm test` 7/7。
- 浏览器导入四张图片；三次 Qwen 生成成功。第二轮直接引用第一轮历史。第三轮重复 body/key 只产生一个 run，并在 running 状态重启 API 后恢复同一 prompt ID。
- 桌面/390px 手机检查、最终 console 0 errors；未知模型/参数/重复图 400、跨 Origin 403、过期草稿/锁定删除 409。
- 默认启动 `cd reference-workspace && npm ci && npm run build && npm start`，监听 `127.0.0.1:4188`。当前本地数据在 `reference-workspace/.data/`，完整备份该目录。
- 验收样例入口：`http://127.0.0.1:4188/?entity=5821d6dd-2041-40a3-a789-74989c6edd90`。默认“参考实体”为空白，新建实体 API 已提供，管理 UI 尚未实现。
- 没有启动/重启 ComfyUI；真实生成结束后 GPU lease 均释放，本批 output 已回收并清理。

## 交付边界

### Generation 2 用户反馈调整

- 所有本轮 ref 改为同尺寸网格，无主图；素材库移入“添加引用”窗口，确认后应用，取消不修改草稿。生成结果独立显示，按用户选择保留大图。设定图片点击只放大，不混入结果预览。
- 补充 Image 编号和逐图职责说明。验收样例之前保存的是“引用整张已合成人物图”的第二轮提示词，不是通用默认；新草稿仍为空，不改写已有文字。
- 点击历史卡片/缩略图恢复全部输入与来源 run ID，显示原始提交图，结果区切换该历史输出。历史固定模板/模型/风格变化时阻止静默替换；最初两条无模板 hash 的记录通过完整提交图比对兼容。
- `npm run build` 成功；浏览器四图恢复为同尺寸，1536×1024 / seed 42 / steps 25，完整图中四条 images 输入，取消选择保持 4 图、确认应用为 3 图，390px 无横向溢出，console 0 errors。证据见 `experiments/sean_reference_workspace_phase1_20261002/sean_review_20261003.md`。本轮未新增 GPU 生成或运行单元测试。
- 用户要求的三点调整在原实现任务内交付，未创建重复任务；仍只实现设定图片和概念图。

主形象/三视图/声音和实体管理 UI 留后续，当前没有内嵌 Agent。Qwen 16 图声明来自节点，实跑只覆盖 4 图与历史单图；Krea 备选没有实跑。本次运行原生 ComfyUI 深链未验证，只提供实际提交图与 ID。

PNG、截图、SQLite、依赖和 dist 留本机；manifest/输入快照/提交图、应用源码、测试与说明做 scoped commit。远端 main 之前已积累其他任务的未推送提交，本期不混合推送。
