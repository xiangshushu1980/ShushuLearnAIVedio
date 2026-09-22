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
- 用户反馈修正了服装方向：之前的 `modest brown linen clothes` 会把人物推成中世纪农夫；已改为高质量人类奇幻服饰、剪裁羊毛、染色布料、皮革饰边、实用金属件和蓝金联盟色点缀，边境破败主要作用于环境。参考校准对象为暴风城人类视觉、西部荒野、死亡矿井/迪菲亚，而非泛中世纪农庄。
- 按新约束重跑 SP01 普通人和 SP02 野狼初遇三候选；新输出仍统一 1024×576，旧版服装结果不纳入后续评分。
- 用户进一步指出当前结果仍偏“中世纪农夫”，要求以 WoW 游戏画面为参照并提高到 2K。已删除旧的 `ComfyUI/output/wow_style_probe/` 全部生成图；夹具基线改为 `2048×1152`，新增 `projects/wow-mage-survival/references/wow_visual_refs.md`，将 Northshire、Stormwind、Westfall、Deadmines 和 Defias 的建筑、服饰、阵营色与场景约束写入。
- 2K 新基线已实测成功：SP01–SP06 共 16 张新图（SP01 先做 Jibs 单张，其余五类三候选），全部核验为 `2048×1152`；旧 `1024×576/1024×1024` 产物已删除，不纳入比较。2K 首张已明显呈现蓝金守卫、厚重装备、手绘贴图和 WoW 游戏化块面，后续评分以这批新图为准。
- 已完成 2K 批次的初步评测并写入 `experiments/T-comfy-ops-37/evaluation_v1.md`：Jibs 法术/阵营视觉最强但易英雄化，KREA2 当前整体最平衡且普通人感最好，Gemlight 魔法效果强但人物职业化倾向明显。下一轮按 Jibs `0.6/0.8`、KREA2 `0.8/1.0` 做强度矩阵，并加入 Stormwind/Westfall/Deadmines/Defias 专题图。
- 用户目测复核后修正排序：Gemlight 最合适，Jibs 较风格化，KREA2 最差。确认本轮没有使用参考图；SP02/SP05 已提供同 prompt/seed/尺寸/工作流的横向控制，因此 KREA2 不再扩展大矩阵，后续资源集中 Gemlight 与 Jibs。
- Gemlight/Jibs 的四个 WoW 专题场景已完成 2K 生成：Stormwind、Westfall、Deadmines、Defias，各 2 张，结果登记在 `experiments/T-comfy-ops-37/evaluation_v1.md`。当前主视觉基线确定为 Gemlight；Jibs 作为法术/动作强化候选，不叠加使用。
- 用户决策更新：Jibs 风格固定为当前项目视觉基线；Gemlight 不锁定，后续切换候选风格/LoRA 探索。当前所有测试均为 prompt-only，KREA2 工作流只有 UNET/CLIP/VAE/文本编码/空 latent/KSampler，没有输入参考图或图像条件节点。
- 法术专项 SP17/SP18 已完成 Jibs/Gemlight 对照：Jibs 的火焰/冰面材质和游戏化轮廓更强，但会增加人物、提高英雄化程度；Gemlight 有火焰氛围优势但角色职业化、冰霜物理较弱。下一轮加入单一主角、无第二人物、低装备等级和明确法术接触点约束。

## 2026-09-18 追加

- 按用户目测结论停止扩展 KREA2；此前 7 张 KREA2 结果已移动至 `ComfyUI/output/wow_style_probe/discard/krea2/`，仅归档、不删除，不再作为当前候选。
- Jibs 已完成标志性世界/生物探测：精灵主城、血精灵主城、海加尔山、元素生物、火焰元素、冰霜元素（SP11–SP16）。整体结论：Jibs 对 WoW 式阵营建筑、巨型树木/山体、元素生物轮廓、火焰与冰块材质都很强，适合作为当前世界观和法术视觉基线。
- SP17/SP18 的 Jibs 结果再次暴露同一限制：法术轮廓和接触点清楚，但 prompt-only 容易自动增加第二人物或围观者；冰霜场景尤其容易生成群像。下一轮法术测试改成更近的单主体构图，优先验证“一个普通人 + 一个明确法术接触点 + 一个环境反应”，而不是继续扩大场景。
- 当前服务仍为共享单实例 ComfyUI；本轮未重启、未切换数据库、未创建第二实例。所有有效输出保持 2048×1152。

## 2026-09-18 Object Ref 试生成

