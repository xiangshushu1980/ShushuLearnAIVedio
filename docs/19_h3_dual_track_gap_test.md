# 19 H3 双轨盲区补测（2026-08-09）

> 任务线：h3-prompt-agent。目的：生产双轨（快车道 i2v+turbo 帧链跨段 / 慢车道 Ref2VA 多图）在**最终定档配置**下的速度/显存/兼容性验证——纯客观参数，无目测。
> 环境：RTX 4090 24GB / ComfyUI 0.30（sage 已启）/ fl2va fp8 + ref2va int8 / qwen3vl-32B TE
> 条件：seed 20260809 统一，prompt = IR 级三段式（experiments/ir_samples/i2v_alya_beach.txt，~1600 tokens），768×448 或 1024×576，24fps
> 数据源：/tmp/h3_gap_cases.json + .results.json；产物 ComfyUI/output/video/h3_gap_test/

## 快车道矩阵（fl2va fp8 + sage，8s=192帧 @768×448 除非注明）

| case | 配置 | 耗时 | 显存峰值 |
|------|------|------|----------|
| A1 | t2v + turbo lora v4-600EMA 8步 | 114s | - |
| A2 | i2v + turbo 8步 | 111s | - |
| A3 | i2v firstlast（双帧）+ turbo 8步 | 123s | 21.5GB |
| A4 | i2v firstlast + std 20步 | 132s | 21.9GB |
| A5 | i2v + turbo 8步 @1024×576 | 171s | - |
| A6 | i2v + turbo 4步 | 90s | - |
| D1 | i2v + turbo 8步 5s(124帧) | 94s | 22.3GB |
| D3 | firstlast + turbo 8步 5s | 94s | 21.8GB |

## 慢车道矩阵（ref2va int8，5s=124帧 @768×448 除非注明）

| case | 配置 | 耗时 | 显存峰值 |
|------|------|------|----------|
| B1 | 1图 std 20步 | 130s | - |
| B2 | 2图 std 20步 | 133s | 21.9GB |
| B3 | 4图 std 20步 | 144s | 22.0GB |
| B4 | 4图 std 14步 | 82s * | 22.0GB |
| B5 | 4图 + turbo lora 8步 | 123s | 21.7GB |
| B6 | 4图 std 20步 @1024×576 | 226s | 21.9GB |
| D2 | 4图 std 20步 8s(192帧) | 187s | 21.9GB |

\* B4 与 B3 同 prompt 同图，命中 TE 缓存（省 TE 加载 ~40s），实际 std14 估 ~120s

## 帧链锚定强度（SSIM，首帧提取 vs 输入图）

| 组合 | SSIM | 判读 |
|------|------|------|
| 静态图 alya_768 → A2 首帧（i2v 单锚） | 0.992 | 首帧锚定极强 |
| 静态图 alya_768 → A3 首帧（firstlast 双锚） | 0.992 | 双锚不削弱首帧 |
| 静态图 alya_169 → A3 末帧（尾帧锚） | 0.893 | 尾帧锚定强（构图不同故非满分） |
| 生成帧（A2 末帧）→ C2 首帧（firstlast 双锚 turbo8） | 0.520 | **弱** |
| 生成帧 → C3 首帧（i2v 单锚 turbo8） | 0.456 | **弱** |
| 生成帧 → C4 首帧（i2v 单锚 std20） | 0.136 | **更弱** |

## 核心结论

