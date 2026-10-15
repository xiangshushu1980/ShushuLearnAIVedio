# Qwen Turbo 图表美学重构

Owner: Sean。任务 remote-caf48d7f-9cb6-4a6a-a035-be7b6357879d。

参数、调试与独立复核 seeds、联合验收规则在 plan.json 中，生成前冻结。初轮三材质仅改变材质描述，共用几何、采样与 seeds。几何、文字与实质美学变化同时通过才算成功。原始图不做修复。

原生 TextEncodeQwenImage21 使用视觉文本编码和 VAE reference_latents；返回的是参考尺寸的全零采样 latent，不是参考图 img2img 初始 latent。图像编辑和参考生图不是本地两套已证实独立方法。官方模板副本来自前轮实验；本轮已重新核对在线官方文档和本地源码。

## 结果与复现

112张原图（100正式＋12调试），507.49秒回执耗时，观测峰值显存23283MB/76°C。正视玻璃20/20、金属20/20、纸雕14/20联合通过；最大实体高度误差1.918/1.087/3.569单位。建筑20seed、斜视20seed均未建立稳定全几何路径。圆柱仅2调试，违反相机约束后不做稳定性声明。

[完整评估正文](../../../infograph-research/hands-on/qwen-turbo-chart-aesthetics/notes.md) · [原图浏览](review.html) · [summary](summary.json) · [QC](qc.json)。建筑8/20投影必要检查与斜视8/20前棱候选不等于完整通过率；透明/隐藏几何不可判定时不计通过。

运行 generate.py debug/confirm；分阶段运行 generate_stage.py stage2_plan.json debug，confirm glass_building_v1；generate_stage.py stage3_plan.json debug/confirm。脚本检查共享队列，成功acquire后才提交；TTL600s，<=90s续租，finally释放。仅复用当前实验成功回执；新复核需新目录与独立seed。采样与节点链详见各workflow。未重启共享实例，无生成后修复。

measure.py的蓝色阈值仅为候选；金属白色反光边缘需 measurement_overrides.json 的灰度测量。summarize.py同时检查实际实体底-顶高度、顶位置、基线和轴，纸雕6张失败包括2.005单位边界，未放宽容差。measure_buildings.py和measure_spatial.py保留不充分的几何证据，不能自动当作成功。spatial_review_sheets.py仅产生独立QC联系表，images/始终原图。

原始PNG/contact本地保留，不入Git；manifest保存hash。模型hash继承前轮全量计算并核实size/mtime；不是本轮重新hash。官方模板副本/本地节点hash用于溯源。无PE改写，未使用文件中继承的T2I PE权重。
