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

### 2026-08-09 双轨盲区补测（18 case 全完成，无 OOM）
- **快车道定档实测**（fl2va fp8+sage，IR 级 prompt）：i2v turbo8 8s=111s（=t2v 零惩罚）、5s=94s；firstlast 静态双锚 turbo8=123s（+12s 便宜）；turbo4=90s（收益递减）；1024 档=171s
- **慢车道定档实测**（ref2va int8）：1/2/4图 std20 = 130/133/144s（4图仅 +11%）；std14=82s（含 TE 缓存命中，估 ~120s）；4图@1024=226s 不爆显存（21.9GB）；**ref2va+turbo lora 兼容但无价值**（123s > std14）
- **帧链硬桥判死刑（关键负面）**：生成帧做 first_frame 锚定 SSIM 0.14-0.52（静态图 0.99）；std20 比 turbo8 更差 → 非步数因素，生成帧分布 OOD。快车道跨段改：独立段+静态锚+prompt 连续性 / firstlast 静态双锚转场段
- 显存全批峰值 ≤22.3GB，4图+1024 也安全；监控纪律生效（阈值 23.6GB 告警 + OOM abort，未触发）
- IR 级长 prompt 使速度 vs turbo-pilot 短 prompt 数据差 ~1.7x（A1 114s vs 67s），对比需折算
- 产物 ComfyUI/output/video/h3_gap_test/（18 mp4）；数据 docs/19_h3_dual_track_gap_test.md；runner=scripts/h3_gap_runner.py（支持帧链依赖/断点续跑/OOM abort）

## 下一步（明日开工）
1. **工具 A**：剧本+参数头 YAML → DeepSeek 分镜表/导演拍摄本（镜头/景别/运动/时长/角色卡引用），2-3 场景验证——补测结论已入设计：跨段不用帧链硬桥，转场段用 firstlast 静态双锚
2. **工具 B 升级**：拍摄本 → 三核心段/六段式，few-shot 换官方 ref 示例
3. 全链路试跑：Alya 海边 → 拍摄本（用户审）→ Ref2VA 出片（std14/20，多图 4 张内）
4. 用户视频验收打分（compare.html，onsen 音频）+ 补测产物可顺带归档

### 2026-08-09 工具 A stage1 落地（剧本→导演拍摄本）
- **scripts/h3_shotlist_gen.py 完成**：剧本（YAML 参数头+正文）→ DeepSeek → 拍摄本 YAML（镜头/景别/运动 type+amplitude+speed/时长/角色卡/声音三层/连续性），内嵌校验（时长和=总时长±1s/镜头预算/字段齐全/camera.type 枚举），自动重试，纯 YAML 落盘
- **3 场景验证全过**：alya_beach（8s first_static 日系清新 3镜 中全景→中近景→全景）、alya_stage（8s firstlast_bridge 舞台 3镜）、cyberpunk_rain（10s independent 赛博朋克 3镜 无角色卡）；chain 策略正确写入首镜 continuity
- 角色卡机制启用：experiments/shotlist/rolecards/alya_v1.md（从 IR 实测 i2v_alya_beach 提取外观锚定）；剧本库 experiments/shotlist/scripts/
- 踩坑：YAML 1.1 sexagesimal 把 16:9 解析成 969 → 参数头加引号 + 脚本 str() 双保险；system prompt 里 `{camera_type}` 需避开 .format 占位
- 拍摄本 = 中文导演控制面（用户审阅），工具 B 负责英文化合成——下一环节

## 下一步（明日开工）
1. **工具 B stage2**：拍摄本 → 三核心段（快车道）/六段式（Ref2VA 慢车道），few-shot 换官方 ref 示例；拍摄本 YAML 直接消费
2. **全链路试跑**：拍摄本（用户审）→ 六段式 → Ref2VA 出片 → 与 IR 版并排
3. 用户视频验收打分（compare.html，onsen 音频）+ 工具 A 产物可并入对比

