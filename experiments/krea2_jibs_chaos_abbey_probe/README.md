# KREA2 + Jibs：红色虚空腐化人类修道院探针

## 定位

独立风格实验，不属于 `wow-mage-survival` 正式剧情或视觉资产。目标是测试 KREA2 + Jibs 能否表达：人类修道院空间骨架、红色主题、虚空混沌腐化、重甲人类卫士和虚空牧师。

## 工作流与参数

- 模型：`krea2_turbo_fp8.safetensors`
- 文本编码器：`qwen3vl_4b_fp8_scaled.safetensors`，`CLIPLoader type=krea2`
- LoRA：`Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors`
- LoRA strength：`1.0`
- 尺寸：`2048×1152`
- Steps：`8`
- CFG：`1.0`
- Sampler / scheduler：`er_sde / simple`
- Seed：`37231`
- Reference image：无，纯提示词 + Jibs LoRA

## 初步观察

- 成功保留了中央塔楼、两翼、长台阶和修道院入口的空间识别度。
- 红色天空、红黑重甲、裂隙和紫色虚空火焰表达清晰。
- Jibs 能把“混沌重甲 + 中世纪建筑”整合成一张统一画面。
- 人类卫士和牧师的角色分工可读，但人物数量较多，局部细节会互相竞争。
- 画面偏概念插画和游戏宣传图，不是 WOW 原作截图，也不是正式项目风格结论。

## 原始工作流请求

- [request.json](request.json)
- 输出：`chaos_abbey_red_human_guard_priest_00001_.png`
