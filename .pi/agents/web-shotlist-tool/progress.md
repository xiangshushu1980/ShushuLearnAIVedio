# 任务进度：web-shotlist-tool（网页拍摄本工具）

## 任务
- 目标：网页拍摄本工具——剧本 → 拍摄本的交互式工具：分段视频提示词（重要颜色标色）、时间轴、渲染输入源
- 当前状态：🟡 进行中（2026-08-12 启动，设计讨论阶段）
- 我负责的文件区：（设计阶段无文件；确定后认领新目录，如 web-shotlist/ 或 tools/shotlist-web/）

## 进度日志（append-only，每条带日期）
### 2026-08-12（第二阶段：开发启动）
- **脚手架完成**：web-shotlist/ monorepo（pnpm workspace + Node22 + Vite7 + React19 + Fastify5 + Tailwind v4 + shadcn 风格组件 + zod4）；packages/shared（类型/校验/tokenizer/标色）+ apps/server + apps/web；typecheck 全绿
- **工具 A/B TS 重写完成**：h3_shotlist_gen.py / h3_prompt_stage2.py / prompt_validator.py → TS（模板忠实搬运 + zod 校验）；DeepSeek client（llm.ts）+ 角色卡/few-shot 注入 + 重试循环 + 自审（--review 等价）
- **API 完成**（docs/22 六节）：projects CRUD + generate-shotlist + generate-prompt + inputs + entities；项目=目录格式（data/projects，gitignored）
- **前端三段式骨架 + 标色完成**：剧本区/拍摄本卡片流+时间轴概览/侧栏输入源/输出区标色（PromptHighlight tokenizer：ref chip+徽章、[Shot N]深底、<d>台词、motion 斜体、声音三层、N/A 灰徽章、bgmdesc 紫）
- **e2e 实测通过**：Alya 海边黄昏剧本 → 工具 A 25s 生成 3 镜拍摄本（预算/锚点/连续性合规）→ ref2va 87s 六段式（角色卡逐字采用、时间戳递增、BGM 跟随拍摄本）→ i2va 62s 三核心段；历史拍摄本导入（scene 缺失宽容）通过
- **踩坑**：pnpm 11 需 approve-builds --all（esbuild）；tsx 闭包共享 m 变量 null 陷阱（tokenizer）；BGM_DESC_RE 正则回溯 bug（\s*+前瞻）；PORT 环境变量被 shell 污染（改 SHOTLIST_PORT）；中文项目 id 白名单
- **发现**：scripts/h3_shotlist_gen.py 当前编译失败（line 191 IndentationError，h3-prompt-agent WIP 损坏）——已提醒该线，未动其文件

### 2026-08-12（第一阶段：设计）
- 任务登记：T-20260812-05（用户拍板：成片试跑告一段落后新开任务讨论）
- 用户确认的成片反馈（本工具需求上下文）：① 镜头主体绑定要写死"主体+配角在边缘"（seg1 教训）② 环境音不随台词变轻（seg2 教训，grow lighter 参数效果持续考察中）③ Ref2VA 站位由 prompt 主导（T-01 已验收 flip）
- 设计讨论启动（待用户输入需求细节）

## 下一步
1. ✅ 脚手架 + 工具 A/B TS 重写 + 三段式骨架 + 标色（2026-08-12 完成）
2. 用户浏览器验收（http://localhost:5173；后端 8787）
3. 输入源解析增强 + 侧栏联动（hover/跳转/返回栈，docs/22 开发计划第 4 步）
4. 实体注册表 + 详情面板（V1 基础版，第 5 步）
5. 导入导出、项目 meta、样式打磨（第 6 步）

