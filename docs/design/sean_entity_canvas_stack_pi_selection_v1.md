# 实体画布：组件选型与原生 PI 接入 v0.1

> Owner: Sean。2026-10-07。设计建议，待整体设计审阅；未安装依赖、运行构建或性能测试，未创建施工任务。

## 1. 建议

采用 React + Vite + React Flow，卡片用普通 React 组件，服务沿用 Node/Express 技术体系。画布先做自动分区布局，PI 采用 AI 视频端的原生 PiWeb 会话与项目扩展接入方式。第一期不合并实体与视频数据库，不搬入影片制作流程。

“快速”优先理解为开发和交互响应速度；下面是依赖声明与能力对照，没有实测证明某个库最快。界面是否现代主要取决于卡片、排版和交互设计。

## 2. 当前框架兼容性

本地 `reference-workspace/package.json` 与 `film-editor/package.json` 均声明 React/React DOM 19.3.0、Vite 8.3.2、Node >=24、Express 5.2.1。两端使用 React 页面，无需因画布组件重写应用框架。以下版本来自本次 npm 元数据查询，正式施工锁定版本与 lockfile。

| 组件 | 本次版本 / React peer | 许可 | 适配判断 |
|---|---|---|---|
| @xyflow/react | 12.12.0 / >=17 | MIT | 首选：任意 React 卡片、表单、图片、状态与选择交互 |
| @excalidraw/excalidraw | 0.18.1 / 17、18、19 | MIT | 版本兼容，更适合手绘白板；业务卡片集成成本较高 |
| tldraw | 5.5.2 / ^18.2.0 或 ^19.2.1 | 自有 SDK 许可 | React 兼容；生产需有效许可证，不按宽松开源组件采用 |
| react-konva | 19.3.0 / ^19.3.0 | MIT | 版本兼容；底层绘制灵活，业务表单、布局和可访问性需更多开发 |

