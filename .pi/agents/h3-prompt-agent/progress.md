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

### 2026-08-08 生成器前期准备执行（第二轮）
- **IR 样本库建成 13 条**：experiments/ir_samples/ = 8 新（4 t2v 多风格 + 4 i2v 真实素材 Alya/森林/甜点）+ 3 官方（t2v 10s/i2v 8s/ref2v 5s，从 vendor README 提取含 token 用量）+ 旧 A/B 2 条；脚本 scripts/h3_ir_sample_batch.sh（可复用，t2v/i2v 分段）
- **官方示例（#4）✅**：README full-2k 3 case 全提取；**发现官方脚本媒体格式**：image_url/video_url/audio_url 需嵌套 `{type:{url:...}}` + 本地文件传 mm_file:// 引用（修复 h3_ir_rewrite.py 两处 bug：file_id 嵌套读取 + 媒体嵌套结构）
- **社区 skill（#3）benjiyaya 拆解 ✅**：7 维创作增强框架 + 时长→镜头预算 + 运动语法（type+amplitude+speed）+ 10 坑 + 验证清单 + showcase 7 个完整 pattern（含 SeeDance→H3 转换）；蒸馏入 docs/17
- **docs/17_h3_prompt_writing_rules.md 新建**：生成器合成规则手册（模式契约/镜头规划/对话声音语法/Ref2VA 六段式/七维增强/高级 pattern/验证清单）
- **docs/18_ir_sample_teardown.md 新建**：13 条样本逐条拆解（开场三件套/每镜描述层次/声音三层/配乐公式/六段式规律/i2v 读图锚点）
- **新发现（mem0 备选）**：① IR 会加戏（alya_beach 输入海边→输出夜景街道+海滩两幕）——黑盒不可控再实证；② diegetic 音乐可入 soundscape（与社区规则出入，以官方输出为准）；③ i2v 比 t2v 长 2-3 倍（图驱动细节）；④ 媒体嵌套结构 bug 修复
- docs/16 收集清单状态已更新（#1/#2/#4 ✅，#3/#5/#6/#7 🟡，#8 待）

### 2026-08-08 视频验收批次（路线 1 收尾）
- **Pro 确认提示词**：deepseek-v4-pro 10 场景全部合规（few-shot+校验器+重试；max_tokens 24000；reasoning effort 参数化）
- **关键校准**：IR 实测 i2v 输出本身不带 [Shot 2] 标签（[Shot 1] 段内嵌切点），t2v 才带——校验器 i2v 规则对齐 IR 基准（降为 warn）；重试逻辑修复（最后一次生成也校验）+ --allow-warn
- **视频验收 12 条完成**（t8 960×544 同 seed 20260810）：onsen/wow/cyberpunk/streetfood/alya_beach/dessert × DS-Pro/IR，输出 ComfyUI/output/video/h3_prompt_ab/，对比页 experiments/prompt_compare/compare.html（左右并排+打分表）；耗时 100-245s/条
- **音频响度检查**：onsen DS 版 -39.7dB 近静音 vs IR -15.9dB（安静场景+turbo 静音规律 DS 未规避，**待用户验收确认**）；其余 5 场景 DS/IR 均在正常档（-14~-35）
- i2v 提交坑：LoadImage 需要子目录前缀（start/xxx.png）

### 2026-08-08 设计定稿轮（H3 模式梳理 + 工具架构确认，会话收尾）
- **H3 模式全景**：FL2VA 模型（T2VA/I2VA/FL2VA/L2VA 图片模式，无视频输入、无多图参考、Turbo 加速 ✅）+ Ref2VA（图≤9/视频≤3/音频≤3，多图 slot + <Subject N>，唯一视频入口，无 Turbo 只能 std 20 步）+ IR（预处理）+ Regenerate-2K（未测）。多图参考（多角色/物品/场景固定）= Ref2VA 独有（实测多图零速度惩罚，甜点 2-4 张，九宫格必须拆开）
- **用户硬需求确认**：后续要 i2v + 主角/道具/场景跨画面固定 → 三层锚定（角色卡文本 + Ref2VA 参考图 + <Subject N> 标签）；生产双轨=单主角 i2v+turbo 快车道（帧链跨段） / 多角色物品 Ref2VA std 慢车道
- **工具架构确认（用户对齐）**：工具 A=剧本→导演拍摄本（标杆=IR 理解力，不求短期超越）+ 工具 B=拍摄本→IR 级提示词（= 替代 IR 的格式化职能，与 LightX2V Qwen LoRA 目的同，但多拍摄本控制点）；IR 降级为可选精修层（输入已确认拍摄本，不是模糊剧本）；做成一脚本两阶段（--stage1/--stage2 断点审阅）
- **模型**：deepseek-v4-flash（试错）/ pro（精写），用户授权随便用；纯文本模型看不到图（i2v 首帧靠文本描述注入，一致性靠角色卡+参考图）
- **FL2VA 图用法边界**：槽位语义锁死（first/last_frame），但 prompt 可指定图内元素选择性延续（提示词主导>图锚定，实测）；物品/主题参考槽只在 Ref2VA
- **onsen 音频问题待验**：DS-Pro 版 -39.7dB 近静音 vs IR -15.9dB（安静场景+turbo 规律 DS 未规避）

