# ComfyUI 节点来源与更新记录（Owner: Sean）

## ComfyUI 核心

- ComfyUI：`v0.35.0-16-g7193f562`
- 前端包：`1.52.7`
- 工作流模板：`0.11.59`
- 工作流模板配套包：`core 0.3.339`、`json 0.1.74`、`media-assets-01 0.1.44`；`pip check` 通过。
- Transformers：`5.14.1`
- H3 相关核心更新已包含：PDD LoRA、H3 Fun ControlNet model patch、H3 Max、Reference 节点增强、H3 denoise mask 修复。

## 已有 Git 节点

2026-09-12 已将此前的非 Git 目录建立本地 Git 基线；有上游的目录同时配置了 `origin` 并抓取上游。

| 目录 | 来源/性质 | 本次状态 | 当前定位 |
|---|---|---|---|
| `ComfyUI-H3-NativeAudioLock` | `Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow` 子目录 | 已同步上游；提交 `18424e6` | 当前数字人基础链，保持启用 |
| `ComfyUI-H3-FaceRefine` | `Carasibana/ComfyUI-H3-FaceRefine` | 已同步 `v1.1.1`；提交 `e891d2a` | 后期小脸精修；历史效果差，暂不进基础链 |
| `ComfyUI-H3-ContactSheet` | 旧仓库已迁移至 `matlowai/ComfyUI-MAINodes` | 建立本地基线并绑定迁移后的上游；未覆盖旧目录 | 五视图/转身 LoRA 辅助，暂不替换 |
| `ComfyUI-MiniMax-H3-CondCache` | 本项目自有节点 | 建立本地基线；提交 `a947666` | 批量条件缓存，可选 |
| `ComfyUI-MiniMaxH3_Ref-Patch` | `lihaoyun6/ComfyUI-MiniMaxH3_Ref-Patch` | 与上游一致；建立基线 `ed2d172` | 参考图兼容补丁，按工作流需要 |
| `ComfyUI-SolAttn_triton` | `kijai/ComfyUI-SolAttn_triton` | 已移至 `/home/sean/projects/ComfyUI/archive/custom_nodes/ComfyUI-SolAttn_triton`；保留 Git 基线 `c8d99b9` | 已弃用，不加载、不进正式链 |
| `comfyui-material-gallery` | 本项目自有修改 | 建立本地基线；提交 `213a8d5` | 本地素材库入口 |

## SolAttn 回归

- 工作流：`workflows/attn3way_dance_sol.json`
- 配置：H3 FL2VA int8、Turbo v4、1024×576、124 帧、8 步、无 SageAttention
- 结果：成功，H.264/AAC，124 帧，24fps，5.167 秒；输出 `dance_sol_00001_.mp4`
- 静态检查：`compileall` 通过，SolAttn 节点导入通过
- 原生替代回归：ComfyUI 核心 `BlockSparseAttention`（显示名 `Model Sparse Attention`）使用 `sol-attn` 模式，参数通过当前动态组合输入格式传递；同一工作流成功，输出 `dance_sol_00002_.mp4`。
- 依赖确认：`comfy-kitchen==0.2.33`，与核心 `requirements.txt` 一致；核心源码位于 `comfy_extras/nodes_sparse_attention.py`。
- 结论：Sparse Attention 已进入 ComfyUI 核心，并由 comfy-kitchen 提供 kernel；旧 SolAttn 不是方向被放弃，而是独立 custom node 被替代。旧节点目录和两个活动测试工作流已移入 archive，不再加载；正式工作流只使用原生 `Model Sparse Attention`。

## 加载检查

- 归档前 ComfyUI 日志显示 NativeAudioLock、FaceRefine、ContactSheet、CondCache、Ref-Patch、SolAttn、Spectrum 均成功加载；这用于确认旧节点此前可复现。
- 归档重启后 `SolAttnPatch` 已不再加载，核心 `BlockSparseAttention` 正常注册。
- RMBG 的 SAM 可选模块仍缺 `segment_anything`、`iopath`；不影响 H3 基础链。
- 启动时存在 `user/comfyui.db` 锁竞争；不影响当前 HTTP 生成，但后续应避免多实例同时使用同一数据库。

## 后续纪律

- 更新前先保留本地提交；更新后用 `git log` / `git diff` 对照。
- NativeAudioLock 跟随上游更新后必须跑基础数字人回归。
- FaceRefine 只在基础成片稳定后做独立后期 POC。
- SolAttn 仅保留为历史复现，不作为新生产路线。
- 旧节点归档：`/home/sean/projects/ComfyUI/archive/custom_nodes/ComfyUI-SolAttn_triton`
- 旧工作流归档：`workflows/archive/solattn-legacy/attn3way_dance_sol.json`、`workflows/archive/solattn-legacy/attn3way_wave_sol.json`

