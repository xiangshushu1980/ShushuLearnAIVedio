# T-comfy-ops-41：TaoMate 与 HyperFlow 的 MiniMax H3 对照评估

## 目标

在当前 H3 基线下判断 TaoMate 与 HyperFlow 的优势、适用边界、能否在本机 4090/24GB 使用，以及二者是否可以与 PDD/Sage/H3Memory 组合。

## 2026-09-19：开题与一手资料结论

- TaoMate-H3 是阿里 TaoLive AIGC 团队发布的 MiniMax-H3 流式音视频运行时，不是普通 ComfyUI 优化节点。
- TaoMate 当前公开版本是 T2AV 3-step LoRA；FL2AV/Ref2AV 版本在仓库中标为后续发布，当前不能假定支持本项目的 FL2VA/Ref2VA 外部音频链路。
- TaoMate 的主要优势是流式小块低延迟、联合音视频生成、clean KV cache/持久 anchor 的长程连续性、4/8 GPU 的 TP2 + Ulysses 并行；官方验证环境是 Hopper/SM90，README 性能数据为 8×H20 96GB。
- TaoMate README 报告：480×864、10 秒、8×H20 上，Pure DiT 14.810s vs MiniMax H3 169.572s；首个可播放视频 17.287s vs 183.313s。该数据不可直接外推到单张 RTX 4090。
- HyperFlow 是 Video Rebirth 的 H3 专用 8-step LoRA，使用固定 sigma grid，覆盖 t2va/fl2va/ref2va；应使用专用 loader，不能按普通 LoRA 加载。
- HyperFlow 与 PDD 属于同一层级的采样轨迹/步数加速，不应直接叠加；应做 PDD vs HyperFlow 的单变量 A/B。
- 由于本机项目纪律，实际 ComfyUI/GPU 跑批前须先获得宿主权限并检查共享实例队列；TaoMate 官方路径还存在 4/8 GPU 与 Hopper 硬件阻断。

## 2026-09-19：B站/社区本地路线核对

- B站检索命中大量 MiniMax H3 本地 ComfyUI 教程，但没有找到足以证明“官方 TaoMate runtime 在单张 4090 上运行”的一手视频；相关视频多是普通 H3、其他 4/5/8-step LoRA 或 SelfLift 组合。
- 社区已将官方 TaoMate 3-step adapter 转为 ComfyUI safetensors：`CZMartin22/TaoMate-H3-3step-ComfyUI`，权重约 1.24GB；另有 Robert1212star 等镜像。该路线是“只用 LoRA”，不是阿里官方 TaoMate streaming runtime。
- 社区经验报告称该转换 LoRA 可在 4090/16GB 等消费卡上运行，但目前不是本项目同条件实测，不能直接采信速度或画质结论。
- 因此 4090 可测试的是 `TaoMate 3-step ComfyUI LoRA`，不可复现的是官方 4/8-GPU Hopper streaming runtime。41号任务改为三方替换式 A/B：PDD 8-step vs TaoMate-3step vs HyperFlow-8step，统一 Sage/分辨率/seed/prompt/音频。

## 待测矩阵

1. 当前基线：PDD 8-step + SageAttention（必要时记录 H3MemoryOptimization）。
2. HyperFlow 8-step + SageAttention；分别测试 FL2VA 和若可用的 Ref2VA。
3. 若 TaoMate 发布 FL2AV/Ref2AV 且具备硬件条件，再测 TaoMate；当前 T2AV 仅做可运行性/架构审查，不冒充同口径 H3 测试。
4. 指标：端到端时间、首块可用延迟、采样/解码时间、VRAM/RAM、音画同步、身份保持、跨段连续性、长时稳定性。

## 来源

- TaoMate 官方仓库：https://github.com/TaoLiveAIGC/TaoMate-H3
- TaoMate 论文：https://arxiv.org/abs/2607.24359
- HyperFlow 官方代码：https://github.com/Video-Rebirth/hyperflow
- HyperFlow 权重卡：https://huggingface.co/videorebirth/hyperflow
- 社区 TaoMate ComfyUI 转换权重：https://huggingface.co/CZMartin22/TaoMate-H3-3step-ComfyUI

