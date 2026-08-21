# T-comfy-ops-16 — MiniMax Music 3 测试：评估替代本地音乐方案

## 任务目标
用 ComfyUI v0.33.1 原生支持的 MiniMax Music 3，评估能否替代本地现有音乐方案（Qwen-TTS 语音链 / MV 外部音乐）。

## 需求（用户 08-20 给）
- **风格**: WOW（魔兽/MMO 冒险）史诗配乐
- **主题**: 新手村蜕变：启航 → 观察 → 冒险 → 生存 → 胜利 → 劫后余生 → 振奋 → 期待
- **情绪曲线**: 从平静启程 → 渐强冒险 → 危险生存 → 凯旋胜利 → 余韵 → 振奋展望

## 模型选择决策（拍板依据）
- 参照独立实测（RTX 5080 16GB / v0.33.1，60s 歌）：FP16 比 INT8 更快（376s vs 416s），VRAM 相当（15.9GB vs 15.9GB）。差值小 + FP16 更快 → 用户拍板**成片挡 FP16**。
- 选文件：
  - diffusion_models/minimax_music3_dit_fp16.safetensors (4.58GB)
  - text_encoders/minimax_music3_text_encoder_pruned_bf16.safetensors (15.56GB)
  - vae/minimax_music3_dav.safetensors (0.20GB)
  - 合计 ~20.3GB（hf-mirror 下载）
- 时长估算: ~6 秒生成/音频1秒（FP16）；目标 60s 约 6 分钟引擎耗时。

## 进度
- [x] ComfyUI 核心更新至含 Music3 支持（T-comfy-ops 当天）
- [x] 模型文件清单确认（Comfy-Org/MiniMax-Music-3）
- [x] 生成时间/VRAM 实测调研（FP16 拍板）
- [ ] 下载模型（20.3GB hf-mirror）
- [ ] 搭 Music3 测试工作流（歌词+风格 → 歌曲 demo）
- [ ] 生成 demo、听评、与现有音乐方案对标
- [ ] 结论落盘 + 归档

## 2026-08-21 进展（下载进行中）
- 模型方案最终确认：dit_fp16(4.58GB) + TE_pruned_int8(8.57GB) + DAV(0.19GB) = 13.34GB
  - 依据：官方模板 audio_minimax_music_3.json 即此组合；日本实测(v0.33.1/5080)FP16比INT8快约10%(376s vs 416s)且VRAM相当；24GB 4090 无压力
- hf-mirror 下载中（curl 断点续传），dit_fp16 → TE → DAV 顺序
- 已构造标准 API workflow: minimax_music3_api_template.json
  - UNETLoader+CLIPLoader(type=minimax)+VAELoader → MiniMaxMusic3TextEncode → EmptyMiniMaxMusic3LatentAudio → KSampler(30步/euler/simple/cfg1.7) → VAEDecode → SaveAudioAdvanced(mp3)
  - 参数照官方模板：cfg_scale=1.7, top_k=50, steps=30, cfg=1.7
- 测试输入已写：wow_newbie_caption_lyrics.md (WOW 新手村史诗配乐，情绪线 启航→观察→冒险→生存→胜利→劫后余生→振奋→期待)
- 待：模型下完 → 填充 caption/lyrics → 提交工作流 → 听评

## 2026-08-21 实测 + 社区经验（用户听评完）
### v1 试听反馈（60s，seed 20260821）
- 中文男/英文女固定声线：很好 ✅
- 对唱一男一女交替：✅
- Chorus 转 epic：✅
- Bridge 哼唱（童声）：**丢失 ❌**（无哼唱）
- 结尾唢呐：**没有，唢呐反而在开头 24s** ⚠️
- 用户核心观察：**Music3 按自己理解排布结构，不是严格按用户的节奏/段落顺序** —— 符合官方定位

### 官方/社区经验（查证来源：HF 模型卡 README + 官方 blog + music-caption-rewriter skill + prompt_guide）
**官方定论（HF README 原话）**：
"Section tags and music descriptions provide GENERATIVE CONTROL rather than STRICT SYMBOLIC GUARANTEES. The generated tempo, key, instrumentation, lyrics, and song structure may not always match every requested detail."
→ 段落标签/描述是"生成式控制"非"精确符号保证"，节奏/调性/配器/结构不会精确匹配。

**架构根源**：8B Global LLM（Qwen3.5-8B 初始）+ 0.6B Local LLM，**逐帧预测** RVQ 语义 token，全局-局部混合建模长程结构（"song-level structural stability"）。所以它是帧级 AR 生成，不是时间轴编排器。

**官方推荐的结构控制方式**：
1. 歌词 section tags（[Intro]/[Verse]/[Chorus]/[Bridge]/[Outro]...）——真正的结构指令
2. music-caption-rewriter skill：把乐器/人声指令**挂到具体 section 标签上**（section-local directives），而不是全局 Arrangement 段落描述（教的方法：乐器指令应作为 section 局部指令，能改变局部配器但不换全局曲风）
3. Caption Arrangement 部分用"情绪/乐器演变"时间描述（fine-grained temporal descriptions）

**我的 v1 prompt 犯的错（可解释用户的哼唱丢失+唢呐乱位）**：
- 用了很多 `(古筝轻拨)` `(童声哼唱)` `(唢呐主旋律起)` **中文圆括号提示**——官方 skill 明确：只有方括号标签 [XX] 才是可执行结构/乐器/人声指令，圆括号提示是普通文本，易被忽略。
- 唢呐只在全局 Arrangement 里"预告"（Chorus 2 suona motif）和 Outro 出现，没有作为 Outro 段的 section 局部强指令 → 模型自己分配到了开头。

