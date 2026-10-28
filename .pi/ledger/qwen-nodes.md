# Qwen 图像节点与预览结论谱系

## 条目索引

| C-ID | 主题 | 状态 | 备注 |
|---|---|---|---|
| C-QWEN-NODES-20261016-01 | QwenImage21Cache 与 Tiny VAE 预览 smoke | ✅现行 | Cache default/off 同图；int8 近似但细节有变 |
| C-QWEN-NODES-20261024-01 | Qwen Image 2.1 BF16 Fun Control 单视图结构引导 | 🟡定论候选 | BF16 底模+BF16 补丁单角色试跑成功；LoRA 组合与泛化待测 |
| C-QWEN-NODES-20261025-01 | 深度 strength 与宣传图灰化假设 | 🟡定论候选 | 两个正面 seed 中未见 strength 0.75/1.00 导致明显褪色；范围有限 |
| C-QWEN-NODES-20261025-02 | Hy3D mesh depth 作为 turnaround 深度输入 | ✅现行 | 当前 ComfyUI 0.42.1 + wrapper commit 实测单视角及 0/90/180/270 四视角成功；阶段 3 画布适配待验 |
| C-QWEN-NODES-20261025-03 | Hy3D 深度的阶段 3 适配与单样本视觉结果 | ✅现行 | 左/后深度中心裁切至 768×1024 后可运行；后视水壶可见而未通过 QC |

### C-QWEN-NODES-20261016-01 | QwenImage21Cache 与 Tiny VAE 预览 smoke
- 状态：✅现行（valid_from 2026-10-16）
- 现行值：四张有序参考图经 `TextEncodeQwenImage21` 可完成 Qwen Image 2.1 Turbo 生成；同 seed 的 cache `auto/default` 与 `off/default` 输出像素完全相同；`auto/int8` 平均绝对 RGB 差为 0.572/255，但小细节有变化。Tiny decoder 接入 KJNodes live preview，最终输出仍由 BF16 VAE 解码。
- 时间线：
  - 2026-10-16 实测：1024×1024、8 步、seed 421016、四张身份/服装/护具/刀参考图；单次耗时受首轮模型加载影响，不作为加速比结论。来源：2026-10-16 自由会话（无 Task Center T-ID）。
- 证据锚：`docs/50_qwen_image_2_1_nodes_and_tiny_vae.md`；`experiments/sean_qwen21_cache_textencode_tinyvae_20261016/README.md`。

### C-QWEN-NODES-20261022-01 | 固定调用：通用图、三视图与 MV 输入边界
- 状态：📝已修正（被 C-QWEN-NODES-20261022-02 收窄）
- 现行值：共享 `workflow.py` 的 `qwen-image-v1` 使用同图的 `general`（Turbo INT8 8 步，多参考图＋提示词）与 `three-view`（标准 BF16 25 步，一张外观图到前／侧／后人物图）预设。旧三视图 INT8 权重当前不可用，不自动恢复；新配置单独验证。四视图定义是前／侧／后＋脸部特写，本轮未接入。
- 本轮证据：默认 general 四图、three-view 一图实际生成并回收 PNG；H3 21＋Qwen 9＋MV 5 项测试通过。仅各一个样本，不推断普遍身份/配件/几何稳定性。
- MV 边界：已定位旧链为 Qwen 图片 → Hunyuan3D-2mv；共享 `hunyuan-mv-v1` 从准备好的 front/left/back 三图生成无贴图原始 GLB，本轮回收与结构验证成功，未做 Blender、拓扑或贴图验收。
- 覆盖关系：补充 C-QWEN-NODES-20261016-01 的稳定调用入口，不改变原缓存精度结论；不沿用旧 INT8 三视图质量为 BF16 新预设背书。
- 证据锚：[接口扩展报告](../../experiments/qwen_workflow_interface_20261022/REPORT.md)；[Qwen 当前输入契约](/home/sean/.pi/agent/skills/comfyui/references/qwen-image.md)；MV 契约已按用户澄清撤回，原试跑仅保留实验记录。