### 2026-08-09 工具 B stage2 + 全链路试跑（闭环打通）
- **scripts/h3_prompt_stage2.py 完成**：拍摄本 YAML → 三核心段（i2va 快车道）/ 六段式（ref2va 慢车道），消费工具 A 输出 + 角色卡注入，few-shot=官方 IR 样本（i2va）/ ref-en 指南（ref2va），复用 prompt_validator 确定性校验
- **文本端全链路通**：剧本→拍摄本→提示词，i2va 与 ref2va 各一次通过（时间戳 2.5/5.0 与拍摄本精确对齐、label 定义正确、角色卡逐字保留）
- **视频端试跑（E 批）**：E1 快车道 i2v turbo8（stage2 提示词）首帧锚定 SSIM=0.992 **= IR 版基准**，音频 -17.1dB 正常；E2 慢车道 ref2va 4图 std20 音频 -18.2dB 正常、显存 22.0GB 安全；速度与 IR prompt 相当（E1 计时 420s 含队列排队 ~300s，实际运行 ~120s）
- 踩坑：DeepSeek reasoning 模式 max_tokens 给不足（4000）会被思考吃满导致正文空——review/stage2 统一 max_tokens 16000-24000；.format 占位符两处（{camera_type}/{style}）
- 工具 A --review 导演自审验证有效：抓到真实问题（屏幕方向矛盾/一镜双动作/chain 与 camera 不一致/配饰锚点命名不统一）
- 工具 A 非确定性：同剧本重跑镜头结构会变（多 draft 抽卡特性，可多次跑选满意版）
- 队列纪律实证：E1 慢 4 倍原因是 turbo-pilot 线任务先入队（runner 计时含排队）——跑批前查 /queue 确认空位

## 下一步
1. **反推优化第一轮**：对比 E1/E2 产物与 IR 版（补测 A2/D2），客观指标（音频/锚定/时长）已齐；拍摄本层面可让用户审阅三个拍摄本（experiments/shotlist/）
2. 按反推结果针对性补模板库（docs/16 清单 #3/#5/#6/#7）
3. 用户验收打分（compare.html 12 条 + onsen 音频）

### 2026-08-09 反推第一轮 + 首帧底图规范（用户发现图被压缩）
- **切点检测工具**（/tmp/h3_cutdetect.py，帧差峰值）：模型 100% 执行提示词声明切点——E1/E2（声明 2.5/5.0）实际 2.42-2.50/4.62-5.04s；A2/D2（IR 声明 1.5）实际 1.54s。拍摄本 3 镜结构在视频中可见 → 镜头规划语法有效，工具 A/B 可信
- **控制有效性验证（E3）**：改拍摄本时长 2.5/2.5/3.0→2.0/3.5/2.5，重跑出片切点跟随 2.00/5.25s → 拍摄本改什么视频变什么，控制点生效
- **首帧变形坐实（用户观察"图被压缩"）**：first_frame 纯拉伸注入，方形底图变形传导产物（产物首帧 vs 无变形参考 SSIM 0.474 vs 拉伸输入 0.992）；16:9 原生底图 0.993
- **适配库建成**：ComfyUI/input/start/169/（35 张 center-crop 16:9，偏上保脸）；原生 16:9 仅 alya_169；Alya LoRA 已被清理（anima 工作流暂不可用，重生成需重新下载 LoRA 或 img2img 扩图）
- 规则：i2v 首帧强制 16:9（docs/19 + mem0 global 已落）；尾帧 center-crop 任意比例；ref2va 参考图任意比例
- 产物：E3（时长控制）170s、E5（16:9 首帧）130s，全指标正常

## 下一步
1. 16:9 角色图库补强（重新下载 Alya LoRA 或 img2img 扩图）——生产快车道底图储备
2. 反推第二轮：可用 E3/E5 与 E1/A2 四产物做同场景对照组
3. 用户审拍摄本 + compare.html 验收打分

### 2026-08-10 角色图库重建（Alya/Yuki LoRA + 16:9 首帧）
- **anima 生图栈修复**：发现 qwen_3_06b_base.safetensors（ANIMA 文本编码器）也被误清，从 HF circlestone-labs/Anima 补回（1.19GB，hf-mirror 直连）；qwen_image_vae 仍在
- **Alya LoRA ×3 重下**（civitai 匿名下载）：roshidere 28695（72MB，原版）/ tokidoki 557213（39MB）/ ayra 955584（109MB）；热门的 558240（7051 下载）需登录未取
- **Yuki LoRA ×1**：yuki_suou_v1120706（civitai 1000015，114MB）
- **16:9 角色首帧生成 4 张**：alya169_tokidoki/roshidere/ayra + yuki169_stand（768×448，input/start/169/），全部成功——首帧底图库现共 39+4 张
- docs/02 模型清单已同步

## 下一步
1. 反推/生产储备已完成：快车道（i2v turbo8 + 16:9 首帧）与慢车道（ref2va 4图）配置 + 角色图库就绪
2. 待用户：审拍摄本（experiments/shotlist/3 个）+ compare.html 12 条验收打分（onsen 音频）
3. 工具链可选增强：拍摄本模板库（docs/16 #3/#5/#6/#7）按需补

