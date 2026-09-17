# 批量实验与质检

## 最小实验契约

每个实验至少记录：模型、文本编码器、VAE、分辨率、steps、CFG、sampler、scheduler、seed、prompt 版本、输出路径和人工判断。

## 对比方法

- 一次只改变一个变量。
- 同一组实验固定 seed 和尺寸。
- 使用 contact sheet 或网格图进行并排比较。
- 失败结果保留，不只保存最好的一张。
- 结论必须标明适用模型、版本、硬件和是否经过用户目视确认。

批量运行先查 [工作流索引](README.md) 中的现成 JSON 和 `scripts/h3_batch_runner.py` 等对应脚本；API 提交与结果查询见 [环境与 API 文档](../../../../../docs/01_environment.md)。新节点的验证方法见 [core/validation.md](../core/validation.md)。
