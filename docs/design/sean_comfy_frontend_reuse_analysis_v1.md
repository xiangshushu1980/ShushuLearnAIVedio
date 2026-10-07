# ComfyUI 前端复用边界分析 v0.1

> Owner: Sean。2026-10-07。源码静态调研与设计建议；未克隆/修改 ComfyUI，未启动服务、安装依赖、运行构建、测试或生成。用户已确认独立项目和 Vue/TypeScript 方向；完整施工设计尚待审阅。

## 1. 结论

建议建立以官方 ComfyUI 前端为基础的独立项目，锁定上游版本，采用有限改造加独立业务模块。首期不抽取一个通用 ComfyCanvas SDK，不重写节点控件，不改变共享 ComfyUI 后端。这里的独立项目指独立仓库/部署及业务数据，同时保留前端代码的上游来源和更新关系。

不是“换成 Vue 即无缝”。实际复用的是前端应用运行环境、节点注册、图加载、控件、插件加载和运行展示；业务层仍需开发。不能承诺所有第三方节点无修改兼容。

## 2. 源码证据

本次直接检查官方仓库 main 源文件与官方扩展文档，检索本项目升级记录作对照。main 是移动引用，读取期间页面缓存也可能不同；未固定 commit，不将这些源码行号作为施工基线。施工前必须固定 release/tag 与 SHA，再复核下列接口。GitHub commit API 本次无法通过网页工具访问，未据此猜测 SHA。

| 证据 | 事实 | 对本项目的判断 |
|---|---|---|
| [package.json](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/package.json) | private 应用，含 workspace 依赖；本次显示 1.57.0、Node >=26.8.2 <27、pnpm >=11.3 | 不能假定 npm 安装一个画布组件即可使用；新应用工具链也不能照搬旧 Node 24 |
| [GraphCanvas.vue](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/components/graph/GraphCanvas.vue) | 依赖 comfyApp、多个 Pinia store、布局和持久化；结合 Canvas 与 Vue 节点层 | 抽离会牵动大量应用依赖；优先保留完整运行环境 |
| [app.ts](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/scripts/app.ts) | graph 加载与清理、扩展钩子、工作流状态相互关联 | 首期按单一活动图设计，不假设多个完整编辑器实例能直接并列挂载 |
| [ComfyExtension 类型](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/types/comfy.ts) | 有初始化、节点注册、控件、命令、菜单及选择工具钩子 | 优先通过扩展增加对象操作，缺口通过少量显式接缝补齐 |
| [扩展加载](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/services/extensionService.ts) | 从后端取得扩展并动态加载，先加载核心扩展 | 必须兼容资源路径与核心模块导出，不只是取 object_info |
| [API 客户端](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/scripts/api.ts) | 定义加载、提交、媒体和 WebSocket 客户端身份有关联 | 通过统一网关适配，业务 runId 必须映射 prompt_id 与客户端身份 |
| [Vite 配置](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/vite.config.mts) | 分开代理 API、WS、扩展等；开发 /api/extensions 可返回空列表 | 不能原样使用默认开发代理宣称插件兼容；开发/生产均要明确加载策略 |
| [执行序列化](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/utils/executionUtil.ts) | 同时生成 workflow 与 API output；执行图转换有虚拟节点和子图处理 | 保存可视图与提交图的关联快照，避免业务对象进入执行序列化 |

