# 实体画布：原生 PiWeb 消息与工具协议 v1.0 草案

> Owner: Sean。2026-10-07。静态分析依据与拟议适配契约。未访问运行中 PiWeb API、创建会话或调用模型；本文件不是接入已实现报告。

## 1. 版本证据

本机已安装 `@agegr/pi-web` 0.10.0，包声明依赖 `@earendil-works/pi-coding-agent` 1.0.0。视频实现文档记录的 0.8.11/0.84.3 是历史证据，不能当本次协议版本。

本次将官方 v0.10.0 源码只读下载至 `/tmp/sean-piweb-design-20261007`，tag 对象 c809370509b5550fb168794590de55a42496dbf4，解引用 commit **6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068**。没有安装依赖或运行源码。已安装包与 tag 的字节一致性未审计，运行服务版本也未查询；施工以实际运行包及协议核验为准。

源码入口使用固定 commit：

- [会话创建](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/app/api/agent/new/route.ts)
- [会话命令](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/app/api/agent/%5Bid%5D/route.ts)
- [SSE 路由](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/app/api/agent/%5Bid%5D/events/route.ts)、[流实现](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/lib/agent-event-stream.ts)
- [历史快照](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/app/api/sessions/%5Bid%5D/route.ts)、[历史分页](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/app/api/sessions/%5Bid%5D/context/route.ts)
- [RPC 和工具选择](https://github.com/agegr/pi-web/blob/6fcd7d44981ab51a21d6cd6eb06d361d0e3d3068/lib/rpc-manager.ts)

## 2. 接入方式

新 Vue 应用自己实现轻量讨论侧栏，应用服务转接上述原生协议。复用 PiWeb 会话运行时，不把 Next/React 聊天页面移植到 Vue，不嵌 iframe 作为最终体验，也不重做模型推理循环。视频端的绑定、幂等、更新收件箱作参考，FilmPiBridge 不直接复用为实体授权服务。

浏览器只连接应用服务。服务只允许访问当前项目已绑定的 PI 会话；不透传任意 cwd、sessionId 或命令。原生 PiWeb 仍是独立本机服务，模型凭据沿用宿主配置，不复制到浏览器/项目。

## 3. 可用原生协议与适配

| 原生接口 | 已读源码行为 | 本应用处理 |
|---|---|---|
| POST /api/agent/new | ensure_session 创建空会话；支持 cwd、provider/modelId、toolNames | 幂等 launch 记录，先绑定并核验，再发送首轮；不自动生成作品 |
| POST /api/agent/:id | get_state、get_tools、set_model、prompt、abort 等 | 命令白名单；模型切换不保存全局默认；普通文本不开放管理 slash 命令 |
| GET /api/agent/:id/events | SSE；connected、消息、工具及完成/错误事件；可唤醒已存会话 | 只在用户打开讨论时订阅；连接不等于推理授权 |
| GET /api/sessions/:id | 历史 context、entryIds、snapshotRevision、当前分支 | 首次/重连建立权威聊天快照，忽略 filePath 等宿主路径 |
| GET /api/sessions/:id/context | tail、before、leafId 分页 | 只加载当前绑定会话的历史，按 entryId 去重 |

原生 prompt 的 HTTP 成功表示 preflight 接受，不表示回复完成。提示被拒有显式 prompt_rejected/accepted=false；网络断开没有此保证。原生没有应用 turnId 幂等契约，必须在应用层做记录和对账。

## 4. 发送和恢复

1. 应用事务保存 turnId、用户文本、ContextSet/hash、操作意图、requestId，状态 prepared；同 requestId 不同内容返回冲突。
2. 获取项目单轮互斥；生成 turn receipt，在原生 prompt 中带应用签发的关联标记。上下文由实体扩展按 turnId 从服务读取，不信任模型自行提供的项目 ID。
3. 扩展 input/before_agent_start 钩子校验当前真实 sessionId、bindingVersion、turn receipt，记录接收；加载本轮选定对象、方法和规则。收到非应用入口的创作请求时拒绝业务执行。
4. POST prompt 已接受则状态 accepted；SSE 显示正文与工具活动；native message entryId、turnId、toolCallId 用于后续关联。
5. 回复结束后重取历史快照固化聊天引用。原生 entryId 才是消息稳定身份，不能用 token 片段时间戳当持久消息 ID。
6. POST 超时置 delivery_unknown，查询 receipt、会话状态和历史中 turn 标记，禁止自动再发。只有明确未接受才允许人工重发；应用重启也不自动续发计费推理。

会话创建同样先写 launch operation。已返回 sessionId 后的失败只恢复该会话。连 sessionId 都未得到的未知创建，先按工作区和时间核对，未定位前阻止再次创建；空会话可能尚未落盘，不能仅以磁盘搜索不到断言未创建。

原生 SSE 没有 id/Last-Event-ID 的持久重放机制；不能套用业务 outbox 的 after=seq。重连先挂事件缓冲，再取历史快照和 connected 的流中消息，合并后继续应用增量；发生交错/无法对应时重新取快照，完整 message_end 取代临时片段，不能追加两份正文。历史快照有 entryIds，流中临时气泡不能假冒最终 entryId。

停止调用 abort，仅停止该 PI 轮次；已创建 run 的生成继续进行。删除会话会连带删除历史，首期只提供归档/解除显示，不透传原生 DELETE。

## 5. 工具限制与上下文

PiWeb 的 toolNames 只接受内置工具名。空数组进入 chat-only，会连业务扩展一起关闭；非空内置工具选择会保留部分扩展工具，不能当完整白名单。

本机 PI 1.0 类型契约显示：setActiveTools 控制声明工具集；codemode/deferred 工具即使不 active 仍可能被嵌套调用。因此仅设置 active tools 不够。

首期实体项目扩展须：

- 注册唯一 entity_studio 业务工具，内部按服务提供的 schema 分发；每个调用绑定本轮 receipt 和真实 sessionId。
- 在 session_start/每轮开始收窄 active 工具，并用 tool_call 钩子拒绝其他工具（包括嵌套调用）；检查重载后的生效状态。未核实守卫能力即禁止执行轮次。
- 通过业务工具读取登记的方法包，保留版本/hash 与实际读取记录；不依赖通用 read/bash 加载创作方法。
- 使用独立产品项目目录，不在 comfy-ops 开发目录运行。项目提示明确创作身份；通过本轮 prompt/context 钩子构造产品上下文，不将开发 AGENTS/Task Center 指令作为创作规则。最终模型请求需审计实际提示和工具集。
- 服务端独立校验项目权限、读取范围、基准修订和 ActionIntent。不能用模型声称已读/已授权代替记录。

这是本机可信扩展下的调用约束，不是操作系统沙箱；已加载第三方扩展代码本身不受 tool_call 钩子隔离。首期不改用户全局 PI 文件、不默认自动信任工作区、不对现有视频会话加守卫；只对明确绑定的实体会话启用。若共享宿主扩展互相影响导致不能稳定约束，施工应停在接入检查点，改为产品专用原生 PI 宿主配置后再验收，不静默放宽。

看图工具返回实际 ImageContent、assetId/hash 和视图类型，登记缩放/裁剪情况；服务确认 PI 模型有视觉与工具能力。不沿用视频端文字默认模型就宣称可以看图，不暗中改模型或增加第三方识图计费。没有可用视觉配置时保留明确阻塞，文本和画布仍可使用。

## 6. 用户更新与任务

人工编辑写业务事实及持久更新收件箱；界面显示待处理更新，不自动调用模型。下一次用户发送时将更新版本纳入新的 ContextSet。若未来开启主动通知，必须单独定义计费/打断策略，不直接复制影片端自动发送 prompt 的机制。

本地创作 goal 保存在应用数据库；不强制每项目/实体创建远程任务。Codex 施工任务与产品 PI 会话身份独立。未来远程制作模式才追加 Coordinator controller/generation 校验；旧影片流程的校验不变。