## 关键链接
- 相关文档：docs/16_prompt_generator_plan.md（工具 A/B 方案）、docs/17_h3_prompt_writing_rules.md（提示词规则）、docs/21_pipeline_acceptance.md、docs/22_shotlist_web_tool.md（设计+开发计划）
- 代码：web-shotlist/（monorepo：packages/shared + apps/server + apps/web）
- 相关脚本（重写源，未改）：scripts/h3_shotlist_gen.py、scripts/h3_prompt_stage2.py、scripts/prompt_validator.py
- ⚠️ h3_shotlist_gen.py 编译失败（line 191）——h3-prompt-agent 线 WIP 损坏，已提醒
- 相关 mem0 条目：recall "网页拍摄本 工具"；[STATE] agent=h3-prompt-agent（上游任务线）
### 2026-08-12 全域调研：导演台类工具（设计讨论输入）
**结论：无现成"剧本→拍摄本→H3 提示词"独立 Web 工具；现有工具分三类，可借鉴 UI 范式但核心链路（LLM 生成拍摄本）需自研**
**A. ComfyUI 内嵌时间线编辑器（最接近的 UI 参考）**：
- seesee75-commits/ComfyUI-MiniMaxH3-Director（⭐179，LTX Director 移植 H3）：主轨/参考视频轨/音频轨、秒/帧标尺、拖拽素材成 keyframe 或 <Picture i>、每段 prompt zone、编译 prompt 实时预览面板（shot 数/帧数/引用统计/警告）、@char 角色槽、本地 VLM Enhance Prompt 节点、retake/stitch、参考限制强制（≤9图/≤3视频/≤3音频/≤12总）
- j955229/ComfyUI-MiniMax-H3-Motion-Director（⭐23，AIMixer+MotionContext 合并版）：**Prompt chip 可视化引用**（<Picture N> 等 chip 化、素材勾选自动重新编号）、Common References 浮动素材管理器、latent-first Motion Context、Color Re-anchor 防色彩漂移、Source Bridge
- eaglering/MiniMaxRefDirector-ComfyUI（⭐8）：可视化 9 主体管理（名称/描述/参考图/音频）、VLM 提示词增强、尾帧自动转首帧
**B. Web 应用**：
- NickPittas/DirectorsConsole（⭐318）：Cinema Prompt Engineering 规则引擎 + Storyboard Canvas 无限画布 + Gallery + 多 ComfyUI 并行编排（WebSocket 进度）。偏通用电影级管线，非 H3 专用；UI 成熟可参考
- mwilber/ai-storyboard（⭐1）：AI video prompt 规划 web app，过于简单
**C. Skill/协议层**：
- huangserva/h3-film-studio（xyz-video-skill）：story.json → framework.json → storyboard.json → refs → assets → compose 三层 JSON 协议 + 用途驱动参考协议（first_frame/reference_character/prop/composition/style/stage/target_state）+ continuity_mode/chain_from_previous + 质量两阶段审查——协议结构与我们的剧本→拍摄本高度同构，值得对比 schema
- instann/minimax-h3-director（⭐6）：skill 形式（Claude Code/Codex）
**技术栈结论**：无独有技术可抄；FastAPI + 前端单页即可。UI 参考=seesee75 时间线（ruler+tracks+prompt zones+编译预览）+ j955229 chip 标色 + DirectorsConsole 布局成熟度
**UI 设计**：用户建议让 Gemini（Google）出界面设计稿——待用户提供 key/确认渠道后执行
**候选交互**：用户拍板=每镜候选多选一（整本候选=重拍无意义）；当前阶段先生成单本，候选后续加
### 2026-08-12 设计文档定稿（docs/22）
- **全部关键决策已确认**：全 TS 单栈（Node22+Fastify+React19+Vite7+pnpm+Zustand+TanStack Query+Tailwind/shadcn+zod）；分层（审阅层 web / 执行层 ComfyUI）；V1 纯看板三段式+侧栏输入源；实体系统（类型色+重要度+chip/tooltip/详情/返回栈）；标色方案；项目=目录格式+导入；剧本 YAML 预留 branch 扩展点；Python-only 边界=demucs/AudioSep 两脚本（child_process 调用）
- **架构讨论结论**：不用 ComfyUI 实现（执行引擎≠审阅工作台）；不用无限画布作主界面（V2 tldraw 探索视图）；分支=剧本层路径展开（拍摄本线性）；表现变体=候选多选一（每镜，V2）
- docs/22 已写并登记 INDEX；docs_check 通过
- 下一步：脚手架+工具 A/B TS 重写（见 docs/22 开发计划）