- 使用 Shushu 头像的外观描述作为角色提示词，生成 3 张独立 Object Ref：
  - `OR01_SHUSHU_CHARACTER_OBJECT`：普通男性、反戴黑帽、蓝黑联盟风格服饰、正面全身对象卡。
  - `OR02_FIRE_ELEMENTAL_OBJECT`：独立火元素对象，火焰、黑色火山岩和熔岩裂隙分层清楚。
  - `OR03_EMBER_RUINS_SCENE_OBJECT`：无人物火元素战斗环境，石桥、浅溪、湿石和草地空间关系清楚。
- 有效输出位于 `ComfyUI/output/wow_style_probe/OR01_*` 至 `OR03_*`，均为 2048×1152，使用 Jibs strength 0.6。
- 首次使用通用 `img_qc_test.py` 时发现该工作流没有正确替换提示词/LoRA，生成了默认狐耳女孩；3 张错误产物已移至 `ComfyUI/output/wow_object_ref/discard/invalid_script_injection/`，不纳入测试。
- 参考图链最小验证已完成：使用 H3 `H3ContactSheet` 真正接入 `shushu_identity_rebuilt_v2_cap.png`，生成的角色保留了 Shushu 的脸部特征、反戴黑帽和普通成年男性比例，再转换为蓝色联盟风格服装。结果明显比纯提示词接近，说明“不像”的主要原因确实是此前没有图像条件，而不是 fantasy 风格本身完全不能保留人物。
- 当前 KREA2/Jibs T2I 工作流没有参考图节点，因此尚未伪造 Jibs 0.3/0.6 的参考图对照；已新增 `workflows/h3_shushu_object_ref_probe.json` 作为参考图链路验证样本。后续若要做严格三档对照，需要接入 KREA2 兼容的参考图/IP-Adapter/主体参考节点。

## 2026-09-22 目标收敛

- 用户将参考资料目标拆为三层：① WoW 原作目标物/地点/人物/装备/怪物的补全参考；② 融合 WoW 元素的原创设定参考；③ 火、冰、土法术塑形与环境互动，作为重点研究线。
- 第一阶段收敛到人类出生地附近、Classic/早期北郡 1–6 级体验；用户描述的野狼、矿洞、盗匪更符合此线。现代版本北郡的黑石兽人入侵暂不混入，版本差异单独记录。
- 新增 [`projects/wow-mage-survival/references/northshire_v1.md`](../../projects/wow-mage-survival/references/northshire_v1.md)，列出第一批地点、人物、敌人、物件和火冰土法术切口。ArtStation 第一轮只按五类少量筛选，不建立大图库；用户选定后再下载/归档。

## 2026-09-18 KREA2 Reference 方法核查

- 核查确认：KREA2 官方支持 Style Reference；ComfyUI 官方模板为 `Krea-2 Turbo style reference`，使用专用 `krea2_style_reference.safetensors` 与 `krea2_turbo_int8_convrot.safetensors`。本机当前缺少这两个权重，因此官方风格参考模板暂不能直接运行。
- 获取社区 `ComfyUI-Krea2-Reference` 源码到 ComfyUI `custom_nodes/ComfyUI-Krea2-Reference`（commit `bae20b3`）。其 `TextEncodeKrea2Reference` 支持角色/风格分工：`character1` 作为 Shushu 身份，`style1` 作为 WoW 插画风格；并配套 `krea2_reference_v1` 参考 LoRA，理论上可再叠加 Jibs。
- 当前共享 ComfyUI 未重启，API 尚未加载新节点；本机也只有 `qwen3vl_4b_fp8_scaled.safetensors`，社区工作流要求 BF16 Qwen3-VL 视觉路径。下一步需要补齐兼容权重后，才能做“Shushu + WoW 风格图 + Jibs”的真实对照。

## 2026-09-20 KREA2 Reference 路线续接核查

