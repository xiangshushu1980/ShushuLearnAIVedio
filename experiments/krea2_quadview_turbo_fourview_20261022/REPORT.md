# Krea2 Turbo QuadView 四视图正面留空试跑

日期：2026-10-22

任务：T-comfy-ops-48

## 工作流

以作者的 `QuadView_krea2_v1` ComfyUI workflow 为来源，另存为本机 Turbo 四视图版本：[UI workflow](../../workflows/ui/krea2_quadview_turbo_fourview_frontblank.json)。同一份文件已复制到 ComfyUI 工作流目录，可直接打开。配套 API graph：[krea2_quadview_turbo_fourview_frontblank_api.json](../../workflows/krea2_quadview_turbo_fourview_frontblank_api.json)。本机底模为 `krea2_turbo_fp8.safetensors`，LoRA 为 `QuadView_krea2_v1.safetensors`。

底层通用触发提示原样保留：

```text
Convert the character in the image to a Character Sheet showing a face close-up, front full body, side full body and back full body views.
```

额外的 panel-specific 规则按首轮结果修订为：

```text
Panel-specific face rule: In the leftmost first panel, the face close-up shows the normal recognizable face with eyes, eyebrows, nose, and mouth. In the second panel (front full-body view) only, the face is a smooth blank surface with no eyes, eyebrows, nose, or mouth. In the third panel (side full-body profile), show the normal visible profile face. Do not leave the face blank in the close-up or side-view panel.
```

角色提示只补充角色独有的外观/签名物品，不重复视图布局。三张参考分别是剑士、红法师、矮人工程师；seed 为 `202610220401`、`202610220402`、`202610220403`。参数：1536×1024、10 steps、CFG 1、Euler/simple、LoRA 1.0、ref boost 1.0、grounding 768、positive grounding 0。

## 结果

| 角色 | 首轮 wall time | 面板规则修订后 wall time | 面部/视图检查 | 配件观察 |
|---|---:|---:|---|---|
| 剑士 | 51.288 秒 | 21.270 秒 | 修订后特写有脸、正面留空、侧脸可见；四栏顺序正确 | 腰侧剑具可见 |
| 红法师 | 21.163 秒 | 21.123 秒 | 修订后特写有脸、正面留空、侧脸可见；四栏顺序正确 | 法杖仍缺失 |
| 矮人工程师 | 21.087 秒 | 21.156 秒 | 修订后特写有脸、正面留空、侧脸可见；四栏顺序正确 | 背部铜齿轮包未稳定还原 |

首轮规则虽然写了“front view only”，却把三张脸部特写都画空，且剑士、法师的全身正面仍有脸。把规则改成明确的第 1/2/3 栏之后，三张都符合目标。这是同一参考与 seed 的 prompt 迭代，结果只说明本批样本中的面部 panel 控制有效。红法师法杖仍丢失，矮人工程师背部包也不稳定，说明 QuadView prompt + 特征提示仍不能保证配件完整。

耗时为 runner wall time，包含 HTTP 提交和轮询，不等同纯采样耗时。第二轮均值约 21.18 秒/张。

## 产物

- 两轮参考、提示词、固定 seed、实际 API workflow、receipt、生成图均保存于本目录的 `v1/` 和 `v2/`。
- 结果图：`v2/swordswoman/output.png`、`v2/red_mage/output.png`、`v2/dwarf_engineer/output.png`。
- 本轮只验收静态视图板 prompt 行为；未做 H3 下游验证，也没有晋升 canonical reference。
