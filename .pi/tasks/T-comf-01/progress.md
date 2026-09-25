# T-comf-01 进度：LongCat 1.5 V1 本地数字人推理链路

> 4090 24GB。验收：① ComfyUI 节点+GGUF 部署 ② 粤语口型验证 ③ AT2V 双条件+分段续接 ④ 同音频对照 InfiniteTalk 不劣化 ⑤ HTTP 服务 API

## 状态总览

- [x] ① 部署（节点+模型成本已沉没，因产能判死刑）
- [x] ~~②/③/④/⑤~~ 未开展，产能根本性不达标
- [ ] **→ 搁置/弃：LongCat Avatar 判不达标（2026-09-01 用户拍板放弃）**

## ⚠️ 当前结论（2026-09-01 已拍板：放弃 LongCat）
单 4090 产能实测+社区/第三方：LongCat Avatar ≈ 44s 算 1s 成片（A800-40GB），多段续接必 KV-offload，4090 1min=1h+。每日 3min/1-2h 预算物理不可达 → **放弃 LongCat 当 V1 引擎**。模型/节点/工作流资产保留在磁盘，成本已发生。

## 会话日志

### 会话1 (2026-08-29)

- 开场登记完成（hive-context saved）。读 INDEX.md、h3-digital-human-research 相关结论。
- **冲突提示**：Mem0 first-soul 池有 2026-08-28 记忆「主路线=MiniMax H3，LongCat Avatar 1.5 仅作对照/备用」，本任务将其立为 V1 引擎，疑似决策反转；收尾 retain 时需更新该记忆。
- 现状：本机 custom_nodes 无 LongCat 相关节点，docs 无 LongCat 资料 → 部署需从零调研。
- 已有可复用资产：粤语播音音频+逐字口播稿（research 04-inferences 固定输入对，④对照时必须同音频）；InfiniteTalk 基线经验（research 03）。

### 阶段① 调研结论（2026-08-31，深档：Exa+Tavily+GitHub原文+HF仓库）

**模型**：LongCat-Video-Avatar 1.5（MeiGen-AI/meituan-longcat，2026-05-21 发布），支持 AI2V/AT2V/音频驱动续接，官方称比 InfiniteTalk 更强。音频编码器=Whisper-large-v3（非 wav2vec2）。

**节点三候选**：
1. **rookiestar28/ComfyUI-LongCat-Avatar**（推荐主路径）：CUDA 专用，9 节点，Avatar 1.5 专用。支持 at2v（免图）、单人/双人、480p(480x832)/720p(768x1280)、DMD distill 8步 CFG=1、25fps（非25会口型失稳）、分段续接内置（首窗93帧+每段80帧/13帧重叠，Audio Window 节点）、official_sharded / official_int8_sharded / 单文件int8。**GGUF 明确不支持**。Python 3.10-3.13，需 ffmpeg on PATH。
2. smthemex/ComfyUI_LongCat_Avatar：中文社区版，单人/双人测试过，更新较早（6月初）。
3. kijai WanVideoWrapper：LongCat Avatar 支持已进 wrapper（issue #1780，实测质量/表现力好评，10步 distill lora 可用），走 GGUF 的可能路径。

**GGUF 现状**：vantagewithai/LongCat-Video-Avatar-1.5-GGUF-ComfyUI 有全套量化（Q2~Q8，Q4_K_S≈11.7GB，Q8≈19GB），但 Reddit r/comfyui 反馈「GGUF does not work with longcat avatar」；rookiestar28 明确拒收 GGUF。→ **验收①的「GGUF」字样与现实冲突，见待用户拍板**。

**24GB 显存方案**：official_int8_sharded（4 shards，官方量化）或单文件 int8（smthem merge）≈14GB 级；bf16 全量 6 shards 也可能塞得下但紧。

**所需模型清单**：DiT（三选一）+ VAE(LongCat-Video-Avatar-vae) + whisper-large-v3.safetensors(audio_encoders) + dmd_lora(loras) + UMT5-XXL fp8（本机已有 Wan 同款可复用）+ 可选 Kim_Vocal_2.onnx。

### 阶段① 部署执行（2026-08-31，未完成，下会话继续）

**已就位**：
- 节点：rookiestar28/ComfyUI-LongCat-Avatar v0.3.0 装在 custom_nodes，9 节点（`LongCat_Video_SM_*`）全部注册 ✅
- 模型全就位：INT8 sharded DiT(15G) + VAE + whisper-large-v3(3.1G) + dmd_lora(2.5G) + 官方 LongCat-Video tokenizer/text_encoder(22G, models/longcat/LongCat-Video) + Kim_Vocal_2.onnx ✅（TE 用官方目录版，非 umt5 单文件）
- 依赖已装（注意 diffusers 被升到 0.40.0）
- 测试工作流：`workflows/longcat_avatar15_at2v_test.json`（API 格式，at2v/480p/8步/sageattn，4s 测试音频）✅ 可入队
- run_workflow.py 只吃 UI 格式，API 用 POST /prompt（脚本见会话记录）