- 共享 ComfyUI 只读检查：服务正常，版本 `0.36.0`；`ComfyUI-Krea2-Reference` 已注册 `Krea2StyleReference`、`TextEncodeKrea2Reference` 等节点。RTX 4090 当时约占用 18.3 GiB，未提交生成任务。
- `qwen3vl_4b_bf16.safetensors` 已存在，旧进度中“只有 FP8 编码器”的状态已过时；KREA2 底模实际位于 `models/diffusion_models/krea2_turbo_fp8.safetensors`，VAE 和 Jibs LoRA 也已存在。
- 社区 `krea2_reference_v1.safetensors` 未找到，因此社区节点路线暂缺关键参考 LoRA。公开仓库只说明从 Civitai/Hugging Face 获取，未给出可验证直链。
- 已通过 Civitai 官方 API 定位官方 Style Reference 路线：model `2764349` / version `3111281`，`krea2_style_reference.safetensors` 约 446 MB，SHA256 `F50DF5A9E62E4BE8AA926A63DD5BB1A64770C4004F763C1208007AE13DAA82B8`；配套 INT8 ConvRot 条目 model `2746798` / version `3089777`，文件约 12.5 GB，SHA256 `72B278EC2B3E7CA589FEB91B568CF9A98B179FD0FE0B4CFE1944C4508F872556`。
- 当前阻塞从“未定位权重/节点未加载”收敛为“等待用户确认是否下载约 12.5 GB 官方 ConvRot 权重”；确认后先下载并校验，再用官方 Style Reference 模板做最小双图验证。
- 用户决策（2026-09-20）：选择社区 `ComfyUI-Krea2-Reference` 路线，不下载官方 INT8 ConvRot；保留现有 KREA2 Turbo FP8 作为底模，补齐 `krea2_reference_v1.safetensors` 后测试“角色参考 + WoW 风格参考 + Jibs”组合。

## 2026-09-20 社区身份参考路线纠偏

- 进一步核查确认：`ComfyUI-Krea2-Reference` 是实验性原生 vision-token 角色/风格参考节点包，README 声称需要 `krea2_reference_v1.safetensors`，但仓库和 issue 未提供可验证下载地址，暂不作为主路线。
- 已找到公开且有完整节点/权重的社区身份路线：`lbouaraba/comfyui-krea2edit` + Hugging Face `conradlocke/krea2-identity-edit` 的 `krea2_identity_edit_v1_2.safetensors`（约 1.83 GB）。v1.2 使用 VAE 外观 token + Qwen3-VL 语义 grounding 双路参考，支持 Krea2 Raw/Turbo、单参考和双参考；节点 README 明确推荐 Turbo 8 steps / CFG 1。
- 该路线的模型输入顺序是“LoRA 已先应用到 Krea2 model，再接 `Krea2EditModelPatch`”；因此后续可用 Identity Edit LoRA + Jibs 先叠加，再进入 edit patch。Jibs 叠加效果仍需 A/B 实测，不能预先宣称兼容。
- 对 T37 的目标，首轮应以单张 Shushu 角色参考 + Jibs prompt/LoRA 为主；第二张图按该节点的 scene/subject 双输入语义单独对照，不直接把 style image 等同于 H3 的 style slot。

## 2026-09-20 Krea2 Identity Edit 下载完成

- 已下载社区节点 `ComfyUI-Krea2Edit` 至 `/home/sean/projects/ComfyUI/custom_nodes/comfyui-krea2edit`，当前 commit `86f886d`。
- 已下载 `krea2_identity_edit_v1_2.safetensors` 至 `/home/sean/projects/ComfyUI/models/loras/`，文件大小 `1,828,256,432` bytes；SHA256 `6adf9a69cc9502d286db7b69964d37da7e9cfe4b05b4d004bc275f087d3fd3cf`。
- 共享 ComfyUI 尚未重启，因此新节点尚未加载；下一步先在不抢 GPU 的情况下准备并审查官方示例工作流，再声明共享资源后做最小身份参考 + Jibs A/B。
- 2026-09-20 已按 `scripts/restart_comfyui.sh` 重启共享单实例；队列重启前为空，服务恢复正常（ComfyUI `0.36.0`，`--use-sage-attention`）。重启后 `Krea2EditModelPatch`、`Krea2EditGroundedEncode`、`Krea2ReferenceLoraLoader` 等节点均出现在 `/object_info`，`krea2_identity_edit_v1_2.safetensors` 也已进入 LoRA 列表；未创建第二实例，尚未提交生成任务。

## 2026-09-20 Krea2 Identity Edit A/B 实跑

