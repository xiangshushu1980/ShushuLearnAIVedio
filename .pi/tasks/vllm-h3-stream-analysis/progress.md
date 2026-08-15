# 任务进度：vllm-h3-stream-analysis

> 解析 B 站 BV1xmuT6dE1M（vLLM-Omni day-0 MiniMax H3 支持直播），提炼技术细节 + 本机可用项。
> 状态标记：🟡进行中 / ⏸暂停 / ✅完成

## 任务
- 目标：解析视频中 H3 架构与推理优化细节，筛出 comfy-ops（4090 24GB / ComfyUI 本地栈）能用的
- 当前状态：🟡（分析+两项调研完成；TODO 已记 T-20260815-08 Infract 量化版 + T-20260815-10 Cache-DiT 实测；待用户确认音画耦合 2×2 试验；hybrid 下载决策见 h3-new-findings-test 线）
- 我负责的文件区：.pi/tasks/vllm-h3-stream-analysis/

## 进度日志
### 2026-08-15
- 抓取视频：标题「vLLM-Omni day-0 MiniMax H3支持：探索最强视频生成模型推理的极限」，UP vllm_project，34:22，播放 1310
- 读全字幕（ai-zh，24KB）+ 评论（无弹幕）；直播资料 PPT 在 drive.google.com/drive/folders/18FfuwaP_OB-JRoTzlY6n-svYGnW2lBAT
- 要点提取：H3 架构（音视频共享 DiT / 双套权重 / encoder+VAE 相同）、vLLM-Omni 优化（任务路由 5720、分 stage 部署、DLO、continuous batching 5810、cache DiT、量化）、Infract 即将发量化版
- 本机可用项清单见会话输出；候选落地：① Infract 量化版发布后对比 ② ComfyUI cache-DiT 类跳层节点调研 ③ 稀疏注意力/算子融合跟踪
- 调研①（Cache-DiT 落地）：ComfyUI-CacheDiT（Jasonzzt）2026.08 已加 H3 支持——官方 T2V/I2V/R2V same-seed 验证 1.41-1.50x，保立体声音频；H3 走 Pattern 3 DBCache 自适应（fn_blocks=8/bn_blocks=0/threshold 0.12/warmup 3）；warmup 3 步对 turbo8 快车道收益存疑（README：<6 步不值得、low-step 未验证），慢车道 std14/20 收益最优；与 MotionCache/Motion-Context 同属 residual reuse 家族，叠加/重叠未测；底层=vipshop/cache-dit（直播"太阳"仓库），已集成 vLLM-Omni/SGLang/TensorRT-LLM/ComfyUI；已登记 T-20260815-10
- 调研②（音画耦合理解）：架构事实三重确认（BGM 调研 2.0 + 直播 + 官方 HF 卡"jointly predicts video and audio latents, unified packed sequence"）；分层结论=①架构事实已确认无需再查 ②写作纪律（soundscape 与画面同级）已有实测支撑（seg2 海浪变轻/环境音生成/音乐正向控制）17 号文档已固化 ③跨模态耦合强度（声音描述影响画面内容/画面影响音频的强度）是真实空白，机制成立（packed sequence 内 attention 跨模态交互）但强度未知，要生产规则级经验需 2×2 低成本试验（4-8 条 5s，可并入下次双轨测试批）

## 下一步
1. 用户确认哪些落地项值得跟进
2. 如需 → 记 TODO + mem0 [STATE]

## 关键链接
- 视频：https://www.bilibili.com/video/BV1xmuT6dE1M
- 字幕全文：/tmp/bili/BV1xmuT6dE1M/zh_full.txt
- 直播资料：https://drive.google.com/drive/folders/18FfuwaP_OB-JRoTzlY6n-svYGnW2lBAT