### C-QWEN-NODES-20261022-02 | Qwen 扩展最终范围（排除 MV）
- 状态：✅现行（valid_from 2026-10-22）
- 现行值：本轮仅提供 `qwen-image-v1/general` 与 `three-view`。三视图为前/侧/后；四视图是前/侧/后+脸部特写，暂不接入。用户澄清 MV 属于 Hunyuan3D 并要求忽略，已撤回本轮新增 MV 接口、模板、专项测试入口和说明，保留试跑证据。
- 覆盖关系：收窄 C-QWEN-NODES-20261022-01 的交付范围。现行回归为 H3 21＋Qwen 9 共 30 项；MV 的5项和GLB试跑不纳入本轮验收。
- 证据锚：[Qwen 最终接口报告](../../experiments/qwen_workflow_interface_20261022/REPORT.md)；[共享 Qwen 说明](/home/sean/.pi/agent/skills/comfyui/references/qwen-image.md)。

### C-QWEN-NODES-20261022-03 | Luna 调用方技能与多组实跑复核
- 状态：✅现行（valid_from 2026-10-22）
- 现行值：独立上下文 Luna 实测可见并读取共享 comfyui 技能与引用、发现流程、自行规划和执行 general 的 0/1/2/4 参考输入及人物三视图，五个 PNG 均生成回收，租约释放；双图 896×1024 参数生效。另五类非法输入全部在提交前拒绝。
- 内容边界：场景、双图角色分工、四图组合和三视图布局可读；单图编辑没有清楚实现坐在木桌旁。少样本不证明普遍身份/配件/几何一致性，未测试未点名时的隐式技能触发率。
- 覆盖关系：补充 C-QWEN-NODES-20261022-02 的调用方实测范围，不改变两预设模型与采样参数，不重新纳入 MV 或四视图。
- 证据锚：[Luna 六组复核](../../experiments/workflow_luna_forward_20261022/SUMMARY.md)、同目录 skill-access.json、execution-summary.json、visual-review.md、manifest.json。

### C-QWEN-NODES-20261022-04 | 座姿提示线索与三视图配件可见性边界
- 状态：🟡定论候选（2026-10-22，待后续样本复核）
- 观察：同输入、同 seed 的 Qwen `general` 单图编辑中，将“坐姿”具体化为臀部接触椅面、前臂置于桌面、桌面横跨前景后，本样本由站姿变为清楚坐姿；人物可辨识度与画面风格目视相近，未做量化身份度量。可作为提示写法示例，不作跨输入/seed 保证。
- 边界：`three-view` 同 seed 两个样本均出现侧视图雨伞缺失；本轮即使明确要求每视图完整可见及与身体分离，侧视图仍遗漏。逐视图检查仍必要，提示词不能保证配件可见。
- 覆盖关系：补充 C-QWEN-NODES-20261022-03 的单图编辑和三视图内容验收边界；不改变工作流、模型或采样配置。
- 证据锚：[本轮报告](../../experiments/workflow_skill_optimization_20261022/REPORT.md)、`qwen_seated_edit/run-v002-log.md`、`qwen_three_view_prop/run-v002-log.md`；[共享 Qwen 说明](/home/sean/.pi/agent/skills/comfyui/references/qwen-image.md)。来源任务 `remote-4b2d4193-7915-4ddc-aaea-c81210eccaf4`。

### C-QWEN-NODES-20261024-01 | Qwen Image 2.1 BF16 Fun Control 单视图结构引导
- 状态：🟡定论候选（2026-10-24，待 LoRA 与更多视角/seed 复核）
- 观察：单角色、seed 423201、768×1024、25 步的三次本机生成中，Qwen Image 2.1 BF16 底模与 BF16 Fun Control Union 补丁可共同运行。灰色 GLB 结构图同时作为文本图像参考和控制图时，输出保留灰模外观；只送进控制节点、外观图只送进文本图像编码后，外观迁移与侧视生成成功。GLB 相机绕竖直轴偏转 +8° 后，后脚可见度更接近 Qwen 侧视样例。
- 边界：未加载 Character Sheet LoRA；只有一个角色与 seed；配件几何仍有漂移，不能据此认定为精确转绘或跨样本稳定结论。
- 证据锚：[试验报告](../../experiments/qwen_fun_control_bf16_side_view_20261024/QC.md)、[A/B/C 对照图](../../experiments/qwen_fun_control_bf16_side_view_20261024/comparison_camera_yaw8.png)、[模型清单](../../docs/02_models.md)。来源任务 `remote-4b2d4193-7915-4ddc-aaea-c81210eccaf4`。


