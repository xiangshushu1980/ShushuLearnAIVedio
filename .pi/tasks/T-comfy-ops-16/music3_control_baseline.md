# MiniMax Music 3 控制能力基线 — 社区经验汇总（2026-08-21）

> 来源：Reddit(r/comfyui/r/StableDiffusion)、B站评测、X、官方 README/blog/skill、第三方分析(orcarouter)、中文社区(Bocha→php.cn 摘要)
> 用途：设计"控制能力基础测试矩阵"（测 Music3 的上限在哪），替代继续盲撞复杂 prompt。

## 0. 架构事实（解释一切控制的根源）
- **8B Global LLM**（Qwen3-8B 微调）：逐帧预测 RVQ 语义 token，管长程结构（主题/节奏/人声音色/编曲推进）
- **0.6B Local LLM**：预测帧内声学 token
- **2.4B Flow Matching + 123M Flow-VAE**：连续 latent 合成 32kHz 立体声
- **本质：帧级自回归（AR）生成，不是时间轴编排器** → 结构是"全局模型感知的涌现"，不是逐段执行
- 无音频输入（不能声音克隆，人声全靠 prompt）；"vocal identity" 是单声线保持一致

## 1. 官方定论（HF README）
"Section tags and music descriptions provide **generative control** rather than **strict symbolic guarantees**."
→ 段落标签/描述 = 生成式控制，非严格符号保证。节奏/调性/配器/歌词/结构不会精确匹配。

## 2. 已知能力（能稳定做到）
- 完整歌曲结构（intro/verse/chorus/bridge/outro）整曲 5 分钟
- 单一主声线 + 和声伙伴（官方 demo"去吧去闯"：female lead + male harmony partner）
- 分层和声（layered harmonies）、长程一致性（主题/节奏/人声音色跨段保持）
- 中英混合歌词/中文字正腔圆（官方 demo 有 Mandopop 案例）

## 3. 已知局限/易失败点（我们踩的坑 + 社区报告）
| # | 局限 | 社区证据/机理 | 对策（社区给的） |
|---|---|---|---|
| 1 | **多角色公平对唱不稳定** | v1 偶成（中男+英女）；v2 明确写"two permanent lead voices"→塌缩成单女声；社区:多角色对唱混淆 | 用"1 lead + 1 harmony"结构；角色分配代号；必要时分轨生成（Music 3 无音频输入，但可分段生成拼接）|
| 2 | **童声/儿童人声易失真** | 中文社区：中文童声失真 | 用声学描述+年龄限定+音色锚定（如"boy soprano around 10 years old, pure and unpolished"）|
| 3 | **段落标签响应不可靠** | 我们：v2 [Bridge] 未独立成立、全片在唱；社区：结构标签响应不可靠 | 单行单标签、空行分隔；每段标签后直接写该段指令；避免在标签内混入太多说明文字 |
| 4 | **BPM/调性偏移** | 社区：BPM 与调性偏移 | 前置数值、双重复合表述、可校准 |
| 5 | **乐器时段控制弱（唢呐跑到开头）** | 我们 v1：唢呐在 24s 而非结尾；v2：[Outro] 钉死仍无效 | 只在该段标签内写乐器；全局描述不写；接受"生成式"结果 |
| 6 | **纯音乐/器乐段不稳** | 社区：纯音乐生成不稳定 | 用否定指令（"no vocals here"）、重复风格词 |
| 7 | **无音频输入（无声音克隆）** | Reddit：Music3 未带 audio encoder，不能 voice input | 人声全靠 prompt 描述 |

## 4. 我们 v1/v2 的实证（同 seed 对比）
- v1（全局描述人声+圆括号提示）：中男+英女✅ 对唱✅ epic✅ 中式✅ 唢呐开头24s⚠️ 无童声❌
- v2（"two permanent lead voices"+section 局部指令）：女声+童声合唱（中英混合"挺好"）✅ 无男声❌ 无 epic/中式❌ 无唢呐❌ 全片在唱❌
- **结论**：声线分配高度不稳定；[section] 局部指令能影响结构但不可靠；复杂多声线需求超出模型稳定区