1. **i2v 零速度惩罚**：A2(111s) ≈ A1 t2v(114s)。快车道 768×448 = 8s ≈ 1.9min/条、5s ≈ 1.6min/条
2. **firstlast 双帧便宜**：静态双锚 turbo8 仅 +12s（vs 单锚）；旧档 int8 是 +52s，新档开销更小。转场/桥接段可用
3. **长视频 turbo 收益递减**：8s 下 std20(132s) 只比 turbo8(123s) 慢 9-21s（firstlast 双锚对比）；turbo 优势在 5s 内短段。且 IR 级长 prompt 使每步耗时上升（A1 114s vs turbo-pilot 短 prompt 67s，≈1.7x）——速度矩阵标注 prompt 级别才有可比性
4. **ref2va 多图惩罚小**：4图(144s) vs 1图(130s) 仅 +11%；4图@1024 不爆显存（21.9GB）
5. **ref2va + turbo lora 兼容但无价值**：123s > std14（~120s 含 TE）> 4步档无意义；慢车道最优 = std14（折中，画质结论沿用 docs/09 步数矩阵）
6. **帧链硬桥不可靠（关键负面结论）**：生成视频帧做 first_frame，锚定 SSIM 仅 0.14-0.52（vs 静态图 0.99）；std20 比 turbo8 更差（0.136），非步数因素，疑似"生成帧分布 OOD"（H3 训练首帧为真实图/渲染图）。**快车道跨段不能靠 段2 first=段1末帧**
7. 显存峰值最高 22.3GB（D1），全批 24GB 内安全；4图+1024 也仅 21.9GB——之前对多图/高分辨率爆显存的担忧解除

## 生产建议（双轨落地）

- **快车道**：每段独立 i2v + turbo8（首帧=角色静态图），跨段一致性靠角色卡 prompt + 静态锚；连续场景用 firstlast 静态双锚转场段（+12s）；**放弃帧链硬桥**
- **慢车道**：ref2va 4图 std20（144s/5s）或 std14（~120s 估）；成片档 1024×576 = 226s 可行；不用 turbo lora
- 帧链若后续仍要：可尝试 段1末帧后处理（锐化/增噪）或 last-frame 反向桥接，需另测

## 备注

- runner：scripts/h3_gap_runner.py（支持 t2v/i2v/firstlast/ref2va、lora、帧链依赖 chain_from、显存监控 >23.6GB 告警、OOM abort、断点续跑）
- analyze：scripts/h3_gap_analyze.py（ffprobe/volumedetect/SSIM）
- 音频响度全批 -14.6~-26.6dB mean，无静音/爆音异常（IR 级 prompt 稳定音频，与 onsen DS 近静音形成对照）
- 本批 prompt 为 IR 级长文本；turbo-pilot 的 67s/45s 是短 prompt 数据，直接对比需折算

## 首帧底图规范（2026-08-09 实测补充）

**问题**：`MiniMaxH3ImageToVideo` 的 first_frame 注入是**纯拉伸**（"disabled"，源码 nodes_minimax_h3.py）；方形底图（768×768）拉伸到 16:9 画布后**变形传导到产物**——产物首帧对拉伸输入 SSIM 0.992（忠实复刻），但对无变形参考仅 0.474。用户目测"图被压缩"坐实。

**验证**（同 seed 同 prompt，仅换首帧）：
| 首帧底图 | 产物首帧 vs 无变形参考 SSIM | 结论 |
|---|---|---|
| alya_768（方形，被拉伸） | 0.474 | 变形传导，不可用 |
| alya_169（16:9 原生） | 0.993 | 无变形，生产标准 |

**规则**：
- 快车道 i2v 首帧 = **必须 16:9 底图**（与画布同比例，任意分辨率）
- 尾帧（firstlast last_frame）是 center-crop（保比例）→ 任意比例可用，构图会被裁
- ref2va 参考图是 match 缩放（保比例）→ 任意比例安全
- 适配库：`ComfyUI/input/start/169/`（35 张 center-crop 16:9，构图略偏上保脸；裁剪丢构图，角色图优选原生 16:9 重生成）
- 原生 16:9 角色图现仅 alya_169.png（1280×720）；Alya LoRA 文件已被清理（anima 工作流暂不可用），需重生成 16:9 角色图时：重新下载 LoRA 或 img2img 扩图（denoise 0.5-0.7）
