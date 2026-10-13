# QC：Krea 2 多参考图合成

> Owner: Sean。目视检查人：Codex。检查日期：2026-10-01。结论仅覆盖本批输入、提示词和 seed。

## 条件结果

| 条件 | 两个 seed 的观察 | 判定 |
|---|---|---|
| `one_face`：剑士脸部图，法师身份只用文字 | 两张都生成了黑发剑士与红发法师；剑士身份/服装稳定。法师的红发与服装由文字生成，脸部没有独立身份锚点。画面合成自然，但双人全身构图多数裁到靴子。 | 单身份参考的可用基线；第二人物可由文字补出，不能据此声称身份锁定。 |
| `two_faces`：两张脸部图 | 两张都保持黑发剑士与红发雀斑法师的区分；脸、发色和服装没有互换，未出现额外人物或参考拼板。 | 2/2 通过；两张脸部身份参考有实际增益。 |
| `two_faces_scene`：两脸 + 场景图 | 两张都把石墙、拱门、庭院路径和红叶融入同一背景，没有保留独立空场景面板。生成图吸收了场景的建筑与秋叶色彩，但不复刻原参考构图/冷蓝照明。 | 2/2 融合通过；场景语义/色彩迁移明显，几何和光线仍由提示词与模型重组。 |
| `two_faces_scene_prop`：两脸 + 场景 + 法杖图 | 两张都出现明显独立的竖向法杖展示区；法杖没有稳定地作为法师手持物进入主体场景，产生物品重复/目录板式伪影。 | 0/2 通过；当前第四张物品图的语义归属失败。 |
| `two_faces_scene_prop_split025`：上述四图 + `layout_split=0.25` | seed `6100101` 仍有额外独立法杖，同时法师手中也出现法杖；seed `6100102` 将法杖并入法师手中，画面没有独立竖幅。两张的人脸和场景仍可读。 | 1/2 完全融合；layout split 有改善信号，但不足以稳定解决物品重复。 |

## 关键样本

- 双脸：[`two_faces_seed6100101_01.png`](outputs/two_faces_seed6100101_01.png)、[`two_faces_seed6100102_01.png`](outputs/two_faces_seed6100102_01.png)
- 加场景：[`two_faces_scene_seed6100101_01.png`](outputs/two_faces_scene_seed6100101_01.png)、[`two_faces_scene_seed6100102_01.png`](outputs/two_faces_scene_seed6100102_01.png)
- 四参考失败：[`two_faces_scene_prop_seed6100101_01.png`](outputs/two_faces_scene_prop_seed6100101_01.png)、[`two_faces_scene_prop_seed6100102_01.png`](outputs/two_faces_scene_prop_seed6100102_01.png)
- 布局切分对照：[`two_faces_scene_prop_split025_seed6100101_01.png`](outputs/two_faces_scene_prop_split025_seed6100101_01.png)、[`two_faces_scene_prop_split025_seed6100102_01.png`](outputs/two_faces_scene_prop_split025_seed6100102_01.png)

## 结论与边界

1. 当前节点对**两个不同人物脸部参考 + 一张场景参考**的组合可用：小样本内身份没有互换，场景也进入了同一画面。
2. 单独添加道具全图时，模型会把道具连同其竖版展示构图一起带入，导致场景外多出一根展示用法杖；仅靠“由法师手持”文字不足以稳定指定物品角色。
3. `layout_split=0.25` 对抗拼板可能有帮助，但这个四参考样本只 1/2 完全成功；不能作为默认补救结论。
4. 所有主体都是已有生成角色，且提示词详细描述了脸、服装与道具。本批不是对真人面孔保真的验证，也不测试无提示词的纯图像复制。
5. 两 seed/条件只用于先导判断。多视图正式资产仍应走现行主图→H3→抽帧→QC 流程；这些结果不提升为 canonical。

## 运行时记录

- Krea2 Turbo：8 steps / CFG 1 / `er_sde` + `simple`。
- 多参考 encoder：BF16 Qwen3-VL-4B；完整文件 8,875,719,384 bytes，SHA256 `36f3ff447ef59201722e8f9ce6020c9819fdcfba6aa2608c4e09b1c0ce114e34`。
- Reference LoRA：`krea2_style_reference.safetensors`，text fusion 1.0 / DiT body 0.0。
- 1280×832。五个条件共 10 张，单张采样约 8–14 秒；场景和法杖辅助图另行生成，各一张。
- ComfyUI workflow 与 API 提交记录在 [`api_workflows/`](api_workflows/)；逐图输出和所有 seed/prompt/run ID 在 `manifest.json`。
