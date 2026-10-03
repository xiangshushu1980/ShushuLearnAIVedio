# 项目工作区与共用创作上下文 v2

Owner: Sean。2026-10-03。任务 `remote-8ac0f653-9980-494d-ba73-42ac4e97b71a`。

## 使用顺序

1. 打开 Reference 的「项目工作区」，新建或选择项目。
2. 保存项目介绍、故事梗概、世界规则、风格规则、已确定的创作决定。尚未确定的部分可留空，助手不会默认补成事实。
3. 从资料库加入已有实体，或进入「项目实体」新建。项目中派生的实体自动加入项目，原形象/声音/空间及派生策略沿用原流程。
4. 在实体详情填写「本项目的剧情作用」与剧情背景/约束；设定关系仍描述穿着、使用、掌握等实体事实，剧情关系只属于当前项目。
5. 点击「与项目助手讨论」或实体的「与创作助手讨论」，选择模型并新建对话，输入自然语言。项目介绍自动带入，实体资料每轮读取最新版本。通用讨论不要求图片。
6. 场景实体点击「与助手讨论空间布局」，继承同一项目；选择参考图，讨论锚点，应用草稿，再人工核对并确认固定空间。图片一致性没有自动审核。
7. 「检查项目一致性」打开已填好检查要求的项目对话。发送后消耗所选模型额度；保存实体不触发后台 LLM。报告区分资料冲突、待补充和建议，显示完整读取的实体范围。只读索引摘要不等于完整审核。

项目设置修改建议有逐字段“当前／建议改为”的预览，点击「接受并应用项目修改」才写入。实体修改建议在详情编辑；检查报告不自动修改实体、关系或确认状态。

## 数据与兼容

- 继续使用 `agent_projects` 的原 ID；旧 `brief` 作为项目介绍，新增 `synopsis/worldRules/visualStyle` 缺省为空。旧字段不会被重新解读或模型补写。
- 全局 `entities` 是实体事实与素材的权威资料库。项目的 `entityIds` 是明确的成员集合，同一个实体可用于多个项目。
- `project_entity_roles` 保存项目内 `role/plotNotes`、修订、更新时间；不会覆盖实体的全局介绍。
- `project_relations` 保存项目内剧情关系的稳定 ID、两端、类型、说明、active/removed、修订与时间。只允许当前项目成员参与。
- 全局 `entity_relations.setting` 继续使用；旧全局 `story` 保留并标明未归属项目，在项目上下文中单独提示，不默认采纳，也不静默复制到多个项目。资料库只查看这些旧剧情关系；项目中重新建立明确归属的关系。
- 移出成员时移除对应项目角色记录，并将涉及该成员的项目关系软删除；实体与素材保留。当前 UI 使用加入已有实体，成员移除可通过项目 PATCH。
- `agent_sessions.entity_id` 升级为可空，以表达真正项目级对话；迁移保留会话 ID、消息、runs、Pi entries 和旧空间提案。工作模式 `project-authoring` 与 `scene-spatial` 各自保存会话。
- `agent_project_proposals` 保存不可变检查报告与项目资料修改建议及依据；只允许更新应用修订指针。原 `agent_proposals` 继续保存空间提案。
- 本地部署建议单实例，启动时做 SQLite 迁移；不要让新旧版本服务同时写同一数据库。

## 上下文、版本与费用

`GET /api/projects/:projectId/context` 从权威资料读取项目、当前实体文字、剧情作用、设定关系、项目剧情关系、派生来源与空间版本。返回 `contentHash`、`knowledgeIndex` 和项目缺失字段。实体修改不会自动递增项目设置 revision；实体自己的 sourceRevision 与整个 context contentHash 会变化。

每轮保存不可变 `agent_run_contexts` 和 basis，包括项目整体资料哈希、当前空间版本、证据状态、所选图片实际字节哈希、提示词/方法版本。系统自动注入项目设置和实体索引摘要；`get_project_entity` 可按稳定 ID 读取完整实体资料。聊天历史用于恢复讨论，不能盖过最新资料。用索引摘要减少默认输入量，不把截断部分当缺失；完整资料按需读取。

应用提案时检查整个项目当前 basis，一旦项目成员、角色、实体、关系或参考图变化，旧建议标明过期并要求重新讨论；不会用旧建议覆盖新资料。报告记录已完整读取的实体 ID，明确其余是摘要。图片必须调用观察工具，不把选图等同于已看图或已确认。单轮工具/时长仍受原 Pi 接入限制，因此大型项目可能需要分批检查。

