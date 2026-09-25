# T-comfy-ops-38 角色参考生成方案

## 当前结论（2026-09-17）

- 采用逐级增加参考变量的路线：单人物 → 3 人物 → 4 人物 → 固定场景 → 道具互动 → 技能参考 → 声音参考。
- 每一级先做同一角色/元素在多个镜头或多个短片中的一致性验收，通过后才增加下一类参考。
- H3 的 9 张图片是输入上限，不是推荐数量；公开资料没有每张图的 attention 权重或独立强度控制。
- 参考图按有序列表进入请求，prompt 用明确语义角色和稳定 Subject 绑定；同一镜头优先保持最小参考集。
- Character sheet 是由多张独立参考生成的一张复合文档图，不能假定它等于多个独立参考。生产测试应同时比较：独立图输入、从 sheet 裁出的独立图、整张 sheet 单图输入。

## 实验阶梯

1. 单人物：身份参考 + 固定场景，制作多个短视频，检查脸、发型、服装、体型、镜头变化下的一致性。
2. 三人物：每人独立身份参考，固定场景和简单互动，检查人物互相串脸、服装串用和站位稳定性。
3. 四人物：同上，记录新增人物后的身份保持率和错误类型。
4. 场景参考：固定人物，增加一个固定场景 ref，检查背景是否压过身份或改变构图。
5. 道具参考：单人物与一个固定道具互动，检查道具归属、尺寸、手持关系和人物身份。
6. 技能参考：单人物使用一个固定技能，检查技能形态、颜色、人物和背景是否互相污染。
7. 声音参考：最后再加入声音；分别测试人物声线、场景环境音、技能音效和道具动作声，避免把音频问题混入视觉基线。

## 验收记录要求

- 每级固定 prompt、分辨率、时长、采样参数和随机种子范围。
- 只增加一个变量；保存输入图顺序和每张图的语义角色。
- 记录身份、服装、场景、道具、技能、声音六类结果，分别标记稳定/漂移/串用/未观察。
- 任何失败先缩减参考数量或拆分职责，再考虑搜索新的节点或工作流。

## Sources 线索

- MiniMax H3 Guide Plan v2：Image Reference 区分 identity、wardrobe、scene、style、keyframe；Subject Binding 可将多张图合并为一个 Subject。
- MiniMax H3 Reference Space：最多 9 张图片，但按读取顺序进入请求，顺序改变会改变请求。
- JahJedi MiniMax-H3-Character-Sheet：多张独立参考生成一张冻结的 8 面板文档图；网格可能出现面板重复和互相污染。
- 社区反馈：多主体视觉身份可保持区分，但多主体声音身份存在 bleed 风险，因此声音应后置。

## 首轮执行记录（2026-09-18）

- 基线配置：`01_identity_host_krea.png` + `02_empty_studio_scene_krea.png`，768×448，124 帧（约 5.17 秒），20 steps，`ref_image_size=match`。
- A 例成功生成：`/home/sean/projects/ComfyUI/output/video/T38/t38_single_identity_scene_a_00001_.mp4`，约 100 秒。
- A 例抽帧初检：同一短片内脸型、发型、身份和浅灰背景保持稳定；这是单片帧内初检，不等于跨片一致性结论。
- B 例已在服务恢复后完成：`/home/sean/projects/ComfyUI/output/video/T38/t38_single_identity_scene_b_00001_.mp4`。
- A/B 帧抽样初检：两条片中脸型、发型和人物身份保持较稳定；B 例出现白色无肩带服装与更明显的场景横线，说明当前 prompt 没有锁住服装/构图，不能把“身份稳定”误判成“全身设定稳定”。
- A 例生成后曾触发 ComfyUI 服务断开，B 例在恢复后成功；该服务中断单独记为基础设施问题。
- 下一步：先补一轮“身份 + 明确服装约束”的单人物对照，固定景别和服装，再决定是否进入三人物；暂不扩展新参考类别。

## 第二轮执行记录（2026-09-18）