### 2026-08-10 方法论落地：规则分层 + IR 逆向学习（用户方法论确认）
- **规则分层体系确认**（用户质疑"规则千千万怎么选"后定稿）：参数层(用户控制)/规则层(判断性按阶段注入)/样本层(IR few-shot)/代码层(校验器)/反馈层(视频指标剪枝)；能代码化的不进提示词
- **IR 逆向全量完成**：scripts/h3_ir_shotlist_extract.py 逆向 13/13 条 → experiments/shotlist/ir_reverse/（镜头结构/景别/机位/声音三层）
- **工具 A 升级**：--fewshot（IR 样本注入）+ --shot-style（分镜剪辑默认|长镜头流）+ 规则 8-10（镜头信息密度/音乐场景驱动判断）
- **验证**：海边 few-shot 后镜头内信息密度达 IR 级（动作链+跨镜配乐衔接）；舞台长镜头流 1 镜 8s 对齐 IR 策略，bgm 自动写"无（演出即 diegetic）"——IR 专业判断被规则吸收
- docs/17 补音乐场景判断规则；docs/20 对比结论 + 效果落盘

## 下一步
1. 拍摄本样本库按类型归档 + 代表样本标注（3-5 条够用）
2. 全链路复测：新版拍摄本 → stage2 → 出片 → 切点/音频/SSIM 验证（与 E 批对比）
3. 待用户：compare.html 验收 + 拍摄本审阅（新版）

### 2026-08-10 新管线全链路验收（用户拍板：删旧验收，测新管线）
- 旧验收体系删除：compare.html ×2 + README_验收.md + http server 停止（旧 12 条视频产物保留 output）
- **F 批出片 5 条全达标**：切点执行 100%（海边 3 镜 3.54/5.92、雨夜 3 镜 2.88/6.12、舞台长镜头零切点）、音频全正常 -14~-21dB、速度无回归（docs/21）
- **核心发现：首帧锚定 = 首帧图与 prompt 场景一致性**（解释全部历史数据）：场景一致 0.99 / 场景冲突 ~0（模型重绘首帧，F3 海边图+舞台prompt 归一化结构 SSIM -0.086）/ 生成帧 0.14-0.52 / 场景匹配 0.993（F3b 舞台版首帧图验证闭环）
- 生产规则：i2v 首帧必须匹配拍摄本第一镜场景（按场景备角色图：海边版/舞台版/夜景版）；图库 input/start/169/ 新增 aliya169_stage（暗场舞台版）
- 工具 A few-shot/shot_style 升级版全链路验证通过（docs/20 效果确认）

## 下一步
1. 工具 B 首句防重绘规则（instruction line 注明首帧画面=参考图内容）
2. 图库按场景归档（169/ 子目录：beach/stage/night/…）
3. 角色图库扩充（Yuki 场景版等）+ 拍摄本 schema 加 scene 字段

### 2026-08-10 音乐策略定版（用户决策：视频不生成 BGM，后期配乐）
- **问题确认**：短片内 BGM 无法连续（每段独立生成，旋律跨切点断裂、跨段无记忆）；音量层面平稳（F1 三段 -15.0/-14.2/-14.4dB）但内容不连续
- **用户方案 = 社区主流**：Sogni 官方示例 "Everything is diegetic and natural. No music of any kind."；Medium/Scenario 文章；MiniMax 官方 Music 2.6 独立音乐线——音乐后期配
- **改工具 B**：i2va/ref2va 模板 non_diegetic_music 默认 N/A；diegetic 声音（环境音/音效/对话/演出音乐）保留
- **对话/音效社区共识**：对话用官方 <d>[语言]</d> 语法保留生成；音效 diegetic 保留在 soundscape
- docs/17 音乐策略规则更新；本地 BGM 管线 docs/13（MusicGen/ACE-Step）为后期配乐准备

### 2026-08-10 工具链 vs IR 公平对比（G1）+ 无 BGM 版验证（H1）
- **G1 对比结论（同参数唯一变量=提示词）**：切点/音频持平；**首帧锚定工具链完胜**——IR 加戏改开场（夜景街道 vs 海边剧本）→ 首帧重绘 SSIM -0.127；工具链忠实执行拍摄本 → 0.989。IR 黑盒不可控再实证（docs/21）
- **H1 无 BGM 版**：切点 100%、音频 -17.5dB 正常——音乐策略定版后生产管线成立（BGM 后期配 docs/13）
- 老视频已删：h3_gap_test/ 仅保留对比集 6 条（F1/F2/F3b/F4/G1/H1）

