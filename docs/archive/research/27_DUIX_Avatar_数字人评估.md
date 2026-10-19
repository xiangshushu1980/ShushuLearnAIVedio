# 27_DUIX_Avatar_数字人评估.md

> 生成：2026-09-01（T-comf-01 转向调研，来源：官方 README/DeepWiki 架构文档、社区部署实测、第三方对比，深档检索）
> 前提：4090 24GB / 每日 3 分钟视频 / 1-2h 预算。LongCat Avatar 已因产能判死刑（见 T-comf-01 progress）。

## TL;DR
DUIX-Avatar 是**全离线、可自托管**的开源数字人口播视频工具：~10s 真人参考视频克隆形象+声音，音频/文字驱动口型。核心是「参考视频上做 face-swap lip-sync」，**非** LongCat 那种生成式 AGDR 大模型 → 算力需求低一个量级（**最低 RTX 4070 8GB**，8GB 显存可用，4090 余量充足），**速度接近实时**（官方称 1 秒视频近实时生成、支持长视频/批量）。是本地 Heygen 类方案的强候选，专治 LongCat/InfiniteTalk 的产能短板。

> 注意：用户提的「HeyGen 2.0」有歧义。**HeyGen 是商业云端 SaaS**（分钟计费，非本地）。开源本地替代对应 **DUIX-Avatar** 及 **DUIX.Heygen** 系列（Duix 团队产品线）。本文聚焦开源可自托管的 DUIX-Avatar。

## 架构（3 层）

1. **Electron 客户端**（Windows10+/Ubuntu22.04）：Vue3 UI、FFmpeg 处理、管理数字人/项目（SQLite 元数据）
2. **3 个 Docker 微服务**（需 NVIDIA GPU）：
   | 服务 | 镜像 | 端口 | 职责 |
   |---|---|---|---|
   | ASR | guiji2025/fun-asr | 10095 | 语音识别（TTS 预处理） |
   | TTS/语音克隆 | guiji2025/fish-speech-ziming | 18180 | 声音克隆+文字转语音（/v1/invoke）|
   | **口型视频生成** | guiji2025/duix.avatar-gen-video | **8383** | **音频+参考视频 → 对口型视频** |
3. **存储**：SQLite 元数据 + 文件系统二进制

## 关键点：口型视频服务（duix.avatar-gen-video，端口 8383）
- **异步**：POST `/easy/submit`（传 `audio_url` WAV + `video_url` h264 参考视频路径）→ 返回 task code → GET `/easy/query?code=` 轮询 → `completed` 返回 `result_url`（mp4）+ `duration`。
- 输入走**挂载卷路径**（host↔container 映射，如 `D:/duix_avatar_data/face2face` ↔ `/code/data`）。
- 视频合成 `chaofen`(超分)=0 / `watermark_switch`(水印)=0 / `pn`=1（固定）。
- **对需求 ⑤（HTTP 服务 API）几乎开箱即用**：本身已是 HTTP 服务，DGB 可直接调 submit+query。
- 调优：`PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb`、`shm_size:8g`（1080p 60s 建议 8GB，4K 12GB+）。

## 硬件要求（DeepWiki 官方）
| 项 | 最低 | 推荐 |
|---|---|---|
| GPU | **RTX 4070 8GB**（sm8.9）| 4090/5090（16GB+）|
| CPU | i5-13400F | i7-13700K+ |
| RAM | 32GB | 64GB |
| 盘 | 系统100GB+SSD / 数据30GB+ | 250GB NVMe / 100GB+ |
- 部署三档：Full Stack（ASR+TTS+VideoGen）/ **Lite（仅 VideoGen，低资源）** / 5090 优化（CUDA12.8，向后兼容 30/40 系）
- **Docker + NVIDIA Container Toolkit + WSL2**（Windows）或 Ubuntu22.04 原生。首次拉镜像 ~70GB 流量。

## 语言/粤语
官方称多语言支持（中英日韩法德阿西…8+），检索到「支持粤语」表述；口型是**音频驱动的 face-swap**，理论上喂任意音频（含我方粤语 TTS 母带）即可对口型，不受 TTS 语言限制。**但粤语口型精度无官方专项数据，须同 LongCat 一样实测**（复用 04-inferences 固定粤语输入对）。

## 与 LongCat / InfiniteTalk / H3 定位对比
| 方案 | 类型 | 4090 速度 | 3min 日产能 | 粤语口型 | 备注 |
|---|---|---|---|---|---|
| **DUIX-Avatar** | 参考视频 face-swap lip-sync | 近实时（1s/s 量级），8GB 可跑 | **大概率满足** 1-2h | 我方可测 | 克隆真人形象，非生成式；长视频/批量支持 |
| LongCat Avatar 1.5 | 生成式 AGDR | ~44s 算 1s（A800-40GB）| **不达标** | 我方可测 | 已放弃（产能）|
| InfiniteTalk | Wan2.1 生成式 | 4090 720p OOM / 8×H200 ~9min/1min | 不达标 | wav2vec2 存疑 | 比 LongCat 更慢 |
| H3 (MC) | 联合音视频生成 | 3min≈58min | **达标** | 已验证链路 | 当前主线/备用 |

> 关键差异：DUIX 走「真人参考视频克隆」路线——需要一段 ~10s 真正的本人出镜视频作参考，产出的是「数字分身对口型」，**不是**凭空生成角色。若需求是给已有真人 KOL/主播做口播分身 → DUIX 契合且快；若需求是生成式虚拟形象 → 回到 H3。

## 待定/风险
- 图像/声音克隆涉及**肖像/声音授权合规**（涉他人形象须先处理授权）。
- 官方无 4090 精确生成秒开 s/s 的量化 Benchmark，需实测校准（10s 片计时）。
- WSL2 部署：项目官方主打 Windows+WSL2+Docker，本机 WSL2 环境契合，但需确认 Linux 侧 compose/GPU passthrough。
- 下载量 ~70GB（镜像），磁盘余量需确认（当前 ~221GB 可用）。

## 下一步建议（待用户拍板）
1. 在本机起 Lite compose（仅 VideoGen，省 ASR/TTS）→ 用现成音频+一段参考视频跑通 submit/query → 实测 10s 校准速度 + **粤语口型验证**（第一验收项）。
2. 通过后决定是否起 Full Stack（需 ASR/TTS 时）。
3. 若走 DUIX，验收①/②/④/⑤ 全部重定义（不再是 LongCat 测试流）。
