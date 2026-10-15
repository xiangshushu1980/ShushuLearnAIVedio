# Qwen 数据图表结论谱系

Owner: Sean。

### C-QWENCHARTS-20261015-01 | Turbo 数据几何的可控范围

- 状态：✅现行（valid_from 2026-10-15；仅所测本地实现、数据和编辑范围）。
- 现行值：Qwen Image 2.1 Turbo INT8 ConvRot，BF16编码器/VAE，1536×1024，Euler/CFG1/官方8步sigma：四类别单系列T2I精简/详细×PE off/on各0/20，比例与网格明确版另0/20；完整字体/线条参考编辑5/20。程序准确绘图后，仅换背景的原生参考编辑单系列及双系列各20/20，满足≥18/20操作阈值，最大几何误差0.14/0.152单位（容差2单位）。
- 时间线（append-only）：
  - 2026-10-15：提出；任务 infograph-research/Qwen Turbo 简单图表控制 · remote-31c37e9c-c14a-45ca-a261-963e846990c2。176张图，160正式/16调试，2次专用PE改写。PE每输入固定一次，不代表跨PE seeds的普遍效果；非盲文字复核＋像素测量。20/20 Wilson95%区间83.9%–100%，未证明总体成功率≥90%。
- 证据锚：[实验参数与结果](../../experiments/sean_qwen_turbo_chart_control_20261015/README.md)、[逐图QC](../../experiments/sean_qwen_turbo_chart_control_20261015/qc.json)、[研究正文](../../../infograph-research/hands-on/qwen-turbo-chart-control/notes.md)。
- 适用边界：背景色的小范围编辑；自由重设计、任意新数据、折线与更多类别未验证。不是纯文本生成稳定的结论。

### C-QWENCHARTS-20261015-02 | Turbo 实质材质重构与空间边界

- 状态：✅现行（valid_from 2026-10-15；固定数据、正视高度编码、所测本地实现）。Owner: Sean。
- 现行值：程序准确几何＋原生参考编辑，Turbo INT8ConvRot/BF16编码器及VAE、Euler CFG1官方8步，PE off；玻璃/金属各20/20联合通过文字、实体高度/基线/轴与材质重构，最大实体高度误差1.918/1.087单位（容差2）。纸雕14/20；建筑与斜视各20seed未建立稳定全几何路径。
- 时间线（append-only）：
  - 2026-10-15：任务 infograph-research/图表美学重构 · remote-caf48d7f-9cb6-4a6a-a035-be7b6357879d，112张原图（100正式/12调试），非盲主Agent复核。扩展C-QWENCHARTS-20261015-01的背景编辑证据，不回写前轮未做实验。完整约束含实际实体底-顶高度，不能只测顶部相对轴位置。20/20不等于证明总体成功率≥90%。
- 证据锚：[当前运行基线](../../docs/qwen-chart-aesthetics-baseline.md)、[实验manifest/QC入口](../../experiments/sean_qwen_turbo_chart_aesthetics_20261015/README.md)、[研究正文](../../../infograph-research/hands-on/qwen-turbo-chart-aesthetics/notes.md)。
- 适用边界：柱体材质实际改变，未证明任意排版/数据/物体形式/视角均稳定。建筑8/20仅投影必要检查，斜视8/20仅前棱候选，不得写成联合通过率；透明反射与隐藏几何不明时不计通过。原始图无后期修复。
