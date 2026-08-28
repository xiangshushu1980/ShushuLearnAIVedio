# 10 H3 fl2va 机制与批量优化（2026-08-04/05 讨论定稿）

> ⚠️ **2026-08-16 修正（cond-cache-node 线 T2 受控复测）**：本文「TE 加载 ~80s / DiT 冷 171s」为 **swap/内存压力污染数据**，健康态实测 TE 冷 ~11s（load_clip 惰性 4.5s + 首次前向 nvfp4 反量化 6.7s）/热 ~4s、DiT int8 冷 ~15s/热 ~3.4s（posix_fadvise 真冷控）。两阶段真实收益 = 省 **(N-1)×~22s**（冷加载），非 80s。已落地：custom_nodes/ComfyUI-MiniMax-H3-CondCache + scripts/h3_two_stage_batch.py（N=3 实测省 ~37s）。下文「80s」数字保留原讨论语境，修正值以本条为准；详见 .pi/tasks/cond-cache-node/progress.md。

> 本轮讨论背景：用户目标是「快速得到受提示词控制的视频」，固定分辨率迭代。
> 讨论焦点：fl2va 的 TE 阶段为何 CPU 慢、能否 API 化、批量时缓存机制、批量优化策略。
> 结论已同步：mem0 [STATE]（共享状态）+ 经验。

## 一、结论速览

1. **TE（Qwen3VL-32B）是完整 LLM 前向编码**，不是传统提示词编码；**API 化不可行**，方向是缓存复用
2. **TE 权重加载是固定开销**：实测冷 ~11s/热 ~4s（2026-08-16 修正，原「~80s」为 swap 污染），编码本身仅几秒
3. **同 prompt 多 seed 批量已自动最优**（ComfyUI 节点缓存命中，TE 只加载一次）
4. **不同 prompt 批量每任务重付一次模型加载**（TE+DiT 冷 ~26s/热 ~7s；TE 与 DiT 无法同驻 24GB）→ **两阶段流水线**解法

## 二、fl2va 节点机制（源码依据 comfy_extras/nodes_minimax_h3.py + comfy/text_encoders/minimax.py）

fl2va（MiniMaxH3ImageToVideo）执行 = 三件事：

```
1. _empty_av_latent()     创建全零 video+audio latent（零成本，fl2va 不是"编码视频"，
                          首帧只是 keyframe 条件，不参与去噪、每步注入）
2. clip.tokenize + encode  TE 编码：prompt 文本 + 首帧图像 → 同一 token 序列
                          （图像作为 <Picture 1> vision token，见 tokenize_with_weights）
                          → Qwen3VL-32B 完整前向
                          → 输出【每 token hidden states（5120 维）+ 每 token 模态标签】
                          → 作为 DiT 条件（每步注入）
3. vae.encode(首帧/尾帧)   VideoVAE（5GB fp16）单帧编码（快）
```

关键认知：
- TE 不是 CLIP/umt5 那种"句子→向量"，是**序列级上下文表示**（每个 token 一个向量），本质就是一次 LLM 前向（不采样、只编码）
- 首帧图像也进 Qwen 前向（视觉 token），cond 里含图像语义

## 三、开销分析（日志证据）

- TE 权重加载（15.7GB nvfp4，MixedPrecisionOps emulated op → CPU 反量化）≈ **11s/次冷**（load_clip 惰性 4.5s + 首次前向 6.7s）／热 ~4s（2026-08-16 修正）
  - 旧证据「同条件 214s vs 130s 差 84s = TE 加载」系 swap 压力下测量，已作废；健康态下该差值 ~7-11s
- TE 编码本身：几秒（cond 输出仅 ~30-40MB）
- **TE(14.9GB) + DiT(17.1GB) = 32GB > 24GB 无法同驻** → 采样时 TE 被挤出，下个不同 prompt 任务重新加载

## 四、TE 能否 API 化：不可行（三个硬障碍）

| 方案 | 障碍 |
|------|------|
| 通用 LLM API（OpenAI 等） | 只返回生成文本，不暴露 per-token hidden states |
| Embeddings API | 单向量、不支持图像 token；必须与 MiniMax 训练时特定 Qwen3VL 版本对齐，几乎不可能 |
| 自托管（vLLM/SGLang） | 32B 也要 ~20GB 显存，没省资源，还多一跳传输 |

