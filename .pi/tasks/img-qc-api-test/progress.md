# 任务进度：img-qc-api-test（ComfyUI 出图质检 - 线上便宜 VL API 选型与测试）

> 项目级私有进度（只有本任务线读写）。共享状态在 mem0 [STATE]，不写在这里。

## 任务
- 目标：为 ComfyUI 出图后的客观质检（内容/文字/崩图/比例）选定一个便宜可用的线上图片识别 API；测功能、延迟、费用；与本地 LM Studio（Qwen3.8-27B 多模态，免费）互补分层
- 当前状态：🟡（测试矩阵完成，结论已落 docs/24；剩余项低优先）
- 我负责的文件区：`.pi/tasks/img-qc-api-test/`、测试脚本（拟 `scripts/img_qc_test.py`）

## 背景（2026-08-16 定）
- ComfyUI 出图后 LM Studio 主模型做不了实时质检（互斥显存调度，谁干活谁独占），故客观质检走线上便宜 API；主观审美仍用户判断
- 候选：①阿里云 DashScope qwen-vl 系（国内直连快、便宜，需 DASHSCOPE_API_KEY）②deepinfra VL（海外，直连不通，需代理）③qwen-mm-plugins-api（MCP server 未接入 + 需 key）
- 现状盘点（2026-08-16 本会话已解决）：qwen-mm-plugins-api 已接入 MCP 网关（tag v1.0.3，12 工具）；DASHSCOPE_API_KEY + 专属 MaaS 端点已写入 ~/.qwen-mm-plugins/config（600 权限，key 不进 git/记忆）；VL 默认 qwen3-vl-flash（最省档，实测看图出中文描述通过）；deepinfra 弃（直连不通）

## 进度日志（append-only）
### 2026-08-16
- 任务启动。API 现状盘点完成（见背景）。待用户定：用哪家 API + 提供 key
- 测试样本候选：output/compare/text_ctrl3_matrix.png、h3_facerefine_T1.png（ComfyUI 真实出图）

### 2026-08-16（续，本会话）
- 用户拍板选型与纪律：本地优先、线上只看图（DeepSeek V4 视觉补充）、严格最省档 qwen3-vl-flash、贵档需确认、听用本地 whisper、Omni 五段式报告不需要
- API 侧全部就绪（见背景更新）；开始第一步联测：ComfyUI 生图 → vision_chat 识别比对

### 2026-08-16（首次联测通过）
- anima_alya_768_t2i 生图（seed 42，lora 修正 anima-highres-aesthetic-boost 强度 0），12s 出图 → output/anima/anima_apirecog_test_00001_.png
- vision_chat(qwen3-vl-flash) 识别：发色银白/瞳色赤红/黑色哥特裙/雪夜森林 全部与 prompt 对上，描述极详细
- 用量：prompt 608 tok（其中图 578）+ completion 947 tok = 1555 tok/张；按 flash 档估算 ~0.003 元/张（可忽略）
- 踩坑：workflow 的 LoraLoaderModelOnly 里 lora_name 指向已删除的 alisa_mikhailovna_kujou-roshidere-ana-soralz.safetensors → /prompt 400；脚本 img_qc_test.py 加 --lora/--lora-strength 覆盖解决

### 2026-08-16（二，测试矩阵全闭环）
- 首次联测通过后（见上），本会话完成剩余测试：
  - ✅ OCR（qwen3.5-ocr）text_ctrl3_matrix.png → "MIDNIGHT CAFE" 提取正确（无空间定位能力）
  - ✅ 崩图判定双向验证：好图 h3_facerefine_T1 → 全 PASS 可用；崩图 attn3way_dance（6 格 Sol-Attn）→ 逐格检出全部缺陷总体需重跑（与已知崩坏吻合）
  - ✅ 视频识别：vision_chat videos 参数 + video_max_frames=6 → 帧采样正常（无音频符合听用本地）
  - ✅ 写实图识别：krea_scene_city → PASS 描述吻合
  - ✅ 生图→识别对照：krea2_t2i 生图 20s → 识别 PASS；⚠️ 发现 krea2_t2i_test workflow 实际动漫系 checkpoint（Q 版狐娘，photorealistic 未生效）
- 费用实测：单图 ~1500 tok <0.001 元/张、6 格大图 ~4000 tok、视频 6 帧 ~1900 tok（单价锚 $0.022/M in + $0.215/M out）→ 可忽略
- 延迟实测：单次调用 20-30s（含上传+推理），适合异步批处理不适合交互式
- **选型定论落 docs/24_vl_qc_api.md**（+INDEX 同步）：qwen3-vl-flash 最省档 + qwen3.5-ocr 文字 + vision_chat videos 视频，质检 prompt 模板已固化

## 下一步（剩余低优先，可新会话继续）
1. 写实人脸样本测试（需换写实 checkpoint workflow；动漫主线非核心）
2. 质检脚本化：将质检 prompt + 批量识别封装为 scripts/img_qc_check.py（对接 img_qc_test.py 输出）
3. 接入 ComfyUI 出图后自动质检流程（跑批收口时）

## 关键链接
- 相关 skill：qwen-mm-plugins-api（Cloud VL）、qwen-mm-plugins-core（本地读图）
- 相关文档：docs/ 音频/出图质检相关分册（待定位）
