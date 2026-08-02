# Bernini-R int8_convrot — 调研与下载经验快照

> **日期**：2025-08-02（本会话）
> **用途**：独立存档本次 Bernini int8 调研 + 下载经验，供文档重整（Mem0）时纳入整理。
> **状态**：int8 已下载就绪；对比测试未跑（计划见文末）。

---

## 一、背景现状

- 当前生产用的 Bernini-R 模型是 **fp8_scaled** 版（`wan2.2_bernini_r_{high,low}_noise_fp8_scaled.safetensors`，各 15.57GB），
  图像编辑（重打光）与 v2v 视频编辑均已测通。
- Bernini-R = ByteDance 官方 Bernini 的 **renderer-only**（Wan 2.2 基础上，in-context 条件注入），**不含 MLLM 规划器**；
  完整版需官方仓库（H100/多卡，固定 torch 2.5.1+cu124），ComfyUI 场景用 renderer + 自写详细 prompt（或官方 `--use_pe` 增强）。

## 二、int8 版本查找结果（已确认存在）

来源仓库：**Comfy-Org/Bernini-R**（HF，revision `e5674fad`，2026-06-30 更新）。
diffusion_models/ 下现有版本清单（大小实测）：

| 文件 | 大小 | 说明 |
|---|---|---|
| `wan2.2_bernini_r_{high,low}_noise_fp16` | 28.58 GB ×2 | 原始精度 |
| `wan2.2_bernini_r_{high,low}_noise_fp8_scaled` | 15.57 GB ×2 | 当前在用 |
| `wan2.2_bernini_r_{high,low}_noise_int8_convrot` | **14.54 GB ×2** | **int8，最小** |
| `wan2.2_bernini_r_{high,low}_noise_mxfp8` | 14.97 GB ×2 | MXFP8 块缩放（备选） |
| `wan2.1_bernini_1.3B_fp16` | 2.84 GB | 小模型 |

- **int8_convrot 含义**：int8 量化 + ConvRot（量化前对权重做 Hadamard 旋转，压低离群值 → int8 精度损失更小）。
- **兼容性**：本地 ComfyUI 0.29.0 原生支持（`comfy/ops.py` 有 `int8_tensorwise` + convrot 分支，comfy_kitchen 有 ConvRot 实现），UNETLoader 直接加载，无需换节点。

## 三、社区调研结论（int8_convrot vs fp8_scaled）

