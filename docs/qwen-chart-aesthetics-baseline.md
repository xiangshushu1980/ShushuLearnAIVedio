# Qwen Turbo 图表材质重构基线

Owner: Sean。2026-10-15；仅固定人工数据甲20/乙70/丙40/丁90的1536×1024正视高度编码。

程序参考固定数据几何、文字与排版，原生TextEncodeQwenImage21同时接视觉编码和VAE reference_latents，resolution=0。节点输出的采样latent为参考尺寸全零张量；不声称另一套无参考latent算法。Turbo INT8ConvRot、BF16 Qwen3VL8B/VAE、Euler CFG1、官方8步sigma，PE off。

厚玻璃与拉丝金属各20/20独立seed联合通过文字、实体高度/基线/轴和实质材质变化；容差2单位，最大实体高度误差1.918/1.087。玻璃具有折射边壁与内部反射，金属具有反射、拉丝与明暗切边。纸雕14/20，建筑/斜视未建立稳定路径。不外推真实隐藏进深、体积、任意新数据或自由排版。

执行时先查队列与hive-resource，成功acquire再提交，持续续租并finally释放。每图检查实体自身底-顶高度，不能只核柱顶；灰白反光不可用纯蓝色阈值误判实体边缘。

权威评估：[研究正文](../../infograph-research/hands-on/qwen-turbo-chart-aesthetics/notes.md)。复现参数、实际提示、原图hash、workflow与逐图QC：[实验目录](../experiments/sean_qwen_turbo_chart_aesthetics_20261015/README.md)。沿用该目录冻结提示，不以手册摘要替代完整参数。
