# 任务进度：story-e2e-v1（新故事端到端第一轮）

## 任务
- 目标：跑通「AI 根据剧本出视频」最小闭环（2026-08-08 最终目标首次全链实测）：剧本闸门 → 工具 A 拍摄本 → 人工版工具 C 图需求 → 实体生成 → 六段式 → Ref2VA 出片 → 组装 → 验收
- TODO：T-comfy-ops-15（截止 2026-08-18）
- 当前状态：🟡 进行中（阶段 0：故事设定，等用户故事概念）
- 我负责的文件区：.pi/tasks/story-e2e-v1/、本任务产出的剧本/拍摄本/图需求/设定图（落 data/entities/ + input/start/169/）、docs 更新

## 收敛范围（快速闭环设计）
- 时长 20-30s，单场景，≤2 角色，无复杂特效，对白极简/旁白式
- 实体预算：角色 2 + 场景 1 + 风格板 1 = 4 张设定图（side/back 视镜头需要再加）
- 总时间盒：一天内闭环（对话 2-3h + 跑批 1h）

## 四阶段流程
| 阶段 | 内容 | 产出 | 闸门 |
|---|---|---|---|
| 0 | 故事设定：Brief + 8 拍大纲 + 主角 Want/Need/flaw | Brief + 大纲 | 用户能用自己的话重述（理解闸门） |
| 1 | 场景意图笔记 → 工具 A 拍摄本 | 导演拍摄本 | 逐镜审阅，可回溯到意图笔记 |
| 2 | 人工走工具 C 决策树 → 设定图生成 | refimage_plan + 设定图 | 设定图验收（同人度/风格统一） |
| 3 | 工具 B 六段式 → Ref2VA → 组装 + BGM | 成片 | 成片验收 + 管线缺口清单 |

## 进度日志（append-only）
### 2026-08-18（任务启动）
- T-comfy-ops-15 已建、认领、开始（owner=story-e2e-v1）
- 待用户输入：① 故事概念（一句话 What-if）② 角色决策（新角色 vs 沿用 Alya/Yuki）

## 下一步
1. 收用户故事概念 + 角色决策
2. 出 Project Brief + 8 拍大纲，过理解闸门
3. 场景意图笔记 → 工具 A 拍摄本
4. 人工工具 C → 设定图生成
5. 六段式 + Ref2VA + 组装

## 关键链接
- 3d skill 流程骨架：.pi/skills/3d-animation-short-generator/SKILL.md（STEP 0-2 = Brief/大纲/闸门模板；community 来源，仅借流程，执行走工具 A/B/C + ComfyUI）
- 工具 A：h3-prompt-agent 线（stage1 已验证：剧本→导演拍摄本）
- 工具 C 决策树：docs/23_refimage_system.md §四
- 设定图目录规范：data/entities/<实体id>/assets/art/ + input/start/169/

### 2026-08-18（本会话，接力）
- 恢复被误删的 progress.md（git checkout HEAD，内容完好）
- 会话前检查完成：recall 命中（工具 A stage1 已验/工具 C 决策树/Ref2VA 甜点配置/六段式经验）；git status 无本任务冲突 WIP；docs/INDEX 确认 17/21/22/23 相关文档在位
- 工具链确认可用：工具 A = scripts/h3_shotlist_gen.py（+ experiments/shotlist/rolecards）、工具 B = scripts/h3_prompt_stage2.py、出片 = scripts/h3_gap_runner.py（Ref2VA std20）、拼接 = scripts/h3_concat.py、BGM 组装 = docs/12 流程
- 缺口确认：data/entities/ 尚不存在（阶段 2 建）；169/ 现有 canon：alya169_portrait_uniform / yuki169_portrait_uniform（正脸）+ yuki169_stand（全身）+ 各场景版
- 待用户输入：① 故事概念（一句话 What-if）② 角色决策（新角色 vs 沿用 Alya/Yuki）③ 风格方向（风格板 1 张预算）

### 2026-08-18 风格调研（阶段 0 后半程）
- **故事输入已收**（用户 2026-08-18）：核心 = 弱 NPC 靠聪明冷静理解/组合/驾驭魔法系统，做到玩家做不到的事（逆袭向，非纯沮丧）；实体清单 = 人族出生地（北郡式修道院小镇/艾尔文森林氛围）+ 任务 NPC + 守卫 + 其他玩家 + 首任务野狼 + 火球术（主角用不出、玩家随手用）
- **风格对比板已出**（scripts/style_probe.py 新建，ANIMA×5 风格词变体 + KREA×1）：A 日系赛璐璐 / B 水彩吉卜力 / C 油画厚涂 / D 美式卡通（实际仍日系）/ E 韩漫 webtoon（风格词弱效）/ F 游戏 stylized（Pixar 3D 卡通渲染感，内容最准）
- **结论：纯 prompt 词拉不开 ANIMA 的风格差异**（A/B/D/E 均收敛到日系幻想插画）
- **LoRA 路线三条路全断**：① CivitAI 搜索 API 持续 503（tags/query 全挂，仅单模型/列榜接口通）② 本地 ACE 栈（SDXL）被 ComfyUI 0.33 按 AceStep1.5 视频架构处理，无 t2i 节点 → KSampler 维度错（已定位：ace_step15.py prepare_condition torch.cat 3v4；CLIP 双 TE 已用 DualCLIPLoader 修好）③ HF 无 qwen-image（ANIMA 基座）风格 LoRA 生态。3 个 ntc-ai SDXL LoRA 已移至 /tmp/ntc_lora_backup/（未删，待用户决定是否装 Illustrious 基座）
- 备选路径（超今天闭环预算，未执行）：Illustrious/NoobAI 基座 ~10GB → 海量动漫风格 LoRA
- 待用户：① 从 A-F 选风格（或指定调整）② 确认主角形象细节（性别/年龄/装束）
