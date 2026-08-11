# prompt-audio 任务线：提示词与音效/音乐的关系（2026-08-11 启动）

> 任务线目标：搞清楚 MiniMax H3（本地 ComfyUI）提示词内容与输出音频（环境音/音效/BGM）的关系，
> 找到"要音效不要 BGM"的可靠生产写法。每天做一点，持续关注社区进展。
> 判定权威 = 用户试听（频谱谐波误报多，海浪/风声共振像音乐）。

## 当前定论（2026-08-11 实测，16 条 std20 i2v 8s seed 20260810 768×448）

### 触发矩阵（多镜头 × 描述内容）

| 组合 | 音乐 | 样本 |
|---|---|---|
| 多镜头 × 温情/氛围描述（serene/warm smile/calm/nostalgic） | **有** | V11(3612字Alya)、C1(Yuki)、D2(血精灵) |
| 多镜头 × 舞台/演出场景（spotlight/stage） | **有** | D3、D5（去 warm 词仍触发）|
| 多镜头 × 中性客观描述 | **无** | C2(写实)、C3(血精灵)、C4(街道)、D1(Alya 海边) |
| 多镜头 × 中性 + 丰富音效 soundscape | **无**（只响了一声音效）| D4 |
| 单镜头 × 任意描述（视觉 337-1584 字/音效丰富度均可） | **无** | V6、V10、V12 |
| 动画/写实/场景 任何首帧图本身 | 无关 | D1(Alya 无) vs D2(血精灵有) 证明触发器是描述 |

### 已排除
- 步数（8/20/32 步均无效变：V1-V4）、写法（N/A/none/否定句）、shift_audio（1/3/12）、量化（fp8/int8）、turbo LoRA
- 首帧图角色类型（动画少女/写实/动画法师/街道均不独立触发）
- 官方/API 无任何音频开关参数（API 参数表、diffusers 文档、Runware guide 全查过）
- 架构原理：音频与视频同 packed sequence 联合去噪（33B Omni-Transformer），语音/音效/音乐联合建模不分离（官方设计哲学），CFG 已蒸馏

### 生产结论（快车道可用）
1. **每段单镜头 prompt = 无音乐**（最稳；8s 单镜头慢推镜）——已验证 7 样本：V6/V10/V12/E1-E4（覆盖动画/写实/舞台/全剂量温情词/长视觉/丰富音效，全部无音乐）
2. 多镜头段：**中性客观描述**（不写情绪词、不写舞台/演出语义）= 无音乐（C2/C3/C4/D1/D4）
3. 舞台/演出语义 × 多镜头 = 必触发（D3/D5/E5）；舞台 × 单镜头 = 安全（E2）
4. 温情氛围词（serene/warm smile/calm/nostalgic/twilight mood）× 多镜头 = 触发（V11/C1/D2）；× 单镜头 = 安全（E4 全剂量验证）
5. **重要发现（2026-08-11 AudioSep 分离验证）**：触发音乐态的音轨 ≈ 纯音乐（music 分离轨与混音相关度 0.986-1.0，残差 -44~-71dB 近静音）——环境音/人声/音效被音乐完全替代，不是混合！所以触发时不存在"要音效"的内容，分离工具无混合可分。

## 音频分离工具（2026-08-11 装好）
- AudioSep（LA-Sep）：/home/sean/projects/audio-sep + 权重（ckpt 1.26GB + CLAP 2.35GB）
- 封装脚本：scripts/h3_audio_sep.py（CPU ~7s/8s 音频）
- 用途："音乐+人声/音效混合轨"去音乐保留其余（如 ref2va 带语音场景）；对纯音乐轨无意义
- 备选：FlowSep（同团队 2025，rectified flow，效果更好但依赖重）未装

## 后续方向（待做）
- [x] 温情词"剂量"测试：E4 单镜头+全剂量氛围词=无音乐（单镜头免疫）
- [x] 舞台触发点定位：舞台/演唱会 × 多镜头均触发（D3/D5/E5）；单镜头免疫（E2）
- [ ] 持续关注社区：ComfyUI PR #15375（per-token 视频/音频 latent 噪声掩码）、#15439（任意帧音频 guide 锚定）——合并后可能是"音频静音/控制"接口
- [ ] diffusers `audio_latents` 参数实验（注入静音 latent）——未做
- [x] 后期分离工具验证：AudioSep（LA-Sep）装好并实测——结论：触发态音轨=纯音乐无混合可分；工具留作"音乐+人声"场景（ref2va 带语音）备用。FlowSep（更优）未装
- [ ] 每天扫一遍：r/StableDiffusion H3 帖、HF discussions、ComfyUI issues、X #MiniMaxH3
- [ ] E5 演唱会样本值得留存（舞台×多镜头=触发 的第三个样本）

## 热文件
- 实验产物：ComfyUI/output/video/h3_verify/（V1-V12, C1-C4, D1-D5）
- 脚本：/tmp/h3_verify2_submit.py（支持 shift_audio/ref2va+静音参考）
- 基准 prompt：experiments/shotlist/prompts/黄昏海滨的银发少女_i2va.txt（触发版）、/tmp/h3_sfx_prompt.txt（337字无音乐版）
- 记忆：mem0 comfy-ops 池「H3 BGM 调研 2.0」系列
