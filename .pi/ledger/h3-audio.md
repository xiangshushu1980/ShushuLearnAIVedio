# H3 音频/音乐结论谱系

> 音频定论演进史。规则见 README.md。append-only。

## 条目索引

| C-ID | 主题 | 状态 | 备注 |
|---|---|---|---|
| C-20260816-11 | H3 BGM 触发条件 | ✅现行 | 三因素 + 触发矩阵 |
| C-20260816-12 | 音乐先验恒定 + 触发态纯音乐 + 去 BGM 工具 | ✅现行 | 否定写法无效 / demucs 定案 |
| C-20260816-13 | Ref2VA 纯音频参考可用 | ✅现行 | 语音生成必要条件 |
| C-20260816-14 | H3 音频劣化归因（sage 零影响 / MC 跳步） | ✅现行 | |
| C-20260917-01 | Breeze TTS 2 标准流程与运行模式（BF16/cuda_graphs） | ✅现行 | GPU 主流；CPU 为兜底 |
| C-20260917-02 | Breeze TTS 2 生成耗时基线（GPU vs CPU） | ✅现行 | 同参对照 |
| C-20260917-03 | Doctor Wang 声音克隆产出与参数 | ✅现行 | 含情绪增强版 |

---

### C-20260816-11 | H3 BGM 触发条件
- 状态：✅现行（valid_from 2026-08-10；矩阵 2026-08-11）
- 现行值：**i2v + 长 prompt（IR 级 ~340+ 字）+ 8s（192 帧）三因素缺一不可**触发 AI 氛围音乐；t2v 任意组合 / i2v 短 prompt 任意时长 / i2v 5.2s 段均无；多镜头 × 温情/氛围词或舞台/演出语义 = 必触发；多镜头 × 中性客观描述 = 无；单镜头 × 任意描述 = 无；首帧图角色类型无关（触发器是描述内容）；判定必须试听（频谱谐波误报多）
- 时间线：
  - 2026-08-10 提出：i2v+长prompt+8s 三因素缺一不可、同 seed 重跑可复现非随机；生产含义=快车道（i2v+turbo8+8s+IR长prompt）必带 AI 氛围音乐、5s 段无（来源任务 h3-prompt-agent）
  - 2026-08-11 修正：触发矩阵细化（多镜头×温情/舞台=有、×中性=无；单镜头=无；首帧图无关；16 条 std20 实测）（来源任务 prompt-audio）
- 证据锚：.pi/tasks/prompt-audio/progress.md（触发矩阵）/ .pi/tasks/h3-prompt-agent/progress.md（BGM 触发调查）

### C-20260816-12 | 音乐先验恒定 + 触发态音轨性质 + 去 BGM 工具
- 状态：✅现行（valid_from 2026-08-11；工具定案 2026-08-12）
- 现行值：①**否定/静音/N/A 写法全无效**（音乐先验与 prompt 解耦：N/A、显式否定句、全静音指令、极端否定在 8s 触发组合下全无效）；②**触发态音轨 ≈ 纯音乐**（music 分离轨与混音相关 0.986-1.0，残差 -44~-71dB 近静音——环境音/人声/音效被音乐完全替代，无混合可分，不存在"要音效"内容）；③**去 BGM 正解 = demucs htdemucs_6s**（去音乐=保留 vocals+other；G1-G5 复杂条目 + F2 演唱会用户试听"效果都很好"）；AudioSep/FlowSep 淘汰
- 时间线：
  - 2026-08-10 提出：prompt 级去音乐 4 写法全无效（N/A/否定句/静音指令，H3 音乐先验与 prompt 解耦），后期分离待定（来源任务 h3-prompt-agent，git ac1d28f）
  - 2026-08-11 修正：触发态音轨≈纯音乐（AudioSep 分离验证 0.986-1.0）；"静音"=场景无内容非 N/A 功效、音乐先验恒定（修正 nobgm 结论；来源任务 h3-prompt-agent，git b5fe763）
  - 2026-08-12 定稿：demucs 6s 工具定案（G1-G5+F2 实测）；AudioSep/FlowSep 淘汰（复制混音相关 0.99 / 输出能量低 20dB+内容疑似幻觉，定位是任意声源文本提取非音乐分离；来源任务 T-20260812-06）
- 证据锚：.pi/tasks/prompt-audio/progress.md（工具定案节）/ scripts/h3_demucs.py / scripts/h3_audio_sep.py / git b5fe763、ac1d28f

### C-20260816-13 | Ref2VA 纯音频参考可用
- 状态：✅现行（valid_from 2026-08-11）
- 现行值：仅 ref_audios（无图无视频）20 步成功生成——音频 -11.3 LUFS 有真实语音（无静音段）vs 同 prompt 无音频参考 -31.3 LUFS 几乎静音 → **纯音频参考今天起可用且是语音生成必要条件**（README 放宽实测验证）
- 时间线：
  - 2026-08-11 提出：T3 实测（来源任务 h3-today-testing）