- 修正 prompt：严格使用 Ref2VA 六段式；`detailed_description` 扩展到约 350–500 词；将身份、服装/手部、场景拆为 `<Subject 1>`/`<Subject 2>`/`<Subject 3>`，并固定 medium head-and-torso、单人、无切镜。
- A/B 均成功生成：`t38_single_identity_outfit_scene_a_00001_.mp4`、`t38_single_identity_outfit_scene_b_00001_.mp4`。
- 抽帧初检：两条片的身份和深色外套大体稳定，但领口细节不一致（A 更接近内衬，B 出现明显领巾/蝴蝶结）；背景的墙面分界和下沿也有变化。
- 结论：单独增加服装参考后，服装大类稳定性提高，但细节和场景构图仍未完全锁定；当前仍不足以进入三人物测试。下一步应先做“同一人物 + 同一服装 + 不带场景 ref”的对照，判断场景图是否与服装图发生冲突。

## Fellow 人物首轮记录（2026-09-18）

- `xss_2.jpg` 为 3648×2736 高分辨率源图；本机 Krea 节点当前是文生图/风格参考，不作为身份 i2i 放大器，因此 xss 先直接使用原图。
- xss A/B：身份图 + 固定空演播室场景，`ref_image_size=max`，768×448/124 帧/20 steps；两条均成功。
- xss 抽帧初检：脸、短发、耳形和整体身份稳定；B 例比 A 例出现更宽的构图，说明身份保持强于镜头构图保持。
- `cc.jpg` 为 700×700 源图；CC A/B 同样使用身份图 + 固定场景，`ref_image_size=match`，两条均成功。
- CC 抽帧初检：脸、短发、眼镜和整体身份在两条片中较稳定，镜头和背景变化小于 xss 的 B 例。
- 以上为抽帧初检，不代表正式定论；尚未测试 CC/xss 同镜三人物，也尚未测试服装、道具或技能参考。

## 高清输入对照（2026-09-18）

- 对 `cc.jpg` 尝试 `4x-ClearRealityV1.pth`：输出出现明显脸部拉伸/变形，判为不可用，不进入 H3 测试。
- 生成保守 Lanczos 2048×2048 放大版：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/cc_lanczos_2048.jpg`。
- 用 Lanczos 版替换原 CC 图，保持同一场景、prompt、分辨率、时长和 steps，A/B 均成功。
- 抽帧初检与原 700×700 CC 结果基本相同：眼镜、脸和身份稳定，但没有观察到可确认的身份提升；纯像素放大没有恢复原图不存在的面部细节。
- 当前结论：CC 的差异不应简单归因于分辨率；需要身份保真的多视角/更清晰原始照片或专门 identity-preserving i2i，不能用会改脸的通用超分替代。

## Shushu 后续参考资产（2026-09-18）

- 使用 `xss_2.jpg` 作为 shushu 源图，生成身份重建候选：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/shushu_identity_rebuilt_v1.png`。该图用于身份参考，保持正面头肩构图、短发和中性表情，替换为干净灰色背景。
- 生成固定服装候选：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/shushu_outfit_charcoal_v1.png`。人物穿深炭灰色翻领外套和黑色圆领内搭，采用腰部以上正面构图，供下一轮“身份 + 服装 + 场景”对照。
- 生成固定空场景候选：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/shushu_empty_studio_scene_v1.png`。16:9 灰色演播室墙面与地面，无人物、道具和文字。
- 三张图目前是候选参考资产，已做肉眼检查；下一步先用 shushu 身份图 + 空场景跑 A/B，再加入服装图跑 A/B，沿用 Ref2VA 六段式 prompt 和 `ref_image_size=max`，之后才判断是否进入多人物。

## Shushu H3 验证（2026-09-18）

- 身份 + 空场景 A/B 成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_identity_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_identity_scene_b_00001_.mp4`
- 身份 + 服装 + 空场景 A/B 成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_identity_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_identity_outfit_scene_b_00001_.mp4`
- 参数：768×448、124 帧、20 steps、`ref_image_size=max`、两个 seed 对照；提示词为 Ref2VA 六段式。
- 抽帧初检：身份 + 场景两条片中脸型、短发、耳形和整体身份稳定；B 片中段出现轻微侧脸动作，但回到正面后身份未漂移。加入服装后，两条片的炭灰翻领外套、黑色内搭、口袋和纽扣大体保持，身份仍稳定；服装细节和墙面分界仍有小幅变化。
- 当前判断：shushu 单人物身份参考可进入后续动作/道具测试；服装参考已足够作为当前测试基线，但不能把它视为逐像素锁定。多人物测试前仍需先确认动作幅度不会放大场景与服装漂移。

## Shushu 动作测试（2026-09-18）

