# 任务进度：mc-test（Motion Context 跨段连续性验证）

## 任务
- 目标：验证 H3 Motion Context（NikoDemon80/ComfyUI-H3-Motion-Context，429★）能否解决跨段衔接一致性——latent 级把上段尾部 pin 进下段 conditioning，替代帧链硬桥/静态双锚
- 状态：🟡 准备中（2026-08-12 孵化，用户确认待测方案）
- 归属：web-shotlist-tool 线孵化，独立任务线（与 web 工具开发正交）
- 背景调研（2026-08-12 h3-prompt-agent 线）：作者实测 16-clip 4:34 多机位情景剧@736×576≈2h；视频链中位 seam level step 0.905→带音频跨载后 0.16；v0.2.0 'No more visible seam'（pin 帧直接从 latent 取）；上限判断：解决相邻段音画平滑衔接上限高，但①链式质量递减（音频高频先损，长链在自然乐句处重开）②分辨率链内锁定 ③成本线性堆叠 ④不解决长距离一致性 ⑤许可 EU/UK/KR/US 未覆盖

## 进度

### 2026-08-12 第二批：同场景连续动作（用户反馈驱动）
- **用户验收首批**："貌似 chain 好一点"；但换场景看不出衔接（天台→海边），且"注意用同样的片段合成"、"base 动态看起来更好"——重新设计：同场景（天台）连续动作测试，**同一段1** 对比两种段2
- **设计**：段1 结尾 Alya 答应后离开栏杆向左走（动作未完成，留给段2）；段2 开头 Airlock 2s 延续步伐无对话 → Yuki 迎上"太好了！说定了！" → 双人近景"嗯，明天见。"；chain 版时间码 +0.92s（2.0→2.92、4.5→5.42）
- **跑批**（seed 20260812，同配置）：same_seg1 152s（存 h3_ctx_same clip1）/ same_seg2_baseline 151s / same_seg2_chain 167s（存 clip2）；显存 22.2GB 峰值安全
- **seam_probe**：chain mean corr 0.586（16/35>0.6，无锁边）vs baseline 0.504（12/35，1 锁边）——同场景下差距缩小（环境音天然相似），lag trend chain -20.3ms 待查（脚步声瞬态事件干扰相关窗口）
- **freeze**：chain 段2 头部 motion 2.42x 中位——Alya 走步延续，无冻结
- **产物**：output/video/h3_mc_same/（same_base_chain.mp4 + same_mc_chain.mp4，相同段1 拼接）
- **待用户验收**：目视段2 开头 Alya 走步/位置衔接 vs baseline 新起点

### 2026-08-12 跑批完成（首批：两段 MC 链式 vs 基线静态锚）
- **ComfyUI 重启**（队列已空，MC 5 节点注册成功含 SeamProbe）
- **跑批**（scripts/h3_mc_runner.py 新建 + experiments/mc_test/mc_cases.json，ref2va int8 std20 768×448 192帧，seed 20260812，同 agreement_v2 配置）：
  - seg1_rooftop_latent 185s（存 clip_00001.safetensors）
  - seg2_beach_mc22 **168s**（MC ctx=22/audio=24，trim 后 170 帧/7.083s，漂移 0.01ms，存 clip_00002）
  - 显存峰值均 21.9GB 安全；MC patches 安装成功（interior keyframe anchors + keyframe/ref coexistence）
- **seam_probe 对比**（pin 22 帧）：MC 链 mean corr **0.739**（27/35 窗口 >0.6，lag 漂移 -0.10ms/rms 0.09ms）vs 基线静态锚 mean corr **0.277**（0/35 >0.6，lag 锁边）——MC 音频强延续+零漂移，基线完全不锁相
- **level_step**：MC 链接缝 broadband 0.405(+7.5dB) vs 基线 0.501(-9.6dB)——两者均 MARGINAL，跳变源于场景差异（天台静→海边响）非接缝机制问题
- **freeze_detect**：段2 无冻结（头部 motion 0.72x 中位）
- **坑**：runner 运行中编辑不生效（进程内存旧代码）→ untrimmed 音频缺失 → 用新代码单次重提段2（168s 复现成功，MC 可复现）
- **产物**：output/video/h3_mc/（seg1 + seg2_ctx22 + untrimmed.flac + mc_chain_preview.mp4）；基线预览 baseline_chain_preview.mp4
- **待用户验收**：目视接缝（段2 开头是否延续段1 运动/人物位置/音频）+ 与基线对比；通过后跑变体（ctx=5/39/56、audio=0）

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