- 首次尝试使用 `qwen3vl_4b_bf16.safetensors` 失败；ComfyUI 明确报告该 safetensors 文件不完整/损坏（`o_proj.weight extends past the end of the file`）。保留该文件未删除，runner 改用本机已验证可用的 `qwen3vl_4b_fp8_scaled.safetensors`。
- 新增可复用 runner：`tools/krea2_identity_edit_runner.py`。固定 Krea2 Turbo FP8、Qwen3-VL FP8、Qwen Image VAE、Shushu 单人参考图、seed `20260920`、1024×1024、8 steps、CFG 1、ref_boost 4.0；LoRA 顺序为 Identity Edit v1.2 后接可选 Jibs。
- A 基线（Jibs 0）：成功，约 26 秒；输出为 `ComfyUI/output/T37_krea2_identity_base_seed20260920_retry1_00001_.png`。
- B 对照（Jibs 0.6）：成功，约 15 秒；输出为 `ComfyUI/output/T37_krea2_identity_jibs06_seed20260920_00001_.png`。
- 两张图均为单个成年男性、保留反戴黑帽和主要脸部特征，没有出现多人复制、角色表或拼贴。B 相对 A 明显增加 Jibs 的奇幻装备/披风/蓝金风格；身份仍可辨认，但服装和姿态变化更大。该结论是单 seed 目视初筛，不代表最终身份保持率。
- 当前社区路线已完成“身份参考可用 + Jibs 可叠加”的最小功能验证；下一步应先由用户确认 A/B，再扩展 Jibs `0.3/0.6/0.9` 小矩阵，随后再考虑 2K 输出。

## 2026-09-20 去帽子与 CC 人物批次

- runner 提示词已改为明确“完全无帽/无头饰”，同时要求保留参考图的脸部、发型、肤色和眼镜（如有）。
- Shushu + Jibs 0.6 生成 3 张：seed `20260921/22/23`，均成功。无帽效果生效，但由于原始 Shushu 参考图的帽子遮住头发，三张多数补全为秃顶；身份仍保持，说明这是参考信息不足造成的发型补全，不是推理失败。
- CC（`input/ref2va_refs/fellow/cc.jpg`）+ Jibs 0.6 生成 3 张：同样 seeds，均成功。眼镜、脸型和无帽状态保持更自然，三张均为单人全身，无重复/拼贴。
- 输出目录：`ComfyUI/output/T37_krea2_identity_nohat_{shushu,cc}_jibs06_seed2026092{1,2,3}_00001_.png`。
- BF16 重新下载已从官方 Mage-Flow 地址启动：远端完整文件约 `8,875,719,384` bytes；当前下载到 `/tmp/qwen3vl_4b_bf16.safetensors`，完成后需校验并替换 ComfyUI 模型文件，再重启后单张复测。期间继续使用 FP8，不影响本批结果。

## 2026-09-20 身份高清基准阶段修正

- 用户明确纠正流程：不能直接用“参考图 + 风格提示词”重绘人物脸；必须先从原始照片生成 1:1 高清头像，用户确认后，再把确认头像作为唯一人物参考进入风格生成。
- 原始照片确认：Shushu 为 `fellow/xss.jpg`（另有戴帽 `xss_2.jpg`）；Chuanchuan 为 `fellow/cc.jpg`。此前使用的 `shushu_identity_rebuilt_v1/v2_cap` 属于已重建图，不应再当作原始照片基准混用。
- 已停止未完成的错误流程批次；未保留其未完成任务作为后续基线。
- 已按 identity-preserve 目标从原始照片生成两张第一阶段高清正方形头像（1254×1254），不含 WoW/Jibs/单片眼镜设定：
  - `ComfyUI/input/ref2va_refs/fellow/processed/identity_hd_stage1/shushu_identity_hd_stage1.png`
  - `ComfyUI/input/ref2va_refs/fellow/processed/identity_hd_stage1/chuanchuan_identity_hd_stage1.png`
- 当前等待用户确认这两张身份基准；确认前不再生成风格人物。Chuanchuan 单片眼镜应放在第二阶段角色设定，不放进第一阶段身份基准。

## 2026-09-20 角色基础参考图阶段

- 用户确认需要统一姿态/服装作为第二层基础参考图；已基于两张第一阶段身份高清头像生成统一模板：正面全身、自然垂手、同一灰色棚拍背景、蓝金联盟基础长 tunic、棕色裤子和棕色靴子。
- Shushu 基础图无帽、无眼镜；Chuanchuan 基础图保留普通眼镜，单片眼镜尚未加入，留到后续角色设定阶段。
- 输出（均 `1024×1536`）：
  - `ComfyUI/input/ref2va_refs/fellow/processed/character_base_stage2/shushu_character_base_stage2.png`
  - `ComfyUI/input/ref2va_refs/fellow/processed/character_base_stage2/chuanchuan_character_base_stage2.png`
- 下一步等待用户确认统一基础图；确认后再使用它们作为 Krea2 Identity Edit 的人物输入，加入 Jibs/WoW 风格和 Chuanchuan 单片眼镜。

