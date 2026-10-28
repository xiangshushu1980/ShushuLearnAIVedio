# Qwen Image 角色外观与三视图

本工作流拆为两个可独立调用的 skill：

1. [character-reference-image](/home/sean/.pi/agent/skills/character-reference-image/SKILL.md) 负责角色外观参考图的提示词、生成、视觉确认与成对保存。当前生成器是 Qwen Image 2.1；以后可在该 skill 下增加经过验证的 Krea2、Flux 等生成器。每个结果与实际提示词、模型和参数一起归档，供后续角色卡或其他工作流复用。
2. [qwen-character-sheet](/home/sean/.pi/agent/skills/qwen-character-sheet/SKILL.md) 负责用 Character Sheet LoRA 生成并检查三视图，当前唯一 Qwen Image 2.1 角色三视图配方为 BF16 base + `character-sheet-qwen-image-2.1-edit-lora-e9`。它可接收零张或一张外观参考图；纯文本模式仍属待验证实验。

两项能力共用 ComfyUI 执行、上传、资源租约和运行记录契约，但参考图生成与角色卡生成分别保留提示词及视觉验收边界。Krea2 的既有三视图方案继续保留为独立路线；Qwen Turbo 三视图不再是可发现的角色三视图预设。

## 当前 LoRA 配方与证据

共享工作流 ID 为 `qwen-character-sheet-v1`，预设 `three-view`。固定配置为 Qwen Image 2.1 BF16、Character Sheet LoRA strength 1.0、25 steps、CFG 1、Euler/simple，默认 1344×768，支持 0–1 张参考图。版式固定为同一角色的正面、严格侧面、背面三个全身栏；该路线不要求空白正脸，也不包含脸部特写。

LoRA 提示词边界、空间锚点及逐栏检查维护在 skill 和[原始道具实验报告](../../experiments/qwen21_character_sheet_lora_props_20261022/REPORT.md)。该报告里的两张参考插画、seed 7 样例显示腰侧剑鞘在正/背面保持在右腰，侧面部分遮挡；左腰包/瓶在三栏可见。那组样例没有背挂武器或跨 seed 测试；后续对照才覆盖两个角色和三个 seed 的背挂观测杖/弯刀。纯文本输入仍未验证。

本轮 18 张版式对照的面板数量统计保留在 [BF16 LoRA 视图数量对照](../../experiments/qwen_character_sheet_lora_view_count_ab_20261023/QC.md)，但用户复核指出首轮把正面+背面误标成正面+侧面，三视方向的旧 QC 不再作为通过证据。随后使用 LoRA 发布方官方 head-to-toe Angle sheet caption 原文，在两张参考图和三个 seed 上生成六张；正、背、严格侧面都可辨（6/6），但它们散布在六格中，且四张存在目标正/背面板裁头；沙漠守卫背负弯刀虽在背视可见，严格侧面 0/3 能清楚读出武器。它不是生产三栏正/侧/背提示。详见[官方提示词复核](../../experiments/qwen_character_sheet_lora_official_prompt_3view_20261023/QC.md)。

此前两视图、三视图、三视图加脸的 Turbo 对照记录在 [视图数量一致性实验](../../experiments/qwen_character_threeview_workflow_20261023/REPORT.md)，该证据不能替代 BF16 LoRA 配方的质量测试。H3 使用时从通过视觉验收的角色卡中选取一个完整全身视图，再依当前 H3 Ref2VA 规则构建提示词；不能把多栏版式要求复制到视频 prompt。

最新的无外观描述复测沿用生产三视 suffix，只传一张角色参考图和一句通用图像用途说明；两种角色、三个 seed 共 6 张，三栏方向与全身完整度 6/6。用户复核指出背挂武器不完整、常只剩刀柄，侧视多数不出现；武器可见性的初轮结论已撤回。当前只支持清晰参考图足以维持大体人物外观和三视布局，不支持背挂武器已正确还原。请求、结果、manifest 与逐项 QC 见[无外观描述三视测试](../../experiments/qwen_character_sheet_lora_no_appearance_prompt_3view_20261023/QC.md)。