**踩坑记录**：
1. hf snapshot_download 走 hf-mirror 对 LongCat-Video 仓库反复 LocalEntryNotFoundError → 改 curl 直拉 resolve URL 可靠
2. LongCat 自管采样循环不吃 ComfyUI interrupt，杀跑只能重启
3. text_encoder_root 必须是相对 models/longcat 的路径（如 `LongCat-Video`）
4. Sampler 非输出节点，需 CreateVideo+SaveVideo 收尾
5. **性能/稳定性问题（核心未解）**：480p 93帧 8步 at2v，SDPA ~8.5min/步；sageattn 无提升；跑 ~2 步后 GPU 0% 挂死（24GB 常驻），~2.5h 未完成。疑点：INT8 反量化 CPU 回退 / WSL / BSA 注意力路径。SDPA 回退因 flash_attn2 缺失

**下会话实验计划（优先序）**：
1. 装 flash-attn2（官方默认后端）再跑
2. 换 official_sharded bf16 + block_num streaming（1-64）对比 int8 反量化开销
3. 确认 WSL/CUDA13 下 torchao int8 matmul 是否 CPU 回退（node debug_mode 已开，看 profile 输出）
4. 跑通后进入验收②粤语口型验证

### 会话2 (2026-08-31 第二轮：性能诊断 + 社区对照 —— 已落盘停跑)

**实验**：改 sageattn 重跑（d3520d35），两次均正常跑完 ~50%+（GPU 持续 100%，无挂死复现 → 上次 0% 挂死疑似内存压力偶发，非必然）。实测：**480p 93帧 at2v 每步 ~7min，sageattn 与 SDPA 无差异**。RAM 稳 12GB，无泄漏。

**flash-attn2 装不上**：torch 2.13.0+cu130、py3.13、sm89；官方 wheel 只到 torch2.8/cu12（ABI 不兼容；源码编译需 nvcc + 1-2h）。

**社区 4090 数据（深档检索）**：
- kijai WanVideoWrapper issue #1806：4090D、480p、10步、105帧 → **LongCat-Avatar ≈60s/步**（LongCat_TI2V ≈20s/步）；kijai 回复“audio_cfg 会把推理时间翻倍”。
- comfy.icu Sampler 页：~6 秒片在 4060Ti 要 17-20 分钟；5090 也叫慢。
- 我们节点 7min/步 ≈ 社区 60s/步的 **7× 慢**（差距：SDPA vs flash-attn2、INT8 朴素反量化 vs bf16/fp8、节点封装 BSA 关闭）。

**产能模型（关键决策依据）**：3分钟视频 = 180s×25fps = 4500帧，按首窗93帧+每段80帧/13重叠 ≈ **56 个续接窗口**。
- 社区 60s/步 × 8步 × 56窗 ≈ **7.5 小时/3分钟**  —— 远超每日 1-2h 预算。
- 即使优化到 ~20-30s/步（fp8/fa2/sage），仍需 ~2.5-3.7h/片，仍超预算。
- H3 对照：5s≈1.6min → 3分钟≈58min（MC 链式，线性估）→ **单 4090 上 H3 产能才基本满足 3min/1-2h**。

**⚡决策点（待用户拍板）**：单 4090 上 LongCat Avatar 1.5 产能不满足每日 3 分钟/1-2h 要求。三条路：
  A. 继续优化 LongCat（装 fa2 需重装 torch/nvcc、换 kijai wrapper+bf16/fp8、开 BSA/Triton）——预计最多到 3-4h/3min，仍超预算，且任务⑤⑥还没跑。
  B. 现实化产能预期：LongCat 定位短句/单段（<30s）口型精修，长片绕回 H3 MC（本次记忆冲突其实指向这个）。
  C. 降分辨率/降帧率/改窗口叠量再实测（收益有限，最低已 480p）。

**已弃坑速记**：interrupt 杀不死 LongCat 自管采样；py-spy 需 sudo；WSL 下 CUDA13 缺乏 fa2 轮子。

### 会话5 (2026-09-01：产能误解纠正 + 建 Duix 任务 + 在线方案调研)

**关键纠正**：「3min≈58min」是 H3，不是 LongCat！LongCat 真实产能：VisionStory A800-40GB 44s/s → 1min≈44min/3min≈2.2h；kijai 4090D 每窗8min → 1min≈2.5h/3min≈7.6h。用户方向调整：见下方「在线方案」。

