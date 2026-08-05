# 05 会话交接（2026-08-04 深夜，H3 测试完结）

> 本文件是会话起点：新对话从 `docs/INDEX.md` + 本文件 + `.pi/skills/comfyui/SKILL.md` 开始即可无缝继续。
> 结构：activeContext 模板（`docs/05_TEMPLATE.md`）——焦点/环境/变更/活跃决策/模式偏好/待办/链接。
> 已完结的测试细节/大段报告已归档，此处只留指针与交接必需信息。

## 一、当前焦点

MiniMax H3 全流程测试完结（速度/参数/量化/参考已定论）→ 下一步：声音专项评估 + 提示词智能体 + 素材管线整合。

## 二、环境状态（基线，变化时更新）

| 项 | 状态 |
|----|------|
| ComfyUI | ✅ 运行中 http://127.0.0.1:8188（v0.30.0；start.sh = `--enable-assets --use-sage-attention`，**勿加 asset-hashing**） |
| 模型栈 | ✅ Wan2.2 I2V Lightning + Bernini-R int8 + ANIMA/KREA + **MiniMax H3 全家桶** |
| MiniMax H3 | ✅ fl2va/ref2va pruned int8 + fl2va fp8_scaled + qwen3vl-32B nvfp4_awq TE + 双 VAE（GPU 架构定论：4090 用 fp8，30系用 int8） |
| mem0 | ✅ HTTP 常驻（http://127.0.0.1:8899/mcp） |
| 队列 | ✅ 空闲 |

## 三、最近变更（已归档项只留指针）

### 08-03：H3 落地首测（详情见 git 历史 + skill nodes/workflows 分册）
- 4 文件 42.5GB 就位（hf-mirror + `HF_HUB_DISABLE_XET=1`）；ComfyUI 升 0.30
- **nvfp4_awq TE 15.7GB 可全量入显存**；低 VRAM 分载 6.1GB offload
- 工作流：`workflows/minimax_h3_{i2v,t2v}_api.json`（API 格式可直接跑）+ `minimax_h3_r2v.json`（官方全内联模板，参考用）
- 首测成片：I2V/T2V 各 1 条（1344×768，AAC 32kHz 音频）✅

### 08-03/04：H3 夜间系统化测试（完整数据 → `docs/09_h3_test_plan.md`）
- **速度矩阵定论**：768×448 = 115/234/403s，1024×576 = 165/295/503s（5/10/15s）；steps 14 省 27%
- **管线定论已固化进 skill params 分册**（见四）
- 产物：output/video/ 下 h3_* 系列 ≈46 条 + output/review/ 对比 56 条（A-G + H_audio + I_sg_mc 分组语义命名）
- 08-04 晚已跑提示词 8 变体/首尾帧/量化等补测（docs/09 补测批 A/B/C）

### 文档体系（长期约定，勿丢）
- `references/nodes.md` 节点速查册：来源分层标签 `[官方]/[社区]/[本地实测]`；搭新工作流先查它
- `learning.md §3.5` 新节点落地流程：读源码→读官方用法→最小验证→沉淀
- `params.md` 无标签 = 本地实测；官方/社区值只作基线
- 提示词智能体完整方案 → `docs/08_h3_prompt_agent.md`（官方六段式已开源，推荐自建 LM Studio Qwen3.6-35B 视觉 + pi skill）

## 四、活跃决策（最容易丢，最重要）

### 已定
- **H3 成片档**：fp8 + sage + 20 步 @ 1024×576（5s≈2min / 10s≈5min / 15s≈8min）
- **H3 快速抽卡档**：fp8 + sage + MC(MotionCache) + 14 步 @ 768×448（~1.5min/条；MC 音频劣化，抽卡可接受）
- **sage/MC 对画面主体零影响**（三状态同 seed 对比）；**SageAttention 必须开**（10s+ 快 40-48%）；MC 音频劣化
- **H3 无 cfg**（BasicGuider 等价 cfg=1，CFG-distilled）；**显存策略 = 低 VRAM 分载**，未用 lowvram patch
- **4090 用 fp8、30系用 int8**（量化架构定论，同速）；GGUF 暂不可行
- **Ref2VA 视频参考必须 CLIPLoader device="cpu"**（否则显存打爆卡死）；单图参考零惩罚
- 文本编码器只用 nvfp4_awq（int8 27GB 超显存，别下）

### 待决
- **声音专项**：sage/MC 对音频频谱影响量化、成片档声音基线（h3_audio/ 4 条待听测）
- 提示词 8 变体目视评估（p3 六段式/p6 场景/p7 中文/p8 声音）
- steps 14 vs 20 画质确认；FL2VA 首尾帧双图价值
- Ref2VA 21GB 实战价值验证（下载已就位）

## 五、模式与偏好（反复出现的坑）

- **跑批前先重启 ComfyUI 清内存**（内存压力下采样慢近 2 倍：9.5 vs 4.5s/it）——铁律
- 手动启动别漏 `--use-sage-attention`（10s+ 慢 40-90%）；勿加 `--enable-asset-hashing`（视频多时 RSS 33GB）
- 杀进程先 pgrep 拿 PID（pkill -f 会误杀自己 shell）
- H3 下载：`HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 hf download ...`（Xet 401 坑，直连不用代理）
- 跑工作流：`python3 run_workflow.py workflows/<xxx>_api.json` 或 MCP comfyui_enqueue_workflow
- 参数/踩坑经验实时 retain 到 mem0（comfy-ops 池），不堆文档；结论性条目强制日期+条件

## 六、下一步（按优先级）

1. **声音专项**：听测 h3_audio/ 4 条（sage/MC 音频劣化表现、成片档声音基线）
2. **提示词 8 变体目视评估**：p3 六段式 / p6 场景 / p7 中文 / p8 声音响应
3. **提示词智能体**：按 docs/08 方案启动（LM Studio Qwen3.6-35B 视觉 + 官方六段式指南 `/tmp/guide_ref.md`）
4. **素材管线整合**：抽卡档选片 → 成片档出片一键化
5. skill workflows 分册补 H3 工作流档案（3 个 API 工作流已就位）
6. **记忆整理（顺手级）**：H3 速度旧条目（mem0 id `00d44594`）与 docs/09 最终矩阵并存——recall 命中时 update 补"含加载"条件

## 七、常用链接/命令

- H3 成片：`http://localhost:8188/view?filename=<文件名>&subfolder=video&type=output`（output/video/）
- H3 工作流：`python3 run_workflow.py workflows/minimax_h3_i2v_api.json`
- 测试全数据：`docs/09_h3_test_plan.md`；提示词智能体：`docs/08_h3_prompt_agent.md`
- 对比成片：output/review/（56 条，A-G + H_audio + I_sg_mc 分组语义命名）
