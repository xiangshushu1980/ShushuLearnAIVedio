# 实体浏览、关系与派生 v1

Owner: Sean。2026-10-03。仅 PC；沿用现有素材创作和确认流程。

## 一个界面的操作顺序

打开 `http://127.0.0.1:4188/?view=manage`。左栏浏览、搜索名称/介绍/flag、多 flag 全部或任一匹配，以及新建；中栏实体资料编辑、当前三视图/主形象放大、声音描述/播放与创作入口；右栏设定/剧情关系切换、显示和编辑。自定义 flag 与人物/物品/技能/场景预设同等保存，flag 不代替正式 type。旧实体没有 flag 或描述时显示为空，不补造资料。

新建先填写名称、flag、介绍、外观和声音描述，保存后再进入已有设定图片、概念图、主形象、多视图和声音页面。编辑与切换之间有未保存提示；编辑资料期间暂不编辑关系。页面 URL 保存当前实体，可刷新续读。

## 两类关系

- `setting`：穿着、使用、拥有、掌握、使用时显现、位于等；类型可自定义。
- `story`：同伴、敌对、合作、师徒、亲属、相识等；类型可自定义。

关系有独立 UUID、方向、类型、说明、active/removed 状态、创建/修改时间及目标来源修订。显示入向和出向关系；编辑和解除须在来源实体进行。解除为软删除，不删除实体或素材。并发修改通过 expectedUpdatedAt 拒绝旧输入；资料通过 expectedRevision 校验。

创作页“引用其他实体／建立设定关系”可选对方图片，将原字节复制为当前实体独立设定图，同时明确选择关系用途。默认仅作引用，不推断穿着或拥有，也不改写提示词。选图顺序仍由概念图引用列表决定；请明确逐图职责。每次复制记录来源实体、assetId、素材 hash 和实体修订。创建阶段关系与浏览管理页使用同一张关系表。

## 派生是独立实体

在实体资料上点击“创建派生实体”，填写新名称和变化说明。可选择复制介绍/外观、当前主形象作为引用图、沿用声音、复制出向设定关系。剧情关系不复制；原实体不覆盖。新实体保留不可修改的“派生自”关系与基础来源修订；可继续增加新技能、翅膀、武器等关系。

- 新图片是未确认设定引用，已准备概念图草稿；变化说明进入草稿，只有存在第一张引用才使用 Image 1。新主形象和三视图仍需创作、挑选、确认。
- 沿用声音复制原文件为新 assetId，建立独立当前声音版本/确认；内容 hash 相同。真实原生成 run 作为来源保留，metadata.inheritance 记录来源实体/声音/素材/生成实体。不制造派生实体的虚假生成记录。可以继续在声音页创作替换。
- 复制素材失败或事务失败回滚本次数据库记录与新文件。

**后续来源变化提醒尚未实现。** 当前已保存基础修订、引用来源哈希与关系 targetRevision，未来可比较武器外观、基础形象或声音的变化并提醒关联实体。现阶段只保存独立快照，不自动传播更新；导出 capability.derivation.changeNotifications=false。

## 数据与接口

沿用 entities.name/context：context 中维护 flags、description、appearance、voiceDescription，保留其他已有上下文。新增 entity_relations、entity_derivations；原草稿、生成记录和确认版本不迁移、不重写。启动自动建表；整个 `.data` 备份边界不变。

所有接口使用已有 loopback/Host/Origin 限制和 JSON 错误结构。

| 方法 | 路径 | 输入/返回 |
| --- | --- | --- |
| GET | /api/manage/entities | q、flags（逗号分隔）、match=all/any；列表和 flag 计数 |
| POST | /api/manage/entities | name、flags、description、appearance、voiceDescription；201 详情 |
| GET | /api/manage/entities/:id | profile、revision、visualState、voiceState、relations、derivedFrom、descendants |
| PATCH | /api/manage/entities/:id | 完整 profile + expectedRevision |
| POST | /api/manage/entities/:id/derive | profile + expectedBaseRevision、changes、copyProfile、copyReference、reuseVoice、copySettingRelations；201 新实体详情 |
| POST | /api/manage/entities/:id/relations | targetEntityId、category、type、description；201 来源实体详情 |
| PATCH | /api/manage/entities/:id/relations/:relationId | 上述关系字段 + expectedUpdatedAt |
| DELETE | /api/manage/entities/:id/relations/:relationId | JSON {expectedUpdatedAt} |
| POST | /api/manage/entities/:id/references | sourceEntityId、assetId、relationType（默认 null）、description、category（默认 setting）；201 新素材 |

name 必填 1–100 字；flag 最多30个、每个1–40字、禁止逗号/重复；介绍/外观最多8000字、声音描述4000字；关系类型1–60字、说明4000字。未知合法 ID 为404、格式400、过期版本/重复关系409。派生来源仅由派生操作建立，不允许自行添加或解除。

导出 API 沿用 v1，新增可选 flags、derivedFrom、relationRevisions、asset.inheritance、prompt.sourceEntityId；关系 direct 仅返回两端均被选中的 active 关系，不递归。旧已保存 manifest 原样读取。导出详情见[导出契约](reference-export-v1.md)。

## 启动、复核与限制

启动沿用 README 的 `npm run build`、`npm start`。本次构建通过；在端口4196的隔离 SQLite/素材副本进行1440×1000 PC 操作与接口手动复核，ComfyUI 地址指向未使用端口，未提交生成。复核覆盖新建/资料/flag筛选、设定和剧情关系、派生沿用声音、进入旧创作页、明确关系引用/纯引用、导出 schema/快照/声音哈希及400/409。记录见[validation.json](../../.pi/tasks/entity-management-v1/validation.json)。本轮未新增或运行单元测试。生产用户资料与定稿选择未修改。

暂缺正式单值实体 type、音效管理、人工审核、独立提示词版本与来源变化提醒。无实体删除、合并、自动同步或手机端适配。