## 2026-09-20 身份母版流程二次修正

- 用户进一步明确：基础图不应加入角色服装；核心是统一脸部、姿势、取景和背景，以减少服装等无关因素对身份判断的干扰。
- 之前的蓝金全身图标记为偏题候选，不作为基础参考。已直接从原始 `xss.jpg`/`cc.jpg` 重新生成严格正面头肩身份母版：同一灰色背景、同一灰色圆领上衣、正面居中、肩线水平、无帽、无眼镜/单片眼镜。
- 当前候选（均 `1254×1254`）：
  - `ComfyUI/input/ref2va_refs/fellow/processed/identity_master_stage2_v2/shushu_identity_master_stage2_v2.png`
  - `ComfyUI/input/ref2va_refs/fellow/processed/identity_master_stage2_v2/chuanchuan_identity_master_stage2_v2.png`
- 等待用户确认这组母版后，才进入第二阶段：以母版为人物参考，加入统一角色服装、Chuanchuan 单片眼镜与 Jibs/WoW 风格。

## 2026-09-20 统一景别最终母版

- 用户要求统一景别以降低无关因素影响；已从原始 `xss.jpg`/`cc.jpg` 生成最终统一身份母版：`1254×1254`、严格正面头肩、同一灰色背景、同一灰色圆领上衣、无眼镜/单片眼镜/帽子/角色服装。
- 正式基础图：
  - `ComfyUI/input/ref2va_refs/fellow/processed/identity_master_final/shushu_identity_master_final.png`
  - `ComfyUI/input/ref2va_refs/fellow/processed/identity_master_final/chuanchuan_identity_master_final.png`
- 本轮旧候选（身份高清初版、蓝金服装全身版、旧景别版）未删除，已移动到 `processed/discard/identity_superseded_20260920/`；正式流程只使用 `identity_master_final/`。
- 下一步：用户确认最终母版后，才加入角色服装、Chuanchuan 单片眼镜和 Jibs/WoW 风格。

## 2026-09-20 最终身份母版→风格人物首轮

- 使用正式 `identity_master_final` 作为唯一人物参考，未使用旧身份图或服装图；Krea2 Turbo FP8 + Identity Edit v1.2 + Jibs 0.6，seed `20260951`。
- Shushu 输出：`ComfyUI/output/T37_final_identity_shushu_jibs06_seed20260951_00001_.png`；无帽、蓝金联盟 WoW 风格、单人全身，脸部身份可辨。
- Chuanchuan 输出：`ComfyUI/output/T37_final_identity_chuanchuan_monocle_jibs06_seed20260951_00001_.png`；单片眼镜成功出现，蓝金联盟 WoW 风格、单人全身，脸部身份可辨。
- 首轮目视结论：统一身份母版进入风格阶段后仍可保持主要脸部特征；Chuanchuan 单片眼镜与 Jibs 服装/场景兼容。待用户确认后再扩展多 seed、不同姿态和场景。

## 2026-09-20 Jibs 强度扩展

- 按 `0.6/0.9 × seed 20260961/20260962 × Shushu/Chuanchuan` 扩展，共 8 张全部成功；Chuanchuan 每张均启用单片眼镜。
- 输出命名：`ComfyUI/output/T37_expand_{shushu,chuanchuan_monocle}_jibs{06,09}_seed{20260961,20260962}_00001_.png`。
- 初步目视：Jibs `0.6` 仍是身份保真优先的较稳档；`0.9` 的装备、金蓝装饰和 Jibs 风格更强，但英雄化和服装变化也更明显。官方/发布页建议范围约 `0.75–1.5`，本项目暂以 `0.6` 作为身份基线、`0.9` 作为风格增强档；runner 默认参数仍是 `0.0`（不加载 Jibs）。

## 2026-09-20 Jibs 1.0 / 1.5 对照

- 使用正式 `identity_master_final`，Shushu/Chuanchuan 各两个 seed（`20260971/72`），两档共 8 张；Chuanchuan 均启用单片眼镜。
- `1.0` 输出目录：`ComfyUI/output/T37_jibs_strength_10/`。
- `1.5` 输出目录：`ComfyUI/output/T37_jibs_strength_15/`。
- 目视初判：`1.0` 在风格增强与身份保持之间仍可接受；`1.5` 的材质/装备更强，但英雄化和服装漂移明显，暂不作为人物身份基线。

## 2026-09-20 Jibs 1.0 人脸可读性增强

