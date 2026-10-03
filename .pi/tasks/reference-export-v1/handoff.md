# Reference 只读导出 API v1 交付上下文

Owner: Sean。2026-10-03。用户明确要求实现四个只读导出端点及schema/最小自动化验证。本次远程 Task Center 冲突查询成功：没有同范围 API 实现任务；remote-750a1fff-c5dc-426c-81d1-4e33811caab4 是使用临时 bundle 的短片下游验证，仍 queued，未借用其范围或控制权。当前请求没有新立项要求，未创建或改写远程任务。此文件只保存实现上下文。

## 范围与真实模型

现有 entities(id/name/context/created_at)、稳定 assets UUID/hash、runs 不可变提示词快照、主形象/视图/声音确认表。正式实体类型/介绍/外观编辑模型、关系表、音效、人工审核和独立提示词版本缺失；以null/空关系、能力信息和missingFields如实声明。context显式字符串只做有限映射，声音描述可映射当前声音source run prompt。locked不充当确认，不把workflow版本当提示词版本。

## 实现

- GET /api/reference/v1/entities
- POST /api/reference/v1/manifests
- GET /api/reference/v1/manifests/:manifestId
- GET /api/reference/v1/assets/:assetId/content

仅选中实体/角色素材，无图谱扩展；可选assetIds精确选取并检查归属。默认仅真实确认记录（包含仍存活的历史确认素材，isCurrent标识当前）；候选需includeUnconfirmed。独立SQLite reference_manifests与禁止update/delete触发器保存创建时JSON，内容/修订hash用于更新识别。素材不复制，删除后原内容404，短片工具导入时须下载/校验并保存。路径/密钥/完整元数据/执行图不暴露，文件限Reference media，保留本机Host/Origin边界，返回MIME/ETag/Range及400字段级错误。

不改实体编辑或生成流程。仅将原本机HTTP访问中间件抽为local-access共用，以便HTTP测试；仅无活动run时重载4188应用。不启动/重启/提交ComfyUI。本次只新增导出表和快照，不改实体/定稿/素材/业务草稿。

## 证据

5项新自动化验证+已有7项共12项全部通过，npm run build通过。新测试临时数据/HTTP端口，不调用ComfyUI。真实4188调用/schema校验记录见 validation.json，manifestId 5629ce2a-a44d-411e-a3f2-94cad9baeb6a；GET与POST字节一致，实际音频Range206及audio/wav、坏JSON400字段body。实际请求返回一个实体和4项确认素材（两多视图/两声音，包含历史确认）；未导出其他实体。

权威契约、字段映射/缺口、示例/调用/验证：reference-workspace/docs/reference-export-v1.md；机器schema位于docs/schemas，演示快照example-manifest.v1.json不含用户数据。应用4188继续服务，运行数据与SQLite留本机，不混合提交其他工作区修改。
