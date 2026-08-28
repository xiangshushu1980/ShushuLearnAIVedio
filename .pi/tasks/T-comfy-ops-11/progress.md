# T-comfy-ops-11 Spectrum 采样加速 A/B 测试

## 结果：✅ 完成（2026-08-28）

**一句话**：Spectrum v0.2.20 仅推荐 std 慢车道 20 步 @1024×576（采样 1.55x/端到端 1.22x/画质反升）；低步数档无价值，4 步档零收益。

## 过程

1. 安装 Spectrum v0.2.20（锚点写 v0.2.15，clone 到手已是最新 v0.2.20）→ `custom_nodes/ComfyUI-Spectrum-MiniMax-H3/`
2. 重启 ComfyUI（restart_comfyui.sh，15s 就绪）
3. 写 `scripts/h3_spectrum_ab_runner.py`（独立文件，复用 easycache runner 测量框架：/free 冷态 + 进度条采样段 + 日志解析）
4. A/B 矩阵：同 seed 20260814，native vs Spectrum（默认参数），wave（低动态）+ dance（高动态）双场景 × 4 档位：
   - t20 std：int8 无LoRA 20步 @1024×576
   - s8 成片档：int8+v4 8步 @1024×576
   - f8 快速：fp8+v4 8步 @768×448
   - f4 极速：fp8+v4 4步 @768×448
5. VL 初审（qwen-vl，5 张对比拼图，帧 12/60/115）

## 数据

| 档 | 采样加速 | 端到端 | VL 评分 |
|---|---|---|---|
| t20 std | **1.55x** | **1.22x** | 8.5/10 画质反升 |
| s8 wave | 1.50x | 1.19x | 6.5/10 天空垂直拖影 |
| s8 dance | 1.55x | 1.16x | 2/10 高动态崩 |
| f8 @768 | 1.63x | 1.0x | 7.5/10 可接受但无端到端收益 |
| f4 | 1.0x | ≈1.0x | 无意义 |

调度（RES multistep）：20 步=12A+8F；8 步=6A+2F；4 步=4A+0F（warmup 1 + bootstrap + RES 三步尾保护吃满）。

## 关键认知

- **forecast 误差与 sigma 间隔成正比**：8 步每步间隔大，2 步 forecast 误差放大 → 高动态崩；20 步 anchor 密 → 准且 replay 双向平滑带来去噪红利（VL 判 Spectrum 版更清晰锐利）
- **端到端收益 = 采样占比 × 采样加速**：768×448 采样占比 ~45% → 无感；1024×576 20 步占比 62% → 可见
- wall_s 口径含 pass 间开销不可用；进度条口径与端到端自洽
- motion 分叉是预期内（forecast 改变去噪轨迹，README 明示），不计缺陷

## 产物

- docs/09_h3_test_plan.md §补测批 E（全量数据）
- docs/10_h3_batch_optimization.md §七（加速家族对比表）
- .pi/ledger/h3-speed.md C-20260828-01
- experiments/spectrum_ab/（results + frames 拼图）
- output/video/spectrum_test/（10 条 mp4）
