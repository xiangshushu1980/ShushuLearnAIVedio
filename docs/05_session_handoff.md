# 05 会话交接（2026-08-04/05）

> 本文件是新会话起点：INDEX → 本文件 → memory_recall → 按需读分册。结构按 05_TEMPLATE.md。
> 旧版（08-03 首测细节 + 08-04 夜间测试全量报告）已归档：git 历史 + docs/09_h3_test_plan.md（全量数据）+ docs/10_h3_batch_optimization.md（本轮技术分析）。

## 一、当前焦点

MiniMax H3「受提示词控制视频」快速管线：测试与速度矩阵已定论（08-04），本轮完成 fl2va 机制/缓存/批量优化分析（docs/10）→ **下一步：固定基线 + 提示词智能体落地**。

## 二、环境状态（已就绪）

| 项 | 状态 |
|----|------|
| ComfyUI | ✅ 运行中 http://127.0.0.1:8188（0.30.0，start.sh: --enable-assets + --use-sage-attention；asset-hashing 已移除）|
| 模型栈 | ✅ Wan2.2 Lightning + Bernini-R int8 + ANIMA/KREA + MiniMax H3 全套（fl2va int8 21GB + nvfp4 TE 15.7GB + 双 VAE）|
| 缓存 | 默认 --cache-ram（RAMPressureCache，进程内存，重启清空）|
| mem0 | ✅ HTTP 常驻（http://127.0.0.1:8899/mcp）|
| 队列 | ✅ 空闲 |

## 三、最近变更（摘要，细节进 git 历史/专题文档）

- **08-03**：H3 落地首测（下载/ComfyUI 0.30/首测 I2V+T2V 带音频）
- **08-03 晚**：提示词增强方案调研完成 → `docs/08_h3_prompt_agent.md`（官方六段式格式已开源 → 推荐自建提示词智能体）
- **08-04**：系统化测试 46 视频全量数据 → `docs/09_h3_test_plan.md`（速度矩阵/steps/提示词/Ref2VA/量化/MotionCache/目视反馈）
- **08-04/05（本轮）**：fl2va 技术分析 → `docs/10_h3_batch_optimization.md`（TE 机制/80s 加载成本/缓存机制/两阶段批量方案）

## 四、活跃决策（最重要，勿丢）

### 已定
- **分辨率甜点**：1024×576（画质均衡 5s≈165s）| 768×448（快速批量 5s≈115s）；1344×768 10s+ 非线性飙升不推荐。**用户目标固定分辨率迭代 → 待固化 1024×576 为基线**
- **steps 双档**：14 快速（121s 省 27%）/ 20 成片（声音明显更好；眼睛 14-16 崩）
- **量化 int8**（fp8 采样同速、冷加载更慢，画质待多案例统计）
- **MotionCache 默认不启用**（画质差异小但音频明显变弱，待音频专项）
- **TE 只用 nvfp4_awq 15.7GB**（int8 27GB 放不下）；显存策略=低 VRAM 分载；Ref2VA 视频参考必须 CLIPLoader device="cpu"
- **fl2va 机制定论**（docs/10）：TE=Qwen3VL-32B 完整前向（per-token hidden states）；TE 权重加载 ~80s 占任务 40-60%；**同 prompt 多 seed 批量自动缓存免 TE**；API 化 TE 不可行
- 测试纪律：**跑批前重启 ComfyUI 清内存**（内存压力采样慢近 2 倍）

### 待决
- **两阶段流水线**（docs/10）：不同 prompt 批量每任务付 80s TE 加载 → 是否实现（N≥3 划算）；cond 落盘格式待验证
- **fp8 vs int8 多案例画质统计**（2-3 条即可定论）
- 提示词智能体实现方式（docs/08 方案，LM Studio Qwen3.6-35B 视觉 + pi skill）
- SageAttention 对 H3 是否生效（部分层 dtype 回退属正常，需验证实际增益）
- 中文 `<d>` 标签专项、声音细粒度边界（鸟鸣等弱指令）、15s 动作上限

## 五、模式与偏好

- **H3 下载**：`HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 hf download ...`（Xet 401 坑）
- **跑工作流**：`python3 run_workflow.py workflows/minimax_h3_i2v_api.json` 或 MCP comfyui_enqueue_workflow
- **批量**：同 prompt 多 seed 直接队列跑（fl2va 自动缓存）；不同 prompt 批量先看 docs/10 两阶段方案
- **参数/踩坑经验实时 retain 到 mem0**（comfy-ops 池），不堆文档；handoff 只放恢复上下文必需信息
- H3 成片查看：`http://localhost:8188/view?filename=<名>&subfolder=video&type=output`

## 六、下一步（按优先级）

1. **目视评估收尾**（docs/09 待办：8 prompt 变体 / steps / fp8-int8 画质）→ 固化默认参数（1024×576 × steps14/20 × int8）→ 更新 comfyui skill params 分册
2. **提示词智能体落地**（docs/08，核心杠杆：目标=受提示词控制，提示词主导 > seed 锚定）
3. **两阶段流水线**（docs/10，确认不同 prompt 批量需求后实现）
4. **fp8 多案例统计**（2-3 条定论量化选择）
5. 专项：中文 `<d>` 标签、声音边界、15s 动作上限、MotionCache 音频对比

## 七、常用链接/命令

- H3 成片：`http://localhost:8188/view?filename=<名>&subfolder=video&type=output`
- H3 工作流：`python3 run_workflow.py workflows/minimax_h3_i2v_api.json`
- 专题文档：docs/08（提示词智能体）/ docs/09（测试全量）/ docs/10（fl2va 与批量优化）
- 节点源码：`ComfyUI/comfy_extras/nodes_minimax_h3.py` / `comfy/text_encoders/minimax.py` / `comfy_execution/caching.py`
