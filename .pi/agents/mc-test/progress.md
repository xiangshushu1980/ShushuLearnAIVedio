# 任务进度：mc-test（Motion Context 跨段连续性验证）

## 任务
- 目标：验证 H3 Motion Context（NikoDemon80/ComfyUI-H3-Motion-Context，429★）能否解决跨段衔接一致性——latent 级把上段尾部 pin 进下段 conditioning，替代帧链硬桥/静态双锚
- 状态：🟡 准备中（2026-08-12 孵化，用户确认待测方案）
- 归属：web-shotlist-tool 线孵化，独立任务线（与 web 工具开发正交）
- 背景调研（2026-08-12 h3-prompt-agent 线）：作者实测 16-clip 4:34 多机位情景剧@736×576≈2h；视频链中位 seam level step 0.905→带音频跨载后 0.16；v0.2.0 'No more visible seam'（pin 帧直接从 latent 取）；上限判断：解决相邻段音画平滑衔接上限高，但①链式质量递减（音频高频先损，长链在自然乐句处重开）②分辨率链内锁定 ③成本线性堆叠 ④不解决长距离一致性 ⑤许可 EU/UK/KR/US 未覆盖

## 进度
### 2026-08-14 恢复上下文
- **队列已释放**（seedance-h3-verify 已完成 34 条 AB 对比收尾）：可随时重启 ComfyUI + 跑批，无需再等
- mem0 已整理：MC 调研/社区评价截断重复版已删（完整版保留）；本线 [STATE] 已建（comfy-ops 池）
- 跑批前先 [STATE] 声明队列占用

### 2026-08-12 孵化
- 用户确认待测方案 = Motion Context；决定独立任务线
- 装节点：ComfyUI-H3-Motion-Context clone 到 custom_nodes/（未重启，不干扰 seedance-h3-verify 跑批）
- 节点生效需重启 ComfyUI（2026-08-14 已确认队列释放，可直接重启）

## 测试计划（待跑批）
**对比实验**：两段链式（MC） vs 现有方案（Ref2VA 静态锚/帧锚）
1. 基线：约定系列两段（seg1→seg2），现有 pipeline（无 MC）→ 观察接缝（现有 seg2 首帧）
2. 实验：同两段，段 2 加 MC 节点（context_length=22 帧起，可选 5/22/39/56）→ 接缝对比
3. 判定：用户目视接缝（人物/场景/动作连续性）+ 音频连续性；seam level 数据
4. 变量：context_length 档位；音频是否跨载（作者数据：带音频跨载 0.16 vs 0.905）

## 注意事项
- 队列：跑批前 [STATE] 声明占用（当前 seedance 线在跑）
- 长链风险：质量递减 → 长链在自然乐句处重开
- 商用注意：EU/UK/KR/US 许可未覆盖

## 关键链接
- 节点仓库：NikoDemon80/ComfyUI-H3-Motion-Context
- 背景：mem0 "Motion Context 社区评价正面…"条目；docs/19 帧链负面结论
- 上游：.pi/agents/h3-prompt-agent/progress.md（成片试跑产物）
