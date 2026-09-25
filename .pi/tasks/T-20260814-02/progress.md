# 任务进度：vimax-dissect

> 项目级私有进度（只有本任务线读写）。
> 状态标记：🟡进行中 / ⏸暂停 / ✅完成

## 任务
- 目标：拆解 HKUDS/ViMax（agentic 视频管线开源项目），对标 comfy-ops 剧本→拍摄本→六段式管线（工具 A/B），产出可吸收的设计分析
- 当前状态：✅完成（阶段1框架 + 阶段2一致性层深入）
- 执行者：codex（gpt-5.6-luna），pi 侧调度审查
- 我负责的文件区：`.pi/tasks/vimax-dissect/progress.md`；产出后续交 web-shotlist-tool/h3-prompt-agent

## 进度日志（append-only，每条带日期）
### 2026-08-14
- 认领：T-20260814-02，分阶段执行（阶段1=模块地图+对标框架，控制 token 成本）
- 阶段 1 派发：GitHub API 获取仓库元数据 + README，产出模块地图与对标点

### 2026-08-14 阶段1：框架搭建

> 数据范围：按要求尝试 GitHub API 的仓库元数据与 README 两次请求；执行环境 DNS 无法解析 `api.github.com`，未 clone 仓库、未追加目录 API。改以 GitHub 仓库页面可见的 README 与顶层目录信息完成框架级拆解，不进入实现细节。

#### ViMax 模块地图

1. **叙事规划层（Idea2Video / Novel2Video）**：把概念或长篇文本压缩、扩展为故事、角色、剧本等可制作的结构化叙事资产。
2. **剧本驱动层（Script2Video）**：接收已有 screenplay，沿用其创作意图拆成多场景、多镜头的视频计划。
3. **分镜与镜头设计层（storyboard / shots）**：将剧本场景转换为视觉分镜、镜头顺序、机位与转场等可执行镜头规格。
4. **一致性与参考资产层（references / first frames / continuity）**：管理角色、物体、环境参考图及首帧，并把跨镜头的外观和站位连续性纳入生产链。
5. **媒体生成层（image/video generators）**：通过可配置的图像、视频模型提供商生成参考素材、首帧与短视频镜头。
6. **音视频与成片组装层（producer / final assembly）**：把镜头及角色语音、音效等媒体绑定并合成为最终视频。
7. **Agent Runtime 与工具层（agents / agent_runtime / tools）**：以 Agent Loop 调度规划、修订、artifact 检查、渲染控制和会话恢复，并通过工具调用各生产阶段。
8. **交互与项目工作区层（Web UI / TUI / interfaces）**：提供命名项目、对话式操作、artifact/分镜/渲染预览、上传、配置和 TUI 会话入口。

#### 与我们的对标点

1. **中间产物显式化**：ViMax 把故事、角色、剧本、分镜、镜头作为可检查 artifact；工具 A 可将“拍摄本”设计成同样可持久化、可回看和可修订的中间层，而不是一次性文本。
2. **输入模式分流**：Idea2Video 与 Script2Video 分开，提示我们保留“概念→拍摄本”和“已有剧本→拍摄本”两条入口；当前主线直接对齐 Script2Video。
3. **一致性前置到资产/首帧**：它将参考图、首帧和 camera continuity 放入统一生产链；工具 A 应在镜头表中绑定角色/场景/道具参考与前后镜头锚点，工具 B 的六段式提示词只消费这些结构化锚点。
4. **拍摄本与提示词之间增加镜头规格层**：ViMax 的 storyboard/shots 是叙事与生成器之间的组装层；我们可把工具 A 的每镜头字段固定为景别、机位、运动、动作、声音、时长和衔接，再由工具 B 映射成六段式，而非让 B 重新理解剧本。
5. **组装层独立于生成器**：ViMax 将 video generator/provider 与最终 assembly 解耦；我们的 H3/其他视频模型应视为可替换渲染后端，镜头清单、文件命名、音频绑定和合片规则保持稳定。
6. **交互式修订与断点恢复**：Agent Loop/TUI 支持讨论、局部修订、渲染状态持久化和 resume；工具 A/B 可吸收“按 artifact/镜头局部重跑”的状态模型，避免全管线重生成。
7. **并行化要建立在兼容性分组上**：ViMax 并行生成兼容镜头和素材；我们的并行边界应放在不共享连续性依赖的镜头组，跨段 Motion Context/首帧链仍保持顺序处理。
8. **阶段 1 暂不吸收其具体 Agent prompt 或模型实现**：当前只确认模块边界与接口关系，阶段 2 再选择叙事规划、一致性或组装层之一深入，控制 token 与实现发散。

### 2026-08-16 阶段2 决策（宿主 pi）
- 方向定为「一致性/参考资产层」（references/first frames/continuity）——与当前痛点（角色/场景跨段一致）及 T-20260812-03 设定图体系直接相关
- 执行者由 codex 改为 flash-worker（deepseek-v4-flash，宿主编排循环试点）
- GitHub 直连可达，允许 clone 至 /tmp/vimax 读实现代码

## 下一步
1. 阶段 1 产出后 pi 审查，决定阶段 2 深入方向 ✅（方向=一致性层）
2. 阶段 2：深入一致性/参考资产层 ✅（flash-worker 完成，产出 stage2_consistency.md，5 条可吸收建议）
3. 下游吸收：建议 1/3/5 → T-20260812-05 工具A；建议 2/4 → T-20260812-03 设定图体系 + h3-prompt-agent 工具B

## 关键链接
- 关联文档：https://github.com/HKUDS/ViMax
- 关联 mem0 条目：T-20260814-02（TODO）

### 2026-08-15 阶段2：一致性层深入拆解（flash-worker）
- 完成：clone 至 /tmp/vimax（commit 05a4894）只读源码，产出 `stage2_consistency.md`（数据建模摘录 + 机制说明 + 5 条可吸收建议）
- 核心发现：①角色 static/dynamic 特征分离 + 三视图肖像库（front→side/back 级联生成）；②每镜头 ff_desc/lf_desc + ff/lf_vis_char_idxs 双锚点；③相机树父子依赖 + 过渡视频切帧实现站位/场景继承；④参考图两级筛选（文本粗筛→多模态精筛）+ "Image N" 元素级绑定；⑤全中间件幂等落盘断点恢复
- 建议优先吸收：镜头表加首/尾帧双锚点字段 + depends_on_shot 锚点链（对工具 A/B 都是低成本高收益）