## 5. 控制能力地图（推论，待基础测试验证）
| 控制维度 | 稳定度 | 说明 |
|---|---|---|
| 整曲时长 | ✅ 稳定 | 60s/120s/300s 都出满 |
| 单声线保持 | ✅ 稳定 | vocal identity |
| 主唱+和声双声线 | 🟡 较稳 | 需"lead + harmony"写法 |
| 双主唱公平对唱 | ❌ 不稳 | 超能力区 |
| 段落结构跟随 | 🟡 弱 | 能出段，但顺序/时长自定 |
| 乐器出现时段 | ❌ 弱 | 唢呐跑到开头 |
| 哼唱/无词段 | 🟡 弱 | 易混入合唱 |
| BPM/调性 | 🟡 漂 | 需校准 |
| 中西混搭风格 | 🟡 可 | v1 出过中式+epic |
| 童声 | 🟡 弱 | 易失真，需音色锚定 |

## 6. 现成社区指引：multimodalart prompting-guide（HF space，重要发现）
来源：huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide（static guide，已存本地）

**对 v1/v2 失败的直接解释 + 正确写法：**

1. **「Text on the same line as a leading tag is dropped」** → 标签同行的文字会被模型丢弃。每个 tag（[Verse] 等）必须独占一行；指令写在 tag 下一行。我们 v2 把部分指令写在标签行可能导致被吞。
2. **每个 tag 独占一行**（

## 6. 现成社区指引：multimodalart prompting-guide（HF space，重要发现）
来源：huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide（已存 multimodalart_prompting_guide.html）

**直接解释 v1/v2 失败 + 正确写法：**
1. **「Text on the same line as a leading tag is dropped」** → 标签同行的文字会被模型丢弃。每个 tag 必须独占一行，指令写在 tag 下一行。
2. **结构 = guidance not guarantee**（再次确认）。想生成好的结构，caption 要写成**故事弧线**（tension/release/respite/climax），不是静态规格罗列。
3. **「Leaving vocals unspecified = #1 cause of instrumental drift」** → 人声必须写明。
4. **官方声线写法 = "Singer A (Male/Female). The vocalist possesses a ... timbre"** → 用命名角色（Singer A/B），不用 "two permanent lead voices"。
5. **guide 所有示例 = 单主声线(Singer A) + harmony/backing**。没有"双主唱对唱"示例 → 证实设计主场景是单声线+和声。
6. **风格融合写法**：「Fusing two styles? Name both explicitly... caption must commit to how the two palettes share the arrangement」→ 中式+弦乐+epic 要明确两调色板如何分配。
7. 官方 prompt 库 ~1000 参考 caption / 18 风格家族（music-caption-rewriter skill 内置）。
8. **硬限制（Hackernoon 评测）**：文本 5000 token 上限；音频 9000 帧≈360s。

## 7. 实证实验（2026-08-21 深夜，seed 202608xx，45-120s）
| 测试 | 内容 | 用户试听结论 |
|---|---|---|
| **T-A** 双主唱极简(seed777777) | 去童声去唢呐，Singer A男中音/女高音，gen lyric 圆括号去掉,caption Singer A/B 抽象描述 | **无中男，中英歌词有且稳定** → 双主唱仍不稳，高声部胜出 |
| **T-B** 童声单测(seed20260801) | 纯童声哼唱 solo，ffmpeg ~8岁 | **哼唱很好，但“童”不明显**（像成人/中性哼唱）→ 无词段是强项，特定年龄音色是弱项。**对比：v2/v3 和声/穿插场景童声却很明显** → 童声在合唱情境易识别，独立哼唱时偏中性 |
| **T-C** 唢呐单测(seed20260802) | 纯器乐 epic，[Finale] 唢呐 solo | **无唢呐，出的是【弦乐+歌舞剧=迪士尼腔调(美女与野兽)】** → Music3 极擅长歌舞剧，风格倾向盖过指令乐器 |
| **V4** v1原写法+120s(seed20260821) | v1 圆括号角色标注原样复刻，拉长120s | 能量曲线漂亮(开场静→45s升→60-75s高潮-14dB→90-105s低谷-23dB bridge→105结尾)，结构留存待听 |

### 关键实证结论
1. **双主唱仍不稳**：T-A 极简版也只剩高声部 → "两个平级主唱"不是可靠基本功能，v1 那次是意外涌现。
2. **哼唱强、音色年龄弱**：无词哼唱是 Music3 强项，但"童声 vs 成人"的年龄区分模糊。**成人哼唱可能更自然**。
3. **歌舞剧/迪士尼是 Music3 强项**：C 测试直接涌现出美女与野兽风格，能力极强，且**盖过了唢呐指令**。
4. **指令乐器(唢呐)是弱项**：多次试都出不来/跑位。可能是训练数据里唢呐样本少。
5. **v1 圆括号角色标注 > caption Singer A/B**：v1(圆括号)双主唱成功，v2/v3(caption抽象)失败 → 模型读歌词内联标注比读抽象声线描述更可靠。
6. **输出文件**：T-A=wow_00004.mp3, T-B=TB_child_00001.mp3, T-C=TC_suona_00001.mp3, V4=V4_v1_120s_00001.mp3

