# T-comfy-ops-37 进度

## 2026-09-17

- 已领取并启动任务线：`comfy-ops_jibs`。
- 任务范围：只做总风格候选资料、缩略图/测试板与兼容性评估；不生成正式角色、场景或技能资产；不叠加多个总风格 LoRA。
- 剧情方向已明确：穿越 WoW，主修火系与冰系法术；核心卖点是法术的细节操作、塑形、与环境互动、战胜强敌并逃出生天。
- 本轮用户补充并确认的故事母设定：现代普通男性穿越到 WoW 人类出生地/北郡式修道院，不改时间线（后期时间线/平行空间反转另作大揭示）；无金手指、无玩家复活能力，NPC 行为和游戏特色保持原味；从杀附近增多的野狼开始，经过矿洞、盗贼等早期任务，但每个任务按极限求生处理。
- 法术系统方向：火焰、冰霜（后续可扩展土系）从基础物理/魔法操作学起；游戏中的法术名称是功能化的成型标签，主角实际可以控制基础元素的形态、移动、空间位置、攻击、防御和环境作用。战斗允许直接压制，也允许利用物理特性、地形和时机“四两拨千斤”；“火柴人元素战斗/绿灯侠式构造”是动作设计参考，不是最终美术风格。
- 旧任务关联：`.pi/tasks/story-e2e-v1/progress.md` 已有同一故事线的早期版本（弱 NPC 靠聪明冷静理解/组合/驾驭魔法系统，完成玩家做不到的事）。当前尚未发现独立小说项目或独立世界观文档库。
- 风格判断不能再按“泛高幻想好不好看”进行：必须优先满足法术构造的轮廓清晰、因果可读、空间位置明确、火/冰/土的材质反应可辨、普通人脆弱感成立，以及后续 H3 动作继承。火柴人动画只作为战斗编排/信息可读性的参考，不作为角色外观。
- 当前候选：Jibs Midjourney Fantasy Style（Civitai model 1276784，Krea2）、KREA2 Midjourney（2751419）、Gemlight Dream Midjourney Style（2744307）；必要时加入 Cinematic Dark Fantasy 对照。
- 初步流程建议：先写一页“视觉目标/剧情卖点”而非完整剧本；用同一组火冰法术与环境互动样本做候选横向测试；再按测试暴露的缺口去 Civitai 定向寻找补充 LoRA；选定一个总风格后再制作角色复合参考表、火系/冰系法术复合参考表，最后进入 H3 兼容性小测。

## 待执行

1. 整理统一测试 prompt 与判定表：角色、火塑形、冰塑形、环境互动、强敌/逃生、场景氛围。
2. 对三个候选做单总风格 LoRA A/B，不混用总风格 LoRA；记录模型、LoRA 权重、seed、分辨率和输出路径。
3. 按“角色一致性、火冰可读性、材质/光影、动作叙事、环境互动、H3 首帧/参考图适配、后续可控性”评分并选出首选。
4. 仅在首选暴露明确缺口后，再检索 Civitai 的局部补充 LoRA；补充项不得改变总风格方向。

## 文档架构待决

- 若故事继续长期扩展，应把小说母库从 `comfy-ops/.pi/tasks/` 拆出为独立项目；Comfy-ops 只保存视觉测试、角色/场景/法术设定图和 H3 生产映射。
- 独立母库至少需要：`world/`（时间线、地点、规则）、`magic/`（元素操作与法术构造）、`characters/`、`story/`（章节/任务/伏笔）、`canon/`（已确认定论）和 `decisions/`（变更记录）。在用户确认项目名和落点前不创建新项目，避免形成第二个未授权的设定真相源。
- 独立母库建议采用稳定 ID（如 `CHAR-PROTAGONIST`、`LOC-NORTHSHIRE-ABBEY`、`SPELL-FIRE-001`、`QUEST-S01-E01-WOLF`），并区分 `proposed / working / canon / retconned`；comfy-ops 仅消费已确认的角色、场景、法术视觉卡，不反向成为世界观真相源。

## 项目边界建议（待用户确认）

- 建议新建与 `comfy-ops` 平级的独立项目（暂名 `wow-mage-survival`），而不是在当前工具项目下新增子文件夹。原因：小说/短剧母库将有独立生命周期、多人协作和未来 Unity/游戏逻辑需求；`comfy-ops` 则应保持可复用于多个作品的工具链。
- 依赖关系：`ComfyUI` 是外部引擎运行时；`comfy-ops` 是插件、工作流、模型清单、测试脚本、实验和 QC 的工具链项目；`wow-mage-survival` 是内容/产品项目，拥有世界观、魔法规则、角色、任务、分镜和美术方向。内容项目只消费版本化的工具能力与导出产物，不依赖工具项目内部实现。
- 用户是作品总监/产品 Owner。Agent 可以提交 `proposed` 设定、实验结果和工具变更，但只有用户确认后才能升级为 `canon`、锁定总风格或修改时间线。
- 交互分三类：故事会话维护母库；`T-comfy-ops-*` 任务维护工具/模型/批量实验；集成任务把已确认的角色/法术/场景 ID 映射为 ComfyUI 资产。每个产物记录来源 ID、模型、工作流、seed、参数和 QC 结果。
- 建议的母库目录：`canon/`、`world/`、`magic/`、`characters/`、`story/`、`art-direction/`、`production/`、`decisions/`、`exports/comfy-ops/`；工具项目继续保留 `workflows/`、`custom_nodes/`、`scripts/`、`experiments/`、`docs/`。

