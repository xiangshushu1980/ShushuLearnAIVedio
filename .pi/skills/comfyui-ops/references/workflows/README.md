# 工作流索引（按目的）

| 目的 | 当前入口 | 说明 |
|---|---|---|
| KREA 文生图 | [workflows/krea2_t2i_test.json](../../../../../workflows/krea2_t2i_test.json) | 8 节点基础链 |
| Krea2 QuadView 参考图多视图 | [Turbo 四视图 UI 工作流](../../../../../workflows/ui/krea2_quadview_turbo_fourview_frontblank.json) / [API 工作流](../../../../../workflows/krea2_quadview_turbo_fourview_frontblank_api.json) | 原版 QuadView 提示词；脸部特写与侧脸保留五官，正面全身脸部留空 |
| ANIMA 文生图 | [workflows/anima_t2i_test.json](../../../../../workflows/anima_t2i_test.json) | 动漫生图基线 |
| H3 文生视频 | [workflows/minimax_h3_t2v.json](../../../../../workflows/minimax_h3_t2v.json) 等 | 以 H3 文档为准 |
| H3 图生/参考生视频 | [workflows/minimax_h3_ref2va_img_vid_api.json](../../../../../workflows/minimax_h3_ref2va_img_vid_api.json) 等 | 读 video/ref2va |
| 图像批量实验 | `scripts/img_qc_test.py`、现有工作流 JSON | 固定 seed/参数后比较 |
| 放大/图像后处理 | 先查旧版 `nodes.md` 对应节点 | 暂不作为 KREA 研究前置依赖 |

## 按目的选工作流

- 想验证模型能力：从最小工作流开始。
- 想验证风格：固定模型/seed/采样，只改变风格块。
- 想验证 Object ref：先生成临时样本，再测试视频输入语义，不先建正式资产。
- 想验证长视频：先读对应视频分册和现有实验 progress，不直接复制旧 JSON。

完整历史档案仍在 [旧版 workflows.md](../workflows.md)，后续按目的逐项迁移。