- 用户确定使用 Jibs `1.0` 风格，并指出原始人物眼睛较小，风格化后眼球/瞳孔不易读。
- runner 新增 `--stylized-face`：要求轻度增强全身画面中的眼睛可读性，明确虹膜、深色瞳孔和小高光，同时保留原眼形、眼距、眉骨和脸部身份；禁止动漫大眼、Q版和换脸。
- Shushu/Chuanchuan 各跑两个 seed，输出目录：`ComfyUI/output/T37_jibs_strength_10_face_stylized/`；Chuanchuan 保留单片眼镜。
- 初步目视通过：Jibs 1.0 下眼睛出现可见虹膜/瞳孔/高光，仍保持 WoW 手绘风格，没有变成动漫大眼；单片眼镜没有完全遮挡 Chuanchuan 的眼部识别。

## 2026-09-20 Jibs 1.0 高分辨率脸部特写

- 用户判断全身 1024 构图会压缩脸部细节，要求先做高分辨率风格化脸部特写；runner 新增 `--closeup` 和可调宽高。
- 使用正式 `identity_master_final`、Jibs `1.0`、`stylized-face`、胸像/头肩近景提示，输出 1536×1536：
  - `ComfyUI/output/T37_face_closeup_1536/shushu_jibs10_seed20260991_00001_.png`
  - `ComfyUI/output/T37_face_closeup_1536/chuanchuan_monocle_jibs10_seed20260991_00001_.png`
- 初步目视：脸部占画面主体，眼睛虹膜/瞳孔/高光、胡须和手绘皮肤笔触均清晰；Chuanchuan 单片眼镜细节完整。该批作为后续风格人物的脸部质量基线。

## 2026-09-20 Jibs 1.0 近景身份保持修正

- 用户要求先去掉 Chuanchuan 单片眼镜，并进一步保持原始五官；runner 的 `stylized-face` 提示改为“参考图是五官唯一真值，只改变渲染画法，不改变五官比例”，同时把 `ref_boost` 从 4.0 提高到 6.0。
- 新输出目录：`ComfyUI/output/T37_face_closeup_1536_identity_preserve/`。
- 输出：Shushu 与 Chuanchuan 各一张 1536×1536 近景，均无单片眼镜；目视上身份特征比带单片眼镜版本更稳定，仍保留 Jibs 1.0 手绘风格与眼部可读性增强。

## 2026-09-20 原始照片直连身份修正

- 用户反馈 Shushu 仍不像原始人物，并要求 Chuanchuan 同样修正；改为直接使用原始 `xss.jpg` / `cc.jpg`，跳过生成的身份母版，Jibs `1.0` + `stylized-face` + `ref_boost 8.0` + 1536×1536 近景。
- Shushu：`ComfyUI/output/T37_face_closeup_1536_shushu_original_ref/shushu_jibs10_refboost8_seed20261011_00001_.png`。
- Chuanchuan：`ComfyUI/output/T37_face_closeup_1536_chuanchuan_original_ref/chuanchuan_jibs10_no_monocle_refboost8_seed20261011_00001_.png`。
- 目视初判：Shushu 的眼距、鼻口、胡须和整体脸部结构较前版更接近原始照片；Chuanchuan 去掉单片眼镜但保留了原照片普通眼镜，五官更自然。两张仍为风格化结果，待用户确认后再确定正式人物参考链。

## 2026-09-20 Chuanchuan 去眼镜与结果归档

- 用户要求两张原始照片直连结果放入一个文件夹，并明确去掉 Chuanchuan 普通眼镜。
- runner 新增 `--no-eyewear`，明确移除所有眼镜；使用原始 `cc.jpg`、Jibs `1.0`、`stylized-face`、`ref_boost 8.0`、1536×1536 近景生成：
  - `ComfyUI/output/T37_face_closeup_1536_original_ref_final/chuanchuan_jibs10_no_eyewear_seed20261021_00001_.png`
- Shushu 原始照片直连结果同步复制到同一目录：
  - `ComfyUI/output/T37_face_closeup_1536_original_ref_final/shushu_jibs10_refboost8_seed20261011_00001_.png`
- 该目录现在是原始照片直连风格特写的统一归档目录；Chuanchuan 版本无普通眼镜、无单片眼镜。

## 2026-09-20 风格-only 提示词实验

