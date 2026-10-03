# Reference 只读导出 API v1

Owner: Sean。Reference 是实体和素材的唯一权威来源。短片工具通过此接口读取，导入后自行保存 manifest 与素材字节，不读取 Reference 数据库或磁盘路径。创建、命名、关系编辑界面留实体浏览/管理阶段；本次不改编辑和生成流程。

## 启动与边界

```bash
cd /home/sean/projects/comfy-ops/reference-workspace
npm ci                    # 仅首次安装需要
npm run build
npm start
```

默认 `http://127.0.0.1:4188`。既有 REFERENCE_PORT / REFERENCE_DATA_DIR 仍适用。只绑定 loopback；Host 只接受 localhost/127.0.0.1；带 Origin 的 POST 必须同源。未添加 CORS、远程监听、API key 或外网权限。短片应用后端可本机请求；不同端口浏览器前端应通过自己的后端调用，不能直接跨源 POST。

仅添加 reference_manifests 表与禁止 update/delete 的触发器。POST 只保存导出快照，不更新实体/素材/确认/生成数据。启动应用沿用原机制，导出路由不连接 ComfyUI。

## 接口

| 方法与路径 | 返回 |
| --- | --- |
| GET /api/reference/v1/entities | 轻量实体列表与真实能力信息 |
| POST /api/reference/v1/manifests | HTTP 201，已持久化的不可变快照 |
| GET /api/reference/v1/manifests/:manifestId | 创建时同一 JSON；编辑/换定稿/删除素材不会改写 |
| GET /api/reference/v1/assets/:assetId/content | 原图片/音频，正确 MIME、ETag、Range；自动支持 HEAD |

未知合法 UUID 的实体/素材/manifest 为 404。坏 UUID、空选择、重复 ID/角色、未知字段、无效角色、跨实体 assetIds 为 400；details.fieldErrors 使用字段或点路径。归属异常、登记 hash 与实际内容不符为 409。删除的素材内容 404。Host/Origin 拒绝为 403。不接受 path 或其他查询参数，不提供任意文件读取。

```json
{"error":"无效导出请求","details":{"fieldErrors":{"entityIds.0":["Invalid UUID"]}}}
```

## 请求

```json
{
  "entityIds": ["5821d6dd-2041-40a3-a789-74989c6edd90"],
  "includeRelations": "direct",
  "assetRoles": ["three_view", "voice", "sound_effect"],
  "includeUnconfirmed": false
}
```

entityIds 为 1–100 个无重复 UUID。includeRelations 默认 none；direct 仅指两端均在明确选中实体里的直接关系，不扩展实体列表、不递归图谱。当前没有关系表，none/direct 都返回 []，同时声明不支持。

assetRoles 默认 main_appearance / three_view / voice / sound_effect。可用角色：

| 角色 | 现有字段映射 |
| --- | --- |
| setting | setting 图片；无确认机制 |
| concept | 尚未作为主形象确认的 concept；无独立确认机制 |
| main_appearance | 有 appearance_versions 确认记录的 concept |
| three_view | multiview 合成图；实际布局另见 layout，可为 three/four/face-front-back-side，未拆分各视角 |
| voice | 基础 voice 样音；兼容旧版没有 voiceRole 的 voice |
| voice_emotion | voiceRole=emotion 的样音；未实现单独确认机制 |
| voice_source | voice-source 原始参考音源；未实现确认机制 |
| sound_effect | 合法请求角色，但当前没有音效登记/数据模型，返回空结果和能力缺失 |

includeUnconfirmed=false 仅接受实际主形象/多视图/声音确认记录，**锁定不等于确认**。包括仍存在的历史已确认素材；通过 confirmation.isCurrent 判断当前选用。未确认或不支持确认的素材默认排除，omissions 给出 not_confirmed/content_missing。需要候选、设定图或情绪样音时显式开启 includeUnconfirmed=true。

可选 assetIds（最多500个、可为空）精确选择素材：必须真实存在并属于已选实体，再与角色/确认条件取交集。空数组只导出实体资料。默认未传时选择请求角色下所有符合条件的素材；不会加入其他实体素材。

## 响应与来源

完整可机读示例见 [example-manifest.v1.json](example-manifest.v1.json)，JSON Schema 见 [schemas](schemas/manifest.v1.schema.json)、[请求 schema](schemas/manifest-request.v1.schema.json)、[实体列表 schema](schemas/entity-list.v1.schema.json)。示例是生成的演示数据，不代表新增了业务字段或用户验收。

列表形状：

```json
{
  "format": "reference-entity-list",
  "schemaVersion": 1,
  "owner": "Sean",
  "capabilities": {"relations":{"supported":false}},
  "entities": [{
    "entityId": "5821d6dd-2041-40a3-a789-74989c6edd90",
    "name": "一期验收 · 四图概念探索",
    "type": null,
    "description": null,
    "contentHash": "<完整实体来源内容的 SHA-256>",
    "sourceRevision": "<同一修订哈希>",
    "missingFields": ["type", "description", "appearance"]
  }]
}
```

