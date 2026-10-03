# Reference 工作台二期交接

Owner: Sean。2026-10-03。

## 任务与授权

任务 `remote-36099f27-c228-4d8d-a84d-09deee97331e`，controller `01a0fd18-7207-77e2-8e7f-197e9421ef93`、generation 1。远程状态以 Task Center 为准，写回前重新查询。

用户已验收一期 `remote-47938b21-ae2e-4c9c-b3ba-12d6696b3375`，已通过 complete 记录。用户授权直接开发三／四视图，主形象直接选择概念图；只做 PC；四视图保留 V3 Simple 原版表情栏。

无重复网页实现任务。T-comfy-ops-48 是其他 controller 的 LoRA 效果研究，旧原生 ComfyUI 画布设计仍隔离；未修改它们。

## 实现

- `reference-workspace/server/store.mjs`：增量添加主形象版本、当前视觉状态、多视图草稿、视图确认记录。主形象源图与当前视图保护；换主形象解除旧图当前保护并自动锁定，清空当前视图，保留旧版本和输出。
- `catalog/qwen-multiview.v3-simple.json`：来源为用户指定 `experiments/qwen_image_2_1_civitai_character_sheet_20261002/source_workflow_v3/v3_simple_static_adapted_api.json`；保存源 hash、原始四视图提示词及无表情栏三视图变体。沿用本地 int8／标准 VAE decode 配置，没有新增依赖或模型。
- `src/VisualPanels.jsx`：主形象选择与多视图 PC 页面；多视图草稿独立保存，固定基础提示词＋选填补充要求，历史恢复，结果确认与锁定／解锁／删除。概念图保留旧流程，并提供“设为主形象”。
- 多视图 run 保存 stage／layout／appearance ID、版本、源资产 hash；只使用已确认主形象，拒绝过期版本。复用一期 GPU lease、进度、回收、重启恢复；完整图 hash 防止历史模板静默替换。
- 运行与接口权威说明：`reference-workspace/README.md`。

## 证据与恢复

`experiments/sean_reference_workspace_phase2_20261003/manifest.json`、`QC.md`，两次真实运行与提交图 JSON、七类 API 拒绝边界及视觉来源状态。

三视图 run `d2fde352-9a1b-4c8b-83ef-766e73972e6b`；原版表情栏 run `3547aa4f-9e72-4c7c-9694-3b74e2a733d5`。均成功；主形象版本 1 来自一期概念图。样例确认操作保存视图版本 1／2，当前为四视图；开发者操作不代表用户质量验收。

默认服务 `127.0.0.1:4188`，样例 `?entity=5821d6dd-2041-40a3-a789-74989c6edd90`。完整数据备份 `reference-workspace/.data`。最终构建成功、PC console 0 errors、GPU leases 为空，未重启 ComfyUI；本批 output 已回收清理。图片、截图、SQLite、dist、依赖留本机，源码／模板／元数据／文档 scoped 提交；不混合推送已有 main 的其他任务提交。

限制：一角色每布局一轮；四视图喜悦表情没有严格生成，需用户挑选；未做 H3 下游或 canonical 验收，声音／管理页／手机未实现。

## 2026-10-03 用户追加：脸部＋正背侧与风格

Owner: Sean。用户要求新增“脸部＋front＋back＋size”，已确认 size 指 side。任务 reopen／claim 后本会话 generation 2 继续执行，四表情原版仍保留。

- 增加 `face-front-back-side` 布局：左侧一张中性脸部特写，右侧正面／背面／侧面全身。独立 `qwen-multiview.v3-simple-face.json` 从 V3 Simple 的本地图派生；旧模板保持内容/hash，旧 run 兼容结果为 true。
- 概念图和多视图同用八种风格，新增摄影写实、日系动画、3D 动画、水彩和水墨。保留已有三个风格快照对象；original 在多视图显示“原图风格”。非 original 多视图替换“严格匹配原图画风”要求，保留服装装备约束，并追加风格词。
- 多视图草稿和生成接口接收 styleId，旧草稿默认 original；历史恢复原风格，结果/历史显示运行时风格。选项与固定提示词均由服务端提供。
- 构建成功；1440px PC 手动页面检查无横向溢出、console 0 errors/warnings，新增布局＋anime 保存与重载正常，原四视图历史恢复 four/original。截图 `sean_face_style_pc.png` 留本机（忽略）。样例草稿目前是 face-front-back-side/anime，先前已确认视图仍保持。
- 这次未增加生成，未运行/新增单元测试。新增布局和风格效果未实跑；只更新工作台服务 4188，未操作 ComfyUI。详细证据见 `sean_layout_style_review.md`。
