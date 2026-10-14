# Qwen 数据图表结论谱系

Owner: Sean。

### C-QWENCHARTS-20261015-01 | Turbo 数据几何的可控范围

- 状态：✅现行（valid_from 2026-10-15；仅所测本地实现、数据和编辑范围）。
- 现行值：Qwen Image 2.1 Turbo INT8 ConvRot，BF16编码器/VAE，1536×1024，Euler/CFG1/官方8步sigma：四类别单系列T2I精简/详细×PE off/on各0/20，比例与网格明确版另0/20；完整字体/线条参考编辑5/20。程序准确绘图后，仅换背景的原生参考编辑单系列及双系列各20/20，满足≥18/20操作阈值，最大几何误差0.14/0.152单位（容差2单位）。
- 时间线（append-only）：
  - 2026-10-15：提出；任务 infograph-research/Qwen Turbo 简单图表控制 · remote-31c37e9c-c14a-45ca-a261-963e846990c2。176张图，160正式/16调试，2次专用PE改写。PE每输入固定一次，不代表跨PE seeds的普遍效果；非盲文字复核＋像素测量。20/20 Wilson95%区间83.9%–100%，未证明总体成功率≥90%。
- 证据锚：[实验参数与结果](../../experiments/sean_qwen_turbo_chart_control_20261015/README.md)、[逐图QC](../../experiments/sean_qwen_turbo_chart_control_20261015/qc.json)、[研究正文](../../../infograph-research/hands-on/qwen-turbo-chart-control/notes.md)。
- 适用边界：背景色的小范围编辑；自由重设计、任意新数据、折线与更多类别未验证。不是纯文本生成稳定的结论。
