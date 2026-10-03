# Reference 工作台 · 图片与声音

Owner: Sean。独立 React + Vite 8 应用，自己的 Node API、SQLite 数据库与图片存储。

一期**设定图片**和**概念图**已获用户验收；二期实现**主形象选择**和**三／四视图**；三期接入**声音生成、试听与定稿**。产品依据是[设计交接](../.pi/tasks/remote-3d1bfef4-93c7-4b19-93e8-1090a7405e04/handoff.md)和[已确认设计说明](../docs/design/sean_h3_reference_workspace_design_v1.md)；部署边界见[架构](../docs/49_h3_reference_workspace_architecture.md)。实体管理界面留后续。

2026-10-03 用户确认先跑通 PC 网页；当前验收与后续迭代仅针对 PC，手机端适配和检查暂缓。

## 启动

本机 Node 24.18.0；最低 Node 24。SQLite 使用 Node 自带的 `node:sqlite`，前后端由一个进程在同一端口提供。Vite 8 的 Node 要求及 SQLite API 分别参见 [Vite 文档](https://vite.dev/guide/)和 [Node SQLite 文档](https://nodejs.org/docs/latest-v24.x/api/sqlite.html)。

```bash
cd /home/sean/projects/comfy-ops/reference-workspace
npm ci
npm run build
npm start
```

打开 `http://127.0.0.1:4188`。开发模式用 `npm run dev`，Vite 以 middleware 模式接入同一服务。端口被占用时启动失败，不自动改端口。

| 环境变量 | 默认值 | 用途 |
| --- | --- | --- |
| `REFERENCE_PORT` | `4188` | 工作台监听端口，仅绑定 `127.0.0.1` |
| `REFERENCE_DATA_DIR` | 应用目录的 `.data` | SQLite 与原始图片；备份时保留整个目录 |
| `REFERENCE_COMFY_URL` | `http://127.0.0.1:8188` | 既有 ComfyUI 单实例地址 |
| `REFERENCE_COMFY_OUTPUT` | `/home/sean/projects/ComfyUI/output` | 回收完成后清理本应用本次运行输出的受控根目录 |

生成还需要当前宿主提供 `hive-resource` CLI 与运行中的资源中心。应用申请 `gpu:0` 租约、续租、采样显存并记录观测，完成或失败后释放；若共享 ComfyUI 队列已有任务，拒绝新增本地生成并提供失败记录。工作台不启动或重启 ComfyUI。

`.data/`、构建目录、依赖和 `.env` 都不提交。数据库和原始图片是工作台业务数据；ComfyUI output 只作回收前的临时落点。生产数据须定期备份。该版本用于本机单用户操作。

## 操作

1. 设定图片：用文件选择器从当前目录多选 PNG、JPEG 或 WebP；可取消部分选择，再“加入设定图片”。一次最多 16 张，每张最多 25 MB。该面板不包含模型、提示词、生成或备注编辑。
2. 概念图：通过“添加引用”窗口从设定图片和历史结果中明确选择图片，再确认使用。本轮引用只有一组同尺寸卡片，没有主图；所选顺序对应 Image 1、Image 2…，可调整顺序。生成结果在独立区域显示大图。没有选中的图片不会进入运行。
3. 填写本轮提示词、选填目的，选择已保存风格和模型参数。“保存本轮输入”保留草稿；“开始生成”另建不可变输入快照。
4. 查看状态、采样进度和回收后的原图。完成或失败触发一次短提示音和 glow；导入图片不触发。提示音可关闭。
5. 新概念图自动锁定进入历史，可直接选入下一轮。明确解锁后可删除；历史运行引用过的图片需再次确认。删除后原文件移除，但原资产 ID、hash、输入快照和“来源图已删除”状态仍保留。运行中的引用及当前主形象来源受保护。
6. 点击生成历史记录或其缩略图，载入该次工作流、提示词、目的、ref 顺序、模型、风格和参数，结果区切换到对应历史输出。未保存输入被替换前需确认。可查看历史原始提交图；继续调整输入后运行会创建新记录。载入操作不会提交生成。

新草稿提示词为空。Image 1 只指第一张已选图；脸、服装、装备和武器若来自不同素材，提示词需逐图说明职责。若只引用已合成的人物概念图，那张图才可能同时提供这些信息。已有草稿和历史提示词原样恢复，不自动改写。

历史载入使用 `sourceRunId` 保留来源，重新生成前校验固定模板版本与内容。早期没有模板 hash 的记录，必须将其完整提交图与按当前模板重建的原输入图逐节点比对；不匹配时阻止直接运行，可明确“改用当前配置”后重新检查输入。被删除的历史 ref 显示来源缺失，移除或替换后才能运行。

界面不内嵌 Agent。外部 Agent 可以读取实体上下文和本轮草稿，提供供用户复制、复核的目的和提示词；自动刷新不覆盖正在编辑的文本。草稿保存使用时间戳比较，另一页面修改过的草稿会产生冲突提示。

## 模型与固定模板

### 选定主形象与多视图

概念图结果可直接“设为主形象”，也可在主形象面板挑选；不另行生成主形象。每次更换建立不可变主形象版本，保存源图 ID/hash 和概念 run。当前源图锁定、受保护；旧版保留，源图自动锁定并带“曾定稿”标记，可明确解锁后按历史删除规则处理。

多视图有独立草稿和生成历史，仅引用已选定的主形象。布局可选：

| 布局 | 提示词与结果 |
| --- | --- |
| 三视图 | 正面／侧面／背面三个等比例全身视角，沿用 V3 Simple 的画风与一致性约束 |
| 四视图 | 按用户确认保留 V3 Simple 原版：左侧中性／喜／怒／哀四个特写，右侧正／侧／背 |
| 脸部＋正背侧 | 左侧一张中性脸部特写；右侧依次为正面／背面／侧面三个等比例全身视角，不含表情栏 |

固定基础提示词可展开查看；补充要求单独追加。沿用用户提供 `experiments/qwen_image_2_1_civitai_character_sheet_20261002/source_workflow_v3/v3_simple_static_adapted_api.json` 的本地 int8 配置，25 步、CFG 1、Euler/simple、1536×1024，默认 seed 6200605。工作台模板 `catalog/qwen-multiview.v3-simple.json` 保存来源 hash 与两种布局提示词；没有接入自动提示词增强或新增模型依赖。这是已有本地适配，不等同于上游 BF16 / DeGrid / 更高分辨率全配置。

新增脸部布局使用独立模板 `catalog/qwen-multiview.v3-simple-face.json`：沿用同一 V3 Simple 本地模型与采样图，布局提示词由 Sean 调整；原三／四视图模板及 hash 保留，旧历史可继续载入。2026-10-03 用户确认此前的 `size` 指 `side`（侧面）。新增布局尚未实跑生图。

概念图和多视图均可选择生成风格：原图风格、电影感写实、概念设定、摄影写实、日系动画、3D 动画、水彩插画、水墨插画。多视图默认“原图风格”，保持原版提示词；其他风格将严格匹配原图画风的要求改为统一使用所选绘制风格，同时保留身份、比例、服装、颜色及装备约束。风格词由服务端追加，不增加参考图片、模型或 LoRA。各风格的生成效果需实际选图确认。

生成时保存确切主形象版本、源图 hash、布局、风格、完整提示词、参数和提交图；输出自动锁定。点击历史记录载入原输入、风格和工作流，旧主形象的结果会显示其来源版本；主形象已更换时须明确“引用当前主形象”后才能开始新一轮。旧多视图草稿没有 styleId 时按 original 恢复。

合成图作为一项完整结果，可“设为当前视图”。确认记录独立版本；换图后旧结果自动锁定。更换主形象会清空当前视图指针，旧输出和确认记录均保留，需为新主形象生成或选择对应视图。概念图生成、主形象选择、视图确认三个操作保持独立。

二期仅对 PC 做浏览器与真实运行检查。两次实跑分别成功输出三视图、原版表情栏合成图；**这次四视图没有严格给出喜悦表情**，布局成功不代表每种表情或身份细节已获质量验收。结果由用户挑选；没有 H3 下游验证或 canonical 晋升。证据见[二期记录](../experiments/sean_reference_workspace_phase2_20261003/QC.md)。

### 概念图模型

首选 **Qwen Image 2.1 本地工作流**，使用用户提供且已生成过的 CivitAI / 分阶段人物实验配置。`catalog/qwen-concept.v1.json` 保存独立、无实体提示词的固定基础图；服务只映射本轮提示词、实际引用、尺寸、seed、steps 和输出前缀。

| 内容 | 当前配置 |
| --- | --- |
| DiT | `qwen_image_2.1_int8_convrot.safetensors` |
| 文本编码器 | `qwen3vl_8b_int8_convrot.safetensors`，`qwen_image` |
| VAE | `qwen_image_2.1_vae_bf16.safetensors` |
| 节点 | `QwenImage21Cache` + `TextEncodeQwenImage21` |
| 默认采样 | 1536×1024，25 步，CFG 1，Euler/simple，seed 42 |
| 引用映射 | `images.image_1`…`images.image_16`；只建立已选图的 LoadImage 节点 |
| 能力证据 | 本机 TextEncode 节点声明 0–16 张；一期端到端实跑覆盖四张设定图及一张历史图，未声称测过 16 张质量 |

Krea 2 文本与 Edit 作为备选工作流保留，能力上限分别是 0 张、1–2 张。Krea 的参考一致性仍需用户评审；本期真实生成验收使用 Qwen。已保存风格位于 `catalog/profiles.json`，概念图与多视图使用同一份风格目录；不自动加入风格参考图片或 LoRA。概念图的 original 表示按用户提示词生成，不追加风格词。

模型能力与参数由后端目录提供，前端展示同一份 schema。每条运行记录保存模型/风格/模板版本、模板内容 hash、原始与生效提示词、目的、参数、实体上下文、实际输入图片 ID/hash，以及提交时的完整工作流。

## 运行恢复与接口

### 声音生成与试听

声音可独立于主形象与多视图开始；共享 GPU 同时只执行受租约保护的生成。使用已安装的 Breeze TTS 2 节点，沿用[本机标准流程](../docs/breeze-tts-standard.md)：BF16、CUDA、SDPA、cuda_graphs，不自动下载模型。当前固定模板为 `catalog/breeze-voice.v2.json`；v1 原文件及历史提交图保留。

| 步骤 | 输入与结果 |
| --- | --- |
| 设计基础音色（design） | 选择预制模板、微调特征、选填补充描述；只生成一段中性样音 |
| 导入音源建立基础样音（clone） | 单人音源、准确转写、听音确认；只生成一段中性基础样音 |
| 固定音色情绪试听（reference） | 明确选择同一基础样音与准确转写；一种或三种情绪共用该音源 |

提供 12 个声音预制模板及声音性别、年龄感、音高、音质、共鸣、基础语速、吐字、气质 8 类特征。一键填入后可微调，改变任意特征即切换为自定义；最终组合描述可展开查看，后端按同一目录编写并快照保存。模板用于设计基础音色，不在情绪阶段重新定义音色。

选定人物基础音色后可点击“用当前基础音色做情绪试听”。全部情绪 Speaker 连接同一个 LoadAudio、使用同一准确转写；只追加保持身份和音色的约束及系统情绪表达要求。每次快照和结果保存基础音源 ID、hash、转写。不会因为当前定稿后来更换而悄悄切换历史所选音源。情绪输出不允许设为人物基础声音，也不能充当新一轮基础参考。

日常、剧情、旁白、冒险与决心、关心与安慰共 5 组中文／英文系统台词；不编辑台词。设计默认 CFG 1.5，音源模式初选 CFG 1；种子与 CFG 可调整。实际音色一致性仍需听音确认，固定引用只保证输入一致，不代表模型效果已验收。

导入支持 WAV、FLAC、MP3，最大 25 MB、30 秒，经 ffprobe/ffmpeg 校验并统一为 24kHz 单声道 PCM WAV。本阶段人工准确转写；修改音源或转写会清除确认，后端拒绝未确认生成。

候选自动锁定。基础候选可“设为人物基础音色”，建立独立版本并保护当前音频；换版保留旧版并锁定。声音定稿不改变视觉状态。音源删除、历史墓碑与运行中引用保护沿用原机制。

草稿独立保存并使用 expectedUpdatedAt 防止覆盖。历史恢复特征、模板、描述、音源、准确转写、确认、语言、范围及参数；原始工作流可查看。旧版文字设计三段输入载入后明确转为一段基础样音，旧版三段直接重试被拒绝，提示先生成基础声音再固定音源试听。当前模板后续发生未知 hash 变化仍阻止直接运行。

首轮 v1 已实际生成中文三段并回收播放。2026-10-03 v2 迭代通过构建、1440px PC 页面和只读工作流检查：12 模板填入/特征自定义、历史恢复、当前基础音源选择、未确认禁用生成、三段相同 LoadAudio 与转写；没有新增生成或单元测试。用户当前选定的基础声音及业务草稿保持原样。v2 情绪实际生成质量、真实录音克隆及英文仍待试听验证；证据见[声音 QC](../experiments/sean_reference_workspace_voice_20261003/QC.md)和 `sean_voice_v2_workflow_review.json`。BGM、环境音、H3 下游和手机不在范围。

保存 `prompt_id` 后重启工作台，会恢复观察同一次 ComfyUI 执行，并续接本 run 的资源租约。提交与保存 ID 之间出现崩溃或传输错误时，标记“提交结果未知”，由用户核对队列与历史后显式决定是否重试；不自动重复提交。失败重试产生新 run，原 run 保留。只能取消尚在队列的本次运行，不能使用共享实例的全局中断。

目前提供“查看本次提交工作流”与原始 `prompt_id`。ComfyUI 原生 UI 的同次运行深链尚未验证，界面没有把普通首页链接标成“本次运行详情”。

| 接口 | 用途 |
| --- | --- |
| `GET /api/catalog` | 模型能力、参数、已保存风格 |
| `GET /api/entities` | 已有实体 |
| `POST /api/entities` | 后续管理页/外部工具创建实体：`{name, context}` |
| `GET /api/entities/:id/workspace` | 只读实体上下文、图片、草稿、运行历史 |
| `PUT /api/entities/:id/draft` | 保存 `{value, expectedUpdatedAt}` 草稿，避免静默覆盖 |
| `POST /api/entities/:id/settings` | multipart `images` 多选导入 |
| `POST /api/entities/:id/appearance` | `{assetId, expectedAppearanceId}` 选定主形象；初次 expected=null |
| `PUT /api/entities/:id/multiview/draft` | 独立的多视图草稿，使用 expectedUpdatedAt 防止覆盖 |
| `POST /api/entities/:id/multiview/runs` | `{layout, styleId?, appearanceId, parameters, purpose, notes, sourceRunId?}`；layout=three/four/face-front-back-side，styleId 默认 original，带 Idempotency-Key |
| `POST /api/entities/:id/multiview/confirm` | `{assetId, expectedAppearanceId}` 确认当前版本的视图 |
| `POST /api/entities/:id/voice/sources` | multipart `audio` 导入参考音源 |
| `PUT /api/entities/:id/voice/draft` | `{value, expectedUpdatedAt}` 保存独立声音草稿 |
| `POST /api/entities/:id/voice/runs` | 声音输入、系统试听模板与参数，带 Idempotency-Key |
| `POST /api/entities/:id/voice/confirm` | `{assetId, expectedVoiceId}` 选定当前声音；首次 expected=null |
| `POST /api/entities/:id/runs` | 运行输入；必须带 `Idempotency-Key` |
| `GET /api/runs/:id` | 执行状态、实际输入与输出 |
| `GET /api/runs/:id/input` | 历史完整输入、原始提交图及当前配置兼容结果 |
| `GET /api/runs/:id/workflow` | 完整本次提交图 |
| `POST /api/runs/:id/retry` | 显式新建重试；必须带 `Idempotency-Key` |
| `POST /api/runs/:id/cancel` | 仅取消该 run 的排队项 |
| `PATCH /api/assets/:id/lock` | `{locked}` 显式锁定/解锁历史 |
| `DELETE /api/assets/:id` | `{confirmUsed}` 删除图片并保留来源墓碑 |

新库先提供“参考实体”以便打开创作页面；实体创建、介绍和关系管理界面未纳入一期。可用 `?entity=<id>` 进入特定实体。

已有数据库启动时添加主形象版本、视图确认、当前视觉状态及多视图草稿表，保留原实体、概念草稿、运行与文件。`workspace` 响应提供 `visualState` 和 `multiviewDraft`；SQLite 及原图仍以整个 `.data` 目录为备份单位。

声音阶段增量添加 voice_drafts、voice_versions、entity_voice_state；`workspace` 同时提供 voiceDraft、voiceState。音频复用资产与运行表，以 mediaType=audio 表示，尺寸字段为 0，metadata 保存时长、采样率、单声道与原文件 hash。备份整个 `.data` 同时包含图片、音频和数据库。

## 验证

```bash
npm test
npm run build
```

七项测试覆盖显式引用顺序/数量、模型参数、模板 hash、保护与解锁删除、来源墓碑、事务、跨实体拒绝和提交幂等性。浏览器检查覆盖多选导入、实际图片预览、草稿重载、桌面/390px 手机视图。真实 Qwen 三轮生成和进行中重启恢复证据见 [一期 manifest](../experiments/sean_reference_workspace_phase1_20261002/manifest.json)，结论及限制见 [QC](../experiments/sean_reference_workspace_phase1_20261002/QC.md)。

2026-10-03 布局与历史载入调整的构建、页面检查见[复核记录](../experiments/sean_reference_workspace_phase1_20261002/sean_review_20261003.md)。本轮没有新增生成或运行单元测试。
