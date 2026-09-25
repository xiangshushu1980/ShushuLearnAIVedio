# 任务进度：refimage-system

> 项目级私有进度（只有本任务线读写）。
> 状态标记：🟡进行中 / ⏸暂停 / ✅完成

## 任务
- 目标：设定图体系研究（角色/场景/道具/技能设定图形态、主次、重点控制、自动推导），产出可落地的设计
- 当前状态：✅完成（研究+设计交付；跑批/立项转下游）
- 执行者：flash-worker（deepseek-v4-flash，宿主编排循环）
- 我负责的文件区：`.pi/tasks/refimage-system/`；产出后续交工具 A/B/C 吸收

## 进度日志（append-only，每条带日期）
### 2026-08-16 产出设计
- 产出 `.pi/tasks/refimage-system/设定图体系设计.md`（四维度 + 落地动作清单），已交宿主审查
- 盘点 169/ 现有资产（portrait 正脸 canon×2 + yuki 全身 + 场景版×5 + multi 双人×3），确认缺口：全部角色缺 side/back、缺佩饰特写、缺道具图、缺变体图集、风格板未资产化
- 设计要点：形态=四类各列必要/可选表（角色 7 形态含变体图集、场景 3、道具 3、技能/风格 3）；主次=主设定图（正脸+全身身份锚定，跨段复用 canon）vs 辅助图（场景/风格/细节按镜头消费）；重点控制=四维分开喂 + 同维度冲突四铁律 + 单镜 ≤4 张预算表 + 禁文本微调变体；自动推导=工具 C 决策树伪代码 + refimage_plan.json 输出契约 + 级联生成顺序
- 落地清单：工具 C 新建（决策树→plan→anima/级联生成）、工具 A 补实体 id 引用 + scene 时段、工具 B 按视角注入 + retention 分维度
- 未跑图、未动共享文件；ComfyUI 资产目录实测在 /home/sean/projects/ComfyUI/input/start/169/（非本项目内）

### 2026-08-15 认领
- 宿主认领 T-20260812-03，执行者=flash-worker
- 输入材料：rolecards（alya_v1/yuki_v1）、ViMax stage2_consistency.md（三视图资产/候选池）、H3 Ref2VA 参考图机制（≤9 slot/<Subject>/<Picture>）、社区方案（rundiffusion/Runware 每图一职责）

## 下一步
1. ~~flash-worker 产出设定图体系设计~~ ✅（2026-08-16 已产出设定图体系设计.md）
2. 宿主审查完成；下游决策交用户拍板：①工具C图需求推导器是否立项新建（决策树已就绪）②资产补全P0批（side/back+风格板，需占坑跑批）

## 关键链接
- 关联 mem0：recall "设定图 参考图形态"
- 关联文件：docs/23_refimage_system.md（设计已归位）、experiments/shotlist/rolecards/、ComfyUI/input/start/169/、.pi/tasks/vimax-dissect/stage2_consistency.md
