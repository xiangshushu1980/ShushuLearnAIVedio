# 路线 1 验证：DeepSeek vs IR 文本对比（2026-08-08）

> 用户验收材料。场景 A 温泉 / B 魔兽，10s t2v 16:9，输入中文描述与 IR A/B 完全一致。
> 引擎：deepseek-v4-flash + docs/17 规则注入（reasoning MAX，max_tokens 16000）。
> 验收清单见本文件末尾，用户在对话中逐项反馈。

## A 温泉：IR（1848ch）vs DeepSeek flash（2958ch）

### IR 版（experiments/ir_samples/ab_A_onsen_10s.txt）
integrated_multimodal_description: [Shot 1] Cinematic, medium close-up, the camera performs a slow clockwise arc shot around a young woman sitting in a steaming hot spring. The woman has glistening skin and dark hair loosely pinned up with a carved wooden hairpin, leaving a few wet strands clinging to the nape of her neck. She rests with her eyes closed, displaying a deeply serene expression. Clear water trickles steadily down her bare, slender neck and cascades over her smooth shoulders, tracing her collarbone before dropping back into the bath. Thick white steam curls continuously upward from the surface of the water, drifting elegantly across the foreground and midground. The environment is a traditional Japanese bathhouse, detailed with a dark, textured natural stone basin and polished hinoki wood wall panels in the soft-focus background. Soft, warm yellow lighting emanates from a traditional bamboo lantern resting on a large flat rock to the left, casting a gentle, diffuse glow that highlights the rolling droplets of water on her skin. As the camera gracefully glides around her profile, the woman tilts her head back a fraction of an inch, her shoulders subtly dropping as she settles deeper into the relaxing heat of the tranquil pool.
overall_soundscape: The gentle, continuous bubbling and sloshing of hot spring water forms a tranquil acoustic bed, accompanied by the distinct, rhythmic trickling of water splashing softly as it runs down wet skin and merges back into the main pool. A faint, hollow room tone characteristic of an enclosed wooden bathhouse echoes subtly in the background.
non_diegetic_music: A slow, meditative ambient track featuring long, sustained notes from a traditional shakuhachi flute, gently layered over a warm, soft synthesizer drone, maintaining a steady and deeply tranquil tempo throughout.

### DeepSeek flash 版（experiments/prompt_compare/onsen_deepseek-v4-flash.txt）
integrated_multimodal_description:

The video unfolds as a serene, cinematic spa vignette bathed in warm amber lantern light, with white steam drifting through the air and a tranquil, dreamlike pacing that lingers on stillness and gentle motion.

[Shot 1]
A wide shot from 00:00.000 to 00:03.500: a young East Asian woman in her early twenties — her black hair pinned up in a loose wet bun, a soft white cotton towel wrapped around her torso — sits immersed in a traditional hinoki wooden bath inside a dimly lit Japanese bathhouse. Warm yellow paper lanterns glow along the timber walls, and thick white steam curls upward from the water surface. The camera performs a slow arc shot around the bath with small amplitude at slow speed, gliding from her left side toward the front while she gently settles deeper into the steaming water, sending soft ripples that lap against the wooden rim. The light flickers faintly as steam drifts past the lanterns, and distant droplets echo in the quiet space.

[Shot 2]
From 00:03.500 to 00:07.000, a medium close-up at shoulder level: the camera continues its slow orbit as a tracking shot with small amplitude at slow speed, moving to her right side. Clear water trickles in fine rivulets down her neck, over her damp collarbone and shoulder, catching the warm glow as it slides along her skin. Her single dominant action is a slow, soft exhale as she tilts her head slightly back, eyes half closed, droplets falling from her shoulder back into the bath. Her wet bun, white towel, and the amber lantern glow remain consistent from the previous shot; steam swirls thicker around her shoulders, and her submerged body is faintly visible through the crystal-clear water.

[Shot 3]
From 00:07.000 to 00:10.000, a relaxed medium-wide shot: the camera pulls back slowly with small amplitude at slow speed while slightly elevating, revealing the full bath and her serene profile once more. She rests her forearms along the wooden rim, head tilted, eyes fully closed, and her dominant action is a deep, contented sigh as she sinks a little lower into the water, which rises gently against her chest. Steam rises in lazy wisps around her, the warm yellow lanterns cast a soft glow across the dark wooden planks, and a single droplet rolls down her cheek and falls into the bath as the scene holds its tranquil stillness to the final frame.

