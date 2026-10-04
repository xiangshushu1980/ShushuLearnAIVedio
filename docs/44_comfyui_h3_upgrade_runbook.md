# [Sean] ComfyUI 与 H3 升级参考 Runbook

> 用途：后续升级 ComfyUI、本体依赖、H3 节点、模型或优化组件时，提供单一入口。
> 更新时间：2026-09-26
> 适用环境：WSL2 / RTX 4090 24GB / Python 3.13；实际版本以运行时探测为准。

## 1. 先判断升级对象

不要把下面几类变化混成一次升级。它们的回归范围不同，也不能用同一条成功标准判断。

| 类别 | 例子 | 必须回归 |
|---|---|---|
| ComfyUI 核心 | 核心代码、前端、工作流模板 | 启动、节点表、代表工作流、队列/API |
| Python/CUDA 依赖 | PyTorch、Transformers、SageAttention、comfy-kitchen | 导入、kernel/fallback、显存、速度、音频 |
| H3 custom node | NativeAudioLock、FaceRefine、CondCache、Ref-Patch | 对应专项最小工作流；NativeAudioLock 必须验音频锁定 |
| H3 模型/量化 | checkpoint、LoRA、VAE、TE、ConvRot/W4A4 | 同输入同 seed 的 smoke + 画质/音画检查 |
| 工作流/提示词契约 | Ref2VA 六段式、reference 标签、时间线 | 结构、标签、时长、音频/身份连续性 |
| 加速/省显存组件 | Sage、Sparse、H3MemoryOptimization、Cache-DiT | 同条件 A/B；不能只看“能生成” |

## 2. 权威资料路由

- 环境、启动、API：[`docs/01_environment.md`](01_environment.md)
- 模型和磁盘实况：[`docs/02_models.md`](02_models.md)
- 节点来源与历史基线：[`docs/dev/comfyui_node_update_20260912.md`](dev/comfyui_node_update_20260912.md)
- 普通 H3 Ref2VA 入口：[`docs/34_ref2va_generation_guide.md`](34_ref2va_generation_guide.md)
- VDN 路线：[`docs/35_vdn_h3_ref2va_route.md`](35_vdn_h3_ref2va_route.md)
- H3 参数/速度演进：`.pi/ledger/h3-speed.md`、`.pi/ledger/h3-models.md`
- 提示词结构契约：`.pi/skills/h3-prompt-writing/` 与 [`docs/17_h3_prompt_writing_rules.md`](17_h3_prompt_writing_rules.md)
- FaceRefine 当前状态：[`docs/43_h3_facerefine_current_state.md`](43_h3_facerefine_current_state.md)

`docs/09_h3_test_plan.md` 是历史测试全量数据，不应单独作为当前默认参数来源；ledger 中标记为“现行”的条目优先，仍须核对适用条件。

## 3. 升级前检查

1. 使用唯一入口检查共享服务：

   ```bash
   ./scripts/comfy-stack.sh status
   ```

   已有健康实例必须复用；不要直接运行 `main.py`、`nohup` 或另起第二实例。
2. 记录可回滚基线：ComfyUI commit、前端/模板版本、Python 关键包、custom node 各自 commit/tag、启动参数、GPU/RAM 状态、队列状态。
3. 确认工作流、参考图、音频、prompt 和 seed 都能定位；升级前先跑一条代表性成功样本，保留输出和日志。
4. 确认磁盘空间、Swap、`/home/sean/projects/ComfyUI/user/comfyui.db` 没有多实例锁竞争。
5. 对每个 Git 节点先保留本地提交，再更新上游；没有 Git 基线的目录先建立基线，不能直接覆盖。
6. 一次只改变一个主要变量。核心、依赖、节点、模型和优化器应分批升级，便于定位回归原因。

## 4. 推荐升级顺序

```text
记录基线 → ComfyUI 核心/前端 → Python/CUDA 依赖 → custom nodes
→ 模型/LoRA/VAE/TE → 优化器或低显存组件 → 工作流和 prompt 适配
→ 分层回归 → 更新 docs / ledger / Mem0
```

每一层完成后都要能启动并通过最小检查，再进入下一层。不要在同一批次同时换核心版本、H3 checkpoint 和采样器。

## 5. H3 专项回归门槛

### P0：结构与加载

