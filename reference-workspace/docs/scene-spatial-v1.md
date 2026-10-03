# 场景固定空间设定 v1

Owner: Sean。2026-10-03。用于多段独立视频共享同一场景空间；不包含拍摄本的角色动态状态。本期只修改 Reference，未运行生图/视频/LLM。

## 评估与最小结构

之前实体仅有 name/context 中的介绍、外观和生成提示词；这些文字可以说明画面风格，不能可靠指定跨镜头位置、方向、路径。当前“图书馆”的外观仅“现代图书馆，明窗净几，装修简洁”，已选参考图可见书架和阅读桌，没有完整平面图、入口或尺寸依据。

新增独立空间 document，不改现有实体 profile，不把历史图片提示词自动当空间事实。普通创建仍先保存实体、加“场景” flag、导入/生成图片；实体管理与创建页共用“场景空间设定”编辑器。

| 字段 | 内容 |
| --- | --- |
| owner / schemaVersion / scope | Sean / 1 / fixed_scene_space |
| frame | 方向基准 description；known/pending |
| elements | 区域 area、建筑结构 structure、固定物体 object；稳定 id、label、description、position、orientation、scale、known/pending |
| links | 稳定 id、from/to 锚点 ID、固定空间关系 description、known/pending |
| routes | 稳定 id、label、按顺序的 via 锚点 ID、固定通路 description、known/pending |
| unknowns | 无依据、冲突、不可见范围等待补充项 |
| referenceAssetIds | 本实体的明确核对图片 ID |

推荐通过“与助手讨论空间布局”选图、说明用途，由 Agent 整理有来源的锚点与空间提案，再由用户应用和确认，详见 [Agent 接入手册](agent-integration-v1.md)。模型调用只由用户发送触发，未知布局不会静默变为事实。原表单改为“手工精修”：填写方向基准、锚点名称和说明，其余折叠为选填；也可粘贴 JSON 草稿。没有依据的部分保持空/pending，不补米制尺寸或隐蔽房间。

方向必须基于固定锚点定义，例如“从某桌朝某墙方向为前向，某书架侧为左”；换镜头后仍使用该基准。截图的屏幕左/右、背面未见、地理朝向不能当空间事实。description 与 position/orientation/scale 应一致；后者留空时只能使用文字已明确说明的内容，不推断精确值。

## 稳定引用与动态状态边界

界面自动生成 ID，改名保留 ID，删除不重排其余 ID。导入草稿时必须保留已有对象原 ID。跨实体完整引用为 `entityId#id`；派生场景可沿用局部 id，新的 entityId 区分独立空间。历史版本不改写。

links 的两端和 routes.via 必须引用真实锚点；known 关系/通路不得依赖 pending 锚点。删除锚点须明确确认，并移除依赖它的本轮关系/通路。时间线、actorPositions、角色当前朝向、物品转移等未定义字段会被严格 schema 拒绝；自然语言仍需人工核对，不声称能自动判断所有动态描述。

拍摄本应使用锚点确定角色站位、身体/视线朝向、交互目标、沿哪条通路移动，并为每段镜头保存开始/结束状态与跨段转移。空间实体只定义可用位置、建筑、默认固定布置和可通行连接，不将一次镜头中的演员位置或移走的杯子永久写回。

## 保存、核对、变化

“保存空间草稿”立即持久化一个新版本；known 代表该项已有依据，**不等于整份空间已确认**。修改任何空间内容后须重新确认。确认条件：已保存、方向基准 known、至少一个 known 锚点、至少一张真实本实体参考图（已有主形象必须纳入当前主形象），以及用户勾选“已对照参考图与实体文字、一致且未固化动态状态”。确认检查当前版本/hash、图片存在/归属/内容 hash，并记录确认时间与图/文字基准哈希。确认人未做登录身份认证，owner=Sean 不冒充审核人员身份。

这项确认是用户核对记录，不是自动图像语义验证。冲突内容改为 pending/unknowns 或修改草稿；不可确认的信息继续阻止其作为已知事实使用。

参考图删除、内容改变、更换当前主形象/视图、实体 description/appearance 改变后，状态为 needs_review；固定事实数组和 promptContext 置空，仍保留原版本与待补充信息。须重新核对明确确认。编辑页不会因轮询覆盖未保存文字；过期版本或核对哈希提交409，旧页面不得直接确认新资料。

新增 scene_spatial_versions、entity_spatial_state；空间版本不可 update/delete，指针选定最新保存版本。数据库和素材仍整体备份 `.data`。版本哈希使用与导出相同的 canonicalJSON/SHA-256。派生复制资料时复制空间为待确认草稿，清除确认；仅映射实际复制的参考图，避免沿用基础场景确认。已选图片/声音/生成流程不改造。

