# 18 IR 输出样本拆解（生成器学习基准，2026-08-08）

> 定位：docs/16 清单 #1/#2 的落盘——真实 IR 输出逐条拆解，提炼结构规律供生成器（DeepSeek）模仿。
> 样本源：experiments/ir_samples/（本任务线收集）+ 官方 README 示例。

## 一、样本清单（13 条）

| 样本 | 模式 | 时长 | 镜头 | 输入 | 输出长度 |
|---|---|---|---|---|---|
| t2v_cyberpunk_rainy | T2VA | 5s | 1 | 赛博雨夜 | 1964ch |
| t2v_doc_streetfood | T2VA | 5s | 2 | 街头小吃 | 2096ch |
| t2v_dream_cloudsea | T2VA | 5s | 1 | 云海日出 | 1336ch |
| t2v_retro_cafe | T2VA | 5s | 1 | 复古咖啡馆 | 1610ch |
| official_t2va_10s | T2VA | 10s | 2 | 太空歌剧（官方） | 2524ch |
| official_i2va_8s | I2VA | 8s | 2（无切，焦点转移） | 拉面家庭晚餐（官方） | 4534ch |
| official_ref2va_5s | Ref2VA | 5s | 1 | 视频编辑+音色参考（官方） | 3574ch（六段式） |
| i2v_alya_beach | I2VA | 5s | ? | Alya 海边 | ? |
| i2v_alya_stage | I2VA | 5s | ? | Alya 舞台 | ? |
| i2v_forest_fairy | I2VA | 5s | ? | 森林精灵 | ? |
| i2v_dessert | I2VA | 5s | ? | 甜点特写 | ? |
| （旧 A/B）温泉 | T2VA | 10s | 1 | 温泉少女 | 1848ch |
| （旧 A/B）魔兽战斗 | T2VA | 10s | 1 | 兽人vs圣骑 | 2819ch |

成本：t2v 每条约 0.1-0.15 元；i2v 带图更贵（官方 i2va 示例 total 22822 tokens）。

## 二、结构规律（三核心段，t2v/i2v 实测）

### 1. 开场三件套（固定模式）
`[Shot 1]` 首句 = **风格 + 景别/机位 + 镜头运动**，逗号串联：
- `Cinematic, wide tracking shot following from behind.`
- `Cinematic documentary style, medium close-up, the camera trucks left.`
- `Vintage film, a medium shot slowly pushes in on ...`
- `Cinematic, time-lapse wide shot, the camera slowly trucks to the right across ...`

风格词池（实测）：Cinematic / Cinematic documentary style / Vintage film / High-fantasy 3D CG / Live-action, cinematic。

### 2. 镜头内描述层次（每镜）
固定叙事顺序：**环境定位 → 主体出场（服装/道具/材质细节）→ 光线 → 动作/运动 → 物理细节收尾**（雾气/反光/尘埃/蒸汽）。例（cyberpunk）：街道环境 → 女子 PVC 雨衣+伞 → 沥青反光+霓虹 → 走路摆动 → 雨滴被霓虹照亮。

细节密度基准：**每镜 300-600 英文词**；每镜至少 3 个具体物理细节（材质、颜色、光源、反射、粒子）。

### 3. 镜头切换与时间戳
- 第 2 镜起：`[Shot 2] At 00:02.650, the camera cuts to ...`（5s 视频切在 2.6s；10s 切在 4.5s）
- 5s 短视频倾向 1 镜（3/4 条 1 镜）；10s 2 镜
- **焦点转移不算切镜**（官方 i2va：全程静态，焦点从前景拉面→背景家庭 = 1 镜 2 段描述）

### 4. 镜头运动语法
IR 用自然英语：`The camera steadily tracks her forward movement, maintaining a fixed distance.` / `the camera trucks left` / `slowly pushes in` / `the camera holds a perfectly static shot`。与 docs/17 的 type+amplitude+speed 语法一致。

### 5. 声音三层结构（overall_soundscape）
固定分层句式，用锚定词串起来：
- **层1 底噪锚点**：`A continuous, heavy rainfall ... anchors the soundscape` / `The constant, loud roaring of a high-pressure gas burner anchors the soundscape`
- **层2 前景物理声**：`layered with the rhythmic, distinct ...` / `accompanied by ...`
- **层3 远景环境**：`while a distant ... sweeps across the background` / `can be heard in the distant background`
- 长度 195-558 字符（1-4 句）