- ComfyUI 正常启动；`/system_stats`、`/object_info`、队列和历史 API 可用。
- 目标 custom node 出现在节点表，日志没有 import error、kernel fallback 或错误的旧节点加载。
- H3 prompt 使用正确模式：T2VA、I2VA、FL2VA、L2VA 或 Ref2VA；Ref2VA 继续使用官方六段式和稳定 reference 标签。
- `NativeAudioLock` 只用于外部音频锁定链路，不能当普通 `ref_audio` 音色参考；验收时必须确认原音频仍在、视频仍受音频条件驱动。

### P1：最小 smoke

同一参考图、音频、prompt、seed 和输出网格，优先使用 5 秒/124 帧或项目已有短 smoke。记录：成功/失败、耗时、峰值 VRAM、主机 RAM、输出帧数、音频时长和错误日志。

### P2：代表性回归

- 普通 Ref2VA：身份、构图、动作和音画同步；
- NativeAudioLock：外部音频锁定、口型/动作响应、音频不被重生成；
- 当前生产尺寸/时长：通常以 `1024×576`、8 秒或项目现行基线为主；
- 若改 FaceRefine：单人近/中景、双人目标选择、远景掉检；8 秒窗口优先，不直接跑整片；
- 若改优化器：同 seed A/B 检查清晰度、动作连续性、脸/手/物体拓扑、闪烁、音量和音频内容。

### P3：接受标准

“能出视频”不等于升级成功。至少满足：无 OOM/异常 Swap、时长和帧网格正确、音频可播放且长度对齐、身份/动作无明显回归；速度收益必须同时报告端到端耗时和显存/RAM 代价。

## 6. 当前已知升级结论

- ComfyUI 核心版本记录曾出现 `0.35.0` 与 ledger 中 `0.36.0` 的时间差；下次升级前必须从运行时和 Git 重新采集，不要把旧文档头部版本号当真值。
- 现行正式出片基线（2026-10 起）：Ref2VA + PDD Acc 8-step + `PatchSageAttentionKJ` + KJ `MiniMax H3 Low VRAM Attention`/`Chunk FeedForward` + NativeAudioLock，1024×576；详见 [34 §0](34_ref2va_generation_guide.md) 与 ledger `C-20260915-01/03`。VDN 与 KJ LowVRAM 不兼容，不作为正式路线。
- ComfyUI 核心已提供 Sparse Attention 路线；旧 `ComfyUI-SolAttn_triton` 已归档，不重新启用，也不把历史 SolAttn 工作流当生产基线。
- `ComfyUI-H3-NativeAudioLock` 更新后必须跑数字人基础回归；`ComfyUI-H3-FaceRefine` 是独立后处理慢车道，不应因安装成功就加入基础链。
- H3 的低显存/加速组件存在组合边界；例如某些 KJ LowVRAM 节点与 VDN 的特殊 list 输入不兼容。任何组合都必须做同条件 smoke，不能凭名称推断兼容。
- `ComfyUI-MiniMax-H3-W4A4-VSA` 当前属于隔离候选，不替换正式基线；只有明确验证低显存或超长/竖幅目标时才做独立 A/B。
- 20 秒及以上实验可以执行，但要明确标为超出官方 H3 4–15 秒目标范围的扩展测试；不能把扩展结果写成默认 prompt 或生产参数。

## 7. 回滚与留痕

- 节点回滚优先切回升级前的本地 commit/tag；核心和依赖回滚要保留升级日志、错误日志及失败产物。
- 不用整树 `reset --hard`、`checkout` 或批量删除来“恢复干净”；只操作本次升级明确涉及的目录和文件。
- 失败结果保留在 `experiments/`，当前稳定参数写 docs/skill，演进覆盖关系追加到 `.pi/ledger/`，动态踩坑写 Mem0 `comfy-ops` 池。
- 升级完成后记录：日期、变更对象、旧/新版本、commit/tag、工作流、输入 hash 或文件名、seed、硬件、耗时、VRAM/RAM、QC 结论、是否回滚。

## 8. 2026-09-26 上游巡检结果

本轮通过 GitHub API、仓库 release/commit 和 Hugging Face 模型卡核对。以下是“上游有变化”与“本机是否应该升级”的分离判断：