## 用户范围纠正（2026-09-17）

- 上述“母库完整目录、常驻专业 Agent、正式内容生产分层”属于过度设计，暂不执行。
- 当前不启动正式小说/短剧项目；`wow-mage-survival` 仅作为轻量概念/参考记录区，保存与风格探索、人物 Ref、技术测试有关的少量上下文。
- 当前只保留工程层分工：ComfyUI 引擎 → comfy-ops 编辑器控制/插件/资源管线 → 作品相关实验包。内容侧没有常驻世界观/魔法/剧情/美术 Agent。
- 其他 Agent 只在需要时领取具体任务；稳定方法沉淀为文档或 skill，不按主题预先拆出 Agent。

## ComfyUI 基线同步（2026-09-17）

- ComfyUI `AGENTS.md` 与 `.pi/skills/comfyui/` 已完成按任务索引/分类 references 的重构，`bash scripts/docs_check.sh` 通过。
- 基线已提交：`f77ad90 [comfyui] route skill through indexed task references`。
- T37 不重新创建或重开；后续按 `.pi/skills/comfyui/INDEX.md → image/prompt-style.md` 进入 WOW 风格与人物 Ref 探索，必要时再读取 KREA2/工作流分册。
- `T-comfy-ops-40` 负责通用 Object ref 能力研究并避让 T37；本线继续负责 WOW 概念相关候选风格与人物 Ref 对照。
- 下一步夹具已建立：`projects/wow-mage-survival/fixtures/style_probe_v1.yaml`。它以第一集野狼任务为背景，固定 KREA2 8-step / CFG 1.0 / 1024×576 / `er_sde` + `simple`，包含修道院普通人、野狼初遇、火焰塑形、冰霜塑形、环境策略和逃生六个 case。
- 候选远端核查完成：三个 Civitai 编号均为 Krea 2 LoRA，可公平比较。Jibs 使用 version `3176271` / `Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors` / trigger `M1djourneyArtStyle` / strength `0.75-1.5`；KREA2 Midjourney 使用 version `3095398` / `KREA_MIDJ_1.safetensors` / strength `0.7-1.0`；Gemlight 使用最新 `Beyond the veil` version `3148897` / `aumirageV2.safetensors` / trigger `m1V8` / strength `0.8-1.0`。
- 初次本地模型核查时上述三个候选尚未下载；另有 `krea2_darkbrush.safetensors`、`krea2_vintagetarot.safetensors`，但元数据未登记，暂只作为 provisional control，不进入正式候选结论。

## 2026-09-17 追加

- 三个 Krea2 候选已下载到 ComfyUI `models/loras/`，并以 SHA256 核验；版本、触发词、建议强度和校验值登记在 `projects/wow-mage-survival/profiles/style_candidates_krea2.yaml` 与 `fixtures/style_probe_v1.yaml`，模型清单同步到 `docs/02_models.md`。
- 新增 `scripts/wow_style_probe.py`：从六 case 夹具读取提示词，逐候选注入一个 `LoraLoaderModelOnly`，支持 `--dry-run` 与 `--submit`；默认只跑 `SP03_FIRE_SHAPING`，用于先验证法术塑形的可读性。
- runner 已通过 Python 编译和单候选 dry-run；ComfyUI 曾健康启动并完成资源扫描，但后台进程随后退出，尚未提交 GPU smoke test。下一步先解决 ComfyUI 服务持续性，再跑单 case，暂不扩展六 case 全矩阵。

## 2026-09-17 运行记录

- 已确认应使用单实例：PID `154190`，唯一监听 `127.0.0.1:8188`，使用默认 `user/comfyui.db`；独立数据库仅是排查 SQLite 锁时的临时方案，未作为项目架构落地。
- GPU 可见的执行上下文中，三个候选均被同一 ComfyUI 实例索引成功。修正 runner 让工作流强制写入夹具的 `1024×576` 和 case seed 后，SP03 火焰塑形三候选 smoke test 有效完成；此前生成的 `1024×1024` 版本不纳入比较。
- SP04 冰霜塑形和 SP05 环境策略已各提交三候选，共 6 张有效输出，位于 `ComfyUI/output/wow_style_probe/{SP04_ICE_SHAPING,SP05_ENVIRONMENT_TRICK}/`。
- SP03 初步观察：Jibs 的火焰轮廓和动作张力最强；KREA2 更克制写实；Gemlight 火焰层次好但人物更容易法师化。仅为初筛观察，需结合 SP04/SP05 及人物普通感再评分。
- SP04/SP05 与 SP01/SP02 已完成三候选对照；当前初步倾向为：Jibs 负责法术/动作表现，KREA2 负责普通人和环境可信度，Gemlight 暂列第三候选。尚未锁定风格，下一步进入同候选的强度 0.6/0.8/1.0 小矩阵，检查 Jibs 与 KREA2 是否能在一个权重区间兼顾两类画面。