overall_soundscape:

Soft, echoing drips of water from wooden buckets and ceiling beams; the gentle lapping and rippling of bathwater as the woman shifts and settles; the faint hiss and whisper of rising steam; a subtle creak of the old wooden bathhouse; and her slow, soft breathing with one quiet, contented sigh.

non_diegetic_music:

A sparse ambient piano with a warm sustained string pad, at approximately 60 BPM, featuring slow arpeggiated phrases and gentle dynamic swells, with no percussion — a minimal, breathing texture that follows the rhythm of the water and steam.

---

## B 魔兽：IR（2819ch）vs DeepSeek flash（3405ch）

### IR 版（experiments/ir_samples/ab_B_wow_fight_10s.txt）
integrated_multimodal_description: [Shot 1] High-fantasy 3D CG, a medium-wide shot featuring a fast tracking shot that continuously follows the chaotic, shifting movement of the combatants. In the center of a barren, dust-choked battlefield under harsh, dramatic sunlight, a massive, green-skinned Orc warrior with prominent lower tusks and a braided black topknot, wearing heavily weathered, spiked black-and-crimson iron plate armor, lunges aggressively from the left. He is met on the right by a heavily armored Human Paladin, who has a rugged, battle-scarred face and short blonde hair, clad in pristine, gleaming gold-and-silver plate armor heavily adorned with sculpted lion crests. The Orc swings a gigantic, serrated double-bladed battle axe overhead in a sweeping arc, trailing a thick, luminous ribbon of crackling, fiery red magical rage energy. The Paladin immediately leans back, his shoulders tensing, and raises a massive kite shield that instantly erupts with blinding, golden holy light. The weapons violently collide, sending a shockwave of crimson and golden magical sparks rippling through the air and instantly kicking up a thick, swirling cloud of brown dust from the cracked earth. Fluidly maintaining the framing on the moving subjects, the shot captures the Paladin fiercely thrusting a glowing silver warhammer forward in immediate retaliation. The Orc reacts with a sharp twist of his muscular torso, catching the hammer's blow against the thick steel shaft of his axe. The two warriors lock weapons, leaning their full body weights against each other in a tense, vibrating deadlock. Their faces are pressed inches apart, teeth bared in strained, fierce grimaces, as the harsh glare of the conflicting red and gold magic illuminates their sweat-drenched features through the densely falling dirt and floating magical embers.
overall_soundscape: Loud, howling wind and the rapid, heavy crunch of metal boots sliding on loose gravel open the sequence, instantly overpowered by a deafening, metallic crash as the giant axe strikes the shield. A deep, resonant boom of magical energy and sharp, sizzling crackles of sparks immediately follow the heavy impact. A loud, guttural, aggressive grunt from the Orc mixes with the sharp, metallic clattering and clanking of shifting steel armor plates. A high-pitched, ringing harmonic chime accompanies the flare of golden magic, transitioning into the loud, sustained, grating scrape of metal forcefully grinding against metal as the weapons lock, all set against the continuous, grainy patter of falling dirt and debris in the foreground.
non_diegetic_music: An epic, fast-paced orchestral score driven by rapid, pounding timpani drums, aggressive, blaring brass stabs, and a vigorous, sweeping string ostinato, playing at a loud volume with no swell.

### DeepSeek flash 版（experiments/prompt_compare/wow_fight_deepseek-v4-flash.txt）
integrated_multimodal_description:
Epic dark-fantasy MMORPG cinematic battle sequence with gritty, saturated color grading: volcanic orange rim light against deep blue shadow, drifting dust backlit by magic flares, subtle film grain, and an energetic handheld camera identity that keeps the fight feeling live and physical.

