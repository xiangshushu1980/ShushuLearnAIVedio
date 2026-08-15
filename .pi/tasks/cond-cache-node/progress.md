# 任务进度：cond-cache-node（H3 两阶段流水线 cond 缓存节点）

> 任务线：H3 两阶段流水线落地（docs/10 批量优化）。前置验证见 cond-roundtrip（已 ✅）。
> 第一步 = 自定义节点 Save/LoadMiniMaxH3Cond；第二步 = 两班倒守护进程。

## 任务
- 目标：把「TE 批编码落盘 → DiT 批采样」做成可编排的流水线，免 TE 重载（省 N-1 次 TE 加载）
- 当前状态：🟡（第一步完成，第二步待设计确认）
- 我负责的文件区：custom_nodes/ComfyUI-MiniMax-H3-CondCache/、scripts/h3_condcache_verify.py、.pi/tasks/cond-cache-node/

## 进度日志（append-only，每条带日期）
### 2026-08-16
- ✅ 第一步完成：自定义节点 SaveMiniMaxH3Cond / LoadMiniMaxH3Cond（custom_nodes/ComfyUI-MiniMax-H3-CondCache/）
  - 参考 nicehero/comfyui-conditioning-saver 思路，适配 H3 cond（标准 [(tensor, {attrs})] list）
  - Saver：torch.save 前递归搬 CPU（可移植）；输出绝对路径 STRING；is_output_node=True；计数器 auto-increment（output/conditioning/<prefix>_NNNNN.pt）
  - Loader：torch.load(map_location=cpu, weights_only=False) → 递归搬 intermediate_device()（对齐 sd1_clip 编码输出设备）
  - 用新 io.ComfyNode API（io.Schema/ComfyExtension/comfy_entrypoint，与本地 H3 节点同款）
- ✅ API 工作流验证 PASS（scripts/h3_condcache_verify.py）：
  - 阶段1（CLIPLoader+MiniMaxH3ImageToVideo+Saver）→ cond 落盘 0.3MB（embeds (1,16,5120) fp32 + tags (16,) int64 + pooled_output=None）
  - 阶段2（Loader+UNETLoader+EmptyMiniMaxH3LatentAV+采样链）→ 出片成功 output/video/h3_condcache_stage2_*.mp4
  - **免 TE 重载坐实**：阶段2 服务端日志窗口内 MiniMaxH3TEModel 加载 0 次 / MiniMaxH3(DiT) 1 次
- 📊 计时新发现（与 cond-roundtrip 直接库脚本的 112s/171s 矛盾，待复核）：
  - API 路径（动态 VRAM loading + 页缓存热）：阶段1 TE 加载+编码 ~7-10s，阶段2 DiT 冷载+20步采样+decode+出片 ~72s
  - 怀疑原因：①OS 页缓存（15.7GB TE / 19.5GB DiT 已在 RAM）②ComfyUI 0.33 "dynamic VRAM loading"（Staged 懒加载）vs 直接库脚本的 load_clip+load_model_gpu 全量反量化路径
  - 影响：若热态 TE 加载真 ~10s 而非 112s，两阶段「省 80s」的价值主张要重估——需一次受控测量（冷页缓存 vs 热）定性
- 工程约定落地：节点源码真相放 comfy-ops/custom_nodes/（git 追踪），ComfyUI custom_nodes/ 下软链指向（ComfyUI gitignore custom_nodes/）
- 踩坑（本线实录）：
  - io.ComfyNode 的 OUTPUT_NODE 要写在 io.Schema(is_output_node=True) 里，不是节点类属性（类属性不生效，报 prompt_no_outputs）
  - 新 API STRING 输出不进 /history outputs（只进 websocket executed 的 result）→ 验证脚本用确定性路径（复算计数器）代替读 history
  - SaveVideo 本版出片在 history outputs 的 "images" 键（不是 "videos"），mp4 文件名在 images 列表里

## 下一步
1. 第二步：两班倒守护进程（TE 班编码→等待窗口→DiT 班采样；任务随时注册；阶段管道 pre/TE/DiT/post + 任务依赖图；双卡预留不实施）——需先出设计方案与用户确认
2. 受控复测 TE/DiT 加载真实冷/热成本（清页缓存 vs 热），定性两阶段收益（省多少秒）

## 关键链接
- 相关文档：docs/10_h3_batch_optimization.md（两阶段方案+前置验证点）
- 前置验证：.pi/tasks/cond-roundtrip/progress.md（cond 往返/采样链路逐位一致，MSE=0）
- 节点源码：custom_nodes/ComfyUI-MiniMax-H3-CondCache/（cond_cache.py + __init__.py + README.md）
- 验证脚本：scripts/h3_condcache_verify.py