## 2026-10-15 ComfyUI 核心更新

- 更新前：官方 `v0.39.2`，commit `3c1b7a17fdf239d35ce98cc777756f572d089795`；Torch `2.13.0+cu130`；前端 `1.53.10`；工作流模板 `0.11.78`；嵌入文档 `0.5.13`；`comfy-kitchen 0.2.37`；`comfy-aimdo 0.5.5`。
- 更新后：官方 `v0.40.0`，commit `3541246a9c997f4b8c32f9f88f3c985d02021c79`；前端 `1.55.17`；工作流模板 `0.11.82`（core `0.3.373`、json `0.1.108`、assets-01 `0.1.48`、assets-02 `0.1.14`）；嵌入文档 `0.5.14`；`comfy-kitchen 0.2.37`；`comfy-aimdo 0.5.6`。Torch/CUDA 未变，仍为 `2.13.0+cu130` / CUDA `13.0`。
- 操作：更新前队列为空、无活跃 GPU lease；停 `comfyui.service` 后切换正式 tag，再按 release requirements 更新固定版本依赖；未清理升级前工作树已有删除项和未跟踪文件。
- 检查：`pip check` 通过；`comfy-stack.sh start/status` 成功；`/system_stats` healthy；`/queue` 空；`/object_info` 注册 59 个 `MiniMaxH3*` 节点。GPU 仅识别 RTX 4090，服务空闲显存占用约 384 MiB。
- H3 相关：release 含单张 H3 image 作为视频首个 latent 解码的支持；没有运行代表性 Ref2VA 生成，因此画质、音频和生产速度回归尚未验证。
- 回滚点：代码 `3c1b7a17fdf239d35ce98cc777756f572d089795`；依赖恢复为前述旧版四个包。工作树其他既有变更保持原状。

## 2026-10-13 ComfyUI 核心更新

- 更新前：`v0.37.0`，commit `73c9bad4d21e7addbe1d13bc92eee0f1431b017d`；Torch `2.13.0+cu130`；前端 `1.52.7`；工作流模板 `0.11.66`；嵌入文档 `0.5.12`；`comfy-kitchen 0.2.35`。
- 更新后：官方 `v0.39.2`，commit `3c1b7a17fdf239d35ce98cc777756f572d089795`；前端 `1.53.10`；工作流模板 `0.11.78`（core `0.3.369`、json `0.1.104`、assets-01 `0.1.48`、assets-02 `0.1.11`）；嵌入文档 `0.5.13`；`comfy-kitchen 0.2.37`。Torch/CUDA 未变，仍为 `2.13.0+cu130` / CUDA `13.0`。
- H3 相关核心变更包含 MiniMax-H3 采样前释放 embedding 临时张量以降低峰值显存、修复 H3 VAE offload，以及 H3 VAE tile 与邻接块融合；需通过服务启动和代表性 H3 工作流回归确认本机效果。
- 安装检查：`pip check` 通过。ComfyUI 服务更新前为停止状态；本轮临时启动后 `/system_stats` 健康检查通过，随后已恢复停止。未运行代表性 H3 工作流，因此生成回归和画质/音频影响尚未验证。
- GPU 可见性：本轮 WSL `nvidia-smi` 与 ComfyUI venv 的 PyTorch 均只枚举到 RTX 4090（24 GiB）。第二张显卡当前没有暴露给此运行环境。
- 工作树保留升级前已有的删除 `input/example.png`、`output/_output_images_will_be_put_here` 及未跟踪目录/文件，没有清理或覆盖这些内容。

## 2026-10-15 H3 custom node 更新（Owner: Sean）