- 使用新版带帽身份图、带帽服装图和空场景，加入一次慢速右手挥手动作，A/B 均成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_action_identity_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_action_identity_outfit_scene_b_00001_.mp4`
- 五个时间点抽帧：身份、外套、场景和手部动作基本稳定；但 H3 在动作视频中去掉了黑色反戴帽，恢复为短发/近寸头。说明帽子属于需要单独锁定的可见服装/配饰变量，不能仅靠身份图带入。
- 结论：动作本身可控，身份主体仍可辨认；帽子保持失败。后续若帽子是角色固定设定，应把帽子作为独立 wardrobe/prop reference，并在 `Subject 2` 中明确锁定；当前不进入多人物，先处理帽子配饰控制。

## 帽子/饰物参考控制检索结论（2026-09-18）

- H3 官方参考提示词规则要求给每个参考明确职责；服装和饰物应在对应的 `<Subject N>` 中显式定义。参考图本身不会自动把图中所有元素都绑定到视频。
- 本次帽子丢失的直接原因：身份 Subject 强调脸、头型和短发，服装 Subject 只写外套、内搭、领口、纽扣和口袋，没有把黑色反戴帽写入 Subject，也没有在 retention/detailed_description 中声明帽子为 mandatory。
- 稳定方案：身份图只负责脸和头部比例；单独帽子/头饰图负责帽子；服装图负责衣服；提示词中把帽子写为 fully_preserved、required visible accessory，并明确禁止替换为短发、寸头或裸头。
- 外部依据：MiniMax H3 Reference-to-Video 说明（每张参考图应有清晰职责、服装图可负责 clothing and accessories）；MiniMaxAI 官方 `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`（Subject 可由多份参考共同定义，服装/饰物需在 Subject 中绑定）。

## 独立帽子 Subject 验证（2026-09-18）

- 新增独立帽子裁剪参考：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/shushu_hat_reference_v1.png`，只保留帽冠、反向帽带、金属扣、发际线和耳部上缘。
- 四参考职责分离：身份、帽子、服装、场景；帽子在 `Subject 2`、`retention_analysis` 和 `detailed_description` 中标为 `fully_preserved` / mandatory visible accessory，并明确禁止短发、寸头或裸头替代。
- A/B 生成成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_hat_identity_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_hat_identity_outfit_scene_b_00001_.mp4`
- 五个时间点抽帧：两条片中帽子均保持可见，说明独立 Subject + 明确绑定有效；身份、外套和挥手动作也基本保持。A 的第一个抽样点出现短暂原始居家背景/动物泄漏，随后回到目标演播室，说明身份图源背景仍可能在首帧竞争场景图；需要下一轮强化场景排除或使用更干净的身份图。

## 清理 Subject 冲突后的复测（2026-09-18）

- 发现上一轮 prompt 残留冲突：summary 把 `<Subject 2>` 写成环境，身份 retention 仍写 `short dark hairstyle` 并要求忽略 hat/animals，和四 Subject 绑定互相矛盾。
- 修正为 `<Subject 1>` 身份、`<Subject 2>` 帽子、`<Subject 3>` 服装、`<Subject 4>` 场景，并删除旧的居家背景、动物和短发冲突描述。
- A/B 复测成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_hat_clean_identity_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_hat_clean_identity_outfit_scene_b_00001_.mp4`
- 五个时间点抽帧均为目标灰色演播室，无首帧居家背景泄漏；帽子、外套、身份和挥手动作均保持。说明上一轮泄漏主要来自 prompt Subject 冲突，而非参考图本身。

## 道具参考测试（2026-09-18）

- 新增独立道具参考：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/shushu_prop_yellow_can_v1.png`，无品牌黄色铝罐。
- 首轮“从画外拿起”测试中，道具未出现；复核发现 Subject 5 没有真正写入 JSON prompt，属于提交构造错误。
- 补齐 Subject 5、retention 和 detailed_description 后，A/B 道具进入画面并保持黄色罐形：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_prop_can_bound_identity_hat_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_prop_can_bound_identity_hat_outfit_scene_b_00001_.mp4`
- 五个时间点抽帧：B 片大部分时间人物手握道具；A 片和 B 片个别时间点出现罐子悬浮/与手部脱离，原因是同一只右手同时被要求握罐和挥手。道具“出现”已验证，但“手部真实互动”尚未通过。
- 下一步应取消挥手，把动作改成双手固定或单手静止持罐，先验证接触关系，再进入更复杂道具动作。

