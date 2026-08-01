# 04 工作流

> 最后更新：2025-08-01 — 主栈已从 Wan2.1 迁移到 Wan2.2 Lightning 快速视频生成。
> 完整工作流档案（节点结构/参数/结果）见 `.pi/skills/comfyui/references/workflows.md`；本文件是快速索引。

## 工作流文件索引（comfy-ops/workflows/）

| 文件 | 任务 | 说明 |
|------|------|------|
| `wan2.2_i2v_lightning_test.json` | 图生视频（主力）| 17 节点，GGUF Hi/Lo + 4 步蒸馏，480²×33帧 ≈ 10-16s |
| `wan2.2_i2v_standard_multiaction.json` | 图生视频（标准多动作）| 20 步 cfg3.5 shift8，动作幅度大但仅开头单阶段 |
| `anima_t2i_test.json` | ANIMA 文生图 | 10 节点，base 30 步 / turbo 12 步 |
| `anima_alya_768_t2i.json` | Alya 角色 768² 生图 | alisa LoRA@1.0，20 步/euler/cfg4 → I2V 标准起始图 |
| `anima_i2v_test.json` | ANIMA→I2V 管线 | 生图 → 上传 → WanImageToVideo |
| `krea2_t2i_test.json` | KREA 2 文生图 | 8 节点，8 步/cfg1/er_sde |
| `wan2.1_i2v_480p.json` | Wan2.1 对照（UI 格式）| 20 步 ~3 分钟；comfy_client.py 内置构建 |

## 主力工作流速览（wan2.2_i2v_lightning）

### 节点结构（17 节点）
```
UnetLoaderGGUF(High) → ModelSamplingSD3(shift=5) → LoraLoaderModelOnly(Hi LoRA) ─┐
UnetLoaderGGUF(Low)  → ModelSamplingSD3(shift=5) → LoraLoaderModelOnly(Lo LoRA) ─┤
CLIPLoaderGGUF(umt5 Q5, wan) → CLIPTextEncode 正/负 ────────────────────────────┤
VAELoader(wan_2.1_vae) ──────────────────────────────────────────────────────────┤
LoadImage(起始图) ───────────────────────────────────────────────────────────────┴→ WanImageToVideo(480×480, 33帧)
                                                                                      → KSamplerAdvanced(Hi: 4步 0-2) 
                                                                                      → KSamplerAdvanced(Lo: 4步 2-4) 
                                                                                      → VAEDecode → CreateVideo(16fps) → SaveVideo
```

### 关键参数
| 参数 | 当前值 | 说明 |
|------|--------|------|
| shift | 5.0 | Lightning 用 5，标准用 8 |
| 采样 | 4 步, cfg 1.0, euler, simple | Hi 0-2 add_noise / Lo 2-4 |
| cfg | 1.0-1.5 甜点 | 2.0+ 画面改动过大 |
| 分辨率 | 480×480（16 倍数）| 384² 更快但糊 |
| 帧数 | 33（4n+1）| 17=1s / 33=2s / 49=3s / 81=5s |
| 起始图 | 原图分辨率直接跑（512→1792² 清晰度线性 +82%）| 高分辨率底图缩放保留细节 |

### 能力边界（实测）
- **单动作**：4 步蒸馏可靠执行（挥手/飞吻 ✅）
- **多动作序列**：不可靠（丢失，只保留最后一个）→ 需要 81帧+ 或 Pusa/artokun-flow 等管线（MCP 有现成包，未测）

## 已生成结果（output/）

| 位置 | 内容 |
|------|------|
| `output/video/` | 全部视频（alya768_i2v_33f_4step / kiss / cfg 对比 / restest / multiaction…）|
| `output/anima/` | ANIMA 生图（anima_alya_768 等）|
| `output/krea/` | KREA 生图（krea_alya_768 等）|
| `output/compare/` | 风格/模型对比拼图（alya768_compare_anima_vs_krea 等）|
| `output/img_anima/ img_krea/` | 题材测试集（cat/cafe/shrine/galaxy）|
| `output/res_test/` | 分辨率测试 |

## 已测管线状态

- **ANIMA→I2V** ✅：anima_i2v_test.json 已验证（主体居中、帧间差异 22-31 有动作）
- **KREA 2 生图** ✅：krea2_t2i_test.json（8 步/cfg1/er_sde，30s 含加载）
- **Alya 角色 → I2V** ✅：alya_768.png → alya768_i2v_33f_4step_00001_.mp4（2025-08-01 标准产物）
- **多动作** ❌：Lightning 单动作可靠；标准模式幅度大但仅开头（详见 SKILL params.md）

## 操作流程（agent 使用）
1. 提交：`comfyui_enqueue_workflow`（API 格式）或 `comfyui_submit_batch`（批量 sweep）
2. 轮询：`curl http://127.0.0.1:8188/history/<prompt_id>` 解析耗时
3. 查看：`http://localhost:8188/view?filename=<名>&subfolder=<子目录>&type=output`
4. 清理：删文件同时 `POST /history {"delete":[ids]}`；`{"clear":true}` 会全清勿用
5. 更多细节与踩坑：见 `.pi/skills/comfyui/SKILL.md`（agent 手册）及其 references/