- ComfyUI 核心维持 `v0.40.0`（commit `3541246a`）；更新前 `/queue` 为空、无活跃 GPU lease。通过 `scripts/comfy-stack.sh stop/start` 停止并恢复唯一共享实例。
- `ComfyUI-H3-Continuum-Plus`：`e870875`（v3.4.4）→ `e5d9037`（v3.4.8）。包含 V3.4 audible-tail/continuity 修复；新建 V3.4 assembler 默认 Video Seam 改为 Auto 3。升级后 `H3Continuum*` 节点已注册。
- `ComfyUI-Spectrum-MiniMax-H3`：`5161f04`（v0.2.28）→ `806fe49`（v0.2.29）。恢复对 Core BSA/Flow/Untwist 当前运行结构的 forecast 兼容；升级后 `SpectrumApplyMiniMaxH3` 已注册。
- `ComfyUI-MiniMaxH3-TimelineDirector`：`a81f13b` → `8fe06e3`（上游 main）。新增低内存分段视频输出节点；`MiniMaxH3FiniteSegmentVideoSampler`、`MiniMaxH3SegmentVideoOutput` 已在 `/object_info` 注册。
- `Comfyui_Minimax_h3_latent_Upscaler`：`620165a`（v0.2.1）→ `1ddcc33`（含 v0.2.2）。增加 H3 feature transfer lattice 与 Flow handoff provider；`MinimaxH3LatentUpscaler3DProvider` 已注册。异构 checkpoint continuation 尚无视觉资格验证，使用时应按上游协调版本单独 smoke。
- `ComfyUI_MiniMax_H3_Extender`：`939f773`（v2.8.4）→ `5183ad4`（上游 main，v3.0.12）。包括 refine VRAM preflight offload 实验功能及 FullBatch 片段间 AIMDO 资源清理；该版本高于最新正式 tag v3.0.6，按 Sean 要求跟进 main。`MiniMaxH3Extender` 已注册。
- 五个仓库均为 Git fast-forward；更新差异没有 Python 依赖文件变化。原 commit 保留在各自 Git 历史中。FaceRefine 本地 `nodes.py` 改动、Latent Upscaler 和 Extender 的未跟踪缓存均保留。
- 启动后 ComfyUI `v0.40.0` 健康，`/object_info` 共 1743 个节点，五组目标节点可加载，队列为空。未执行 H3 视频生成回归；生成质量、速度、音频与新工作流行为仍待实际 smoke 验证。

## 2026-10-19 官方 H3 Model Sparse Attention / Sol-Attn 评估（Owner: Sean）

- ComfyUI 共享实例当前为 `v0.42.1`；本机 `/object_info/BlockSparseAttention` 已注册，显示名 `Model Sparse Attention`，无需安装 custom node。核心源码为 `comfy_extras/nodes_sparse_attention.py`。
- 官方 H3 文档：基础 H3 可用 `method=sol-attn`；`sla`/`vsa` 分别要求对应稀疏注意力训练权重；节点为实验功能，短序列默认阈值 `min_tokens=12288` 以下保持 dense。运行时还要求 CUDA、BF16、head_dim=128、可用 comfy-kitchen Sol-Attn kernel 和无 mask 等条件；verbose 可报告实际是否走 sparse 或回退原因。
- 核心代码把已有 `optimized_attention_override` 作为稀疏节点的 dense fallback；对 H3 可训练层使用独立 block patch 和 `comfy_kitchen.sol_attn_chunked`。因此推断可按 `KJ Patch Sage Attention → Model Sparse Attention → guider/sampler` 连接，让不适配/不达阈值调用回退到 Sage；这是源码路径推断，尚未用当前预览 workflow 验证。
- 适用判断：PDD 8 步 schedule 的前 6 次低分辨率 5 秒预览可能节省长序列 attention 计算，但短时低分辨率能否跨过 12,288 token 门槛尚未从当前 workflow 捕获；不能将 H3 高分辨率/长视频收益外推至本车道。稀疏近似会改变 attention 结果，须人工看动作一致性与画质。
- `Saganaki22/ComfyUI-sol-attn` 的 H3 零拷贝 Triton 节点是社区实现，主要性能基准为 RTX 5090 / SM120（报告对 SageAttention 有 1.38–1.65× throughput）；其 README 明确 SM89/RTX 40 性能尚未基准化。Kijai 旧 `ComfyUI-SolAttn_triton` 已标记弃用，因为 ComfyUI + comfy-kitchen 已内置 Sol-Attn。不要为使用官方节点重新安装旧 custom node。
- 搜索结果还出现社区 `Comfyui-minimaxh3-FBcache-shendumao` 的 “H3 Combined Acceleration V2”；它集成 Sage、可选 Sol-Attn 和 FirstBlockCache，不等同于 ComfyUI 官方 `Model Sparse Attention` 节点。其 Sage V2 启用时要求移除外部 KJ Sage patch，不能照搬到当前流程。
- 决策：保持现有 preview default Sage-only；如需验证，在 640×352 与 768×448 各做同提示词/seed、同 PDD 前 6 步、Sage-only vs Sage+官方 Sol 的热态 A/B，并记录 verbose 实际 kernel 路径、单次/多次采样耗时和视频抽帧。当前没有安装、改线或生成 A/B。
- 资料：ComfyUI [H3 Sparse Attention 指南](https://docs.comfy.org/tutorials/video/minimax/minimax-h3#speeding-up-generation-with-sparse-attention)、核心 [BlockSparseAttention 实现](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_sparse_attention.py)、社区 [Saganaki22/ComfyUI-sol-attn](https://github.com/Saganaki22/ComfyUI-sol-attn)、旧 Kijai 节点 [弃用说明](https://github.com/kijai/ComfyUI-SolAttn_triton)、神都猫 [H3 Combined Acceleration V2](https://github.com/signerzwb/Comfyui-minimaxh3-FBcache-shendumao)。
