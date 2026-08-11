# 16 提示词生成器计划（H3 可控提示词产出，2026-08-08 确立）

> 背景：A/B 实测证明 IR 增强有效（动作+40~60%），但 IR 是黑盒（模糊进→增强出，不可控）。
> 用户决策 2026-08-08：**自建提示词生成器，动机=控制**。最终目标：AI 根据剧本出视频。
> 当前阶段：前期准备（收集 + 学习 IR 输出）。

## 一、分层管线（每层一个控制点）

```
① 剧本（用户自由文本）
   ↓ [DeepSeek：剧本解析 → 拆场景/分镜]
② 分镜表（结构化、可审阅、可改）★控制点1
   场景1: [镜头1: 中景/缓慢环绕/3s] [镜头2: 特写/固定/2s] ...
   ↓ [DeepSeek：按官方指南（base-en/ref-en）合成]
③ 英文提示词（三核心段/六段式，可审阅锁定）★控制点2
   ↓ [可选：IR 精修 / 规则校验]
④ ComfyUI 生成
```

IR 定位：**降级为可选精修层**（黑盒但强，效果不满意时丢给它增强）。

## 二、控制面（用户可交互参数）

| 维度 | 可选值（预设库，可自定义扩展） |
|---|---|
| 风格 | 电影感/赛博霓虹/日系清新/纪实/梦幻/复古胶片... |
| 镜头 | 景别（特写/中景/全景）+ 运动（推拉摇移/环绕/固定/跟拍）+ 节奏 |
| 氛围 | 光线（黄金时刻/霓虹/阴天/月光）+ 色调 + 情绪 |
| 声音 | 环境音风格 + BGM 类型（IR 实测证明 soundscape 稳音频） |
| 素材 | 角色卡（Alya 等）/参考图/首尾帧 |

## 三、工具形态

- **方案 A：剧本文件 + 参数头（优先）**：YAML 头（style/lighting/shots/mood/sound）+ 正文 → DeepSeek 产出分镜表 → 确认 → 合成 prompt → 提交。改参数=改头两行，适合批量
- 方案 B：对话式向导（pi 内反问参数），适合临时想法
- 方案 C：Web UI（最后再做）

## 四、生成引擎

- **DeepSeek V4 flash / Pro（用户已有 key）**：flash 试错迭代、Pro 精写
- key 位置：`~/.config/mem0_deepseek_key` + 环境变量 `DEEPSEEK_API_KEY`（pi 进程内已设）
- 参数：**思考（reasoning）开 MAX**（用户 2026-08-08 确认，深度思考模式效果最佳）
- endpoint：`https://api.deepseek.com`
- 敏感内容策略：**敏感/擦边场景走本地生成器，不依赖 IR**（IR 有 1026 敏感拦截；2026-08-08 实测 A 场景第一次被拦）

## 五、前期准备清单（收集项）

| # | 收集项 | 内容 | 状态 |
|---|---|---|---|
| 1 | IR 输出样本库 | 10-20 条多场景真实输出（每条~1毛），逐条拆解标注六要素 | ✅ 13条（8 新 + 3 官方 + 2 旧 A/B，experiments/ir_samples/） |
| 2 | IR 输出拆解文档 | 结构规律：多镜头/细节密度/时间点/声音三层 | ✅ docs/18（i2v 4条待补） |
| 3 | 社区开源 prompt skill | benjiyaya/Minimax-H3-Prompt-AgentSkill(53★)、kuronzzhan-droid、imagineVid/Awesome 案例合集 | 🟡 benjiyaya 已拆（7维框架/格式规范/showcase）；kuronzzhan、imagineVid 待拆 |
| 4 | 官方示例 | 模型卡 README full-2k 示例 + scripts/readme IR 调用脚本 | ✅ 3 case 已入库 + 官方脚本格式已确认（媒体嵌套结构） |
| 5 | 镜头词汇表 | SeeDance 镜头体系（取词汇不取模板）+ 英文标准术语（dolly/pan/tilt/crane/arc） | 🟡 H3 运动词汇已入 docs/17（type+amplitude+speed）；SeeDance 另表待建 |
| 6 | 风格词汇库 | 光线/色调/质感描述词（golden hour/noir/soft light...） | 🟡 部分实测词在 docs/18 §四；完整词库落 docs/18 附录（待建）|
| 7 | 声音词汇 | 环境音/氛围/BGM 描述词 | 🟡 三层结构+实例在 docs/18；词库落 docs/18 附录（待建）|
| 8 | 成功案例 | docs 09 本地实测 + B站优质案例 | 待收集 |
| 9 | 经验蒸馏 | mem0 音频/动作规律 → 生成器规则（如：安静类词+turbo→静音，需 soundscape 兜底） | ✅ 已有素材（docs/18 §四 规则 3） |
| 10 | 指南文本 | base-en.txt(222行) + ref-en.txt(341行) + h3-prompt-writing skill | ✅ 已装 |

**不做**：敏感词规避表（用户拍板：敏感场景走本地生成器，不需要绕过 IR 拦截）。

## 六、路线

1. **验证**：DeepSeek + 官方指南写 A/B 场景 prompt，与 IR 输出并排文本对比（不跑视频，半小时出结果）；≥90% 接近 → 继续
2. **最小闭环**：剧本文件+参数头 → DeepSeek 分镜表 → 合成 prompt → 规则校验 → ComfyUI 提交
3. **迭代**：样本库扩充 → 经验蒸馏注入 → 预设库完善

## 七、相关

- 格式宪法：`.pi/skills/h3-prompt-writing/references/{base-en,ref-en}.txt`（官方）
- IR 调用：`scripts/h3_ir_rewrite.py`；A/B 提交：`scripts/h3_ab_submit.py` / `h3_ab_turbo_submit.py`
- 实测基准：docs/09（H3 测试计划）+ mem0（音频/动作规律）
- 上游跟踪：vendor/minimax-h3（commit 8d8824e 起）