React Flow 的自定义节点是 React 组件，支持普通 HTML 输入与复杂内容；官方有 Vite 入口。需要引入组件 CSS、明确容器宽高。[自定义节点](https://reactflow.dev/learn/customization/custom-nodes)、[接入说明](https://reactflow.dev/learn)、[包声明](https://github.com/xyflow/xyflow/blob/main/packages/react/package.json)。

Excalidraw 的当前发布依赖范围支持 React 19；仓库主分支包版本与 registry 发布版可能不同，应以锁定发布包为准。[集成文档](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/integration)、[源码包声明](https://github.com/excalidraw/excalidraw/blob/master/packages/excalidraw/package.json)。

tldraw 官方说明 SDK 是 source available，生产使用需要 trial、commercial 或符合条件的 hobby 许可证；不能仅因源码可读就当作 MIT。[许可说明](https://tldraw.dev/community/license)。Konva 中的 HTML 控件通过独立 DOM 层承载，不能自然当作画布图形导出。[DOM Portal](https://konvajs.org/docs/react/DOM_Portal.html)。后两者的取舍是本项目需求判断，并非库的通用优劣结论。

## 3. React Flow 如何适配本产品

业务数据是唯一真源；nodes/edges 只由投影生成，不能将 React Flow JSON 作为实体、流程与结果数据库。

- 固定关闭节点拖动、连接和边更新，禁用默认删除快捷键；保留平移、缩放、选择和键盘聚焦。表单区阻止拖动画布/缩放误触。具体属性以锁定版本 API 为准。
- 卡片分别呈现原文摘要、实体/关系候选、输入、运行和结果；参数、长文和原图进入抽屉或查看器。自定义边带语义标签。
- 工作流依赖边与实体关系边分开。实体关系可能成环，不能一并输入 DAG 布局器。
- 稳定 ID、折叠历史、定位结果；流式文字和采样进度不触发重排，不自动抢视口。

React Flow 提供浏览和交互开关；自动布局需要另行实现。[组件 API](https://reactflow.dev/api-reference/react-flow)、[布局说明](https://reactflow.dev/learn/layouting/layouting)。

首期布局按资料、讨论/候选、输入、运行/结果分区，摘要卡片尺寸有上限，展开细节在侧栏。新增对象只扩展所属区域，持久保存布局版本和视图状态。节点测量后按需修正，异步布局结果必须检查版本，丢弃过期结果。

如生成依赖需要自动排列，可选 MIT 的 Dagre，仅作用于该依赖子图。复杂嵌套组与端口再考虑 ELK；本次 elkjs 0.12.0 元数据许可为 EPL-2.0 OR GPL-3.0-or-later，需按所选许可履行要求，不标注成 MIT。[Dagre](https://github.com/dagrejs/dagre)、[ELK 与 worker 支持](https://github.com/kieler/elkjs)。首期不增加复杂布局引擎强依赖。

性能设计：卡片和回调 memo；按对象订阅变更；聊天 token 流与画布对象状态分离；缩略图代替原图、按需解码、历史折叠。视口裁剪是否开启需以真实卡片验证，不能认为开启必然更快。[官方性能建议](https://reactflow.dev/learn/advanced-use/performance)。

## 4. PI：明确参考视频端原生接入

本地证据入口：[视频接入说明](../../film-editor/PIWEB_IMPLEMENTATION.md)、[扩展说明](../../film-editor/pi/README.md)、`film-editor/server/pi-bridge.mjs`、`film-editor/pi/film-extension.mjs`、`film-editor/src/FilmPiPanel.jsx`。源码通过 codegraph 读取。

### 已有且可借鉴

- 独立 PiWeb 创建原生会话，绑定项目工作区，设置本会话模型并核验状态；不改用户全局默认模型。
- 扩展读取真实 PI sessionId，经服务端绑定获得项目权限；浏览器不接触模型密钥或 bootstrap 凭据。
- 工具目录与 schema、业务修订检查、幂等动作、异步 job/run 查询；不把超时解释为提交失败。
- 人工保存与持久更新收件箱关联；通知 Agent 有变化，由用户决定处理，不因通知自动生成。
- skill 按需读取和实际读取审计；宿主发现 skill 不等于模型已读正文。

### 必须新增或调整

当前 FilmPiPanel 是会话列表与 PiWeb 跳转，五秒刷新状态，未实现画布内聊天。因此右侧内嵌消息、流式回复、工具活动、停止回复和重连是本期新增工作，不能写成直接复用已有组件。先确认 PiWeb 实际支持的会话事件/消息协议，再写薄适配器；若协议不足，应补桥接能力，跳转仅作诊断入口，不替代“不离开画布”的验收。

影片生产写操作目前要求 Task Center 的有效 controller/generation；无绑定讨论是只读。实体首期不强制远程任务，必须新建独立实体扩展及授权适配，不能直接调用旧 FilmPiBridge 然后绕过检查。旧影片权限逻辑保持原契约。

新模式：服务绑定 projectId、discussionId、piSessionId、bindingVersion；提案保存限定当前项目，实际采用由人工服务动作执行。生图另外检查服务签发的 ActionIntent、输入 hash、有效期和一次预算。若未来启用远程制作任务模式，再增加 Coordinator controller/generation 校验。该本地模式是设计新增能力，并非视频端现有能力。

PI 原生宿主可能具有 read/bash/write 等内置工具。业务扩展的受限工具不等于运行环境隔离。首期要确认宿主能对该产品会话限制工具、工作目录和可读文件；不能在未核实前声称 PI 没有 shell。业务写入始终走服务接口，禁止扩展直接写数据库；凭据不放模型可读项目目录。

看图能力也要单独补齐：工具返回实际图片内容及 assetId/hash，确认所选 PI 模型支持视觉。不能以影片已有文字工具推断已具备实体图片审查能力。

## 5. 接入结构与两类事件

```text
画布 + 讨论侧栏
  → 应用 API / PI 消息适配器 → 原生 PiWeb 会话
                                → 实体项目扩展 → 业务 API
业务 API → 项目数据库 / 事件 outbox → 画布 SSE
业务 API → Qwen 固定工作流 → run / 资产 → 业务事件
```

业务事件流负责对象、提案、运行和确认；PI 会话事件流负责消息、工具活动及回复状态。两者分别续传，使用 discussionId、piSessionId、turnId、actionId/runId 关联。回复结束不代表生图结束。

讨论与原生会话绑定持久化；每轮 ContextSet 固定版本，选择变化只影响下一轮。用户改资料保存后写更新收件箱；运行中的 PI 不静默替换上下文或消费新授权。会话压缩/模型切换不改变讨论对象链接。取消回复不取消已有生图。

## 6. 施工前剩余决策

本次可冻结技术方向：React Flow + 自动分区布局；PI 参考视频端原生 PiWeb 与扩展模式。仍需在后续设计中落定独立应用/旧宿主、唯一数据库边界、消息协议、原生工具限制、具体 API/schema 与部署方式。正式施工首个检查点再核验锁定依赖的构建、卡片交互、流式重连与真实素材性能；本轮没有执行这些验证。