- 用户反馈人物仍不像，要求删除提示词中的五官特征描写，直接把参考图人物做风格转换。
- runner 新增 `--style-only`：提示词只要求“对参考图中的人物应用 Jibs WoW 风格”，不再描述或重解释眼睛、鼻子、胡须、脸型等；Chuanchuan 仅额外使用 `--no-eyewear`。
- 使用原始 `xss.jpg`/`cc.jpg`、Jibs `1.0`、1536×1536 近景、`ref_boost 8.0`，两张输出统一放在：`ComfyUI/output/T37_face_closeup_1536_style_only/`。
- 输出：`shushu_jibs10_seed20261031_00001_.png`、`chuanchuan_jibs10_no_eyewear_seed20261031_00001_.png`。

## 2026-09-20 Jibs 1.0 face-only 风格近照

- 用户进一步要求只保留脸部风格化近照；runner 新增 `--face-only`，在 `style-only` 分支中使用极近脸部构图，不再描述五官，也不要求服装、武器或道具。
- 使用原始照片 `xss.jpg` / `cc.jpg`、Jibs `1.0`、`style-only`、`face-only`、1536×1536、`ref_boost 8.0`；Chuanchuan 额外传入 `--no-eyewear`。
- 原始生成图统一放在：`ComfyUI/output/T37_face_only_1536_style_only/`。
- 为严格去除底部残留肩部/服装，另将两张结果裁切为脸部专用版本：
  - `ComfyUI/output/T37_face_only_1536_style_only/face_crop/shushu_face_only_jibs10_20261041.png`
  - `ComfyUI/output/T37_face_only_1536_style_only/face_crop/chuanchuan_face_only_jibs10_no_eyewear_20261041.png`
- 目视：裁切版已基本只剩头脸；Chuanchuan 的眼镜元素仍被参考图条件保留，后续若必须无眼镜需要单独做局部遮罩/修复，不影响本轮脸部构图验证。

## 2026-09-21 统一头像参考与负向约束复测

- 用户指出输出后裁切无效，要求“只把参考图头部送入模型”并统一头像尺寸；因此新增原始头部参考：
  - `ComfyUI/input/ref2va_refs/fellow/processed/face_only_refs/shushu_head_ref.png`
  - `ComfyUI/input/ref2va_refs/fellow/processed/face_only_refs/chuanchuan_head_ref_tight.png`
- 两张均以正方形头部参考、1536×1536 输出、Jibs `1.0`、`style-only`、`face-only`、`ref_boost 8.0` 复测；runner 也加入了 face-only negative prompt（服装、盔甲、道具、眼镜等）。
- 结果仍不合格：Jibs 1.0 会强行注入 WoW 盔甲/背景/眼镜，Chuanchuan 尤其明显；即使输入已裁到头部，人物身份和头像构图仍不稳定。因此这批 `T37_uniform_face_avatar_1536*` 不作为基础头像，不能继续向后传递。
- 结论：仅靠 Krea2 正/负提示词 + Jibs 1.0 不能同时满足“高身份相似度、无服装/眼镜、统一头像构图”；下一步应改为先建立身份头像（不加载 Jibs 或用更低风格强度/局部修复），再把身份头像作为后续风格化参考。

## 2026-09-21 Krea2 官方/社区提示词与身份编辑检索

- 官方 Krea2 仓库提供 `docs/prompting.md` 与 `docs/expansion.txt`，核心是自然语言提示、忠实保留用户指定主体/空间关系、不要凭空添加输入未支持的细节；没有发现官方“身份头像/脸部锁定”固定 prompt 技能。官方更推荐用 style reference / moodboard 表达视觉风格，而不是用长提示词描述风格。
- 官方 Krea2 开源 README 明确区分 Raw 与 Turbo：Turbo 是 8-step 蒸馏模型，适合快速生图；Raw 是未蒸馏模型，适合更可控的研究/微调。官方也明确 Turbo 的主要用途是快速探索，而不是最大一致性生产。
- 社区维护者 `lbouaraba/comfyui-krea2edit` 是当前最相关的 Krea2 Identity Edit 实证来源：v1.2 使用 VAE 外观 latent + Qwen3-VL 语义 grounding 双条件；建议人物可尝试 `grounding_px=1024`，`fit_mode=fit`，`ref_boost>1` 提高身份保真。
- 关键社区结论：普通 restyle 可用 Turbo 8 steps / CFG 1；删除眼镜、服装等显著内容应改用 Raw、CFG 3、约 20 steps，Turbo CFG 1 往往会重新绘制主体而不是删除。这直接解释了当前 `--no-eyewear` 失败。
- 重要纠正：社区官方工作流的 negative conditioning 是“同一参考图 + 空 prompt”的训练无条件分支；我们临时加入“no clothing/eyewear”负向文本并没有官方依据，且实测会产生伪影，应回退。下一轮应分离“身份编辑（Raw）”与“Jibs 风格化（Turbo/restyle）”，不能用 Jibs 1.0 Turbo 同时承担身份锁定和内容删除。

