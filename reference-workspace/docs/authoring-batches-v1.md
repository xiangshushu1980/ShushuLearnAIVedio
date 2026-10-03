# 人物／场景图片批次 v1

Owner: Sean。2026-10-04。批次执行已经审阅的图片步骤，不创建新实体，不自动确认结果。

## PC 使用

在项目工作区「批次生成实验」展开步骤列表，明确选择当前版本的人物/场景/变体步骤，填写实验名，审阅后保存计划。保存不生成。点击「开始／恢复批次」并确认后，后台按固定步骤逐张调用已有生成服务。每个实验有独立批次 ID、标题、状态与输出，可分组比较。

缺少主图的步骤进入等待，仍可先执行同批次中可生成的总览或基础人物图。需要主图时点击「选择依赖主图」，在原界面从结果选择主形象，再返回恢复。选择主图不自动恢复或消耗下一步额度。已存在的主图版本会固定；中途换成另一个版本需重新审阅并建立新批次。

暂停/取消仅停止后续提交，不全局中断共享 ComfyUI，不删除已提交的运行。失败停止后续步骤；重试先核对结果/修订步骤并建立新批次。页面关闭后已授权执行继续；服务重启则标为 interrupted，由用户核对后恢复，不自动提交新步骤。

图片可以放大查看、在多个批次中勾选最多 8 张交给项目助手进行实际观察与一致性检验。也可直接检验某批次前 8 张。生成成功仅表示产物回收，不代表逻辑一致或人工确认；人物主图、场景参考图片组与空间设定仍分别确认。

## 范围与来源

一次最多 48 个当前步骤。批次固定步骤 ID/hash、实体、项目修订/规则、实体与引用实体事实/关系/空间修订、模型/风格/模板指纹、明确引用的图像哈希。资料变化时停止后续提交，要求重新审阅或建立新批次，不能静默采用另一个提示词版本。

待选主图是唯一预先声明的可解锁依赖，首次选定后固定该版本。明确引用只能使用已登记的稳定 assetId；跨实体引用复制到目标实体，保留来源 ID/hash。准备输入不覆盖正在人工编辑的生成草稿。

`authoring_batches` 保存状态、版本及不可修改的范围；`authoring_batch_items` 保存步骤、输入准备结果、稳定 request_key、runId；`authoring_batch_events` 保存状态事件。实际 run 的 authoring provenance 带 batchId/batchItemId/stepId/rootStepId/version，旧生成结果仍属于原步骤版本。

一个 Reference 服务同时调度一个 running 批次，批次内等待前一运行结束再提交下一运行；普通手工生成仍由既有服务和资源仲裁管理。暂停中的已提交运行可能继续执行，开始另一个批次不取消它。

准备输入先持久化再调度；恢复通过 request_keys 找回已经保存的运行，沿用同一请求标识。该检查证明批次调度不会新建重复 Reference run，不替代现有生成服务对 ComfyUI 提交/回收故障窗口的处理。

## API

现有本机 Host/Origin 限制继续有效；未知合法 ID/范围外 ID 404、字段格式 400 且给出 fieldErrors、并发或来源变化 409。

| Endpoint（前缀 /api/authoring/:projectId） | 用途 |
|---|---|
| GET /batches | 当前项目实验计划、状态、事件及输出 |
| POST /batches | 保存计划，不生成 |
| GET /batches/:batchId | 状态、revision、各步骤与真实 runId |
| POST /batches/:batchId/resume | 显式授权开始/恢复 |
| POST /batches/:batchId/pause | 停止后续提交 |
| POST /batches/:batchId/cancel | 取消后续步骤 |

保存请求：

```json
{"requestId":"<UUID>","title":"候车厅日常／受损实验","steps":[{"stepId":"<已采用步骤 UUID>","expectedStepHash":"<SHA256>"}],"acknowledgePlan":true}
```

同一 requestId/相同请求返回同一计划，不同请求冲突。开始/恢复请求为 `{"expectedRevision":1,"acknowledgeGeneration":true}`；暂停/取消仅 `expectedRevision`。响应包含 owner、id/projectId、title、status、revision、error、items、events。状态可为 draft/running/waiting/paused/interrupted/failed/completed/cancelled；每个 item 提供步骤/实体 ID、状态、runId/runStatus、progress 和输出素材，文件入口使用登记素材服务，不接受磁盘路径。

Agent 没有开始/恢复批次的工具权限。创作方案、检查报告和修订继续由 Agent 提出；生成授权留在用户界面。

## 验证与完整目标差距

36 测试与 Vite build 通过。新增 8 项隔离验证覆盖授权、主图等待及恢复、串行调度、暂停/取消、失败、重启找回同一 run、不重复请求、范围/CAS、步骤或事实变化停止、合法生成快照预览及篡改输入拒绝。测试调度器仅保存模拟 run 和色块，未调用 ComfyUI。真实 startPrepared 使用同一纯快照检查，合法路径通过 previewPrepared 验证；真实提交/生成结果尚未验证。

PC 隔离浏览器完成 2 步场景实验：保存计划 → 模拟总览 → 等待 → 原界面选主图 → 恢复细节 → 2/2 完成 → 刷新恢复 → 勾选结果。控制台 0 错误，无横向页面溢出。证据 experiments/sean_reference_authoring_goal_20261004/batch-{waiting-pc.png,completed-pc.png,ui-receipt.json}，模拟来源明确标记。隔离入口 `node scripts/scene-images-ui-fixture.mjs` 的 workflowUrl，结束时清理临时库。

完整目标仍未证明：真实人物/场景多组图像质量、视觉模型反馈效果、图文/关系质量、一致性失败后的完整再生成实验，以及 V3/声音后续步骤编排。不得把模拟批次完成当作整体目标完成。开发 Agent 本轮没有启动/重启/提交 ComfyUI；真实验证需要已有生成授权与共享资源规则。