### 6. 配乐段（non_diegetic_music）
公式 = **配器 + 速度 + 动态结构**，不加情绪词：
- `Slow-tempo, atmospheric synthwave featuring a deep, pulsing analog bassline, sustained icy synthesizer chords, and a sparse, echoing electronic beat, with no swells.`
- `A serene, majestic ambient orchestral track featuring swelling, warm string pads, a slow tempo, and a gradual, uplifting crescendo.`
- **无配乐写 `N/A`**（streetfood、retro 都是 N/A）——合法
- **diegetic 音乐归镜头描述**：retro 的爵士乐来自镜头内留声机 → 写在 Shot 1，配乐段 N/A（官方规则验证）

## 三、六段式规律（官方 ref2va 样本）

- subject_definitions：每行一个 `<label>` + 来源 + 保留特征（3 行：Subject 1 / Video 1 / Audio 1 / Audio 2）
- summary：`[video editing + audio reference + audio reuse] The target video is an edited version of <Video 1>. ...`
- retention_analysis：每 label 一行 + 固定标记（fully_preserved / partially_copy / reference）+ 保留内容说明
- detailed_description：风格句开场 → `[Shot 1]` 时间线；对话 `(S1) speaks softly, <d>[English] Follow the wind, live free.</d>`；动作与口型同步描述
- overall_soundscape / non_diegetic_music：与 base 模式同构

## 四、给生成器的规则启示（本任务线结论）

1. **开场三件套是硬模板**：风格+景别+运动，缺一不可
2. **描述密度有下限**：每镜 <200 词会被判定"不够电影级"（对照 A/B 实测：IR 增强后动作+40-60%）
3. **声音层必须三层齐全**：实测证明 soundscape 缺失/薄弱 → turbo 档静音 -48dB（A/B 规律）
4. **配乐 N/A 合法但 soundscape 不能省**
5. **物理细节词汇是 IR 与自写的最大差距**：材质（glistening/translucent/weathered）、光线（crepuscular rays/amber glow）、粒子（dust motes/steam）——词汇库（docs/16 清单 #6/#7）需重点收集
6. **i2v 输出比 t2v 更长更细**（官方 4534 vs 2524ch）：图给了 IR 更多可引用细节，生成器对 i2v 应基于图面描述

## 五、i2v 样本规律（4 条实测，2026-08-08 补）

### 1. 结构：instruction line + 三核心段
首行逐字：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`

### 2. IR 能精确读图（角色锚点机制）
- alaya_beach：从图中读出银发/红丝带/蓝眼/白外套金扣/黑裙白条纹/过膝袜金带——逐件服装描述，跨镜重复身份锚点（"She retains her exact outfit: ..."）
- forest_fairy："exactly as established in the first frame" 锚定图内容
- **启示**：i2v 输出比 t2v 更长更细（4375-6075ch vs 1336-2096ch）；生成器 i2v 路径应基于图面描述，角色卡/服装必须从图或角色卡提取

### 3. IR 会"加戏"（黑盒不可控实证）
- alaya_beach：输入=海边沙滩，IR 脑补开场"夜景街道+仙女灯"再切海滩（00:01.500 切）
- alaya_stage：开场是图背景的户外路面场景，soundscape 先写夜间环境再转舞台
- **对生成器设计影响**：IR 精修层可能偏离用户控制点（docs/16 §一 ③）；若走 IR，需在输入里明确"只拍一个场景"等约束，或接受其自由发挥

### 4. 镜头预算：5s i2v 也有 2 镜（切 1.5s），t2v 5s 倾向 1 镜

### 5. 声音跨镜衔接模式
night hum → whoosh+magic chime（转场声）→ beach waves；配乐两段式转场（music box+cello → acoustic guitar+piano）。转场处声音有明确过渡设计。

### 6. 与社区规则的一处出入（重要）
- benjiyaya 规则：diegetic 音乐（角色能听到）只进镜头描述，不进 soundscape
- IR 实测（alya_stage）：现场 pop 音乐写进了 overall_soundscape（"diegetic pop music track playing clearly from the stage speakers"），配乐段仍 N/A
- 结论：生成器以官方 IR 输出为准（diegetic 可入 soundscape），社区规则作为更严格可选项；本任务线不强制

## 六、待补

- [x] i2v 4 条样本拆解（完成，见 §五）
- [x] IR 脚本媒体嵌套格式修复（h3_ir_rewrite.py：image_url/video_url/audio_url 需 `{type:{url:...}}` 嵌套，官方脚本格式；本地文件传 mm_file:// 引用）
- [ ] 词汇库初版（docs/16 清单 #5/#6/#7 → 落本册附录；归属 2026-08-11 用户确认）
- [ ] DeepSeek vs IR 文本对比验证（docs/16 路线 1）
- [ ] kuronzzhan-droid / imagineVid-Awesome 社区 skill 拆解
