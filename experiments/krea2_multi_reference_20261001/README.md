# Krea 2 多参考图合成实验

> Owner: Sean。状态由 `manifest.json` 管理。本实验仅评估 Krea 2 多参考图生图，不把结果登记为 canonical 人物资产。

## 目标

在同一张新图中组合两个人物脸部身份、场景和独立物品参考，观察参考数量增加后的人脸保持、元素归属、场景融合、物品迁移和拼贴倾向。

## 本地入口与依据

- 使用当前运行时注册的 `TextEncodeKrea2Reference`，最多接 4 张图；提示词通过 `character1`、`character2` 将两张人脸图绑定到不同人物。
- 使用 `Krea2ReferenceLoraLoader` 的 `krea2_style_reference.safetensors`，text fusion 1.0、DiT body 0.0；社区节点说明称这组值用于 reference addressing/anti-bleed。
- 运行时提示 encoder 用 Qwen3-VL vision tokens；本次采用已注册的 `qwen3vl_4b_bf16.safetensors`。本地 Krea2 文档仍记录 FP8 encoder 作为普通生图基线，本实验的多图编码使用节点 README 推荐的 BF16。
- 单图/身份编辑既有流程见 [Krea2 专题](../../docs/40_krea2_prompt_and_identity_pipeline.md)；视角资产正式流程见 [Reference 手册](../../docs/45_ref_asset_handbook.md)。

## 实验结果

10 张对照已完成。两个人脸参考和场景参考在本批中组合稳定；第 4 张独立物品图容易被当成额外展示面板，`layout_split=0.25` 只在一个 seed 上完全改善。逐图结论见 [QC.md](QC.md)，实际请求与生成参数见 `manifest.json` 和 `api_workflows/`。

## 对照设计

固定 Krea2 Turbo、参考 LoRA、提示词主体、输出尺寸和两组 seed；逐步增加参考：

1. 一张剑士脸部参考；法师身份用文字描述（单人物参考基线）。
2. 两张脸部参考，分别指定剑士和法师。
3. 两张脸部参考 + 独立环境图。
4. 两张脸部参考 + 环境图 + 独立法杖图。
5. 四参考完整条件额外比较 `layout_split=0.25` 与 `0`。

脸部和道具裁切在 ComfyUI 图中完成，裁切坐标固定记录。场景与物品辅助图先由 Krea2 文生图生成；它们只是条件输入，不计入多参考合成结果。

## 评估项

- 两张脸是否各自保留，是否发生身份混合或复制；
- 剑士/法师服装、发型、主色和道具是否归属正确；
- 环境构图是否融合为同一空间，是否退化成参考图拼板；
- 法杖的蓝色宝珠、木杆和金属装饰是否迁移；
- 参考数量和 `layout_split` 对画面布局、提示词服从度的影响。

每张图由人工目视复核，结果完成后更新 `QC.md` 和 manifest。没有人工复核前，实验状态保持 `review`。
