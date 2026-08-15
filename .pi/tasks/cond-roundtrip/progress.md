# 任务进度：cond-roundtrip（H3 两阶段流水线前置验证）

> 任务线：H3 省 80s TE 重载 → 两阶段（cond 批编码落盘 + 批采样）。
> 试验目标：验证 cond（NestedTensor + minimax_token_tags + minimax_keyframes）torch.save/load 往返保真 + 读回后可直接喂 DiT 采样。

## 任务
- 目标：H3 cond 序列化往返可行性验证（docs/10 前置验证点）
- 当前状态：🟡
- 我负责的文件区：scripts/h3_cond_roundtrip.py、.pi/tasks/cond-roundtrip/

## 进度日志（append-only，每条带日期）
### 2026-08-16
- ✅ 试验1 PASS（scripts/h3_cond_roundtrip.py）：cond 序列化往返逐位一致
  - case A（t2va 无图）：cond = [(embeds (1,16,5120), {minimax_token_tags (16,)})] 往返+搬运GPU均逐位一致
  - case B（fl2va 带首帧）：embeds (1,360,5120)（含 vision tokens）+ tags + minimax_keyframes[0].latent (1,24,1,28,48) 往返一致
  - 关键修正：**cond 是标准 ComfyUI 结构 [(tensor, {attrs})] list，不是 dict**（docs/10 假设需更新）；embeds 普通 tensor 非 NestedTensor（单 prompt 场景）
  - 环境经验：ComfyUI 服务驻留 45.9GB，跑独立脚本前先 POST /free {unload_models,free_memory} 释放（队列空闲时安全）
- ✅ 试验2 PASS（scripts/h3_load_time_sampling.py）：落盘 cond 采样 vs 热路径**逐位一致**（video latent (1,24,37,28,48) + audio (1,32,2,207) MSE=0）——两阶段可行坐实（VAE decode 确定性，latent 一致=视频一致）
- 📊 加载时间实测（768×448×124帧 20步 int8，LOW_VRAM 无注意力patch）：
  - TE 阶段（load_clip+首次编码反量化）：冷 ~112s / 热 ~24s（load_clip 本身 lazy 仅 1-6s，真正成本在首次前向 nvfp4 CPU 反量化）
  - fl2va DiT 加载：冷 ~171s / 热 ~14-34s（int8 反量化 19.5GB 主导）
  - ref2va DiT 加载：~71s（受 fl2va 热身影响，真实冷估 ~150-170s）
  - 采样：~60s（20步，保守值）
  - 单视频构成：冷 ~342s / 热 ~118s（TE+DiT+采样）
- 环境坑（本线实录）：①独立脚本无 sage/solattn 采样激活顶满→必须 LOW_VRAM（mm.vram_state）防 OOM；②decode 阶段 DiT+VAE 叠加 OOM→对比用 latent 逐位（decode 确定性）；③WSL 下 torch OOM 错误信息进程信息不可靠；④脚本前 POST /free
- 立项：用户确认两阶段流水线为主路线（4B 暂不启用），先做最小试验
- 背景检索完成：社区现状（HF discussions/38 同款抱怨、ComfyUI Conditioning Saver 已有但未适配 H3、链接节点是主流通路）
- 试验设计：试验1=cond 往返逐位对比（t2va 无 keyframes + fl2va 带 keyframes 两 case）；试验2=读回 cond 喂 DiT 采样 vs 热路径对比（下一步）
- 环境确认：ComfyUI 0.33.0 运行中、venv 可用、TE nvfp4 15.7GB

## 下一步
1. （已完成）试验1 cond 往返 + 试验2 采样链路逐位一致
2. 落地两阶段流水线：批编码 cond 落盘 → 批采样。形态可选：
   a. 自定义节点（LoadMiniMaxCond/SaveMiniMaxCond，参考 Conditioning Saver 但适配 H3 cond）→ **已在 cond-cache-node 任务线落地**（custom_nodes/ComfyUI-MiniMax-H3-CondCache）
   b. 脚本批处理（TE 一次编码 N cond → 落盘 → 逐个采样，comfy 库直调）
   c. API 工作流 + 缓存节点 → **已验证**（scripts/h3_condcache_verify.py，阶段2 无 TE 出片 PASS）
3. 收益：N≥3 不同 prompt 批量，省 (N-1)×~90s（TE 冷重载）或 (N-1)×~20s（热重载）

> 注（2026-08-16）：本线（前置验证）已收口，两阶段落地转 cond-cache-node 任务线；"省 80s TE" 的收益基数在 API/动态 VRAM 路径下测得 ~10s 而非 112s，需受控复测，见 cond-cache-node/progress.md。

## 关键链接
- 相关文档：docs/10_h3_batch_optimization.md（两阶段方案+前置验证点）
- 相关 mem0 条目：2026-08-16 两阶段为主路线决策、H3 TE 生态调研
