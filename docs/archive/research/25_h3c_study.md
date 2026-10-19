# 25 · antirez h3.c 架构研究（h3-metal 学习笔记）

> 研究日期：2026-08-17 · 任务线：comfy-ops-antirez · 源码：https://github.com/antirez/h3.c（2120★，MIT，2026-08-09 创建）
> 项目性质：**纯 C 原生 MiniMax-H3 推理引擎（Apple Silicon / Metal）**，无 Python 依赖，对标 MLX 实现（Iris 风格）。本机是 NVIDIA 环境不可直接运行，本文研究其架构思路与优化方法论。
> 速查：开发顺序 8 个垂直切片 → 每切片一个可验证里程碑；每个优化都留 `--use-slower-*` oracle 开关可 A/B；内存策略核心 = 分阶段驻留 + 激活别名复用 + SSD 流式双缓冲。

## 1. 项目概况

- 33B 参数 H3 模型（FL2VA + Ref2VA 双 checkpoint 树），全程 BF16 存储 / F32 累加，M5 Max 上 int8 默认
- 全 C（~2.7 万行）：`*.c` 纯逻辑 + `h3_gpu.m`（MPSGraph/MTL 封装）+ `h3_shaders.metal`（4332 行内核）+ `h3_metal.m`（设备探测 47 行）
- 单二进制 `h3`：CLI 一次性生成 + Iris 风格交互会话（`!first`/`!ref-image` 等命令）
- 里程碑：8 天（2026-08-09 → 08-11 最后 commit）从 0 到「T2V/T2A/FL2VA/Ref2VA 全通 + M5 全套 int8/TensorOps 优化」

## 2. 架构总览（模块依赖）

```
h3_cli / main ── h3.c（组装+缓存 key）── 各阶段模块
                 ├─ h3_host.c        确定性 host 逻辑（无 GPU）：帧对齐/时间表/token 布局/RNG/Euler
                 ├─ h3_safetensors.c 权重读取
                 ├─ h3_tokenizer.m + h3_text_encoder.c  Qwen3-VL 50 层文本编码（流式 prefetch）
                 ├─ h3_vision_encoder.c  Qwen3-VL 视觉塔
                 ├─ h3_multimodal.c   多模态 deepstack 呈现（<Picture N>/<Video N> 有序参考）
                 ├─ h3_dit.c          DiT 核心（50 块 + 去噪循环，3151 行）
                 ├─ h3_video_vae.c / h3_audio_vae.c  解码器（tile 化视频 VAE、BigVGAN/音频 VAE）
                 ├─ h3_video_encoder.c 条件帧编码（FL2VA）
                 └─ h3_ffmpeg.c       同步音视频封装（RGB24 + 32kHz F32 → H.264/AAC，无中间文件）
h3_gpu.h ── h3_gpu.m（算子库实现）+ h3_shaders.metal（内核）
```

关键设计：**h3_gpu.h 是 100% 可移植的算子接口**（linear/rms_norm/adaln/gate/qkv_rope/sdpa/swiglu/conv3d/euler…），每个算子带 F32/BF16/int8 变体；上层模块完全不知道 Metal 存在，只调算子。Metal 细节（MPSGraph vs 直接内核 vs Metal4 TensorOps）全部封在 h3_gpu.m 内部按机型自动选择。

## 3. 垂直切片开发顺序（git 历史实证，22 个里程碑 commit）

与任务描述完全吻合，每切片**先有可验证出口**：

| # | 切片 | 里程碑 commit | 验证方式 |
|---|---|---|---|
| S1 | 元数据 | host scaffold + model inspection | `--info` 打印模型布局/设备，不 map 权重 |
| S2 | Metal 块对齐 | toy block with MLX parity | **toy 单块 vs MLX fixture 对拍**（相对误差 <5e-3），打通 Metal 编译+对拍通道 |
| S3 | checkpoint 原生布局 | checkpoint-native BF16 Metal path | 权重按 QKV [head,q/k/v,dim] 交错布局直读（早期按常规布局解读是噪声诊断的根因） |
| S4 | prompt 编码 | tokenizer → Qwen block → prompt encoder | 50 层文本编码数值对拍 |
| S5 | T2V | real denoising forward → prompt-to-video baseline | 端到端出片 |
| S6 | T2A | AudioVAE Metal primitives → synchronized audio | 波形 vs MLX 相对 L2 6.94e-5 |
| S7 | 首尾帧 | tiled visual VAE encoder → FL2VA frame conditioning | 条件行 + 0.999 增强 |
| S8 | Ref2VA | ordered image → video → audio references | 有序呈现 + 时间戳 |