### 速度
- ComfyUI 作者（comfyanonymous）确认：**A100 上 int8 tensor ops 仅 2× fp16，而 RTX 30/40/50 系是 4× fp16** →
  **40 系列（我们的 4090）是 int8 收益最大的区间**（[Comfy-Org/ComfyUI#14824](https://github.com/Comfy-Org/ComfyUI/issues/14824)）。
- 官方 v0.27.0（2026-06-30）引入 int8 convrot，宣称大部分 NVIDIA 卡提速 **1.5–2x+**；v0.27→0.29 连续优化 int8。
- ⚠ 平台差异实测：
  - RTX 5090：int8 直通硬件，明显加速。
  - **A100 / A6000（Ampere 数据中心卡）：反而慢 33–50% 或持平**（布局不匹配时后端静默反量化回 float 跑）。
  - AMD ROCm + triton 后端：NaN 黑图 bug（[#15084](https://github.com/Comfy-Org/ComfyUI/issues/15084)）。
  - 上述两个风险点与我们的 4090（NVIDIA/CUDA）无关。

### 画质
- 官方设计目标：ConvRot 质量接近 fp8/fp16。
- 用户实测（krea2 int8_convrot）：有轻微接缝拼接感，**但 fp8 同样有** → 非 int8 特有。
- **Bernini-R int8 刚上架，无专属画质/速度数据，只能实测确认。**

### 关键判断
⇒ **值得下载**。4090 + ComfyUI 0.29.0 = int8 优化的目标硬件组合，三个已知风险点（Ampere/ROCm/第三方节点）均不沾。
唯一不确定是加速幅度：Bernini 本身是 6 步 Turbo（已快），VAE/attention 等非 int8 部分不加速，端到端可能低于官方 2x。

## 四、下载记录

- **URL**：`https://hf-mirror.com/Comfy-Org/Bernini-R/resolve/main/diffusion_models/wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`
- **目标大小**：各 `14535868680` 字节（14.54 GB）。
- **工具**：wget `-c`（断点续传）+ `--tries=0`（无限重试）+ `--timeout=30`，后台并行。
- **落盘**：`/home/sean/projects/ComfyUI/models/diffusion_models/`
- **时间线**：02:30 启动 → VPN 开启后速度飙升 → 02:45/02:48 先后完成（约 18 分钟，远快于预计 60–70 分钟）。
- **网络经验**：`hf-mirror.com` 直连（不开 VPN）实测约 8.6 MB/s；开启 VPN 后大幅提速。GitHub 直连时通时不通（7890 代理端口未监听，勿依赖）。
- **完整性校验（全部通过）**：
  1. 字节数精确等于目标 `14535868680`；
  2. safetensors header 长度 `190464` 可解析；
  3. wget 日志 `rc=0`（正常收尾，非断线中止）。

## 五、当前就绪状态

- int8 双模型已下载、字节校验通过 ✅
- ComfyUI 在线（0.29.0，含最新 int8 优化）●
- GPU：RTX 4090 24GB ✅

## 六、待办：对比测试计划

1. **快速验证（图像编辑）**：复用 `workflows/video_bernini_r_test.json`（length=1 单帧重打光），同 seed 分别跑 fp8_scaled / int8_convrot → 比加载正常性 + 画质 + 单帧速度。
2. **完整验证（视频 v2v）**：复用 `workflows/video_bernini_r_v2v_test.json`（length=41，Alya 金色时刻）→ 比视频长期一致性 + 显存占用。
3. 结果写入本快照 + 原 `docs/06_extras_install.md` 与 SKILL 参数分册。

---

## 七、实测结果（2025-08-02，已完成对比）

### 图像编辑（length=1 单帧，骑士重打光，同 seed 777）

| 模型 | 耗时 | 清晰度 | 说明 |
|------|------|--------|------|
| fp8_scaled | 52.8s | 778 | 基线 |
| int8_convrot | 62.4s | 771 | 慢 18%，画质 -0.9%（几乎无损）|

- 同 seed 像素差异均值 2.08（几乎相同图像）→ **int8 画质无损**
- 单帧任务 int8 慢：模型加载 + convrot 布局转换开销占大头（仅 1 帧生成）

### v2v 视频（length=81，Alya 金色时刻，同 seed 777）← **关键稳态测试**

| 模型 | 耗时 | 平均清晰度 | 帧间差异（一致性）|
|------|------|-----------|------------------|
| fp8_scaled | 133.1s | 999 | 18.61 |
| int8_convrot | **105.1s** | **1023** | 18.72 |

- **int8 快 21%（-27.9s）**，清晰度反而略高（+2.4%），一致性完全持平
- 8 采样帧全部 int8 清晰度 ≥ fp8 → 画质无退化迹象

### 🎯 甜点结论

- **视频任务（v2v/生成）用 int8_convrot**：快 21% + 画质无损 —— **明确甜点，直接换用**
- **图像单帧任务**：int8 加载开销主导反而慢，画质无损 → 单帧编辑仍可留 fp8（或预加载后 int8）
- int8 模型 14.54GB vs fp8 15.57GB（省 1GB），显存压力更小
- 对比图：`output/compare/bernini_fp8_vs_int8.png`（2×2：图像 fp8/int8 + 视频 fp8/int8）

### 待办
- [x] 图像编辑对比（画质/速度）
- [x] v2v 视频对比（速度/一致性/显存）
- [ ] 结果同步 docs/06 与 SKILL 参数分册
- [ ] 默认工作流切换到 int8（`video_bernini_r_v2v_test.json` 等）
