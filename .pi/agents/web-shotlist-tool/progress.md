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