官方支持通过 WEB_DIRECTORY 和 app.registerExtension 扩展现有客户端；这是扩展机制，不是完整编辑器嵌入 SDK。[官方扩展说明](https://docs.comfy.org/custom-nodes/js/javascript_overview)。

本地 [2026-09-12 升级记录](../dev/comfyui_node_update_20260912.md) 记载前端 1.52.7；这是历史安装证据，本次未访问运行环境核对，不能称为当前安装版本。上游 main 的 1.57.0 也不直接作为选定版本。

## 3. 三种工程方式

| 方式 | 首期判断 | 原因 |
|---|---|---|
| 从 Vue 工程抽取 GraphCanvas 组件 | 不采用 | 强耦合应用状态、插件和初始化，接近另造运行外壳 |
| 仅向原版 ComfyUI 安装普通插件 | 不作为主体 | 有利于小功能，但本产品需要独立项目数据、导航、讨论及授权边界 |
| 独立维护官方前端的有限改造版本 | 推荐 | 直接保留节点能力，业务模块独立，允许有明确范围的导航/画布接缝 |

独立仓库建议保留 upstream remote、锁定基线和补丁清单。新业务代码集中在 Sean 模块，不整体重排上游目录、不一开始删除大量上游模块。优先使用扩展钩子；需改核心的接缝逐项记录输入输出与升级检查项。

## 4. 创作层与真实流程如何共存

采用同一个应用、同一套画布技术和一致的导航，但创作图与执行图分别持久化。首期只保留一个活动画布：进入生成节点时切换真实 workflow，面包屑返回创作图，恢复原视口/选择。无需跳转外部页面，不要求同时挂载多个 ComfyApp。

创作层包含 Source、Entity、Relation、Discussion、Generation、Result 的投影节点和语义线。它们是业务对象，不注册成可执行 Python 节点。复用 LiteGraph 浏览与连接呈现，定制业务节点渲染及自动布局；Vue 节点渲染对这些非后端节点的支持需在锁定版本核实，不能假设 registerCustomNodes 即保证所有 Vue 控件自动出现。

执行层加载真实 ComfyUI 可视工作流及对应输入修订，复用原生节点、控件和扩展。节点的完整技术细节可查看；连接、增删、任意粘贴、自动排队和全局中断等入口关闭，只有登记的输入字段可编辑。快捷键、菜单、拖入文件、工作流切换均纳入约束，不能只隐藏按钮。

不将创作图当 ComfyUI 子图提交。业务生成节点引用固定模板和版本；“进入流程”是产品导航。原生可执行子图属于模板内部能力，与项目/实体层级不同。

首期流程显示当前草案或指定历史 run，标题明确两者。历史 run 只读，显示其当时模板、输入与节点结果；切换到新草案不会改写旧图。生成期间离开执行视图仍由服务观察 run。

## 5. 固定工作流与双快照

模板登记至少包括：templateId/version、UI workflow JSON、API prompt 模板、允许修改字段到 nodeId/inputName 的映射、依赖节点包、前后端版本范围。只保存 API JSON 无法完整恢复原始布局、控件和分组；自动导入重建不等同原图。

用户或 PI 修改草案后，同步允许字段与展示图；服务编译并校验固定模板，建立不可变 inputRevision。实际提交以服务编译结果为准，不把任意浏览器 graphToPrompt 输出直接当授权依据。若模板使用前端虚拟节点或特殊控件序列化，必须登记转换规则或提供对应受控编译适配；不能凭字段替换保证全部插件兼容。

每个 run 保存 UI workflow 快照/hash、实际 API prompt/hash、模板版本、输入版本及 nodeId 映射。提交前比较规范化执行结构与允许参数；差异不符合契约则阻止提交，不能展示 A 图执行 B 图。生成前 seed 等自动变化必须进入实际输入快照。

首期只承诺 Qwen 实体流程所需节点集合，不承诺任意导入流程可执行。缺少 UI workflow 或必要扩展时标明无法完整查看并补齐，不能拿示意图当真实图。

## 6. 业务服务与共享 ComfyUI

```text
独立 Vue 创作应用（保留 ComfyUI 前端运行环境）
  ├─ 项目 / 实体 / 讨论 / 采用 → 业务 API → 私有业务库与素材库
  ├─ PI 侧栏 → 消息桥 → 原生 PiWeb → 实体扩展 → 业务 API
  └─ 真实工作流查看 → 节点定义 / 控件 / 资源适配
业务 API → 单次授权与固定模板编译 → 现有 ComfyUI 服务
业务 API ← prompt_id / 历史 / 执行事件 → run → 画布业务事件
```

建议同源应用网关：独立命名空间 /studio-api 承载业务；ComfyUI 原生路径由显式路由适配。生产网关需支持 WebSocket、预览二进制、图片/视频、上传、扩展 JS/CSS 和兼容脚本导出；不能直接把未知 /api 路由全部转发。原生内部端点仅在确有需要时接入。

生成提交唯一经过业务授权服务。原生 queuePrompt/快捷键/插件调用也必须进入该路径或被拒绝；纯 UI 禁用不构成服务端约束。不开放共享实例的全局 interrupt、free、安装更新等操作。

执行事件按本应用 run 与 prompt_id 关联，只展示当前项目任务。原生前端 client_id 与业务提交 client_id 必须明确一致或由适配层重映射，否则节点预览和进度可能无法匹配。图已切换时仍保存后台 run 事件，不能按当前画布节点 ID 误投到其他流程。共享队列不会因切换视图停止。

第三方扩展可能覆写全局 app/API；首期列出 Qwen 必要扩展允许清单，不自动加载全部插件并宣称隔离。独立部署不修改现有 ComfyUI UI、服务进程或其他使用者的设置。

## 7. 维护与许可边界

前端 package.json 声明 GPL-3.0-only；复用并修改完整前端的发行应按其许可处理，不能继续写成 MIT 应用。[官方 LICENSE](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/LICENSE)。这影响代码分发方式，未据此推定所有独立后端或素材必须采用相同许可；具体发布方案另定。

锁定前端与已用节点包版本，保留版本清单及上游差异。升级检查集中在初始化/扩展加载、业务节点投影、图切换、控件序列化、提交授权和执行映射。上游自带 Agent 面板与本产品 PI 不是同一系统，不能直接继承其会话、身份和凭据；按锁定版本禁用或替换入口。

## 8. 后续设计与施工检查点

后续细化已汇总到 [首期施工设计](sean_entity_canvas_build_plan_v1.md)，包含候选锁定版本、Qwen 模板资产、业务 schema/API 与网关；[PI 协议](sean_entity_canvas_pi_transport_v1.md) 已分析原生消息和工具限制，[临时小说](sean_entity_canvas_experiment_story_v1.md) 已提供两章两场草案。以下仍是施工阶段检查点，尚未执行。

用户确认整体方案并启动施工后，首先验证：

1. 锁定版本完整运行环境能连接现有服务，加载 Qwen 必要控件与扩展。
2. 创作图 → 真实 workflow → 返回，视口/选择/草案恢复，无业务节点进入 prompt。
3. 允许参数修改在 UI 与 API 快照一致，所有生成入口受单次授权控制。
4. 真实 run 的节点进度、预览和结果映射正确，切图/刷新不重复提交。
5. 画布内原生 PI 对话与多对象 ContextSet、提案及反馈生图闭环成立。

本轮覆盖官方源码、官方文档与本地历史记录；未覆盖运行实例、第三方插件源码全量审计或性能实测。结论是可实施的架构建议，尚不是已验证兼容性报告。