## 接口

沿用本机 Host/Origin/loopback 限制。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | /api/manage/entities/:id/spatial | document、summary、expectedVersionId、evidenceStateHash |
| PUT | /api/manage/entities/:id/spatial | {expectedVersionId:null或UUID,document}，保存新草稿版本 |
| POST | /api/manage/entities/:id/spatial/confirm | {expectedVersionId,expectedContentHash,expectedEvidenceStateHash,acknowledgeConsistency:true} |

400 返回 details.fieldErrors 点路径，包括坏字段、重复 ID、悬空锚点、外实体/音频参考图；未知实体/素材404，过期版本/依据哈希409。scope 固定，不接受任意 metadata 或文件路径。

## 导出与短片提示词流程

现有 POST `/api/reference/v1/manifests` 无需修改请求，实体增加可选 `sceneSpatial`。外层 schemaVersion 仍为1，空间结构自身 schemaVersion=1。旧已存 manifest 原样重读；旧实体不迁移文字、不自动解析提示词，场景没有空间资料则返回 missing，missingFields 含 sceneSpatial。其他既有资料仍可导出。

sceneSpatial 包含 status（missing/draft/confirmed/needs_review）、version/versionId、contentHash/sourceRevision、confirmedAt、frame、elements、links、routes、unknowns、issues、referenceImages（assetId/hash/available）、promptContext、draft、usage。

- 仅 status=confirmed 的 known 项进入 frame/elements/links/routes 与 promptContext。pending 总是作为待补充，不作为固定事实。
- includeUnconfirmed=false：draft=null，仍有状态/哈希/待补充/依据信息；不阻塞其他素材导出。
- includeUnconfirmed=true：另带完整草稿 document，但未确认/待复核内容仍不会进入固定事实或 promptContext。
- referenceImages 仅为核对依据 ID/hash；不越过 assetIds/assetRoles 自动增加图片下载。下游若需这些图，应明确选择相应素材，核对是否已导入；未选依据的描述不能冒充模型已经看过图片。
- 实体列表/manifest 的 entity.sourceRevision 包含空间修订，支持短片工具识别资料更新。短片工具导入仍保存自己的不可变快照，不能默默刷新旧拍摄本。

提示词生成流程应使用 `sceneSpatial.promptContext` 与稳定标识，保留 unknowns；另叠加拍摄本动态状态。不能用 draft 或历史生成提示词填补缺失空间事实。此处不编写具体视频模型提示词。

当前 film-editor 的 importEntities 原样保存 manifest，inventory 保留实体扩展，exportedFacts 原样传递公共扩展到 generateStage 的 LLM context。只读函数复核已确认本字段进入 exportedFacts；本任务未修改或运行短片应用、LLM或GPU。现有项目须明确“使用最新”新导入，确认空间后再生成空间拍摄方案，不修改旧快照。

## 图书馆实际资料与限制

已对当前主形象 `25958405-ac83-454f-909e-f4aeba33f9a4` 实际看图，保存[空间草稿](../../.pi/tasks/scene-spatial-v1/library-spatial-draft.json)，来源和 hash 见[source](../../.pi/tasks/scene-spatial-v1/library-source.json)。命名 reading_area/left_shelf/back_shelf/near_table/far_table；右侧边界 right_boundary 为 pending。入口、总尺寸、精确朝向、通道及隐蔽区域明确待补充。桌面杯子/纸张/书本不作为固定物体。原 profile、图片及定稿选择未改，**生产空间仅保存草稿，尚未替用户确认**。

单张透视图不足以确定整个空间。用户补充平面说明、其他视角或设计约定后更新草稿并核对；本期不生成额外场景图、平面图或视频，不声称视频模型能保证空间一致性。

## 启动与复核

沿用 `npm run build`、`npm start`，入口 `/?view=manage`。图书馆详情直接打开 `http://127.0.0.1:4188/?view=manage&entity=9971429d-863e-499e-b7c5-902d30e0f6a2`。点击“与助手讨论空间布局”打开对话；原编辑入口为“手工精修”，对照所选图核对，保存后勾选一致性再确认。

构建通过。隔离4197端口、独立 SQLite/图片副本、无 ComfyUI 地址的 PC1440×1000手动复核：保存/确认、待补充排除、字段/锚点校验、并发409、依据变化撤销、不可变 manifest、独立派生、schema及下游扩展保留。未新增或运行单元测试/真实LLM/生成。记录：[validation](../../.pi/tasks/scene-spatial-v1/validation.json)。仅在确认工作台自身无活跃运行后重载4188应用，未操作 ComfyUI。