### 改进计划（v2）
- 把"童声哼唱"做成 **Bridge 的强指令**（Bridge 标签内直接写明 wordless child hum，用英文）
- 把"唢呐"作为 **Outro 段 section 局部指令**钉死（[Outro] 标签后紧跟 suona 主旋律独奏，明确只在结尾）
- 精简圆括号中文提示 → 用英文指令 + 方括号标签
- 可选：用官方 music-caption-rewriter skill 重写 caption（有 1000 模板可参照）

### 产出文件
- output/audio/minimax_music3_wow_00001.mp3 (60s, 44.1kHz stereo, V0)

### v2 试听反馈（60s，同 seed 20260821，改 section 局部指令）
- 没有男声/没有对唱——只有女声 + 童声合唱，中英文混合（但"挺好"）
- 没有 epic、没有中式（跨文化编曲对比没了）
- 整体仍流畅 ✅
- 没有唢呐（[Outro] 钉死未生效）
- 有童声，但在合唱里，不在 Bridge 独唱
- 不觉得是 Bridge，全片都在唱歌（无器乐主奏段落）
- **关键洞察**：v1（中男+英女+对唱+epic+中式）vs v2（女声+童声合唱、无对比、无独立 bridge）——同 seed 不同 prompt，人声结构几乎反转 ⇒ 声线分配高度不稳定，是生成式控制的体现，非纯 prompt 措辞。

### v3 待决问题（需要查证 Music3 多声线能力边界）
- 单模型能否稳定保持 2 个不同音色声线 + 2 种语言 + 童声？官方 demo 是否有此成功案例？
- 声线"分配"是否受 seed/措辞/多声线描述过载影响？
- [Bridge] 器乐留白 + 独唱能否独立成立？

## 2026-08-21 深夜探索链路（v1→v5 全记录）

### 版本演进
- **v1 (60s)**：自由写法，圆括号角色标注，双主唱+对唱+epic+中式 成功，但童声哼唱丢失、唢呐跑开头 → 最惊艳但短。
- **v2/v3**：官方 Singer A/B + section 标签写法，双主唱失败（塌缩单女声/女声像童声），无唢呐 → 官方写法在复杂需求上反而不如自由写法。
- **T-A/B/C 单测**：
  - T-A 双主唱极简：无中男，中英歌词稳定 → 双平级主唱是意外涌现，非稳定功能
  - T-B 童声单测：哼唱好但"童"不明显；对比发现童声在合唱情境明显、独立哼唱偏中性
  - T-C 唢呐单测：无唢呐，涌出迪士尼歌舞剧风格 → 歌舞剧是强项，指令乐器弱
- **E1-E4 情绪哼唱**：E1-E3(平静/绝望/孤独)成人哼唱效果都很好；E4(欢快)后半混入多声"发疯" → 成人哼唱是强项，快乐需克制表达。
- **V4_2min (120s)**：v1写法拉长，1:52前优秀但"想重开段落时间到" → 歌词量不足被稀释(1.52 chars/s)。
- **V4_3min (180s)**：同样歌词硬撑，松散，比v1差，单主唱+童声和音。
- **V5_3min (180s)**：v1 caption + 2倍歌词 + pre-chorus/chorus3/verse3 完整结构 → **完美，全部做到，紧凑完整收尾**。

### 关键架构认知（music3lab 实证）
- Music3 纯文本条件生成，无音频输入，**不支持音频续写/锚定拼接**（MC式走不通）。
- 长曲上限5min，长结构靠8B Global LLM全局叙事，正确做法是"增词而非拉时长"。

### 能力边界总结
- ✅ 强项：单主声线、成人哼唱+情绪、歌舞剧/迪士尼风格、中英混合、完整曲结构、故事弧线
- 🟡 中等：主唱+和声、童声(合唱情境)、结构跟随
- ❌ 弱项：双平级主唱稳定、精确音色年龄、唢呐/指令民族乐器、快乐克制、音频续写拼接

### 交付候选
- **V5_3min_00001.mp3** = 3分钟完整成品（当前最佳）
- v1_00001.mp3 = 60s最惊艳短版

### 待研究项（已转 T-comfy-ops-18）
**歌词密度-节奏定量关系**（用户指出需查明）：
- 已观测数据点：
  - 60s = 14行/273字符 → 4.55 chars/s，紧凑惊艳（v1）
  - 180s = 27行/570字符 → 3.17 chars/s，完美（V5）
  - 180s = 14行/273字符硬撑 → 1.52 chars/s，松散失败（V4_3min）
- 待测：最优密度区间、BPM与密度的耦合、每行字符数与段落时长关系、能否建立可复用长曲歌词量计算公式。
- 关联文件：music3_control_baseline.md（第11节）、V5_3min_00001.mp3

## 2026-08-22 音质探索（延续，音质提升 + 台词修复）
- 目标：解决 Music3 音频"录音机/罐头"质感 → 音质提升链路 + 台词问题
- **定论落 docs/26**：Music3 高频持续音（笛/长音管乐）音质不纯自带杂音，后期不可根治；非高频/短促瞬态干净 → 选材避雷
- **台词坑修复**：lyrics 区非歌词文字被当台词念（"no vocals"→有人读提示词）；修复=歌词区只留方括号标签，描述全放 caption（kotofix 验证无台词纯器乐成立）
- **工具链路（comfy-ops/scripts/）**：upscale_music3.py(FlashSR 48k) + master_music.py(母带) + remix_music_stems.py(demucs 重混) + batch_music.sh
- 产出：output/audio/ 30+ 首各国风格 mastered（含 _fix 无台词版）
- 待续：关注 MiniMax H3 / Music 更新；需要真正成片时继续（docs/26 §6）
