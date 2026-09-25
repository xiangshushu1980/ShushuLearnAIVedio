# T-comfy-ops-40：小说视频 AI 设定图能力研究

## 任务边界

- 目标：为人物、场景、法术准备可批量复用的细节设定图能力。
- 本线聚焦能力层：工作流方法、ComfyUI 节点、参考图/一致性、区域控制、批量生成、质检与资料沉淀。
- 避让 `T-comfy-ops-37` 的总风格确认，以及其他 Agent 的 Civitai 模型/LoRA 搜索。
- 当前工作区存在大量其他 Agent WIP；本任务只新增自己的 progress/研究文件，不修改共享 skill、工作流或模型文件，除非后续明确分工。

## 当前结论

- 项目已有 KREA 2 基础模型、基础文生图工作流和 `Krea2PromptWeight`，但没有完整的设定图生产研究线。
- 研究应先建立能力矩阵，再把候选模型/LoRA 插入固定测试协议；模型/LoRA 名单由另一条线提供，本线不重复筛选。
- 本机已安装节点：`ComfyUI-KJNodes`、`rgthree-comfy`、`ComfyUI-Florence2-main`、`ComfyUI-RMBG` 等；未发现已安装的 `ComfyUI_IPAdapter_plus`、`comfyui_controlnet_aux`、`ComfyUI-Advanced-ControlNet`、`ComfyUI-Impact-Pack`、`ComfyUI_UltimateSDUpscale`。
- 第一轮外部能力核查：IPAdapter Plus 适合参考图的主体/风格/构图迁移；ControlNet Aux 提供姿态、深度、边缘等控制图预处理；Advanced ControlNet 适合时间/权重/遮罩调度；Impact Pack 覆盖检测、分割、Detailer、区域 ControlNet/IPAdapter 与放大管线；UltimateSDUpscale 适合传统 SD 式分块高分辨率细化。
- IPAdapter Plus 当前仓库自述已进入 maintenance-only，因此作为候选能力验证，不预设为长期核心依赖。

## 第一轮边界

- 不抢另一 Agent 的 Civitai 模型/LoRA 搜索；本线只定义测试协议和能力接口。
- 不把 SD 时代的“高 CFG、负面词、LoRA 权重经验”直接迁移到 KREA 2；先做 KREA 2/ANIMA 的小样本 A/B。
- 不先安装大型扩展包；先按“角色参考→结构控制→局部细化→批量/质检”顺序验证必要性。
- 2026-09-17 用户收缩范围：当前优先只研究提示词与风格限制，生成风格统一的人物、场景、法术资源；不预设 ControlNet/IPAdapter/Detailer 等复杂节点。基础链路以 KREA 2 为主，高清放大仅作为可选项。
- 2026-09-17 用户进一步明确：输入是剧本/统一世界观，当前交付优先是供视频工作流消费的 `Object ref` 资产库；分镜脚本图、运动路线图暂不进入第一阶段。
- `Object ref` 最小范围：项目风格锚点、角色基础身份与剧本实际需要的状态变体、场景锚点、剧情关键道具、必要时的法术效果锚点。情绪/动作等不改变外观的状态优先保留在提示词，不为每个组合单独出图。
- 状态组合必须按剧本按需生成，避免年龄×衣着×受伤×情绪×变身的笛卡尔积爆炸。
- 2026-09-17 范围修正：当前不实际完成角色、场景、道具或法术资产；只做 KREA 2 + ComfyUI + 现有资源的可行性测试。测试结果形成文档、参数边界、失败记录和后续工作流需求，正式资产生产与工作流建设留到研究通过后。
- 2026-09-17 完成 ComfyUI skill 首轮兼容拆分：新增 `INDEX.md`，并建立 `core/`、`image/`、`video/`、`workflows/`、`troubleshooting/` 按需入口；综合旧档案暂保留，避免现有链接和其他 Agent WIP 受影响。`SKILL.md` 已收缩为核心入口与纪律。

## 外部资料锚点

- ComfyUI IPAdapter Plus：<https://github.com/cubiq/ComfyUI_IPAdapter_plus>
- ComfyUI ControlNet Aux：<https://github.com/comfyorg/comfyui-controlnet-aux>
- ComfyUI Advanced ControlNet：<https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet>
- ComfyUI Impact Pack：<https://github.com/ltdrdata/ComfyUI-Impact-Pack>
- ComfyUI KJNodes：<https://github.com/kijai/ComfyUI-KJNodes>
- UltimateSDUpscale：<https://github.com/ssitu/ComfyUI_UltimateSDUpscale>

## 待研究

- 角色：正面/侧面/背面、表情、服装、道具、局部细节、角色一致性。
- 场景：大全景/中景/局部、昼夜天气、空间结构、可用于视频首帧的构图。
- 法术：施法动作、能量形态、颜色/材质、冲击/持续/残留三个阶段。
- 节点：ControlNet、IP-Adapter/参考图、区域提示、姿态/深度/边缘、LoRA 组合、放大、抠图、批量与质检。
- 需要与另一条 Civitai 线共享的接口：模型文件名、LoRA 文件名、触发词、推荐权重、许可/来源、适用题材与失败样本。

## 协作状态

- 2026-09-17：创建并认领 `T-comfy-ops-40`；已声明避让 `T-comfy-ops-37` 与 Civitai 模型/LoRA 线。
- 2026-09-17：完成第一轮节点生态核查，未安装候选扩展，等待兼容性实验设计。
