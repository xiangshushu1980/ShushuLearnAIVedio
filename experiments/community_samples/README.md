# 社区 H3 范文精选（2026-08-10 调研落盘）

> 来源：BeatAPI/awesome-minimax-h3-prompts（85★，2026-08-10 更新，205 条全量 clone 自 /tmp/beatapi/，本目录只收精选）
> 选择标准：source-verified（X 原文带视频证据）+ 模式/题材代表性 + 与本地 skill/IR 样本互补
> 格式说明：社区 prompt 多为自由格式（非官方六段式/三核心段），已保持原文不动；json 含 title/description/category/mode/duration/ingredients/source/prompt

| 文件 | 类别 | 模式 | 时长 | 来源 | 入选理由 |
|------|------|------|------|------|----------|
| image-1-starting-frame-474111.json | cinematic-travel | I2V（近似 IR 三核心段） | 20s | @EndFolding79421 | 社区里少见的完整三核心段写法 + `[0-4s]` 时间窗分段（与官方 [Shot N]+At 00:05.000 体系并行的另一种 IR 风格）；试镜读台词+落泪表演，S1 说话标签规范 |
| lilia-astra-title-sequence.json | title-sequence | R2V 多参考 | 15s | @haruuraeadss | 日文角色固定顶级写法：表情递进顺序（眼→眉→睑→口→视线）、材质分离清单、禁止列表（脸平均化/克隆/追加人物）、3D toon 渲染规范；R2V 长 prompt 范例 |
| is-seriously-good-at-this-kind-of-k-pop-lyric-987242.json | music-video | R2V 8图 | 15s | @MrLarus | K-pop 歌词 MV：8 参考图按序锚定 + Image 3 主脸锚 + 全程 lip-sync + 歌词字幕动画；多图角色一致性实战 |
| dark-pop-trio-music-video-performance-with-on-screen-titles-931081.json | music-video | R2V 双图 | 15s | @ivanka_humeniuk | 三人女团 dark-pop：Image1 严格身份锚（脸/发/衣不变）+ Image2 仅字幕样式锚；字幕与表演 beat 对齐 |
| jazz-noir-anime-title-sequence-652641.json | anime | R2V 图+音频 | 15s | @AIWarper | 音频即剪辑时间轴：每 cut 落在音频 beat；角色剪影+纯色底 pop-art 风格；视觉风格段落完整 |
| image-1-for-the-character-image-2-for-the-619967.json | gameplay | R2V 多图 | 15s | @craftian_keskin | 多图分槽用法范例：Image1=角色 / Image2=UI 风格 / 武器参考图=道具，逐槽语义锁定 |
| five-cinematic-dialogue-set-piece-scenes-875568.json | cinematic-story | T2V | 161s | @maxescu | 长片（161s）多场景对话段；跨段保持性写法，长 prompt 结构参考（约 20K 字符） |
| hip-hop-music-video-make-the-character-from-video1-107776.json | music-video | R2V 视频参考 | 108s | @bennash | 极简高效范例：@Video1 角色 + @Audio1 节拍 + lip-sync，一句话驱动；证明短 prompt 也能 R2V 出片 |

## 与本地知识库的衔接

- 官方格式基准仍以 `.pi/skills/h3-prompt-writing/references/*.txt` 为准（[Shot N] + At 00:SS.000 + 三核心段/六段式）
- 本目录价值 = 社区风格词汇/结构变体参考（R2V 长 prompt、多图分槽、字幕 MV、时间窗分段），供生成器 few-shot 与 docs/17 规则蒸馏用
- 全量 205 条在 /tmp/beatapi/prompts/（临时）；如需长期留存可再拷