## 2026-09-21 社区/GitHub 可迁移 Prompt 技能整理

- `lbouaraba/comfyui-krea2edit` 的示例 workflow 提供了可直接迁移的 plain-English 指令范式：重打光、把人物放入场景、修改服装；如果脸变得 generic，再追加“保持准确的面部身份 + 描述可辨识特征”。这说明身份任务不是完全不写五官，而是只写来自原图的稳定识别锚点，禁止加入风格化五官。
- 该 workflow 的参数注释给出：`ref_boost=4` 是强身份保真起点，超过 10 可能使删除/替换失败；Turbo 8/10/12 steps 分别偏构图、平衡、脸部细节；Raw 建议 40 steps、CFG 3–4。模型卡的通用表则给删除任务 Raw 20 steps、CFG 3；后续应把 20/40 作为删除任务的对照，而不是混成一个固定结论。
- RunComfy 社区工作流补充了可迁移原则：提示词要短，只描述要改变的内容；身份最重要时紧裁参考图；固定 seed 做 A/B；局部修改使用 mask；叠加风格 LoRA 时降低对参考图的强依赖，避免过约束/风格冲突。
- 面向视频人物目标的拟定链路：A. 身份头像阶段（Identity Edit，原图为唯一身份依据，不加载 Jibs；必要时 Raw 完成去眼镜/服装）；B. 风格脸阶段（在身份头像上使用 Jibs，仅写“保留该脸，只改变渲染风格”）；C. 人物参考图阶段（短 prompt 指定统一正面头像/景别/姿态）；D. 再交给视频 Ref2VA。`style-only` 全无身份锚点的提示词不再作为默认技能。

## 2026-09-21 三模式 runner 与文档落地

- `tools/krea2_identity_edit_runner.py` 已改为三种明确模式：`identity_portrait`、`identity_remove`、`jibs_style_portrait`。
- 默认基线已改为社区建议：1024×1024、`ref_boost=4`、`grounding_px=1024`、Turbo 10 steps / CFG 1、negative 使用同一参考图的空 prompt。
- `identity_remove` 默认切换 Raw / 20 steps / CFG 3，并在本地缺少 Raw checkpoint 时拒绝提交任务；当前本机确认只有 Turbo，因此未把 Raw 结果写成实测结论。
- 研究正文写入 `docs/40_krea2_prompt_and_identity_pipeline.md`，并加入 `docs/INDEX.md`；模型清单补充 Raw 缺失状态。
- 已通过 Python 编译、模式参数和 Raw 缺失保护测试；尚未运行新三模式生图，等待 Raw 下载或先测试身份头像/Turbo 风格模式。

## 2026-09-21 Prompt 单一来源对齐优化

- 新增 `tools/krea2_prompt_profiles.py`，集中维护 `IDENTITY_PORTRAIT`、`IDENTITY_REMOVE`、`JIBS_STYLE_PORTRAIT` 和视频人物参考图 `VIDEO_REFERENCE` 四个 Prompt profile，版本号 `krea2-identity-v1`。
- runner 改为直接导入 Prompt profile，不再内嵌重复文本；`docs/40_krea2_prompt_and_identity_pipeline.md` 改为维护用途/参数契约并链接唯一 Prompt 来源。
- Krea2 image skill 入口已指向 docs/40；旧 `params.md` 明确标注为普通 Krea2 文生图历史基线，避免与人物 Identity Edit 参数混用。
- 已通过 Prompt 模块导入、runner 编译和 profile 文本唯一性检查；本轮未提交 ComfyUI 生图任务。

## 2026-09-21 Raw checkpoint 补装准备

- 确认应下载 Comfy-Org 为 ComfyUI 重打包的 `diffusion_models/krea2_raw_fp8_scaled.safetensors`（约 13.1GB，SHA256 `48cd5d6c100297968349b41a8e77c6591d1dac18a215807f5f25f59e5c54cd61`），而不是官方原始仓库 26.3GB 的 `raw.safetensors`。
- runner 的 `identity_remove` 默认文件名已修正为 `krea2_raw_fp8_scaled.safetensors`。
- 下载尚未完成：当前 shell 到 Hugging Face 的 DNS/网络请求失败，模型文件未落盘；待网络或本地 HF 镜像可用后继续。