- API 化想省的是"加载"，但加载靠 API 省不了（cond 还得传回 + 对齐）
- 唯一合理的"API"路线：海螺官方 API 整条管线外包（真出片 API），或 API 做 prompt 工程（docs/08 提示词智能体）——与本问题不同

## 五、ComfyUI 0.30 缓存机制（源码依据 comfy_execution/caching.py + execution.py）

- 默认缓存 = `--cache-ram` → **RAMPressureCache**：进程内存 dict，key=节点输入签名（class_type+全部输入+is_changed），value=节点输出
- 驱逐：可用内存低于 headroom（默认 10% RAM）时按 `1.3^代差 × RAM 占用` 评分逐；ModelPatcher 权重最优先逐
- **无磁盘持久化**（cache_provider 机制存在但无 provider 注册），**重启清空**
- cond 体积小（hidden states ~30MB + keyframe latent ~0.5MB）→ 内存不是瓶颈，跨任务/跨重启复用才是价值

## 六、批量策略

| 场景 | 现状 | 策略 |
|------|------|------|
| 同 prompt 多 seed 抽卡 | 自动最优（fl2va 签名命中 → 无 TE 加载）| 直接队列跑，无需改动 |
| 不同 prompt 批量（提示词探索/筛选）| 每任务 +~22s（冷）/+~7s（热）模型加载 | **两阶段流水线** |
| 混合（先筛 prompt 再抽卡）| — | 筛选用两阶段，选中后同 prompt 免费 |

### 两阶段流水线（已实现，2026-08-16）

```
阶段一：TE 加载一次（~11s）→ 连续编码 N 个不同 prompt → 每个 cond 落盘（~30-40MB/个 .pt）
阶段二：逐个加载 DiT 采样（从磁盘读 cond，全程不需要 TE）
```

- 收益：N 个任务只付 1 次模型加载，省 (N-1)×~22s（冷）；N≥3 就划算（实测 N=3 省 ~37s）
- **已落地**：custom_nodes/ComfyUI-MiniMax-H3-CondCache（Save/LoadMiniMaxH3Cond 节点，cond 为标准 [(tensor,{attrs})] list）+ scripts/h3_two_stage_batch.py（API 编排，N=3 实测 158s vs 195s）；守护进程形态判定过度设计不实施
- 前置验证：cond 序列化往返逐位无损（torch.save/load，含 fl2va keyframes latent）已通过（.pi/tasks/cond-roundtrip/）

## 七、跳步加速家族现状（2026-08-28 汇总）

| 家族 | 原理 | 20 步 std 档 | 8/14 步低步数档 | 选型结论 |
|------|------|-------------|----------------|----------|
| MotionCache | residual reuse | 1.25-1.33x（08-04） | 无价值（14 步 1.08x） | 仅 20 步档备选 |
| EasyCache | residual reuse | 未测 | 1.25-1.38x 但高动态崩 | 不推荐抽卡档 |
| Cache-DiT | 官方库，1.41-1.50x | 待测（T-20260815-10） | 待测 | 待实测 |
| **Spectrum v0.2.20** | **跳 transformer blocks + anchor 预测** | **采样 1.55x/端到端 1.22x，画质反升（定论见 09 批 E）** | 8 步采样 1.5-1.63x 但高动态崩/端到端无感；4 步零收益 | **std 20 步档首选；低步数档不用** |

- 共同规律：跳步/复用家族只在慢速高步数档有价值；低步数档 warmup+尾保护占比大且 forecast 误差被大 sigma 间隔放大
- Spectrum 与批量优化（两阶段/CondCache）收益独立，可叠加

## 八、参考

- 源码：`ComfyUI/comfy_extras/nodes_minimax_h3.py`（H3 节点）、`ComfyUI/comfy/text_encoders/minimax.py`（TE）、`ComfyUI/comfy_execution/caching.py`（RAMPressureCache）、`execution.py`（缓存初始化）、`comfy/cli_args.py`（--cache-ram 默认）
- 速度矩阵/测试数据：docs/09_h3_test_plan.md
- 提示词智能体方案：docs/08_h3_prompt_agent.md