没有自动运行的“持续审核”；连续丰富的是权威项目资料与修订索引。要记录跨会话创作结论，应由用户保存到项目的已确定决定或实体事实中。

## API

全部继承现有 loopback Host/Origin 限制、JSON 大小限制；UUID/结构无效返回字段级 400，未知项目或非成员返回 404，修订冲突返回 409。

| Endpoint | 用途 |
|---|---|
| GET /api/projects | 列出项目 |
| POST /api/projects | 创建项目 |
| GET /api/projects/:projectId | 项目资料 |
| PATCH /api/projects/:projectId | 保存项目，带 expectedRevision |
| GET /api/projects/:projectId/context | 最新共用上下文与修订索引 |
| GET /api/projects/:projectId/entities | 项目实体，支持 q/flags/match |
| POST /api/projects/:projectId/entities | 原子新建并加入项目：profile、expectedRevision |
| POST /api/projects/:projectId/members | 加入资料库实体：entityIds、expectedRevision |
| GET /api/projects/:projectId/entities/:entityId/role | 当前项目中的剧情作用 |
| PUT /api/projects/:projectId/entities/:entityId/role | role、plotNotes、expectedRevision |
| POST /api/projects/:projectId/entities/:entityId/derive | 按既有派生策略原子创建并加入：profile、expectedRevision |
| GET /api/projects/:projectId/relations | 当前项目剧情关系 |
| POST /api/projects/:projectId/relations | sourceEntityId、targetEntityId、type、description、expectedRevision |
| PATCH /api/projects/:projectId/relations/:relationId | 修改项目关系，字段同 POST |
| DELETE /api/projects/:projectId/relations/:relationId | 软删除，expectedRevision |
| POST /api/agents/project-proposals/:proposalId/apply | 应用项目设定建议：expectedContentHash |

创建项目示例：

```json
{"name":"示例短片","brief":"项目目的与基调","synopsis":"尚在讨论的故事梗概","worldRules":"已确定的世界规则","visualStyle":"统一的视觉与声音风格","decisions":"已确定的创作决定","entityIds":[]}
```

原 `/api/agents/projects` 的项目读写接口继续委托同一服务。列出会话：`/api/agents/projects/:projectId/sessions?purpose=project-authoring` 为项目级，带 `entityId` 为实体级；旧默认 purpose 仍是 scene-spatial。

通用会话创建：`POST /api/agents/sessions`，`projectId`、`entityId:null`、`purpose:"project-authoring"`、列表中已配置的 `provider/modelId`。消息接口仍需要 requestId/text/referenceAssetIds；通用模式 referenceAssetIds 可以是 `[]`。空间模式至少一张当前场景图片。

## 短片工具导出

原 v1 `POST /api/reference/v1/manifests` 新增可选 `projectId`，带入经过脱敏的 `projectContext` 以及所选实体的 `projectRole`。不扩展 entityIds，不导出其他项目实体或全部图谱。

- includeRelations=direct：两端都选中的全局设定关系＋指定项目的剧情关系。
- 未传 projectId：保留原全局关系导出语义，不生成新的项目归属。
- projectContext 带 sourceRevision、项目设置 revision、缺失字段；projectRole 独立带 sourceRevision。实体导出 sourceRevision 结合实体与项目角色修订。
- 原快照不会重写，外层 schemaVersion=1，新增字段均可选。机读 schema 同步更新。
- 下游需读取 projectContext/projectRole 才能用于视频提示词；本次只改 Reference，不修改其他应用，不宣称已有下游自动消费。

请求示例（替换 UUID）：

```json
{"projectId":"11111111-1111-4111-8111-111111111111","entityIds":["22222222-2222-4222-8222-222222222222"],"includeRelations":"direct","assetRoles":["three_view","voice"],"includeUnconfirmed":false}
```

## 启动与交付边界

在 `reference-workspace/` 使用现有 `npm run build`、`npm start`（默认 http://127.0.0.1:4188）。项目首页 `/?view=projects`。数据继续在 `.data/workspace.sqlite`；模型及登录凭据继续从应用自有 `.data/agent/` 读取，不改 Pi 用户配置。

本阶段编译与 JS 语法检查，不新增/运行自动化测试或真实 LLM 对话，不执行 ComfyUI 操作。页面交互与模型质量由用户实际使用验收。没有新增实体 type 编辑、音效生成、正式审核、自动同步派生实体或图片自动一致性判定。

通用接入方法：[Agent 集成手册](agent-integration-v1.md)。演进经验单独追加到 `.pi/ledger/reference-agent.md`。
