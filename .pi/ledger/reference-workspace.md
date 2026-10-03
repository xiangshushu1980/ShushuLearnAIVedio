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

## C-20261003-05 声音页顺序与选用标记（Owner: Sean）

按用户指定重排 0 当前声音与关联情绪、1 模板/上传创建、2 当前声音确认后的情绪设置、3 历史选择。基础声音从历史选用，条目与样音标黄色；版本/上传源折叠。情绪引用已确认当前声音，UI/API 拒绝其他音源，顶部仅当前 anchor 的最新结果。构建和1440px PC检查通过，无新生成/单元测试，不构成声音质量定论。task remote-1eae8efb-cdeb-416b-8bee-7daf781801af generation3。

## C-20261003-06 Reference只读导出API v1（Owner: Sean）

四端点在/api/reference/v1：entities列表、POST manifests创建、GET manifests/:manifestId读取、GET assets/:assetId/content下载。现有实体/资产UUID、内容hash、run提示词和主形象/多视图/声音真实确认映射；无关系/音效/审核/独立提示词版本，nullable说明与capabilities如实声明。默认仅真实确认，locked不作为确认；角色/assetIds限定选中实体，无图谱扩展。独立manifest表+不可变触发器；原素材不复制，删除后下载404，下游须及时保存字节。保留本机访问边界，无绝对路径/密钥或任意读文件；Range/MIME/字段错误。5新测试+7现有共12通过、构建成功、实际HTTP/schema/快照重读/音频Range206成功；无ComfyUI操作。契约reference-workspace/docs/reference-export-v1.md；交付上下文.pi/tasks/reference-export-v1/handoff.md、validation.json。只读接口用户明确授权，未立项新远程任务；不改实体管理/生成流程。

## 2026-10-03 实体浏览、两类关系与独立派生 v1

Owner: Sean。新增 PC 三栏管理页、名称/描述/flag 搜索、全部/任一 flag 筛选、新建和资料编辑、当前主形象/多视图及声音预览；设定/剧情关系共用新增 entity_relations，入向只读、来源可编辑/软解除。派生建立独立实体与来源修订，新主形象/多视图不自动确认；声音可复制原字节为独立已选版本，真实原 run 为来源，无虚假生成。创作页可引用其他实体图片，并显式指定关系或仅作引用。新增表为增量建表，原生成/确认流程沿用。

基础引用变化提醒后续实现；当前记录 sourceEntityId/sourceAssetId/sourceHash/sourceRevision、派生base_revision及关系targetRevision，不自动传播。只读v1导出新增可选flag/派生来源/继承素材溯源及direct有效关系，旧持久化manifest不变。缺口包括单值type、音效、审核、独立提示词版本。构建/隔离1440×1000 PC操作/接口手动复核通过；未运行单元测试或生成，生产角色资料与定稿未修改。入口 http://127.0.0.1:4188/?view=manage；权威说明 reference-workspace/docs/entity-management-v1.md，证据 .pi/tasks/entity-management-v1/validation.json。

## 2026-10-03 场景固定空间 v1

Owner: Sean。新增 scene_spatial_versions 不可变版本及状态指针，方向基准、稳定空间锚点、固定关系、通路、待补充与参考图绑定；管理/创作复用编辑器，JSON草稿批量导入减小手工填写。整份图文一致确认与单项known/pending分开；依据变化needs_review，固定事实导出暂停，动态字段严格拒绝但自然语言仍需人工核对。既有v1manifest增加可选sceneSpatial，旧快照不变；来源hash包含空间修订；film-editor inventory/exportedFacts已原样保留扩展，无下游改动。

当前图书馆仅外观短句和单张已选参考图。实际看图后另存空间草稿（阅读区/两侧书架/两桌/右侧边界待确认）；原文字/图片/定稿选择未改，生产草稿未代用户确认；入口、精确尺寸/朝向/通路明确待补充。构建/隔离PC及HTTP/schema手动复核通过，无单元测试/LLM/GPU/ComfyUI操作。权威文档 reference-workspace/docs/scene-spatial-v1.md，证据 .pi/tasks/scene-spatial-v1/validation.json。
