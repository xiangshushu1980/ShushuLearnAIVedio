# Sean — 多高清 Ref2VA + Continuum 6×8 秒上限测试

owner: Sean
date: 2026-09-25

## 配置

- 5 张高清参考图，`reference_size=Max Identity`
- Continuum V3.4，6 chunks × 8 秒
- 1024×576，Ref2VA，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step；Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：1152 帧 / 47.999 秒 / 1024×576
- 峰值显存采样：约 23102 MiB / 24564 MiB
- 主机内存采样峰值：约 53575 MiB；最低可用约 5684 MiB
- 执行时间：约 792.2 秒（13.2 分钟）
- 输出：[sean_ref2va_multiref_6x8_1024_00001_.mp4](../comfyui_output_archive_20260928.md)

## 结论

6×8 秒（约 48 秒）在 4090 24GB 上仍可完成。显存峰值仍约 23.1GiB，没有随拼接总时长线性增长；主要代价是每增加一个 chunk，执行时间显著增加。5 张高清参考图本身没有把显存推过上限，主机内存仍是 Assemble/解码阶段的主要风险。
