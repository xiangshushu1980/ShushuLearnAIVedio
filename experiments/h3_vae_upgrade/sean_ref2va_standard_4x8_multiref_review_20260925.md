# Sean — 4×8s 多 Ref 标准驱动动画提示词 Review

owner: Sean
date: 2026-09-25

## Ref 清单

- `<Picture 1>` → `sean_t2_a_identity_front.png`：精灵弓手 A
- `<Picture 2>` → `sean_t2_b_identity.png`：红发女性 B
- `<Picture 3>` → `sean_t2_scene_observatory.png`：观测台场景
- `<Picture 4>` → `sean_t2_spell_cyan_ribbon.png`：青色法术
- `<Picture 5>` → `sean_t2_object_brass_compass.png`：黄铜罗盘
- 未加入角色板、脸部特写和 Sylvanas：这些素材会重复提供精灵/弓/脸部信息，当前测试目标是验证两人物+道具+法术的驱动连续性。

## Review 1：格式与引用契约

- [x] Ref2VA 六段顺序正确：`subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`。
- [x] 全部参考标签先定义后使用；没有未定义的 `<Picture N>` 或 `<Subject N>`。
- [x] 参考图被定义为角色/环境/法术/物品参考，不被误写成首帧或尾帧。
- [x] 32 秒时间线严格分成 00:00、00:08、00:16、00:24 四个 Shot；内部动作点按 00:06.500、00:14.500、00:30.500 递增，最终时间为 00:32.000。
- [x] 每个 Shot 有构图、动作、镜头运动、环境和声音连续性。
- [x] 没有用户未提供的对白或歌词，`non_diegetic_music` 为 `N/A`。

## Review 2：时序、身份和接缝风险

- [x] 两个角色职责分离：A 是银发精灵弓手，B 是红发人类/女性；没有 Sylvanas 第三身份干扰。
- [x] 弓被声明为唯一道具并固定在 A 背上，避免双弓和左右手漂移；A 只使用一张清晰的全身身份图。
- [x] 罗盘只有一个；Shot 1–2 由 B 右手持有，00:14.500 明确转交到 A 左手，之后不再改变归属。
- [x] 法术只有一个，从罗盘周围的小光开始，在 Shot 3–4 连续成长，不在 Shot 4 重置。
- [x] 场景布局和月光方向贯穿四段；Shot 4 的亮光是同一法术的结果，不是新场景。
- [x] Shot 边界均有明确的前一状态作为下一段起点，适合 Native Masked continuation。
- [x] 声音使用连续风声、脚步、罗盘 click 和持续魔法 hum，避免每个 chunk 重新发明环境音。

## Review 结论

提示词可以进入 4×8s 测试。参考图职责清楚，且已经针对上一条 5×8s 出现的“双弓/手部漂移”加入了显式约束。建议工作流使用 5 张 `reference_image_1..5`、`reference_size=Max Identity`、`prompt_mode=Timeline`、Native Masked Strong 39、Sage、PDD 8-step；暂不加入 Sylvanas，也暂不加入 Plus 二采，以便先观察基础驱动动画的身份和 Shot 衔接。
