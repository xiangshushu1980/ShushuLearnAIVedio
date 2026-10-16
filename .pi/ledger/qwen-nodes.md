# Qwen 图像节点与预览结论谱系

## 条目索引

| C-ID | 主题 | 状态 | 备注 |
|---|---|---|---|
| C-QWEN-NODES-20261016-01 | QwenImage21Cache 与 Tiny VAE 预览 smoke | ✅现行 | Cache default/off 同图；int8 近似但细节有变 |

### C-QWEN-NODES-20261016-01 | QwenImage21Cache 与 Tiny VAE 预览 smoke
- 状态：✅现行（valid_from 2026-10-16）
- 现行值：四张有序参考图经 `TextEncodeQwenImage21` 可完成 Qwen Image 2.1 Turbo 生成；同 seed 的 cache `auto/default` 与 `off/default` 输出像素完全相同；`auto/int8` 平均绝对 RGB 差为 0.572/255，但小细节有变化。Tiny decoder 接入 KJNodes live preview，最终输出仍由 BF16 VAE 解码。
- 时间线：
  - 2026-10-16 实测：1024×1024、8 步、seed 421016、四张身份/服装/护具/刀参考图；单次耗时受首轮模型加载影响，不作为加速比结论。来源：2026-10-16 自由会话（无 Task Center T-ID）。
- 证据锚：`docs/50_qwen_image_2_1_nodes_and_tiny_vae.md`；`experiments/sean_qwen21_cache_textencode_tinyvae_20261016/README.md`。
