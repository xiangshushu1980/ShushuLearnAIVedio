# Reference 工作台三期：声音生成

Owner: Sean。2026-10-03。

## 控制权与范围

Task Center `remote-1eae8efb-cdeb-416b-8bee-7daf781801af`；执行 controller `01a0fd18-7207-77e2-8e7f-197e9421ef93`、generation 1。远程生命周期以 Coordinator 为准，续接先 info。

用户授权进入声音阶段，沿用此前分阶段立项授权。检查远程无重复声音实现；旧原生 ComfyUI 画布、界面设计、多视图 LoRA 研究隔离，未修改。二期 remote-36099f27-c228-4d8d-a84d-09deee97331e 仍等待验收。

PC only，声音与视觉状态独立。Breeze TTS 既有 ComfyUI 节点固定工作流；声音设计、音源＋准确转写及可选引导，系统台词多段试听、下载、历史、输入草稿、定稿版本保护/换版。首版人工转写确认；BGM、环境音、手机、实体管理和 H3 下游留后续。

## 代码与数据

- catalog/breeze-voice.v1.json：模型/采样图、日常/剧情/旁白、中文/英文、基础一句或三段情绪试听。
- server/voice.mjs：严格输入校验、不可变快照、模板 hash、工作流构建、历史兼容。
- server/store.mjs：音源识别/时长校验/统一 WAV、增量声音草稿及版本表、当前声音保护、换版保留。
- adapters/runs/index：复用执行、GPU lease、进度、重启恢复和受控输出回收；专用声音端点，音频与图像输入分离。
- src/VoicePanel.jsx：独立声音页面，试听、下载、转写确认、历史与定稿；main.jsx 侧栏入口和阶段过滤。
- 当前基线与 API：reference-workspace/README.md。

## 证据与服务

样例实体 5821d6dd-2041-40a3-a789-74989c6edd90，URL `http://127.0.0.1:4188/?entity=5821d6dd-2041-40a3-a789-74989c6edd90`，进入声音步骤。

run `698812b4-38b6-4c12-b91a-0877b23955f4` 成功回收三段声音 3.92/3.84/4.24 秒，未定稿。输入、提交图、WAV、QC 在 experiments/sean_reference_workspace_voice_20261003；截图 sean_voice_pc.png 留本任务目录本机。音源导入/转写确认及后端拒绝、历史/草稿恢复通过 PC 检查；模型节点可运行。

应用4188继续运行，仅重载本应用，ComfyUI8188未重启。GPU租约已释放，本批 output 已回收。源码/模板/元数据/文档 scoped 提交；图片、WAV、SQLite、dist和依赖留本机。main 混有其他任务提交，不混合推送。

限制：没有人工声音质量验收；真实录音克隆/引导、英文尚未实跑；开发者没有替用户确认当前声音。当前保护与换版实现已接入，仍需用户选样音。未新增/运行单元测试。