## 2026-09-19：启动状态核查

- `hive-task start T-comfy-ops-41 --executor codex` 的认领步骤写入 registry/outbox，但 Codex API `127.0.0.1:3180` 不可达，启动未成功；TODO 状态已回滚为 `open`，租约已释放。
- 发现旧的 `[STATE] comfy-ops_taomate` 未随启动失败清理，已删除该孤儿运行态；当前任务未处于进行中状态。

## 2026-09-19：第二轮一手资料核查与执行边界修正

- TaoMate 官方仓库当前仍将产品定义为 H3 上的低延迟流式音视频 runtime：T2AV 3-step LoRA；FL2AV 计划在 2026-10-15 前发布、Ref2AV 未给出发布时间。官方安装要求 Linux/Python 3.10/3.11、CUDA 12.8、PyTorch 2.8、Hopper/SM90，验证配置为 8×H20 96GB；不能把官方 runtime 当成单张 RTX 4090 的可运行对象。
- TaoMate 官方性能表的口径是 8×H20、480×864、10 秒、seed 8301：Pure DiT 14.810s，首个可播放视频 17.287s；该表明确排除模型加载、文本编码、VAE 解码及媒体编码，不能与本机 ComfyUI 端到端时间直接比较。
- TaoMate 社区 ComfyUI 转换权重确认是官方 T2AV adapter 的 FL2VA ComfyUI 转换版：BF16、约 1.24GB、208 patches；推荐 3 steps / CFG 1.0 / LoRA 1.0 / Euler / simple 或 linear FlowMatch。它是可在本机验证的替代路线，不等于官方 TaoMate streaming runtime。
- HyperFlow 官方仓库确认：这是 diffusers Modular Pipeline 的专用 8-step LoRA，覆盖 t2va/fl2va/ref2va，并把固定 video/audio sigma grid、TwoTimeEmbedder 和专用 loader 一起作为算法契约；禁止按普通 `load_lora_adapter` 或手工指定 `num_inference_steps` 加载。
- HyperFlow 官方单卡示例使用自动 CPU offload，但“24GB reserve margin”只在 H200 运行条件下验证；官方性能表是 H200（1 卡约 130s，4 卡约 60s，1344×768/124 帧），4090/24GB 目前没有一手可采信的运行数据。
- 本仓库当前没有 HyperFlow/TaoMate 专用 runner、loader 或工作流引用；因此不能把 HyperFlow 直接塞进现有 `h3_ref2v_runner.py` 当成 ComfyUI LoRA，也不能宣称三方已经具备同一执行后端。

### 本地 4090 相关社区证据

- Reddit 的 TaoMate ComfyUI 帖子在短时间内出现两极反馈：有人报告 3-step 有慢动作/质量下降，有人认为静态或动画场景的视觉质量很高；也有人反馈动态场景构图、运动、prompt adherence 和音频明显变差。该帖没有统一 GPU、seed、时长或 PDD 对照，不能作为速度定论，但足以证明风险不是偶发单条评论。
- Reddit 的 TaoMate “refiner”复盘帖给出更稳定的社区共识：单独 3-step 在非静态场景容易 slow-motion、jerk、smearing、破音；把它作为高质量前段后的最后 3-step refiner 更容易得到可接受结果。这种两阶段方案总步数可能反而高于 PDD，不能算 TaoMate 替代 PDD。
- Japanese AI-Driven Lab 对官方代码和 ComfyUI 迁移的拆解指出：官方 runtime 的流式/长程 KV continuity 不会随 ComfyUI 权重转换保留；转换版应当只按“3-step 高速 LoRA”评估，不能套用官方首块延迟和 27.66× 口径。
- `matsuo-koya/minimax-h3-notes` 是目前最有价值的消费卡实测之一：虽然主卡是 RTX 5090，不是 4090，但同一工作流实测 TaoMate standalone 在 832×480 文本/图像路径相对 4-step LoRA 约 1.4–2×，相对 Turbo 8-step 生产长度约 2.2×；同时明确记录 reference+audio 小测曾不可用、生产条件下结果方向改变为“身份更强但 prompt/场景遵循更差”。该作者还给出 4090 worker 的 attention/生产长度数据，但不是 TaoMate-vs-PDD 的直接 A/B。
- `Asirus/TaoMate_H3_3_Step_LoRA` 提供 6GB/16GB 的社区 benchmark，报告 TaoMate 约比 Turbo 4-step 快 21–27%；由于没有 PDD 臂、没有 4090、没有统一 Sage 和画质量化，只能作为“能在消费卡跑、可能有速度收益”的弱证据。
- HyperFlow 官方与 ComfyUI Wiki/社区资料显示：官方实现以 8-step 固定 sigma + TwoTimeEmbedder 为核心；现有 ComfyUI 方案分为带 `ComfyUI-HyperFlow` 专用节点的完整转换，以及普通 LoRA loader 的简化转换。后者明确缺少 endpoint conditioning，输出偏离发布版，不能直接拿来代表 HyperFlow。
- HyperFlow 社区早期评价偏正面（质量、稳定性、镜头控制、材质细节优于旧 Turbo），但没有找到 RTX 4090 实测，更没有 PDD 同条件对照。官方 H200 数据和社区赞誉都不足以证明单卡 4090 对 PDD 有明显优势。