## 8. 关键能力边界：Music3 不支持"音频续写/锚定拼接"（music3lab 实证）
来源：huggingface.co/coolpoodle/music3lab（open research toolkit，专门研究此问题）

**结论：Music3 是"纯文本条件生成"，从空 latent 格子从头生成，长结构靠 8B Global LLM 全局叙事涌现，无"吃上一段音频状态"接口。**

因架构原因（无音频输入，官方从未给 audio/voice 输入）而非工程未实现：
1. **原生 WAV→token 音频编码器 unsolved**（不提供）→ 无法像 MC 视频那样吃上一帧/上一段 latent 作锚定条件。
2. **Arbitrary-audio continuation/inpaint/prepend 全部 do not work**（负面结果）。
3. **causal continuation 退化为 "near-exact repeat-tail copy"**（机械复制上一段结尾）。
4. **audio-prepend seam/anti-copy gate 失败**（拼接点必断层）。
5. 唯一跑通的是 music3lab 自训 flow-encoder（WAV→latent, ~1M param）+ LoRA 流适配器做 latent 空间编辑研究，但需重新训练、非即插即用、输出质量未达目标。

**实操含义**：
- 长曲（>5min）原生做不到无缝续写。
- 想"分段生成再无缝接续"（MC式锚定）**不可行**，只能硬拼接（有断层）。
- 要单轨控制（单独哼唱轨 + 伴奏轨合成）Music3 本身做不到，需后期用声音分离工具（demucs / python-audio-separator）拆干声/伴奏后再合成。

## 9. V4 试听定论（v1自由写法 + 120s = 至今最佳交付）
- ✅ 1:52 前整体优秀（与 v1 相似但延长），双主唱(1)+对唱中英互换音色保持(2) 都做到并持续 2 分钟。
- ⚠️ 无唢呐，只有**笛子**（caption 里 dizi 高频出现 → 模型倾向笛子替代 suona）。
- ⚠️ **1:35 哼唱段后 → 1:52 笛子收尾 → 又"重新开场"但时间到** → 精确印证 music3lab：Music3 不续写，能量耗尽会尝试重开段落，2min 卡在结构中间，素材自然长度 > 2min。
- **策略**：给更长时长（3min）或锁 2min 接受笛子+自然收尾。唢呐不可靠，笛子是可行的中式音色替代。

## 10. E 情绪哼唱系列定论
- E1-E3（平静/绝望/孤独）成人哼唱效果都不错 → 成人哼唱是强项，情绪表达清晰。
- E4（欢快）后半段"发疯"混入多声 → 模型把"快乐"理解成"热闹大合唱"，偏离。记偏好：快乐情绪要用克制表达避免大合唱发散。

## 11. V5 成功配方（3分钟 + 2倍歌词 = 长曲正确做法）✅
**V5_3min（180s，v1 caption + 2倍歌词 + pre-chorus/chorus3/verse3 完整结构）用户定论"完美，全都做到了"**

- 节奏紧凑（27行歌词/180s，每行6.7s，密度3.17 chars/s）
- 双主唱+对唱中英互换+音色保持 全程稳定
- 3分钟结构完整收尾（结尾-29dB真收住，不重开段落）
- 童声哼唱[Bridge]独立出现
- 整体远优于V4_3min

**核心配方规律（已验证）**：
1. **长曲要"增词"而非"拉时长"**——歌词量随时长按比例扩，保持每行~4-7s密集节奏。
   - v1(60s)=14行/273字符，密度4.55 chars/s
   - V5(180s)=27行/570字符，密度3.17 chars/s ✅
   - V4_3min(180s)=14行/273字符(硬撑)，密度1.52 chars/s ❌ 松散
2. **v1 成功基因**：圆括号角色标注((男·中文)/(女·English)/(合唱·中英)/(童声哼唱)) + 故事弧线caption。
3. **结构化扩展**：pre-chorus/chorus3/verse3 填充时长，比单纯重复更自然。
4. **唢呐不可靠**（被笛子替代），可接受。若需唢呐感→后期加音源。

**文件**：V5_3min_00001.mp3 = 3分钟完整成品（当前最佳交付候选）
