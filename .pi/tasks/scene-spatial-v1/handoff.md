# 场景固定空间 v1 交接

Owner: Sean。2026-10-03。用户要求评估并完善场景实体文字，支持跨独立视频空间一致性、稳定标识、固定/动态边界、图文一致及持久化导出。

远程任务列表及相关设计/短片任务 info 查询成功。设计任务仅文档/UI，无同范围 Reference 业务实现；短片任务 active 且已兼容导出扩展，本任务只读检查其 inventory/exportedFacts，不修改其代码/运行状态。未明确要求新立项，本次不创建远程任务或更改旧任务状态。此目录为本地上下文。

权威说明 reference-workspace/docs/scene-spatial-v1.md。代码为 additive 空间版本表/状态指针、JSON schema、共用 PC 编辑器及现有 v1 导出扩展。固定事实仅在用户确认图/文字一致后可导出；依据变化 needs_review；动态状态字段拒绝，自然语言需要用户核对。草稿与未知信息仍导出状态/缺口，不阻塞旧资料。沿用原生成/资产确认流程，不更改 H3 提示词或运行生成。

实际图书馆图片经过查看，library-spatial-draft.json 为人工整理草稿，已保存生产数据库；原 profile、图片与定稿未改。生产空间未替用户确认。来源/hash/版本见 library-source.json。

构建、隔离 PC/HTTP/schema及只读下游字段保留复核通过，validation.json。临时端口4197仅本次服务、独立/tmp库和图片副本，无真实 ComfyUI 端点；生产4188重载前检查自身 active runs为空。无单元测试、LLM、GPU生成或ComfyUI启动/重启。

后续：用户核对图书馆草稿；为入口、平面图、尺度、真实通路补足依据。单张图片不能证明不可见空间；pending 不自动晋升。一般派生/武器变化通知仍属后续。