### 针对 RTX 4090 的阶段结论

- **TaoMate：值得做一次最小 FL2VA smoke test，但不值得立刻投入完整矩阵。** 主要验证它是否在本机 PDD 基线的相同 5 秒/分辨率条件下实际更快，以及动态运动、音频、prompt adherence 是否可接受。当前证据不支持“默认替换 PDD”；更不支持在 Ref2VA/NativeAudioLock 生产链直接采用。
- **HyperFlow：若目标是速度，不优先测试；若目标是质量/镜头控制，值得做一次专用节点 smoke test。** 其 8-step 结构与 PDD 同属少步采样替换，预期速度优势不明显；唯一可能的价值是比 PDD 或旧 Turbo 更好的运动/材质/镜头控制，但 4090 证据缺口很大。
- **与当前 PDD 的比较**：本项目已有 PDD + SageAttention 的 1024×576/15s 约 235s、20s 约 335–342s 的本机基线。当前社区没有 TaoMate 或 HyperFlow 在 RTX 4090、同分辨率/帧数/seed/Sage/音频条件下超过该基线的证据；因此现阶段不能宣称二者有明显优势。
- **测试优先级**：TaoMate 3-step FL2VA（一次 smoke） > HyperFlow 专用节点 FL2VA（一次 smoke） > 任何 Ref2VA 扩展。若 TaoMate smoke 出现明显慢动作/音频损坏/提示词退化，则直接停止扩大；若 HyperFlow smoke 只与 PDD 持平或更慢且没有明显质量收益，也停止。

## 2026-09-19：切换 HyperFlow Ref2VA 执行线

- 用户确认当前主线必须是 Ref2VA；TaoMate 因没有公开 Ref2AV，退出主测试矩阵。
- `Addis-Pulse-Studio/ComfyUI-HyperFlow` 节点已安装到宿主 ComfyUI 的 `custom_nodes/ComfyUI-HyperFlow`，未启动第二实例。
- 节点官方 live verification（RTX 5090/ComfyUI 0.36）已验证 `ref2va_int8_convrot` + HyperFlow 1.0：参考图 + 参考音频 → 视频+音频成功，5.167s/124 帧，Ref2VA 音频包络相关系数 0.980、0ms lag、无漂移；首次载入含约 5 分钟 patch/dequant/requant 成本。该数据不是 4090 结果，但提供了本机 smoke 的正确架构和验收指标。
- 节点示例固定契约：非 pruned `ref2va_int8_convrot`；HyperFlow strength 1.0；HyperFlow Sigmas 固定 8-step；Euler；BasicGuider CFG 1.0；不得叠加 PDD/Turbo/TaoMate；Ref2VA 使用 `MiniMaxH3ReferenceToVideo`，参考图和参考音频均保留。
- 宿主已开始下载官方 `minimax_h3_hyperflow_8step_v1.0.safetensors`；当前临时文件约 1.2GB，尚未完成。现有本机 `minimax_h3_ref2va_pruned_int8_convrot.safetensors` 不满足完整节点路线，仍需非 pruned Ref2VA 基座。
- HyperFlow 权重已完成下载：`/home/sean/projects/ComfyUI/models/loras/minimaxh3/minimax_h3_hyperflow_8step_v1.0.safetensors`，大小 2,795,328,008 bytes，SHA256 `9297f4505bfdef59c3014d11274411809c19b0abfe26161cab2b425a696df447`；从观测到的 1.2GB 临时文件增长到完成，下载速度约 4–5 MB/s。非 pruned Ref2VA 基座仍未落盘。

