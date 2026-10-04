# 关系检查证据 v1

Owner: Sean

项目文字检查和图片检查问题支持可选 `relationIds`（最多 30 个 UUID）。助手在问题 entityIds 中包含关系两端，并在本轮 get_project_entity 完整读取两端后，才能保存关系检查意见。关系缺失只能作为建议描述，不虚构 ID。

服务端从当前项目上下文解析实际关系，保存不可变 relationSources：实际 ID、两端 ID/名称、类型、说明、状态（已有字段）、来源及内容哈希。scope 区分 entity-setting（实体固定设定）、project-story（本项目剧情）和 legacy-unassigned-story（历史未分配剧情）。后者不能当成本项目剧情。

重复关系或未读两端/缺少端点引用返回 400；未知及两端不在项目范围返回 404。既有报告依据上下文哈希判断过期，修改关系后旧内容不会重写。旧报告未提供 relationIds 继续兼容，不自动补全来源。

PC 报告可展开查看关系依据。报告只是审阅意见，不修改、确认或删除关系；现有实体及项目关系编辑继续用于人工修订。来源记录证明使用了当前登记关系，不证明语义检验正确或全部关系已覆盖。

验证：78 项测试、Vite build 通过；隔离模拟 PC 关系详情展开、刷新后重新打开、0 控制台错误及无横向溢出通过。新增测试覆盖两端读取、错误范围、重复引用、固定/剧情/历史范围和关系变化后报告保留旧内容并过期。没有模型、ComfyUI 或 GPU 调用。

复现 PC：在 reference-workspace 运行 `npm run build`，再运行 `REFERENCE_PROJECT_REVIEW_FIXTURE=1 REFERENCE_RELATION_REVIEW_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`；打开输出 workflowUrl 并进入项目助手。临时数据库与模拟 Agent，不读取凭据。

Owner: Sean。已有关系的自然语言修订与人工接受见 [关系修订提案](relation-change-proposals-v1.md)。