## 道具左右手分工复测（2026-09-18）

- 按用户建议改为左手握罐、右手做挥舞示意，避免同一只手承担握持和挥手两个动作。
- A/B 五点抽帧：罐子均从首帧出现，颜色和形状保持；B 片左手握持关系明显改善，A 片挥手中段仍有一次罐子与手部短暂脱离，但比上一轮稳定。
- 输出副本：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_prop_can_left_hold_right_wave_identity_hat_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_prop_can_left_hold_right_wave_identity_hat_outfit_scene_b_00001_.mp4`
- 结论：道具出现和左右手分工有效，真实接触关系显著改善但仍有局部漂浮；下一步若要继续，应使用更慢的右手挥舞或完全静止持罐，之后再进入技能参考。

## 技能参考首轮（2026-09-18）

- 清理 T38 视频目录，只保留一条道具测试片：`t38_shushu_rebuilt_prop_can_left_hold_right_wave_identity_hat_outfit_scene_b_00001_.mp4`。
- 新增技能参考：`/home/sean/projects/ComfyUI/input/ref2va_refs/fellow/processed/shushu_skill_blue_orb_v1.png`，定义蓝色能量球、圆形轮廓、青色中心、柔和光晕和少量粒子。
- 使用身份、帽子、服装、场景、技能五个 Subject，测试人物抬起左手，能量球在掌上出现并保持；A/B 成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_skill_orb_identity_hat_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_skill_orb_identity_hat_outfit_scene_b_00001_.mp4`
- 五个时间点抽帧：能量球在中后段稳定出现，颜色、圆形轮廓和蓝色光晕保持；帽子、身份、服装和场景也保持。技能参考首轮通过，可进入更复杂技能动作或声音阶段。

## 声音链路控制样本（2026-09-18）

- 当前项目没有 shushu 本人的声音参考；使用既有数字人短语音 `audio_control_sample_s1.wav` 作为链路控制样本，未将其当作 shushu 音色结论。
- 外部音频锁定与身份、帽子、服装、场景、蓝色能量球同时提交，A/B 均成功：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_skill_orb_audio_control_identity_hat_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_skill_orb_audio_control_identity_hat_outfit_scene_b_00001_.mp4`
- 抽帧初检：帽子、身份、服装、场景和能量球保持；音频是否逐字/逐音节同步需另行听音频和检查口型，当前只确认外部音频链路未阻塞画面生成。

## ElevenLabs 模板声音参考（2026-09-18）

- 用户提供的英文模板声音目录：`/home/sean/projects/DGB/automated-news-avatar-system/data/elevenlabs-template-voices/en/`。目录包含 20 个按 ElevenLabs voice ID 命名的 MP3；这些声音不是 shushu 本人，仅作为通用英文声音参考。
- 选用较长的 `hpp4J3VqNfWAUOO0d1Us.mp3`（约 3.89 秒）复制为 `ref2va_refs/fellow/processed/elevenlabs_template_en_hpp4J3VqNfWAUOO0d1Us.mp3`。
- 与身份、帽子、服装、场景、蓝色能量球一起做外部音频锁定 A/B：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_skill_orb_template_voice_identity_hat_outfit_scene_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_shushu_rebuilt_skill_orb_template_voice_identity_hat_outfit_scene_b_00001_.mp4`
- 抽帧初检：画面参考保持，模板声音链路可用；该结果不代表 shushu 音色或口型同步结论。

## 清理无效声音视频与双人物推进（2026-09-18）

- 因本轮人物不张口，删除 T38 中 `audio_control` 和 `template_voice` 两组无效声音视频；保留道具成功片、技能成功 A/B 和双人物 A/B。声音参考文件和 prompt/结果 JSON 未删除。
- 用户提供的 ElevenLabs 模板声音目录已记录，但模板声音只用于未来开口/音色控制实验，不用于当前闭口人物画面结论。
- 双人物基础 A/B 已完成并抽帧：
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_two_person_cc_shushu_a_00001_.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T38/t38_two_person_cc_shushu_b_00001_.mp4`
- 两人身份在五点抽帧中保持区分，CC 位于画面左侧、shushu 位于右侧，未出现脸部混合；服装属于测试用简化设定，尚未叠加帽子/道具/技能。