### 2026-08-10 音乐控制调查（用户拍板：后期分离以后再说）
- **4 种 prompt 写法实测全无效**：non_diegetic_music N/A（H1）、显式 "No background music of any kind"（H2）、全静音指令（H3）、极端否定描述（H4）——产物频谱均有音乐谐波（87Hz 基频+泛音序列、440Hz 标准音），RMS 0.23 非静音
- **结论**：H3 音频模块音乐先验与 prompt 解耦（训练数据普遍带音乐）；社区"specify no music" 在我们 4K 量化环境不成立
- 用户决策：后期分离以后再定（demucs 候选）；当前生产接受自带氛围音乐
- 模板保留 N/A + 显式句（意图表达，无坏处）；docs/17 已记录
- 视频清理：H1/H3/H4 删除，H2 保留为当前生产版参照；对比集 = F1/F2/F3b/F4/G1/H2

### 2026-08-10 音乐控制逐步对比（修正 h3-nobgm-test 结论）
- **V 系列逐步对比完成**：V1 复现 h3-nobgm-test（苹果 t2v int8 std20 N/A = -60.7dB 近静音）✓；V2 同配置换海边场景 = -39.0dB（有环境音）→ **静音是场景无声音内容的自然结果，非 N/A 功效**
- **对照矩阵**：H2(turbo8)=-19.2dB / T1(fp8 std20)=-28.5 / T2(int8 std20)=-27.9 / V2(t2v std20)=-39.0 / V1(苹果)=-60.7——响度=f(场景声音描述量)；谐波检测全配置存在（15-44 基频）→ 音乐先验恒定，turbo/std 无本质差异
- **结论**：N/A/显式 no-music/静音指令均无法去除有声音场景的音乐成分；完全静音可行（极简 soundscape）；环境音无音乐不可行（后期分离待定）
- mem0 已修正 h3-nobgm-test 误判经验（id 686bf8fb 补对照结论）

### 2026-08-10 BGM 调查收束（上下文压缩点，完整矩阵）
**目标**：H3 视频如何控制背景音乐。**判定权威=用户试听**（频谱谐波误报多，海浪/风声共振均像谐波；87Hz 泛音序列=音乐特征）
**测试矩阵**（seed 20260810，768×448 为主，t2v/i2v × 长短 prompt × turbo/std）：
| # | 配置 | prompt | 结果 |
|---|---|---|---|
| h3-nobgm | int8 std20 t2v | 苹果极简+N/A | 近静音 -64.7dB（mem0 已修正：场景无内容所致，非 N/A 功效）|
| h3-sfx | int8 std20 t2v | 海边短+N/A | 无音乐 ✓用户 |
| H1 | fp8 turbo8 i2v | 海边长+N/A 无否定句 | 87Hz 泛音（疑音乐，未试听）|
| H2 | fp8 turbo8 i2v | 海边长+N/A+否定句 | **有音乐** ✓用户 |
| H3/H4 | fp8 turbo8 i2v | 全静音/极端否定 | 无效 |
| T1/T2 | std20 i2v | 海边长+N/A | -28dB 有谐波（未试听）|
| V1/V2 | int8 std20 t2v | 苹果复现/海边短 | -60.7dB 复现 / -39dB |
| T3 | fp8 turbo8 t2v | 海边短337字+N/A | **无音乐** ✓用户 |
| P1 | fp8 turbo8 t2v | 海边长4872字+N/A | **无音乐** ✓用户 |
| P2 | fp8 turbo8 i2v | 海边短337字+instruction | 频谱像无音乐，**待用户试听** |
**已排除**：N/A vs 否定句（H1 无否定句也疑音乐）；prompt 长度（P1 长 t2v 无音乐）；turbo（T3 无音乐）；fp8/int8；静音写法
**当前锁定**：i2v 模式嫌疑（H1/H2=i2v 有，T3/P1=h3-sfx=t2v 无）。P2（i2v 短）待判：
- P2 无音乐 → i2v 无罪，需再查 i2v+长 prompt 组合触发段（P3 定位）
- P2 有音乐 → i2v 模式触发（机制候选：首帧图多模态联想/instruction line/节点差异）
**生产影响**：若 i2v 触发音乐 → 快车道（i2v）音乐不可控：接受 or std 档（T2 疑）or 后期分离（demucs 待定）
**待回滚**：stage2 模板的 "No background music of any kind" 否定句（实测无效，若 i2v 是主因则无害可留；有副作用则删）
**产物**：ComfyUI/output/video/h3_gap_test/P2_i2v_shortprompt_00001_.mp4（试听中）+ P2_boost.wav；服务 http://localhost:8766/