**在线方案调研（落 docs/28）**：用户放弃 LongCat 后问「有没有在线便宜能看效果」。结论：
- **LongCat Avatar 有免费 HF Space 在线版**（fffiloni，Gradio+A10G，已验 live）：免费看 LongCat 口型/效果，含粤语可测 → 零成本在线验证第一验收项。
- 硅基元镜免费每日5分钟（Duix同源，效果预览无缝）。可灵数字人 0.12元/s（1min≈7元）；HeyGen Free 3片/月；D-ID Lite $5.9/月。百度千帆/智影精品 2000元+/次（排除）。
- 建议路径：先在线白嫖看效果 → 达标再看按量 API/自托管。

**B站 LongCat 资源**（comfyui-lc 面搜到）：
- BV1GiqrB8E5j AIwood爱屋 首发评测 11:33（播放1.4w）
- BV1U5rhBBEuH 极致表情迁移电影级 17:02
- BV18gqmBrEa2 T8star-Aix 全面测试 vs InfiniteTalk 14:32（对比谁更强，直接可参考）
- BV1HnVm63E9H 1.5全解析三套工作流 12:47
- BV1sWrkBwEBS 喂饭级教程48分钟 KD节点
- BV1gdG161EYB 玩具到工具：循环续写/720p全流程 6:09（产能向）
- BV1N7BMBtExk 老许 长视频教程+云端 7:48

**B站 DUIX/HeyGem 资源**：
- BV1rxjo6zEg1 猫宁 HeyGem2.0 DUIX-Avatar一键整合包 无需Docker/bG显存（即用户所指）2:12 播放1.3w

## 待办/备注
- LongCat 优化路径（重新排）：装 flash-attn2（需换 torch 或源码编译，WSL/CUDA13 较难）→ 换 kijai wrapper bf16/fp8 → 开 Triton+BSA → 验证 INT8 反量化是否 CPU 回退。目标把 7min/步降到 <1min。
- 需确认磁盘：LongCat 模型已占 ~43GB，Duix 镜像又要 ~70GB，当前可用 ~221GB 够但注意。

## 待用户拍板

**第三方实测（VisionStory，A800-40GB，官方 demo 输入，非 cherry-pick）——LongCat 1.5 最可靠一手数据**：
- 82 秒片 = 3586s（~1 小时），26 段，**~138s/段**，**~44s 算 1s 视频**；10s 短片也要 ~7min。
- 连续 40GB 显存钉满 98.9%；**多段续接必须 --offload_kv_cache（KV 缓存挪 CPU）才能塞下**，否则第 2 段即 OOM（40GB 上 48 层 KV cache 撑爆）。
- 多卡 context-parallel 在我们的盒上 NCCL 死锁 → 只能单卡 → 无法靠加卡提速单条。
- 效果：照片驱动(ATI2V)身份保持好、口型跟唱准；**双人多说话人各对口型也 work**；但纯文+音(AT2V 无参考图)会脸扭曲/漂移/蜡化。

**InfiniteTalk 实测**：
- 音频编码器=chinese-wav2vec2-base（非多语言鲁棒）→ 粤语须单独验证。
- issue#187：4090 24GB **720p 直接 OOM**，只能 480p。
- issue#191：**8×H200** 上 1 分钟片要 ~9min——资源堆满速度也一般。
- 我们 docs 3 章已有 4090 基线：720p 10s≈5.8min；40 步默认；长片滑窗完整步数每窗可能 1 小时+。

**Apatero 那个“20-30s 算 1s 视频”偏乐观**：它讲的是 LongCat-Video(非 Avatar)+多卡可选，单 4090 且 Avatar 场景视实测为 44s/s（VisionStory）。

**kijai 节点慢=不是效果更好，是没走最优配置**：同模型同权重，差别在封装/后端（fa2/bf16/fp8/BSA、是否 KV offload），不是模型效果差异。效果由权重+量化+上下文决定，节点只是加载。

**产能最终判定（铁）**：LongCat Avatar 单卡永远无法满足每日 3 分钟/1-2h（A800 40GB 都要 ~44s/s → 3min≈2.2h 起步，4090 更慢且需 KV offload）。H3 5s≈1.6min→3min≈58min 仍是唯一达标项。

## 待用户拍板
- ~~验收①GGUF vs INT8~~ → 用户拍板 A（INT8），B 划掉 ✅
- **【新增·阻塞】产能决策（2026-08-31）：单体 4090 + LongCat Avatar 1.5 每日 3 分钟视频/1-2h 预算的可行路径选择。**

## 待办 / 备注

- 阶段计划：调研(节点/模型仓库/GGUF 量化档) → 下载 → 部署跑通 → 粤语验证 → AT2V → 对照 → 服务化
- 若继续 LongCat 优化路线：候选杠杆 = 换 kijai wrapper+bf16/fp8 / 装 fa2（需重装 torch 栈+nvcc）/ 开 Triton+BSA / 验证 INT8 反量化 CPU 回退
