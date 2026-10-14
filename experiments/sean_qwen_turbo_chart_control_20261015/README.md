# Qwen Turbo 简单柱状图控制实验

Owner: Sean。Task Center: remote-31c37e9c-c14a-45ca-a261-963e846990c2。

实验开始 2026-10-15（Asia/Shanghai）。事先锁定 [plan.json](plan.json)：人工构造四类别数据甲20、乙70、丙40、丁90，1536×1024。精简/细节提示词 × 官方 PE 关闭/开启。两个调试 seeds 与20个正式 seeds 分离；每格完整通过至少18/20。

逐图检查标题、四类别、四数值与绑定关系、顺序、柱数、共用基线、纵轴0–100及20单位等距刻度、柱高线性映射、额外/遗漏数据。以实际绘图区坐标校准，柱高误差不得超过纵轴范围2%（2单位）；不要求所有生成图布局位置相同。文字/坐标轴人工核对，几何保存像素测量；不确定结果不算通过。详细提示仅追加视觉描述，数据约束不变。所有生成图保持原样。

PE 使用 qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors 专用权重，固定 rewrite seed 271828，每个输入只改写一次。专用 PE 输出作为冻结纯文本输入到所有生图 seeds；结论限于这两次改写，不代表跨 PE seeds 的稳定性。保留 PE workflow、thinking、实际输出和运行记录。CFG=1 下 negative 无采样作用，不让 PE 改变画布或采样参数。

Turbo diffusion 为本地 INT8 ConvRot，基础编码器与VAE为BF16；Euler、CFG1、官方8步sigma schedule。结论限定该实现，不外推未测 BF16 Turbo/API版本。

官方参考：[Qwen Turbo生成和编辑](https://github.com/QwenLM/Qwen-Image-2.1)；[ComfyUI native workflow](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1)。如纯文本未稳定，按同一数据程序绘图并通过 TextEncodeQwenImage21 的 reference_latents 路径测试图像编辑，单独报告。

`run.py` 在提交前检查共享队列，获取GPU租约、90秒续租、结束释放；按图归档工作流、prompt ID、history、图像hash、耗时和GPU采样。仅归档及清理本批次拥有的ComfyUI临时输出。没有操作共享实例启停。

## 最终结果

共178个成功工作流：176张图（160正式、16调试）与2次专用PE改写。详见 [manifest.json](manifest.json)、[qc.json](qc.json)、[paired_comparisons.json](paired_comparisons.json) 和 [研究评估正文](../../../infograph-research/hands-on/qwen-turbo-chart-control/notes.md)。

| 条件 | 完整通过 |
|---|---:|
| 首轮四格精简/详细 × PE off/on | 各0/20 |
| T2I v2逐柱网格位置和百分比说明 | 0/20 |
| 程序参考＋完整字体/线条风格编辑 | 5/20 |
| 程序参考＋只换背景，单系列 | 20/20 |
| 程序参考＋只换背景，双系列扩展 | 20/20 |

稳定路径限定背景色编辑。它不证明纯文本模型能准确构造数据图形，也不证明任意风格重设计能保留数据。单系列与双系列最大误差分别0.14、0.152单位（上限2单位）。PE为每输入一次固定改写，本轮完整通过率没有提升；提示细节影响依条件而变，不能笼统解释成所有细节都有害。

[完整性检查](integrity_check.json)核对178个回执的产物hash、工作流节点引用和尺寸，没有错误。单/双系列成功组各20个不同像素hash。总运行回执耗时695.04秒，采样峰值显存23,246MB、76°C。队列与GPU租约收尾为空，共享服务继续运行。

原始 `images/` PNG和 `contact*.jpg` 联系表为本地实验产物，不进入Git；manifest保存每张图的SHA-256及运行记录。程序参考PNG、精确坐标、提示词、workflow、回执、QC、完整性记录和复现脚本进入scoped commit。无需下载模型或重启服务即可复现；需要先具备相同本地组件、运行中ComfyUI和成功GPU租约。`run.py pe/debug/confirm`、`v2.py debug/confirm`、`edit.py debug/confirm`、`edit_v2.py debug/confirm`、`grouped.py debug/confirm` 分阶段执行；旧成功回执用于续跑，重新采样需使用独立实验目录。所有GPU入口都有租约、续租及finally释放。
