# 场景参考图片组 v1

Owner: Sean。2026-10-04。场景不强制人物三视图，可使用同一场景的总览、多个角度及细节图。

## 使用

在「项目实体」或「资料库」选择场景，进入「场景参考图片组」，调整选择已登记的设定图或概念图，指定用途与说明，保存草稿。核对图片与场景资料后勾选确认并确认图片组。创作工作流步骤的「管理场景图片组」可直接进入该实体。

一组最多 24 张，有且只有一张总览；已有当前主图时，它必须是总览。主图以原选定界面确认，不由图片组隐式替换。其他角度及细节按同一实体登记，图片字节、生成历史与稳定 assetId 保持原样。可以保存空组解除选择；旧版本保留。

确认图片组不确认新的空间事实。固定方向、区域、结构、物体、通路等仍由[场景空间设定](scene-spatial-v1.md)确认；图片无法看出的尺度和遮挡继续保留未知。Agent 的图片审阅意见不代替用户确认。

## 持久化与复核

`scene_image_versions` 保存不可变 document、内容哈希、人工确认依据与版本，`entity_scene_image_state` 指向当前版本。document 为：

```json
{
  "images": [{"assetId":"<UUID>","role":"scene_overview","label":"入口总览","description":"参考说明","anchorIds":[]}],
  "notes":"地理朝向、绝对尺寸仍待补充"
}
```

role 可为 `scene_overview`、`scene_angle`、`scene_detail`。可选 anchorIds 只能使用本实体空间文档现有锚点；它们表示图像对应位置，不创设新事实。界面首版不要求手填锚点。

确认时比较草稿版本、内容哈希及实际依据：介绍、外观、当前主图、空间版本、图片登记与实际字节哈希。依据变化标记 `needs_review`，默认导出排除这组素材。当前确认组中的图片即使解锁也不能删除；先调整并保存图片组。确认组保护与普通主图保护分别检查，不互相覆盖。

版本比较冲突 409、字段无效 400 且给出字段级错误、未知合法 ID 404。仅本机已有访问边界，不接受文件路径输入。

## API

| Endpoint | 用途 |
|---|---|
| GET /api/manage/entities/:id/scene-images | document、summary、expectedVersionId、evidenceHash、本实体候选图 |
| PUT /api/manage/entities/:id/scene-images | expectedVersionId（可 null）与 document，保存新草稿 |
| POST /api/manage/entities/:id/scene-images/confirm | expectedVersionId、expectedContentHash、expectedEvidenceHash、acknowledgeConsistency:true |

已有导出请求增加三种场景素材角色，默认角色包括它们：

```json
{"entityIds":["<场景 UUID>"],"assetRoles":["scene_overview","scene_angle","scene_detail"],"includeUnconfirmed":false}
```

实体返回 `sceneImages`：schemaVersion、status、versionId/version、contentHash/sourceRevision、confirmedAt、images、notes、issues。images 只包含本次实际选中并导出的素材，不通过图片组自动扩大素材选择。未确认组默认无 images；includeUnconfirmed:true 可带待核对内容，素材确认状态明确为 unconfirmed/needs_review。confirmed 素材记录 kind=scene_image_set。当前总览也支持旧客户端仅请求 main_appearance 时的角色映射。旧 manifest 不改写。机器 schema 同步见 docs/schemas/。

项目 Agent 上下文包含 sceneImages 及实体最新来源修订。下游视频应用必须读取新角色和 sceneImages，本阶段不修改其他 Worker 正在开发的 film-editor。

## 验证与限制

24 项自动测试及 Vite build 通过。新测试覆盖确认/范围/schema、文字与主图变化、并发版本、锚点归属、删除保护、篡改哈希、显式素材选择与旧快照不变。PC 浏览器在隔离 fixture 跑通三图选择、保存、确认、放大和刷新恢复，控制台 0 错误、无页面横向溢出。测试图片为明确标注的色块，只验证操作和数据链路，不证明生成图像一致性。

证据：experiments/sean_reference_authoring_goal_20261004/scene-image-set-pc.png、scene-image-set-manifest.json。运行 `npm test`；浏览器隔离资料入口 `node scripts/scene-images-ui-fixture.mjs`（打印随机本机 URL，结束后清理临时库）。不调用真实模型、凭据、GPU 或 ComfyUI。

完整创作目标仍需批次执行与恢复、Agent 反馈修订、步骤独立版本、人物后续多视图/声音编排和真实图片实验检验。
