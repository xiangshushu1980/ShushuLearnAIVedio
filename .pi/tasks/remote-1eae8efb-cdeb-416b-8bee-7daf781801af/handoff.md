# Reference 工作台三期：声音生成

Owner: Sean。2026-10-03。

## 控制权与范围

Task Center `remote-1eae8efb-cdeb-416b-8bee-7daf781801af`；执行 controller `01a0fd18-7207-77e2-8e7f-197e9421ef93`、generation 2。远程生命周期以 Coordinator 为准，续接先 info。

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

## 2026-10-03 generation 2：固定基础音色与快捷设计

用户要求人物音色一致，情绪只展现相同音质；新增声音特征与模板。任务 reopen/claim 后实现：v2 独立模板，design/clone 各一段中性基础样音，reference 情绪全部绑定一个 LoadAudio 与准确转写。基础候选定稿后可一键选入情绪试听，仍需用户听音确认转写；情绪结果 metadata 带 voiceRole/anchor，不可替换当前基础声音或再用作基础输入。12 预制模板、8 特征、5 台词题材，中英目录；只在设计阶段编写身份特征。

v1 文件/hash、旧历史与工作流保留。旧三段设计载入改为一段基础声音，并明确提示；旧三段直接 retry 拒绝。其余已知模板按原图构建。当前实体已有用户选定的版本 1（asset 47f47dc6-b855-4b62-82ee-fec79ace1704，2026-10-03 04:01 UTC），本轮未修改定稿、业务草稿、视觉状态或历史音频。

npm run build 成功；1440×1000 PC 页面无横向溢出/console error，模板与自定义、历史载入、当前基础音源选择和未确认禁用检查通过。只读工作流检查保存 experiments/sean_reference_workspace_voice_20261003/sean_voice_v2_workflow_review.json，明确 submitted=false / qualityEvaluated=false；三段同一音源/hash/转写，仅情绪要求不同。没有新增 TTS 生成、GPU 消耗或单元测试；音色质量仍需实际试听，不宣称已验证不漂移。仅在应用无活动 run 时重载 4188，ComfyUI 未重启；应用继续运行。