## 2026-09-20：社区 pruned 版本与 4090 生产可行性核查

- 找到社区节点 `Saganaki22/ComfyUI-Hyperflow`：可根据 base 自动匹配 full/pruned 权重，提供约 3.64GiB 的 `custom_node_hyperflow_8step_v1.0_comfyui_pruned.safetensors`，理论上可接现有 21GB pruned Ref2VA 基座，避免下载 34GB 非 pruned 基座。
- 但该节点作者明确标注：pruned build 是 **backbone LoRA only / single-time / off-recipe**；由于 pruned 曲线模型没有 `time_embedder`，无法安装 HyperFlow 的第二个 endpoint time embedder。官方完整 HyperFlow 的 `(t,r)` conditioning 只存在 full build。普通 stock LoRA 转换版同样明确缺少 `(t,r)` conditioning，输出偏离发布模型。
- 因此 pruned 版本最多可做“4090 能否出片”的实验性 smoke，不能作为完整 HyperFlow Ref2VA 质量、速度或生产结论；尤其不能把它与 PDD 的正式 Ref2VA 结果直接比较。
- 当前可接受的生产判定：**否（现有 4090/pruned 基座条件下）**。完整 HyperFlow 需要约 34GB 非 pruned Ref2VA 基座，虽可能通过 CPU offload 勉强运行，但没有 4090 Ref2VA 验证且预计速度不适合生产；pruned 社区版缺少算法核心，不能作为生产替代。
- 若用户仍希望验证社区路线，只做一条明确标记为 `experimental_pruned_backbone_only` 的 5s/低分辨率 Ref2VA smoke，验收目标仅为加载、参考图/音频输入链路和是否出有效视频，不记录为 HyperFlow 正式基线。

### 执行规格（已修正）

1. **ComfyUI 路线**：PDD 8-step vs TaoMate-3step ComfyUI LoRA；统一 FL2VA 底模、首帧、prompt、seed、分辨率、帧数、SageAttention 开关。TaoMate 臂必须锁定 CFG 1.0 / Euler / 3 steps，不叠加 PDD。
2. **独立 diffusers 路线**：HyperFlow 官方 `hyperflow-h3-fl2va`，先跑 1 GPU CPU-offload 的最小 5 秒/低分辨率可行性，再与其 `--baseline` 做同后端 A/B；不把其 H200 数据并入本机速度矩阵。
3. **Ref2VA**：HyperFlow 可按官方 loader 进入 ref2va；TaoMate 当前没有公开 Ref2AV，因此不做伪同口径对照。先完成 FL2VA，再决定是否补 HyperFlow Ref2VA。
4. **组合禁忌**：PDD 与 HyperFlow/TaoMate 都是采样轨迹/步数加速替换项，不叠加；SageAttention 仅在 ComfyUI 路线作为统一 backend 变量。HyperFlow 的 Sol-Attn 另列为独立可选变量，不与本轮 Sage 结果混合。
5. **首个可执行阻塞**：需要宿主权限核查 ComfyUI 共享实例队列、4090 状态及现有 TaoMate 权重；HyperFlow 需要独立 Python/diffusers 环境或用户批准安装依赖。未获权限前只完成静态规格和文件准备，不启动服务、不跑 GPU。

## 证据来源（2026-09-19 核查）

- TaoMate 官方 README：https://github.com/TaoLiveAIGC/TaoMate-H3
- HyperFlow 官方 README：https://github.com/Video-Rebirth/hyperflow
- TaoMate ComfyUI 转换权重卡：https://huggingface.co/CZMartin22/TaoMate-H3-3step-ComfyUI