- 证据锚：.pi/tasks/h3-today-testing/progress.md（T3）

### C-20260816-14 | H3 音频劣化归因（sage 零影响 / MC 跳步）
- 状态：✅现行（valid_from 2026-08-05）
- 现行值：sage 对音频零影响（响度差 0.2 LU 不可辨）；"声音变弱"100% 归因 MC 跳步（联动 C-20260816-05）
- 时间线：
  - 2026-08-05 提出：sage 音频对照实测（来源任务 h3-patch-test）
- 证据锚：params.md §关键参数（MotionCache 音频劣化）/ docs/09_h3_test_plan.md（补测批 D）

### C-20260917-01 | Breeze TTS 2 标准流程与运行模式
- 状态：✅现行（valid_from 2026-09-17）
- 现行值：**宿主 ComfyUI + `ComfyUI-Breeze-TTS-2` 节点 + bf16(best quality) + attention=sdpa + decode=cuda_graphs + 输出 24kHz 单声道 FLAC/WAV**；单人为 `BreezeTTS2Speaker`、多人为 `BreezeTTS2MultiSpeaker`。**device=cuda 为 GPU 主流路径**；`device=cpu, decode_mode=eager` 为可行兜底（CPU 自动把 bf16 回退 fp32）。Flash Attention 在 ComfyUI CUDA 13 环境未安装（sdpa 为当时选择）；连续任务完成后停止/重启 ComfyUI 释放显存
- 已知限制：**int8 hybrid 权重当前缺失**；参考文本留空会触发 Whisper 自动转写，而本机 `openai_whisper-large-v3-turbo` 模型不完整 → **测试必须提供精确 reference_text 并关闭自动转写**
- 时间线：
  - 2026-09-17 提出：CPU 强制路径跑通（两句中文 4.36s，见 C-20260917-02）；GPU VoiceDirection 路径跑通（来源任务 T-comfy-ops-breeze-docker）
- 证据锚：.pi/tasks/T-comfy-ops-breeze-docker/progress.md（后续 TTS 标准流程节）/ mem0 1b5fed07、50531ceb

### C-20260917-02 | Breeze TTS 2 生成耗时基线（GPU vs CPU）
- 状态：✅现行（valid_from 2026-09-17）
- 现行值（ComfyUI 0.36.0，execution_start→success 口径）：
  | 场景 | 模式 | 产物 | 耗时 | 实时倍率 |
  |---|---|---|---|---|
  | 两角色克隆 + MultiSpeaker，两句中文 | device=cpu, eager | 4.36s / 24kHz mono | 64.019s | ~14.7× |
  | 双人克隆 + MultiSpeaker，8 轮中文对话 | device=cpu, eager, bf16 | 18.92s / 24kHz mono | 245.203s | ~13.0× |
  | VoiceDirection（对话/口播） | device=cuda, sdpa, cuda_graphs, cfg_scale=2.0 | 82.48s / 24kHz mono | 131.289s | ~1.6× |
  | VoiceDirection 情绪增强版 | device=cuda, sdpa, cuda_graphs, cfg_scale=2.8, seed=20260918 | 74.40s / 24kHz mono | 107.935s | ~1.45× |
- 结论：**CPU 约 13-15× 实时，GPU 约 1.5-1.6× 实时**（GPU 快约一个数量级）；双人克隆场景中节点 1-3 命中缓存，实际耗时主要来自 MultiSpeaker 的 CPU 生成
- 时间线：
  - 2026-09-17 提出：CPU/GPU 四条基线同批实测（来源任务 T-comfy-ops-breeze-docker）
- 证据锚：ComfyUI output/h3_digital_human/ 下对应 FLAC / mem0 50531ceb、4db724ec、ecbb1491、2c872640

### C-20260917-03 | Doctor Wang 声音克隆产出与参数
- 状态：✅现行（valid_from 2026-09-17）
- 现行值：源 `ComfyUI/input/wang_audio/Wang.mp3`（145.93s）→ **取开头 20s 转 24kHz mono 作参考音频**，用 faster-whisper large-v3 转写；目标稿 82 秒。产出两条：① 基准版（cfg_scale=2.0）82.48s / 131.289s 耗时；② **情绪增强版（cfg_scale=2.8, seed=20260918）74.40s / 107.935s 耗时**，加入共情/疑问/热情/理性分段/鼓励/结尾行动引导
- 产物路径：`ComfyUI/output/h3_digital_human/doctor_wang_voice_direction_gpu_20260917_00001.flac`、`doctor_wang_voice_direction_gpu_emotional_20260917_00001.flac`
- 时间线：
  - 2026-09-17 提出：基准版与情绪增强版同批产出（来源任务 T-comfy-ops-breeze-docker）
- 证据锚：mem0 7ede5d49、ecbb1491、2c872640、1f3ec4cc、996518e1