| 对象 | 上游现状 | 本机对照 | 判断 |
|---|---|---|---|
| ComfyUI 核心 | 最新正式 tag `v0.37.0`（2026-09-21） | 本机 `88ab4a06`（2026-09-24），已在 `v0.37.0` 之后；含 H3 VAE offload 修复和 VAE tile 邻接融合提交 | **不升级**；本机源码已领先 release，先补运行时版本记录 |
| H3 NativeAudioLock | 上游 `master` 最近可见提交为 `11a95f6`（2026-08-05） | 本机基线 `18424e6`（2026-09-12 同步） | **无新上游升级**；更新后仍需基础数字人回归 |
| H3 FaceRefine | 最新 release/main 仍为 `v1.1.2`，上游 commit `d8521d1`（2026-09-13） | 本机含该版本，并有本地 `nodes.py` 未提交修改；本地分支比 `origin/main` 多 4 个项目同步/基线提交 | **不升级**；先保护本地增强，继续使用已验收版本 |
| ContactSheet / MAINodes | 上游 `main` 已到 `f4868b4`，提交标记 `v1.1.3`（2026-08-29） | 本机仍是 `3d558d9` 基线，且与上游分叉 | **仅隔离测试**；这是节点迁移包，不直接覆盖正式链 |
| Spectrum | 上游 `v0.2.28`（2026-09-18）修复 CRLF source-audit | 本机已是 `v0.2.28`，commit `5161f04` | **已完成升级**；docs/09 与 ledger 中的 `v0.2.20` 版本描述需视为历史实测条件 |
| Cache-DiT | 上游仍以 2026-08 H3 支持为主，未发现新的本机适配版本 | 本机未作为正式节点启用 | **继续待验证**；优先测试标准 14/20 步，不插入 turbo8 默认链 |
| FastH3 / VSA | 出现新的实验性 ComfyUI 适配和 checkpoint/gate；官方说明仍限 FL2VA/T2VA，Linux/WSL、Ref2VA 未验证 | 本机 4090/WSL，正式链为 Ref2VA/NativeAudioLock | **不升级正式链**；只建隔离 smoke，不能当低显存方案 |
| MiniMax-H3 模型仓库 | `Comfy-Org/MiniMax-H3` 最近更新 `2026-09-24T16:21:21Z`，revision `bf92c409` | 相比前一 commit，新增 `model_patches/minimax_h3_fun_controlnet_union_2.0_pruned_bf16.safetensors`（8,382,288,792 bytes）；前一 commit 已新增对应 INT8 ConvRot 文件（4,531,220,608 bytes）。本地目前没有这两个 ControlNet 2.0 文件 | **仅在需要 H3 Fun ControlNet 2.0 时下载/测试**；不影响当前 Ref2VA 默认链，不盲目重下全部模型 |

本轮最值得记录的是：ComfyUI 和 Spectrum 实际已经在本机先于文档/正式 release 状态发生变化；因此下次升级先做“本机 commit/tag 与上游 tag 的三方对照”，再决定是否动作。`docs/dev/comfyui_node_update_20260912.md`、`docs/09_h3_test_plan.md` 中的旧版本号不能单独作为当前版本依据。

### FaceRefine 本地未提交修改摘要

当前工作树仅改动 `custom_nodes/ComfyUI-H3-FaceRefine/nodes.py`，约 209 行新增、3 行调整：

- `H3FaceTransformInfo` 增加检测成功率、掉检帧、源脸像素高度统计、权重和连续掉检区间报告；
- 新增 `H3FaceManifestSave` 节点，把源视频 SHA-256、检测/身份选择、阈值、候选框和逐帧 refine/original 决策保存为 JSON manifest；
- `H3FaceSelect` 增加 `analysis_manifest` 输入，可复用已审计的候选框和人物选择，跳过第二阶段的 detector/identity 重算，并校验帧数与分辨率；
- 注册新节点显示名 `H3 Face Analysis Manifest Save`。

这批修改的目的，是解决双人远景中依赖 `face-index` 选错目标的问题，并让分析阶段与 refine 阶段可复用同一份审计结果；它不是上游 `v1.1.2` 的更新内容。

### FaceRefine 的维护形态判断

当前实现不能直接作为“完全独立、零耦合”的外部 wrapper：它修改了官方 `H3FaceTransformInfo`、`H3FaceSelect` 的行为和输入，并新增了节点注册；外部包若只新增节点，无法无侵入地给官方节点增加 `analysis_manifest` 输入。官方仓库为 MIT，可合法 fork/修改，但必须保留许可证和版权声明。

推荐当前采用 **fork/本地分支维护**：

1. 把官方 `main` 作为 `upstream`，把本地增强提交成独立 commit；
2. 每次上游 release 后先合并到分支，再解决 `nodes.py` 冲突；
3. 合并后固定跑官方基础 workflow、单人跟踪、双人目标选择、manifest 复用和 8 秒 FaceRefine 回归；
4. 保留上游版本、合并 commit、测试结果和是否回滚记录。

