# T-comfy-ops-27 进度：LongCat 1.5 本机性能优化

> 目标：4090 上把 LongCat Avatar 480p 93帧 at2v 从 7min/步 降到 <1min/步。

## 状态总览
- [ ] ① 实测基线确认（INT8+SDPA ~7min/步）
- [ ] ② 装 flash-attn2（需评估换 torch 或源码编译成本）
- [ ] ③ 评估/切换 kijai ComfyUI-WanVideoWrapper LongCat 支持（bf16/fp8，社区 4090D ~60s/步）
- [ ] ④ 开 Triton+BSA
- [ ] ⑤ 验证 INT8 反量化是否 CPU 回退
- [ ] 验收：480p 93帧 at2v <1min/步

## 背景（来自 T-comf-01 会话）
- 本机 rookiestar28 节点 INT8+SDPA 480p 93帧 at2v：~7min/步，sageattn 无提升。
- 社区 4090D（kijai wrapper，bf16/fp8+fa2）：~60s/步。
- VisionStory A800-40GB（INT8+distill）：44s/s → 5s≈3.7min。
- LongCat 最小窗 93帧，DMD distill 固定 8 步。
- 测试工作流：comfy-ops/workflows/longcat_avatar15_at2v_test.json（API 格式，at2v/480p/8步/sageattn）。

## 待办/备注
- 瓶颈疑点：INT8 QLinear naive 反量化（每前向全量 int8→bf16）、SDPA 回退、WSL/CUDA13 缺 fa2 轮子。
- flash-attn2：官方 wheel 只到 torch2.8/cu12，本机 torch2.13+cu130+py3.13 需换 torch 栈或源码编译（要 nvcc，1-2h）。