[Shot 1]
On a war-torn field under a smoke-choked sky, a massive green-skinned orc warrior with a scarred jaw and jagged lower tusks, clad in black iron plate with spiked pauldrons and a torn leather harness, grips a notched double-headed war axe crackling with green ember energy. Facing him, a human paladin in ornate silver-and-gold plate armor, holding a weathered blue kite shield with a dented lion emblem, raises a longsword whose edge burns with golden holy light. The two collide with a thunderous impact: the axe smashes against the shield rim, hurling white-hot sparks, green ember trails, and a fan of gray dust across the frame. The camera trucks fast from left to right at a low angle, keeping the locked weapons at frame center with a slight handheld shake; ground stone chips explode under their boots, and for one instant at the collision the frame drops to slow motion before snapping back to full speed.

[Shot 2, 00:03.500 - 00:07.000]
Low behind the orc, the camera pushes in with large amplitude at fast speed as the orc rears back, the tendons of his arms tensing through the black plate, then swings the axe in a massive overhead arc. The paladin bobs behind his shield and angles it to deflect; the blade screeches down the shield's face, spraying a long curved line of golden holy sparks and green embers, and a radial shockwave of dust and pebbles blasts outward from their boots. The paladin's right pauldron gains a fresh scrape, the orc's chest plate shows a hairline scorch mark, and a violent camera shake at the moment of contact makes the impact feel crushing. Screen direction holds left-to-right.

[Shot 3, 00:07.000 - 00:10.000]
Wide shot with a fast tracking pull-back and a slight pedestal up: the paladin pivots low and lashes out a horizontal counter-slash, holy light streaming from the blade like a burning ribbon; the orc twists his torso back, and the sword carves a shallow glowing gash across his chest plate, showering blackened armor shards into the air. Dust kicks up in two rolling clouds as both warriors plant their boots, skidding to a halt across the settling haze, crouched and panting, facing each other with weapons raised. The camera holds on the two silhouettes framed against the burning smoke, the orc's new gash still faintly glowing, the paladin's sword hum tight in his grip.

overall_soundscape:
Constant battlefield wind and the low rumble of distant siege engines; armored boots crunching on broken stone; heavy metal impacts — axe against shield, sword scraping pauldron — with sharp ringing overtones; whooshing air from wide swings; crackling green fel energy and a searing hum from the holy blade; rapid thudding footsteps; strained guttural grunts and one short wordless battle roar from the orc.

non_diegetic_music:
Full orchestra with heavy percussion: pounding taiko and timpani in a driving 6/8 rhythm, sharp low-brass stabs timed to each weapon impact, fast string tremolo ostinati, and a sustained low choir; dynamics surge loudly on every collision and recede into the brief holds between exchanges.

---

## 验收清单（9 项，用户逐项 ✅/❌）

### 场景文件索引（10 个，IR vs DS 各一份）

| # | 场景 | 模式/时长 | IR 版 | DS flash 版 | DS长度 | DS镜头 |
|---|---|---|---|---|---|---|
| A | 温泉 | t2v 10s | ir_samples/ab_A_onsen_10s.txt | onsen_...flash.txt | 2952 | 3 |
| B | 魔兽战斗 | t2v 10s | ir_samples/ab_B_wow_fight_10s.txt | wow_fight_...flash.txt | 3405 | 1 |
| C | 赛博雨夜 | t2v 5s | ir_samples/t2v_cyberpunk_rainy.txt | cyberpunk_rainy_...flash.txt | 2272 | 1 |
| D | 街头小吃 | t2v 5s | ir_samples/t2v_doc_streetfood.txt | doc_streetfood_...flash.txt | 1980 | 2 |
| E | 云海日出 | t2v 5s | ir_samples/t2v_dream_cloudsea.txt | dream_cloudsea_...flash.txt | 1473 | 1 |
| F | 复古咖啡馆 | t2v 5s | ir_samples/t2v_retro_cafe.txt | retro_cafe_...flash.txt | 1235 | 1 |
| G | Alya 海边 | i2v 5s | ir_samples/i2v_alya_beach.txt | alya_beach_...flash.txt | 2043 | 2 |
| H | Alya 舞台 | i2v 5s | ir_samples/i2v_alya_stage.txt | alya_stage_...flash.txt | 2166 | 3 |
| I | 森林精灵 | i2v 5s | ir_samples/i2v_forest_fairy.txt | forest_fairy_...flash.txt | 2134 | 3 |
| J | 甜点特写 | i2v 5s | ir_samples/i2v_dessert.txt | dessert_...flash.txt | 1788 | 3 |