后续若希望降低合并成本，可以再拆成 companion package：只放 manifest 保存、统计和审计工具，使用独立节点输出；但要实现“让官方 `H3FaceSelect` 消费 manifest”，仍需要上游提供扩展 hook，或继续保留一层 fork patch。当前不建议用 monkey-patch 或运行时覆盖官方类，升级时更难定位。

### H3 Fun ControlNet 2.0 是否纳入 4090 体系

它应理解为“结构/运动约束支线”，不是普通 Ref2VA 的画质增强器：

- 输入通常是逐帧控制视频，而不是一张普通参考图。单图可以通过重复成控制帧或作为静态结构控制使用，但不能替代 Ref2VA 的身份参考；静态控制也不会自动产生合理的镜头运动。
- Pose 是动作引导，不是逐关节硬拷贝。H3 会结合 prompt、主体参考和时间上下文补全动作，因此可以丰富动作，但也可能改动手部、脚步、节奏和镜头；骨骼本身质量差时，输出不会自动变好。
- Layout 更适合控制多人/物体的空间占位和左右关系；它主要约束“谁在哪里”，不负责身份、表情、口型或具体动作。
- Depth、Canny、HED、MLSD、Scribble、Gray 分别偏向空间、轮廓、线稿和亮度结构；这些控制视频需要先经过外部/前置预处理器生成。
- 2.0 控制分支权重本身约 13.5GB（BF16 文件约 8.38GB，INT8 文件约 4.53GB）。ComfyUI 当前实现会按 `unet_offload_device()` 创建模型 patch，文件大小不等于固定的常驻显存增量；但控制分支仍会在采样时换入/执行，并增加控制 latent、临时 workspace、RAM 搬运和时间成本。当前 4090 正式 H3 已接近 23.1GB 峰值，不能把“可 offload”理解成一定能安全叠加。
- 资源估计：若按当前 23.1GB 峰值基线计算，名义 24GB 显存只剩约 0.9GB；因此 `1024×576`、15–20 秒正式链基本不应预期能稳定叠加 ControlNet。`768×448`、39/56 帧短 smoke 有机会通过动态 offload 跑通；124 帧/约 5 秒只能作为第二级试验，是否成功必须实测，不能从 4.53GB 文件大小推导。

当前决策：**不加入 4090 默认体系，只建立可选隔离支线**。第一优先是 Layout 双人站位 smoke；第二优先是 Pose 动作引导 A/B；暂不为普通 Ref2VA 下载 ControlNet 2.0。门槛为同一参考图、prompt、seed、音频和 5 秒/124 帧短片，记录 VRAM、RAM、耗时、动作丰富度、身份、手脚拓扑和音画同步；只有 Layout 或 Pose 在多个案例中有明确收益且资源可控，才进入正式工作流。

### 本轮证据入口

- [ComfyUI v0.37.0 release](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.37.0)
- [ComfyUI v0.37.0 → 当前 master 的 H3 相关修复](https://github.com/Comfy-Org/ComfyUI/commits/master/)
- [ComfyUI-H3-FaceRefine releases](https://github.com/Carasibana/ComfyUI-H3-FaceRefine/releases)
- [ComfyUI-MAINodes main](https://github.com/matlowai/ComfyUI-MAINodes)
- [Spectrum MiniMax H3 v0.2.28](https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3/releases/tag/v0.2.28)
- [FastH3 VSA experimental ComfyUI adapter](https://github.com/exportAnything/ComfyUI-FastH3-VSA)
- [Comfy-Org MiniMax-H3 model repository](https://huggingface.co/Comfy-Org/MiniMax-H3)
- [MiniMax-H3 latest model commit](https://huggingface.co/Comfy-Org/MiniMax-H3/commit/bf92c4091e333e69b8ca1998e0a669f15cb0832b)
- [MiniMax-H3 preceding model commit](https://huggingface.co/Comfy-Org/MiniMax-H3/commit/8bd883dd07e101e219eb3c554cbbc45c255b7b86)

## 9. 收尾检查

```bash
./scripts/comfy-stack.sh status
bash scripts/docs_check.sh
```

文档更新遵守单一权威正文：本 Runbook 只维护升级流程和门槛；具体参数仍回链到 H3 专题文档，实验细节不复制进本页。
