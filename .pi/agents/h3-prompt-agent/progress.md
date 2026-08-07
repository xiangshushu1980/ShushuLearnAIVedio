# 任务进度：h3-prompt-agent（H3 提示词智能体/官方 skill + IR API 接入）

## 任务
- 目标：落地 H3 提示词增强（doc 08 方案）：官方 h3-prompt-writing skill 装好即用；接入海螺官方 H3-Context-IR 提示词 API（用户拍板 2026-08-08：据说效果与自写差别非常大）；评估自建增强层（规则校验/mem0 回环）取舍
- 当前状态：🟡 进行中（2026-08-08 启动）
- 我负责的文件区：.pi/skills/（官方 9 skill 镜像）、vendor/minimax-h3（sparse 克隆，跟踪上游）、scripts/h3_ir_*.py（IR API 调用）、docs/08 更新、本 progress

## 背景（用户决策 2026-08-08）
- 官方 9 个 skill 全部安装：h3-prompt-writing（核心）+ 8 个风格生成 skill（中英双语）
- 官方更新跟踪：vendor/minimax-h3 sparse clone（仅 skills/），commit 8d8824e 起跟踪
- 接入海螺 H3-Context-IR API（官方托管提示词重写，六段式输出）；本地 LM Studio 视觉方案放弃（无安装 + GPU 切换成本高，见下）
- 在线 API vs 本地视觉 LLM 结论：**在线 API 胜出**——本地需卸载 ComfyUI 模型（H3 多模块 transformer+TE+audio_vae 重载估 3-5min）再载 LLM，来回 6-10min，对 2min/条成片的生产线不可接受

## 进度日志（append-only，每条带日期）
### 2026-08-08
- **官方 9 skill 已装** `.pi/skills/`（h3-prompt-writing + 8 风格，含 SKILL.cn.md，共 18 文件）；源 = vendor/minimax-h3（sparse 仅 skills/，996K，commit 8d8824e）
- 确认 h3-prompt-writing 结构：SKILL.md（34 行，识别模式→读 references 指南→重写）+ references/base-en.txt（222 行，T2VA/I2VA/FL2VA/L2VA 三核心段）+ ref-en.txt（341 行，六段式）
- 六段式 = 官方 ref 指南定义（非自创）：subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music；base 模式 = integrated_multimodal_description / overall_soundscape / non_diegetic_music
- 规则校验 = 自建层（官方 skill 无）：六段齐全/标签一致性/时长帧数/语言规范，确定性规则脚本
- **架构决策（用户拍板）**：在线 IR API 为主路径；本地视觉 LLM 关闭（GPU 切换 3-6min/次不可接受，无 LM Studio 安装）
- **IR API 接入**：CN 平台（api.minimaxi.com）；用户提供 key（存 ~/.config/minimax_key，chmod 600，不进 git）；文档拉全（创建/查询/上传三接口）；脚本 scripts/h3_ir_rewrite.py 写完（上传→提交→轮询→落盘，dry-run 通过）
- **卡点解除：账户已充值 25 元，冒烟测试通过 ✅**：纯文本 t2va 4s 全链路 OK（创建→queued→succeeded），输出 1602 字符三核心段增强提示词（integrated_multimodal_description/overall_soundscape/non_diegetic_music），7500 tokens ≈ 0.1 元（定价：输入 5.8/百万，输出 23/百万 tokens）；25 元 ≈ 200+ 次 IR 调用
- 输出质量观察：一句话输入 → 电影级分镜（光线方向/丁达尔灰尘/呼吸节奏/耳部微动）+ 声音层（底噪+呼噜+皮毛摩擦）+ BGM 建议——远超自写水平，"差别非常大"的传闻初步验证
- 已 commit：a6435d2（9 skill + vendor）；docs/08 已更新接入落地节

## 下一步
1. **A/B 实测（GPU 队列占用，需声明）**：自写 prompt vs IR prompt，同 seed 同素材 2-3 条（用 input/start/ 起始图或用户实际场景）
2. IR 输出与 ComfyUI H3 工作流对接：六段式 prompt 直接填 ref2va 节点
3. 规则校验层优先级重估（IR 输出天然合规；校验留给本地 skill 路径再定）

## 关键链接
- 上游：github.com/MiniMax-AI/MiniMax-H3（skills/ 目录），vendor/minimax-h3 本地镜像
- 官方 skill 安装方式：npx skills add ... --skill h3-prompt-writing（我们走 vendor 复制，未用 npx）
- API 文档：platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir（EN）/ platform.minimaxi.com（CN）
- 相关文档：docs/08_h3_prompt_agent.md（方案调研）、docs/14_skill_governance.md