上例 capabilities 为节选；完整响应声明缺失能力。manifest 顶层包括 format=reference-manifest、schemaVersion=1、owner、manifestId、createdAt、contentHash、capabilities、selection、entities、relations、omissions、missingCapabilities。

实体正文包括稳定 entityId/name、nullable type/description/appearance/voiceDescription、fieldSources、missingFields、当前主形象/声音确认 ID/版本/素材 hash、选中 assets 和对应 prompts。只映射 context 中显式字符串 type/description/appearance/voiceDescription；不猜实体分类，不把 context.purpose 当介绍。声音描述可来自当前声音原始 run 的声音设计 prompt；录音克隆没有描述时保留 null。

素材包含 assetId/entityId/role、mediaType/mime/fileSize、内容 hash/sourceRevision、相对 contentUrl、尺寸/时长、真实确认记录、reviewStatus=null。绝对磁盘路径、任意 context/metadata、API key、执行图及服务配置均不进入 JSON。受支持的说明文本中明显 token/本机路径会脱敏。内容下载保留原始素材字节，短片工具应按 contentHash 校验。

提示词来自被导出素材关联的不可变生成 run，而非正在编辑的草稿：promptId=run:<UUID>、sourceRunId、用途、原始/生效提示词、实际台词和引导、workflow id/version/hash、内容哈希。没有独立提示词版本号，version=null；不能用 workflow.version 假装提示词版本。

### 修订与不可变性

- manifest.contentHash：除 manifestId/createdAt/contentHash 外的完整 payload，按对象 key 递归排序、数组保留顺序、UTF-8紧凑 JSON 后 SHA-256。可使用 server/reference-export.mjs 的 canonicalJSON/contentHash 验证。同一来源/选择可产生不同 manifestId，但 contentHash 相同。
- entity.contentHash/sourceRevision：完整实体导出来源（全部存活素材、真实确认、素材对应提示词和映射文本）的修订哈希，不随本次角色裁剪变化；可与列表对账。
- asset.contentHash 是原文件 SHA-256；sourceRevision 覆盖素材导出元数据（含真实确认状态）。字段 source hash 和 prompt sourceRevision 提供各自来源指纹；prompt.contentHash 为本次导出提示词记录（排除其 contentHash/sourceRevision）。
- manifest JSON 存在 Reference SQLite 的独立表，重读不重建。当前素材删除不修改旧 manifest。
- **不复制或保留素材字节**：旧 manifest 里的 URL 可能在素材删除后返回404。短片工具创建/读取 manifest 后应立即下载、校验并保存文件，再保存自己的快照。导出快照不是编辑流程的新保护状态。

## 缺失字段与能力

当前实体表只有 id/name/context/created_at。创建/命名基础后端已有，但管理 UI 与正式实体类型、介绍/外观 schema 未实现；当前实际实体没有 type/description/appearance 时返回 null 和 missingFields。已有主形象和图像仍能导出。

没有正式实体关系模型、关系 ID/类型/描述/状态；不解析临时任意 context.relations，也不凭空生成关系。没有音效素材类型/管理。没有人工审核状态、审核时间/人员或独立提示词版本；没有实体递增 revision，用内容哈希。情绪样音/上传音源/设定图无单独确认机制；不能把生成成功或 locked/protected 充当审核。

## 调用与验证

```bash
curl -s http://127.0.0.1:4188/api/reference/v1/entities
curl -s -X POST http://127.0.0.1:4188/api/reference/v1/manifests \
  -H 'Content-Type: application/json' \
  -d '{"entityIds":["5821d6dd-2041-40a3-a789-74989c6edd90"],"includeRelations":"direct","assetRoles":["three_view","voice","sound_effect"],"includeUnconfirmed":false}'
curl -s http://127.0.0.1:4188/api/reference/v1/manifests/MANIFEST_UUID
curl -H 'Range: bytes=0-31' http://127.0.0.1:4188/api/reference/v1/assets/ASSET_UUID/content
```

```bash
cd /home/sean/projects/comfy-ops/reference-workspace
node --test server/reference-export.test.mjs  # 5项最小自动化验证
npm test                                   # 现有12项全部通过
npm run build
```

验证使用临时数据库和本机 ephemeral HTTP 服务，不启动/重启/提交 ComfyUI。覆盖默认确认筛选、范围/归属、未知ID与字段级400、schema、脱敏、不递归、同来源 hash、编辑/删素材/服务重建后快照一致、禁止改快照、正确MIME/字节/Range、本机Host/Origin和任意路径拒绝。