## 下一步（明日开工）
1. **工具 A**：剧本+参数头（YAML）→ DeepSeek 分镜表/导演拍摄本（含镜头/景别/运动/时长/角色卡引用），2-3 场景验证
2. **工具 B 升级**：拍摄本 → 三核心段（快车道）/ 六段式（Ref2VA 慢车道），few-shot 换官方 ref 示例
3. **全链路试跑**：Alya 海边/舞台剧本 → 拍摄本（用户审）→ 六段式 → Ref2VA 出片 → 与 IR 版并排
4. 用户视频验收打分（compare.html，重点 onsen 音频）

## 关键链接
- 上游：github.com/MiniMax-AI/MiniMax-H3（skills/ 目录），vendor/minimax-h3 本地镜像
- 官方 skill 安装方式：npx skills add ... --skill h3-prompt-writing（我们走 vendor 复制，未用 npx）
- API 文档：platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir（EN）/ platform.minimaxi.com（CN）
- 相关文档：docs/08_h3_prompt_agent.md（方案调研）、docs/14_skill_governance.md
### 2026-08-08 第二轮（turbo 步数矩阵，全部已标注耗时）
- 8 条 turbo 批完成：t6（132-141s/条）+ t8（161s/条），同 seed 同 prompt 960×544 240帧
- **完整矩阵（耗时必标注纪律已固化 mem0）**：
  | 配置 | 耗时 | A_ir清晰度 | B_ir清晰度 | B_raw清晰度 |
  | std 20步 | 300s | 57.2 | 56.3 | 38.2 |
  | t4 | 115s | 42.3 | 41.3 | 29.6 |
  | t6 | 138s | 43.1 | 47.4 | 33.1 |
  | t8 | 161s | 43.2 | 52.8(94%) | 38.0(追平) |
- **音频规律确认**：A_raw（含"宁静唯美"）+turbo 任意档 → 静音 -48dB（跨批复现）；IR 的 overall_soundscape 段稳住音频
- **用户反馈**：8 步效果不错，待用户时间再确认定档（生产候选 = t8+IR，161s/条 vs std 300s）
- IR 成本换算：1 毛 ≈ 7500 total tokens（输入5.8/百万+输出23/百万，输入输出约 6:4）；输出每 1000 tokens ≈ 2.3 分；10s 复杂场景增强 prompt（~2800字符）≈ 1.4 毛
- 提交脚本：scripts/h3_ab_submit.py（std 批）、scripts/h3_ab_turbo_submit.py（turbo 批，t2v 分支）
- 发现 h3_turbo_runner.py t2v 分支 bug（未建节点6却引用）——已用独立脚本规避，未改其文件（文件认领纪律）
### 2026-08-08 生成器前期准备（讨论结论落盘）
- **用户拍板**：自建提示词生成器，动机=**控制**（IR 黑盒不可控：模糊进→增强出，不能指定风格/镜头/氛围）
- 最终目标：AI 根据剧本出视频；当前阶段：了解提示词产出环节 + 收集资料
- 设计结论：分层管线（剧本→分镜表→英文提示词→ComfyUI），控制点=分镜表+最终 prompt；IR 降级为可选精修层；敏感内容走本地生成器不依赖 IR（用户拍板，不做敏感词规避表）
- 生成引擎：DeepSeek V4 flash（试错）/ Pro（精写），用户已有 key
- 工具形态：方案 A 剧本文件+参数头优先（不做 Web UI 起步）
- 收集清单 10 项 → docs/16_prompt_generator_plan.md（含 IR 样本库/社区 skill 参考/SeeDance 镜头词汇表/风格与声音词汇库/经验蒸馏）
- 本轮 A/B 完整数据已入 mem0（IR 效果/步数矩阵/音频规律/成本换算）
