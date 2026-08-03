# 05 会话交接（2026-08-03）

> 本文件是会话起点：新对话从 `docs/INDEX.md` + 本文件 + `.pi/skills/comfyui/SKILL.md` 开始即可无缝继续。
> 结构：activeContext 模板（`docs/05_TEMPLATE.md`）——焦点/环境/变更/活跃决策/模式偏好/待办/链接。
> 上次交接（08-02）已完成项归档，本次聚焦 08-03 的 MiniMax H3 落地首测。

## 一、当前焦点

MiniMax H3 落地首测（已完成）→ 下一步进入画质验证与 Ref2VA 评估。

## 二、环境状态（已就绪）

| 项 | 状态 |
|----|------|
| ComfyUI | ✅ 运行中 http://127.0.0.1:8188（**已升级 0.30.0**，start.sh 含 --enable-assets + --use-sage-attention）|
| 模型栈 | ✅ Wan2.2 I2V Lightning + Bernini-R int8 + ANIMA/KREA + **MiniMax H3（新）** |
| MiniMax H3 | ✅ fl2va pruned int8 (21GB) + qwen3vl-32B nvfp4_awq TE (15.7GB) + 视频/音频 VAE，4 文件 42.5GB 全部就位 |
| mem0 | ✅ HTTP 常驻（http://127.0.0.1:8899/mcp）|
| 队列 | ✅ 空闲 |

## 三、最近变更（08-03 核心成果）

### 1. MiniMax H3 落地首测（重点）✅
- **模型**：海螺开源全模态音视频生成（文本/图/参考 → 视频+原生立体声音频，24fps，768p 短边，4-15s）
- **下载**：Comfy-Org/MiniMax-H3 4 文件 42.5GB（hf-mirror + `HF_HUB_DISABLE_XET=1` 绕过 Xet 401；~8MB/s，1.5h）
- **ComfyUI 升级 0.30**（原 07-29 无 H3 节点；需 v0.30 `feat: Support MiniMax-H3`）
- **硬件匹配（4090 24GB）实测**：可行但吃紧
  - 扩散模型：13.9GB 显存 + 6.1GB offload（低 VRAM 分载，无 lowvram patch）
  - **nvfp4_awq 文本编码器 15.7GB 可全量入显存**（int8 版 27GB 放不下，别下）
  - 1344×768×124帧(5.2s) 20步：I2V 241s（~9.5s/it），T2V 353s
- **首测结果**：I2V `video/minimax_h3_i2v_first_00001_.mp4`（Alya 起始图→花田夕阳）✅ / T2V `video/minimax_h3_t2v_first_00001_.mp4`（山湖晨雾）✅
  - 均 1344×768 h264 + **AAC 32kHz 立体声音频** ✅
- **工作流**：`workflows/minimax_h3_i2v_api.json` / `minimax_h3_t2v_api.json`（15 节点 API 格式）
  - 结构：UNETLoader→BasicGuider+BasicScheduler(simple,20步)→KSamplerSelect(res_multistep)→SamplerCustomAdvanced；MiniMaxH3ImageToVideo(clip,vae,prompt,w,h,length,first_frame)；VAEDecode+VAEDecodeAudio→CreateVideo(fps24)→SaveVideo
  - **无 cfg**（BasicGuider 等价 cfg=1，CFG-distilled）；无 MiniMaxH3SigmaShift（模板没用，走默认）
  - 官方模板 r2v 全内联可参考：`workflows/minimax_h3_r2v.json`（i2v/t2v 是 subgraph 格式不能直接跑）
- 节点源码：`ComfyUI/comfy_extras/nodes_minimax_h3.py`（H3 节点 schema/参数权威参考）

### 2. 其他
- 显存 100M 占用排查：**mem0 HTTP 服务**（PID 187237，2 个 /dev/dxg 句柄）占 ~122MiB 空转，无碍
- 经验/踩坑已存 Mem0（comfy-ops + global 池）

## 四、活跃决策（最重要，勿丢）

### 已定
- **H3 文本编码器只用 nvfp4_awq 15.7GB**：int8 版 27GB 超 4090 显存，别下
- **H3 无 cfg**：BasicGuider 等价 cfg=1（CFG-distilled 模型），不要加 cfg
- **显存策略 = 低 VRAM 分载**（6.1GB offload），未用 lowvram patch
- **基线参数**：1344×768 × 124帧(5.2s) × 20步 × res_multistep
- H3 工作流用 API 格式（i2v/t2v 官方是 subgraph 不能直接跑，r2v 全内联可参考）

### 待决
- **steps 20 是否可降**？（trained 范围 124-362 帧）
- **Ref2VA 21GB 是否下载**（价值 vs 显存 vs 下载成本）
- **SageAttention 对 H3 是否生效**：start.sh 带 --use-sage-attention，但部分层 dtype 不符自动回退（日志有提示属正常）——需验证实际效果
- 首尾帧双图（FL2VA first_frame + last_frame）测试

## 五、模式与偏好

- **H3 下载**：`HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 hf download ...`（Xet 401 坑已验证，hf-mirror 直连不用代理）
- **跑工作流**：`python3 run_workflow.py workflows/minimax_h3_i2v_api.json` 或 MCP comfyui_enqueue_workflow
- **参数/踩坑经验实时 retain 到 mem0**（comfy-ops 池），不堆文档；本文件只放恢复上下文必需信息
- H3 成片查看：`http://localhost:8188/view?filename=<文件名>&subfolder=video&type=output`（output/video/ 目录）

## 六、待办（新对话优先级）

1. **H3 画质/动作验证**：看 I2V/T2V 成片质量；对比 Wan2.2 Lightning（动作丰富度/一致性/音频价值）
2. **H3 Ref2VA 落地**：多模态参考（≤9图+≤3视频+≤3音频）— 21GB ref2va pruned int8 未下载；`workflows/minimax_h3_r2v.json` 模板已备
3. **H3 首尾帧（FL2VA 双图）**：first_frame + last_frame 输入测试
4. **H3 参数探索**：steps 20→更少？分辨率 768 短边下限；length 124→更长时间；ref_image_size match/max
5. **SageAttention 对 H3 效果**：验证回退是否影响质量
6. 素材库/Bernini 待办继承（见上期）

## 七、常用链接/命令

- H3 成片：`http://localhost:8188/view?filename=<文件名>&subfolder=video&type=output`（output/video/ 目录）
- H3 工作流：`python3 run_workflow.py workflows/minimax_h3_i2v_api.json`（或 MCP comfyui_enqueue_workflow）
- 下载 H3 其他变体：`HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 hf download Comfy-Org/MiniMax-H3 --include "..." --local-dir models`
