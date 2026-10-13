# 提示词工具对比归档（T-comfy-ops-03，2026-08-17）

对比对象：
- **1038lab/ComfyUI-MiniMax-H3-Promptor**（138★，08-14 更新 V1.2.0）— 双节点解耦套件
- **T8mars/comfyui-minimax-h3-prompt-enhancer-T8**（132★，08-17 更新）— 官方 skill 冻结 + 110 案例 selector

结论摘要见 docs/11（工具对比吸收节）+ docs/16（生成器架构模式）+ docs/17（规则强化）。

## 文件清单

| 文件 | 内容 |
|---|---|
| `1038lab_system_base.txt` | 1038lab Promptor 的 system_base 模板（叙事+声音两行契约） |
| `sample_A_1038lab_i2v.txt` | 抽样输出 A：1038lab 契约（I2V 8s，DeepSeek deepseek-chat） |
| `sample_B_T8_i2va.txt` | 抽样输出 B：T8 契约（I2VA 8s，中文兼容 balanced 档） |
| `sample_C_ours_baseen_i2va.txt` | 抽样输出 C：我方契约（base-en.txt 三核心段，I2VA 8s） |
| `t8_case_catalog.json` | T8 案例库完整 catalog（112 项：110 selector + 2 社区 skill，含 Creative DNA 哈希/证据变体/GIF 元数据），仅备查不导入 |

抽样方法：同一用户输入（汉服少女×灯笼街雨夜 I2VA 8s），同一模型（deepseek-chat, temp 0.4），三个契约各生成一次，仅对比结构差异；视频效果未实测（无 API 跑视频）。

## 两工具架构速览

### 1038lab Promptor（cinema 级生产套件）
- **双节点解耦**：H3_Vision_Analyzer（多模态视觉分析，出 JSON vision_context）→ H3_Promptor（纯文本格式化，不再看图）→ 一次视觉分析成本复用
- **Auto 模式路由**：按媒体数量自动判 T2V/I2V/I2VA/L2VA/FL2VA/Ref2VA/V2V/A2V
- **输出契约**：LLM 只写 `[Shot N]` 叙事段 + `Audio:` / `Music:` 两行收尾；六段式结构标签（summary:/retention_analysis）由代码程序注入，LLM 不生成
- 模板可改（templates/*.txt）、vision_prompts.json 可加分析策略、多 provider（OpenAI/Ollama/Gemini/Anthropic）
- v1.2.0：L2VA 反向锚定、I2VA 零秒帧锚定、Audio-First token 同步

### T8 Prompt Enhancer
- 单节点 LLM 增强：用户意图 + 真实媒体 + 官方规则 → 最终 H3 prompt
- **官方 9 skill 冻结**（核心 h3-prompt-writing @ commit 093f3129 + 8 场景 skill，MV 同步 v0.6.6）——与本地 h3-prompt-writing skill 同源
- **110 案例 selector**（129 条案例归并 + 19 证据变体）：每个条目 = label + summary + input_format + recommended_input + required_anchors（2-5 结构锚点）+ 双模型 Creative DNA 哈希
- 优先级链：硬约束 > 用户意图+媒体事实 > 核心契约 > 创意预设 > 参考模板
- strict/balanced/creative 三档改写（温度 0.2/0.7/1.0）
- 参考模板融合：模板只迁移结构/节奏/运镜/转场/风格/声音设计，不迁移人物/道具/剧情

## 三契约抽样对比要点（详见 docs/11）

| 维度 | A 1038lab | B T8(兼容/balanced) | C 我方 base-en |
|---|---|---|---|
| 输出结构 | [Shot N]×3 + Audio/Music 两行 | instruction + 三字段（中文描述） | instruction + 三字段（英文） |
| 镜头数 | 3 镜（8s，略超 17 号预算） | 1 镜 | 1 镜 |
| 音乐 | Music: N/A（尊重默认） | balanced 档自动加配乐 | 自动加 guzheng 配乐 |
| 对话 | 无虚构 | 无虚构 | **虚构了用户未请求的对白 (S1)** |
| 声音行 | 环境+动作声完整 | 三层 soundscape 完整 | 三层完整 |
| token | 1393 | 1676 | 3958 |

- 我方 base-en.txt 契约**缺防虚构句**（T8 COMMON_SYSTEM_RULES 有 "Do not fabricate spoken lines"）→ 已补 17 号 §三
- 音乐默认差异：17 号用户决策（默认无 BGM）与 T8 balanced/creative 档冲突 → 生成器用 strict 档或显式 no-music 句
- 1038lab 的 Audio:/Music: 两行收尾 = 可执行性最强的声音契约（防遗漏防跳段）

## P0 文本级回归（2026-08-17 完成，regression/）

设计：同一输入 × 旧契约（base-en/ref-en 原样）vs 新契约（+17 号强化块 HARD_BLOCK），4 输入 × 2 契约 = 8 调用（deepseek-chat, temp 0.4），检查项脚本化。

| 检查项 | OLD | NEW | 判定 |
|---|---|---|---|
| T1 无台词 I2VA 不虚构对话 | ✗ 虚构 `<d>[English]` 台词 | ✓ 无对话 | 强化句生效 |
| T1 未请求音乐 → N/A | ✗ 擅自加 guzheng | ✓ N/A | 强化句生效 |
| T2 FL2VA 单镜 | ✓ base-en 自带 | ✓ | 无回归 |
| T4 显式音乐请求 → 配器描述 | ✓ 正向触发正常 | ✓ 未误伤 | 无回归 |
| T3 Ref2VA 六段格式合规 | ✗ 偶发 markdown 标题+丢音乐段（约 1/3，补跑 2 次均合规） | ✓ | 需合成层自检+重试（入 16 号 §四.1.7） |
| T3 retention 无 (Sx) | ✓ | ✓ | 稳定 |
| T3 角色图定义 | ⚠ 偶发多定义 `<Picture 1>`（应只作 Subject） | ⚠ 同 | 17 号 §四已有规则，遵循不稳 |

结论：17 号新增规则句（防虚构台词、音乐默认 N/A）确实压住行为且未误伤显式音乐触发；新增风险点=LLM 偶发格式违规 → 合成层必须做解析校验+重试。
