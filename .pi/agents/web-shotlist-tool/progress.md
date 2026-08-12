# 任务进度：web-shotlist-tool（网页拍摄本工具）

## 任务
- 目标：网页拍摄本工具——剧本 → 拍摄本的交互式工具：分段视频提示词（重要颜色标色）、时间轴、渲染输入源
- 当前状态：🟡 进行中（2026-08-12 启动，设计讨论阶段）
- 我负责的文件区：（设计阶段无文件；确定后认领新目录，如 web-shotlist/ 或 tools/shotlist-web/）

## 进度日志（append-only，每条带日期）
### 2026-08-12
- 任务登记：T-20260812-05（用户拍板：成片试跑告一段落后新开任务讨论）
- 用户确认的成片反馈（本工具需求上下文）：① 镜头主体绑定要写死"主体+配角在边缘"（seg1 教训）② 环境音不随台词变轻（seg2 教训，grow lighter 参数效果持续考察中）③ Ref2VA 站位由 prompt 主导（T-01 已验收 flip）
- 设计讨论启动（待用户输入需求细节）

## 下一步
1. 与用户讨论工具形态/功能边界/技术栈
2. 需求确认后写设计文档（docs/22 或独立 doc）
3. 实现

## 关键链接
- 相关文档：docs/16_prompt_generator_plan.md（工具 A/B 方案）、docs/17_h3_prompt_writing_rules.md（提示词规则）、docs/21_pipeline_acceptance.md
- 相关脚本：scripts/h3_shotlist_gen.py（工具 A：剧本→拍摄本 CLI）、scripts/h3_prompt_stage2.py（工具 B：拍摄本→提示词）
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