**之后是性能层**（每个也是一次可测量提交）：per-phase profiling → 融合 MLP → velocity 复用 → gate-ranked 层裁剪 → core 复用 → int8 MLP/QKV/attention-out 三件套 → token reduction → SSD streaming → 256 原生（RoPE 半格适配）→ Metal 4 TensorOps（Morton 调度）。

**核心方法论**：切片的验收标准不是"代码写完"，而是**该层独立可验证的数值出口**（--info / MLX 对拍 / 端到端片 / L2 度量）。S2 的 toy-block parity 是整条链的地基——先把「Metal 执行 = 参照数值」这条信任通道建起来，后面每块 GPU 代码都有对拍基准。

## 4. DiT 块实现（run_block，50 块流水）

单块数据流（`run_block()` + 融合标注）：

```
hidden ──▶ AdaLN(attn) ──▶ QKV 投影(分组 head-major + QK norm + RoPE) ──▶ SDPA(head-major 输出)
                                                                              │
hidden ──▶ [gate(attn残差) + AdaLN(MLP)] ──▶ MLP(fc1→SwiGLU→fc2, 14336 宽) ──▶ [gate(MLP残差)
               （融合为一个内核）                                       + 下一块 AdaLN(attn) 融合]
```

融合链（README + 代码双重确认）：
1. **块内**：attention 残差 gate 与 MLP AdaLN 合一个内核（threadgroup 存行省一次 global 重读）
2. **跨块**：MLP 残差 gate 顺带产出**下一块的 attention AdaLN**，跨循环携带归一化状态
3. **尾部**：final AdaLN 直接绑定 residual 流偏移（省 2 次 slice blit + 18.8MiB）；final head 加载 16×16 投影 tile 时顺带 AdaLN（合计省 37.5/58.9MiB）
4. **int8 路径**：gate+AdaLN+激活量化三合一内核；QKV 投影 tile 内融合 QK 归一化/RoPE epilogue
5. **布局技巧**：SDPA 保持原生 [head,row,dim] 输出，后续投影直接 head-major 收集量化（省全宽 BF16 转置）

## 5. Metal 内存策略（核心借鉴点）

### 5.1 分阶段驻留（最大头）
33B transformer、Qwen 编码器、两个 VAE **永远不共存**：prompt 编码 → DiT 去噪 → 解码各阶段加载/释放，128GB M5 实测峰值物理 ~40GB、零 swap。

### 5.2 权重驻留分级（三个档位，可切换）
| 模式 | 做法 | 效果 |
|---|---|---|
| 默认 M5 | safetensor shard 直接 mmap 进 Metal buffer（zero-copy） | 37GB 权重 file-backed 可回收 |
| 默认 M3 | 拷贝进匿名共享 buffer | 更快（老硬件） |
| `--ssd-streaming` | 仅 2 块 BF16 双槽 + 后台读线程按 checkpoint 顺序预取下一块，GPU 执行与读取重叠；Darwin uncached read 防文件缓存双份 | DiT 驻留 36.5GiB → **2.0GiB**；512² 前向慢 84%，864×480 仅慢 26%；结果字节级一致 |

### 5.3 激活别名复用（零成本省内存）
QKV 投影 arena → 复用为 attention heads → 再复用为 MLP 归一化输入；attention-output arena 被 MLP 消费后变成 MLP 输出。512² 省 61.25MiB、864 级省 99.63MiB，不改变任何 dispatch/算术。

### 5.4 流式文本编码
Qwen 权重预分配 2-3 层环形 buffer，**8 个 I/O worker 预取未来层**，Metal 执行当前层时并行；`H3_QWEN_PREFETCH=0` 回退单层参照路径。

### 5.5 会话缓存（交互复用）
conditioning（prompt+params → key）、prepared DiT、video decoder 三档缓存：重复 prompt 换 seed 直接命中，跳过重新编码；key 含几何/引用数，变更自动失效。

### 5.6 融合省显存合计
final AdaLN/final head 融合省 37.5-58.9MiB；fused patch cast（F32→BF16 在 tile 内）+ pack 直写 hidden 流省 38+19MiB（512 级）～ 60+30MiB（864 级）。

## 6. 性能优化方法论（最值得抄的工程纪律）