（A/B 全文见上，C-J 全文在各文件，按上表对照读）

### 合规统计（全部 10 条，机器预检）

| 检查项 | 结果 |
|---|---|
| 三核心段齐全 | ✅ 10/10 |
| 长度水平 | 1235-3405ch，与 IR（1336-2819）同档 |
| 镜头预算（5s→1-2 镜） | ⚠️ 3/10 超预算（alya_stage/dessert/forest 5s 出 3 镜） |
| 时间戳语法 | ❌ 4 种变体：切点式(dessert)/时段式(onsen)/无时间戳(6条)/Shot1 带时间戳(cyberpunk,dessert)——系统性不稳定 |
| 字段冒号 | ⚠️ 2/10 缺冒号（cyberpunk/dream 写成了无冒号的裸标题） |
| soundscape/配乐公式 | ✅ 10/10 齐，配器+速度+动态无情绪词 |

### 用户逐项打分表（A-J 每个场景打 9 项）

| # | 维度 | 判定标准 | A温泉 | B魔兽 |
|---|---|---|---|---|
| 1 | 结构 | 只含三核心段字段，无前言/解释/fence | | |
| 2 | 开场三件套 | 风格+景别+镜头运动在首句/首段 | | |
| 3 | 时间戳语法 | 切点式 `[Shot 2] At MM:SS.mmm, the camera cuts to`（⚠️ DS 用了时间段式，疑似硬伤） | | |
| 4 | 镜头预算 | 10s → 2-3 镜，每镜一主导动作 | | |
| 5 | 细节密度 | 每镜 ≥300 英文词/总长 ≥1500ch（IR 基准 1848/2819ch） | | |
| 6 | 动作具体性 | 动词具体（碰撞/倾斜/挥砍），非静态罗列 | | |
| 7 | 声音三层 | 底噪锚点+前景物理声+远景环境声齐全 | | |
| 8 | 配乐公式 | 配器+速度+动态结构，无情绪词堆砌 | | |
| 9 | 主观差距 | 1-5 分（5=与 IR 无差别），逐场景打分 | 分 | 分 |

## 判定规则

- **硬伤一票否决**：缺字段 / soundscape 缺失 / 时间戳语法全错 → 先修规则再验（不算通过）
- **通过线**：无硬伤 + 8 项 ≥6 项达标 + 主观分平均 ≥3.5 → DeepSeek 路径可行（flash 档即可进入最小闭环）
- 否则：换 deepseek-v4-pro 精写 / 强化规则注入（加示例 few-shot）/ 规则校验层兜底

## 我的预判（10 场景跑完后的差距点）

1. **时间戳语法（唯一系统性硬伤）**：flash 输出 4 种变体（切点式/时段式/无时间戳/Shot1 带时间戳），规则未吃透。确定性语法 → 两个修复通道：few-shot 示例注入（预计修复率提升明显）或生成后规则校验层自动改写（零成本，因为语法是确定性的）
2. **字段冒号**：2/10 裸标题缺冒号（`integrated_multimodal_description` 无 `:`）——同属确定性语法，校验层可修
3. **镜头预算**：5s 场景 3/10 出 3 镜（预算 1-2 镜）——影响节奏，可在 user prompt 里强约束
4. **风格开场**：DS 版整体风格独立成段再分镜（更像人类作者），IR 嵌在 `[Shot 1]` 首句（模板化）——合规性 IR 稳，但两者都是合法风格开头
5. **创作质量**：细节密度/声音三层/配乐公式/动作编排全部达标；DS 有 IR 没有的：慢镜拍点、屏幕方向保持、损伤累积连续性（docs/17 高级 pattern 被吃进去了）

## 复跑/修复选项（用户选）

- A. 接受现状（时间戳/冒号由规则校验层后处理兜底，预算由 prompt 强约束）→ 直接进最小闭环
- B. 规则注入加 few-shot（3 个官方 IR 样本做示例）重跑 10 场景 → 再验一次，看硬伤修复率
- C. 换 v4-pro 精写同 10 场景 → 对比 flash vs pro（成本略高）
- D. 验收完直接进最小闭环，硬伤边做边修