### C-QWEN-NODES-20261025-01 | 深度 strength 与宣传图灰化假设
- 状态：🟡定论候选（2026-10-25，待不同角色/视角及原宣传图工作流复核）
- 观察：Frost Scout 正面、seed 423530/423531 的同条件对照中，depth strength 0.50/0.75/1.00 未出现明显灰化或随强度增加而饱和度下降；strength 1.00 的两样本整体略暗。seed 423530 三档深度输出均遗漏外观参考中的弓，而 appearance-only 与 seed 423531 各条件保留弓，说明该输入下存在小装备保持偏差，但不能归因于单调强度效应。
- 边界：两 seed、单角色正面、单张深度图，不足以排除宣传图工作流中其他参数或预处理导致发灰，不构成颜色保证。
- 证据锚：[强度对照 QC](../../experiments/remote-dc7a1512-0429-4264-9163-4378e1f6671b_frost_scout_front_ab_20261025/strength_ab_20261025/QC.md)、[并排图](../../experiments/remote-dc7a1512-0429-4264-9163-4378e1f6671b_frost_scout_front_ab_20261025/strength_ab_20261025/strength_contact_sheet.png)。来源任务 `remote-dc7a1512-0429-4264-9163-4378e1f6671b`。

### C-QWEN-NODES-20261025-02 | Hy3D mesh depth 作为 turnaround 深度输入
- 状态：✅现行（valid_from 2026-10-25）
- 现行值：ComfyUI 0.42.1、Torch 2.13.0+cu130、CUDA 13.0、RTX 4090 上，`ComfyUI-Hunyuan3DWrapper` commit `2609efa38f6a98292476f714839b7c1e5f9b699a` 的 `Hy3DLoadMesh`、`Hy3DRenderSingleView` 和 `Hy3DRenderMultiViewDepth` 实际可运行。一个既有 Desert Guard GLB 成功输出 1024² RGB 深度 PNG；多视图显式配置 0/90/180/270 度时返回四张顺序对应的完整视角深度图。深度背景为黑色，RGB 三通道相同；mask 应经 `MaskToImage` 才能交给 `SaveImage`。
- 边界：这是当前单角色/当前运行环境的节点可行性实测，不证明其他版本与网格均兼容。多视图节点会卸载 ComfyUI 已加载模型；阶段 3 目标画布的裁切/留边适配及仰俯角仍待验证。
- 时间线：2026-10-25 初始 preflight 时节点未注册；安装扩展及目标依赖、经 Hive0 服务卡片重载共享实例后，运行时 schema 与单/多视图实际执行通过。单视图第一次将 MASK 直接连接 SaveImage 导致该保存节点类型校验失败，深度输出成功；随后使用 `MaskToImage` 修正并完成四张 mask 输出。
- 证据锚：[阶段 2 skill](../skills/qwen-turnaround-mesh-depth/SKILL.md)、[Hy3D 实验与四视角输出](../../experiments/qwen_turnaround_hy3d_preflight_20261025/README.md)、实验 `schemas.json`、`history-multiview.json`。来源：Sean 授权的 2026-10-25 对话（无 Task Center T-ID）。

### C-QWEN-NODES-20261025-03 | Hy3D 深度的阶段 3 适配与单样本视觉结果
- 状态：✅现行（valid_from 2026-10-25）
- 现行值：将 1024² Hy3D RGB 深度图按 `x=[128,896)` 居中裁切且不缩放，转成 768×1024 8-bit L 灰度后，可在 Qwen Image 2.1 BF16 + Fun Control BF16、seed 423211、strength 0.5、25 steps 的当前环境中分别成功生成侧面与背面输出。正面保留原参考。
- 边界：每视角只有一个 seed；左侧面只有轻微腿/靴重叠。背面生成图显示右后腰水壶，与接受外观参考中水壶位于前侧、直后视应遮挡的空间约束不符；Hy3D 180°图本身也显示该突起。完整三视图未被接受。与 2026-10-24 Blender 深度旧样本 prompt 不同，不能将差异单独归因于深度来源。
- 覆盖关系：补充 C-QWEN-NODES-20261025-02 所列待验证的阶段 3 画布适配，并确认适配方式仅对该 768×1024 目标画布有效；不改变 Hy3D 节点契约及四方位顺序。
- 证据锚：[阶段 3 实验与 QC](../../experiments/qwen_turnaround_stage3_hy3d_20261025/README.md)、`manifest.json`、两视角 `workflow.json` / `history.json` / `receipt.json`。来源：Sean 授权的 2026-10-25 对话（无 Task Center T-ID）。