1. **Oracle 开关制度**：每个融合/量化优化都保留慢速参照路径——`--use-slower-*`（CLI）或 `H3_DISABLE_*`（环境变量），README 逐条列出开关名。作用：A/B 验证字节一致性（byte-identical）或量化差异（relative L2），开关本身就是优化文档。
2. **验证协议**：热平衡 ABBA 交叉测量（thermal-balanced，多机复测：M3 Max + M5 Max ×2）；量化路径验证 = 采样首/中/尾帧目视 + SSIM（如 int8 MLP：完整视频 SSIM 0.919/0.828）+ 独立双 prompt（fox + surfer）防过拟合单场景。
3. **数值对拍分级**：块级 MLX fixture（5e-3）→ 端到端不追求逐像素一致（RNG/执行引擎不同），追求内容/运动一致 + 度量（relative L2 1e-5~1e-4 为"极接近"，SSIM 0.9+ 为"同画面"）。
4. **边界条件写进 README**：每个优化注明适用形状/机型、在什么形状回归（如 TensorOps ≤2048 行生效、>2048 走另一内核；M3 只拆 30/50 命令缓冲因为 24/40 回归）。这是"参数经验文档化"的范本。
5. **自动回退**：机型能力运行时探测（`h3_gpu_is_m5`/`has_int8_mlp`），编译不可用/形状不支持自动落回可移植路径——性能优化永不影响正确性主路径。
6. **不变量**：融合优化追求输出字节一致（byte-identical）才有资格成为默认；数值有差的（int8/token-reduction）标 opt-in 并量化差异。

## 7. 对本项目的启示

### 7.1 H3 模型知识（可直接用于 ComfyUI 工作流调参）
- **帧数对齐**：H3 帧数向上对齐 `5 + 17n`（`--frames 23` → 39 帧）；24fps，秒数按 24fps 换算后再对齐
- **画布规则**：宽高须为 32 倍数，像素上限 768×1344（768p 模型）；256² 原生预览需**空间 RoPE 半格适配**（否则晶格伪影），128² 不可用（4×4 token 网格救不回主体）
- **速度/质量正交控制**（每一步独立验证过）：steps 20→4-7、velocity 复用 reuse 2（20 步只算 11 次）、层裁剪 layers 45/40（按 AdaLN gate 排序、保护首尾块）、core-reuse 4/6（patch/head 每步刷新、core 隔 N 步）、token-reduction（块 3 后横向配对视频 token、早阶段块 40 前恢复/后期块 30 前恢复，-28.3% 但改变构图）、内部画布 384→512 输出（DiT 时间 -33%、VAE -18%）
- **危险组合**：`--token-reduction` + `--layers 40` + `--reuse 3` 一起 → 色环/描边/鬼影肢（实验测出并写入 README）
- **时间表结论**（实测淘汰多个候选）：released linear base grid + 末端一点胜出；tail-heavy 调度会织纹/弱运动/色裁——与本项目 09/19 双轨实测的步数结论可互相印证
- **音频编码坑**：官方 PyTorch/SGLang 把**完整立体声通道折叠进 batch 维**（不是左右交错）；MLX 原实现交错是错的（L2 3.59e-6 级差异）——复现/对比音频路径时注意
- **QKV 布局坑**：checkpoint 的 DiT QKV 行按 [head, q/k/v, dim] 交错，误按常规 [q/k/v, head, dim] 解读 → 噪声输出（他们早期的诊断噪音根因）
- **条件增强**：首尾帧用 0.999 增强 + 固定条件行；Ref2VA 图像 down-only 等比缩放（max_short_edge=2048 可选）、视频参考 24fps 有界解码 + `ceil(T/4)` 压缩 + 2 帧采样 + 时间戳呈现

### 7.2 工程方法论（可迁移）
- **给 ComfyUI H3 批处理**：会话缓存 key 化思路 = 本项目 CondCache 节点的方向性印证（10 文档），h3.c 用「prompt+几何 → key → 命中跳过重编码」做对了同样的事
- **Oracle 开关**：我们做量化/节点替换时也应保留慢速参照路径 + 字节级/度量级 A/B——09 文档的对比方法论可吸收"开关即文档"的写法
- **垂直切片 + 数值出口**：如日后做自研推理/服务化，按「元数据 → toy parity → 单模块 → 端到端」切，每层有独立验证出口

### 7.3 局限（为什么本机不直接采用）
- Metal-only（Apple Silicon 硬依赖），NVIDIA 环境无法运行；工程重点是 Metal 特定优化（MPSGraph 调度/TensorOps/int8 内核），跨平台移植价值有限
- 优化量级在 M5 上是 19.32s vs 36.3s（int8 全套）这类硬件特定收益；方法论价值 > 代码价值
- 若未来要在 NVIDIA 上做类似无依赖推理，思路可借鉴：分阶段驻留、激活别名、oracle 开关、层裁剪——但内核全部要重写（CUDA/TensorRT）

## 8. 参考资料

- 源码：https://github.com/antirez/h3.c（README.md 811 行，含全部优化细节与 A/B 数据；本笔记 3/4/5/6 节原始依据）
- commit 历史：https://api.github.com/repos/antirez/h3.c/commits（切片顺序实证）
- 关联：本项目的 H3 实测体系 docs/09、docs/19；MiniMax H3 ComfyUI 栈见 .pi/skills/comfyui
