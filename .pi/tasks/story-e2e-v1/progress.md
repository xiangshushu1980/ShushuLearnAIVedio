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
