# [Sean] FaceRefine 长度/资源边界基准

日期：2026-09-26  
任务：`T-comfy-ops-47`  
条件：RTX 4090 24GB、1376×800 Continuum 母片、FaceRefine 独立阶段；每档开始前通过 ComfyUI `/free` + 1 帧 report-only 触发模型/显存释放。

## 固定参数

- crop：768×768，crop factor 3
- H3：`res_multistep`，8 steps，scheduler denoise 0.40
- Per-Frame Denoise：small 1.0 / large 0.35，30–120px，smooth 9
- 单人物红发角色，fast-detect face-index 0
- `face_only` stitch，丢检帧 `skip`
- 未使用 VOSR2、manifest、ROI 或 atlas

## 结果

| 输入 | 结果 | 耗时/资源 |
|---|---|---|
| 8 秒 / 192 帧 | 成功 | 222.3s；约 1.16s/帧、27.8s/视频秒；采样阶段约 23.1GiB VRAM，系统可用内存最低约 375MiB |
| 16 秒 / 384 帧 | **中止** | 进入采样后 VRAM 约 22.9GiB、GPU 100%；系统可用内存降至约 300–500MiB，并开始使用约 2.3–2.4GiB swap；为避免主机 OOM 主动中止 |
| 20/24 秒 | 未运行 | 16 秒已达到系统内存危险区，不继续扩大 |

### 源视频总长度对照

代码检查确认：`H3FaceSelect` 先通过 `VideoFromFile` 解码整个源视频，再执行 `frame_load_cap`、`skip_first_frames` 和 `select_every_nth` 裁剪。因此 runner 的 `--length 124` 并不会阻止 32 秒母片先被完整载入内存。

| 源视频 | 实际处理 | 结果 | 耗时/观察 |
|---|---:|---|---|
| 5.17 秒（124 帧） | 5.17 秒 | 成功 | 125.1s |
| 32 秒（768 帧） | 前 5.17 秒（124 帧） | 成功 | 140.6s；同处理帧数仍慢约 12.4%，且占用更多系统内存 |
| 8 秒（192 帧） | 8 秒 | 成功 | 180.2s；结束后显存回落至 740MiB，系统可用内存回升至约 49GiB |
| 8 秒核心 + 17 帧重叠（209 帧） | 8 秒核心 | 成功 | 205.4s；峰值约 23.0GiB VRAM，系统可用内存最低约 7.0GiB，swap 未继续增长 |

本组测试开始前系统 swap 已因之前中止的 16 秒任务累计使用约 3.5GiB，故不能把“swap 总量非零”直接视为本组 8 秒测试新产生的搬运；应以可用内存变化和 swap 增量判断。8 秒短源测试未出现类似 16 秒时可用内存降至数百 MiB 的危险状态。

## 当前结论

1. 8 秒清缓存基线比昨天 c1 的 275.1s 快，说明 c1/c2 的约 20%差异包含缓存/资源状态波动，不是 crop 分辨率差异。
2. 当前瓶颈不是 GPU 利用率不足：采样阶段 GPU 约 100%，显存接近 23/24.6GiB；同时系统内存几乎耗尽，16 秒开始使用 swap。
3. 16 秒可以启动，但不能视为本机安全稳定输入上限；在当前 serial 单脸 768/8-step 路线下，8 秒是目前已验证的安全分段，16 秒是风险边界。
4. 本轮不应直接测试 20/24 秒。下一步应先定位内存占用来源/降低长序列内存，再重新测试 16 秒；或者以 8 秒为生产分段基线。
5. 仅处理源视频前 0–8 秒时，输入文件总长仍然影响内存和耗时；当前实现必须在 FaceRefine 之前物理裁剪源视频。不能只依赖 runner 的 `--length`。
6. 在当前固定 768 crop、8 steps 条件下，已验证“相对安全”的组合是：物理裁剪后的源视频约 8 秒、处理 8 秒；32 秒源即使只处理 5 秒也不是等价低内存测试。由于 swap 基线已被前次 16 秒任务污染，本轮不能宣称“系统 swap 绝对为零”，但已确认 16 秒长序列进入危险区。
7. 8 秒核心段增加 17 帧（约 0.71 秒）重叠后，实际处理 209 帧，耗时从 180.2s 增至 205.4s（约 +14%）；仍未进入 swap 危险区。该配置可作为当前 8 秒拼接段的首个缓冲基线。
8. 接缝 A/B 已完成：第二段从源帧 192 开始，与第一段的源帧 192–208 重叠 17 帧；第二段耗时 201.2s，峰值约 23.0GiB VRAM、最低可用内存约 6.7GiB，swap 未增长。两段输出重叠帧的全画面差异均值约 Y=0.79/U=0.29/V=0.26（8-bit 差异量），说明存在小幅确定性差异，但还未渲染“丢弃重叠后拼接”的最终视频，不能仅凭该数值判定是否可见接缝。
9. 首次硬切评估作废：第二段错误地从源帧 192 开始，再丢弃前 17 帧，实际跳过了源帧 192–208，造成了人为的 17 帧全画面跳变。按正确规则第二段应从源帧 175 开始，前 17 帧作为缓冲，丢弃后从源帧 192 接续。
10. 已按正确帧位重新拼接：第一段保留源帧 0–191，第二段从源帧 175 输入并丢弃其前 17 帧，最终连续覆盖源帧 0–383。切点 Y 差异约 2.57/255，邻近正常帧约 1.65–2.09/255，没有首次测试中的异常全画面跳变。当前 17 帧重叠 + 正确帧对齐可以作为可用拼接基线；是否还有脸部局部差异，需再做 ROI 级比较。

## 产物

- 8 秒成片：`/home/sean/projects/ComfyUI/output/face_solution/bench_duration_red_8s_clean_20260926_00001_.mp4`
- 8 秒跟踪预览：`/home/sean/projects/ComfyUI/output/face_solution/bench_duration_red_8s_clean_20260926_tracking_00001_.mp4`
- 16 秒任务：主动中止，无效成片，不作为质量结果。
- 5 秒短源：`/home/sean/projects/ComfyUI/output/face_solution/bench_source5s_process5s_20260926_00001_.mp4`
- 32 秒源仅处理前 5 秒：`/home/sean/projects/ComfyUI/output/face_solution/bench_source32s_process5s_20260926_00001_.mp4`
- 8 秒短源处理 8 秒：`/home/sean/projects/ComfyUI/output/face_solution/bench_source8s_process8s_20260926_00001_.mp4`
- 8 秒核心 + 17 帧重叠：`/home/sean/projects/ComfyUI/output/face_solution/bench_core8_overlap17_20260926_00001_.mp4`
- 相邻第二段 + 17 帧重叠：`/home/sean/projects/ComfyUI/output/face_solution/bench_chunk2_overlap17_20260926_00001_.mp4`
- 硬切拼接评估视频：`/home/sean/projects/ComfyUI/output/face_solution/bench_stitched_overlap17_20260926.mp4`
- 正确帧位硬切拼接：`/home/sean/projects/ComfyUI/output/face_solution/bench_stitched_correct_overlap17_20260926.mp4`
