# [Sean] T47-1 单物体高清统一流程决策记录

date: 2026-09-26
status: decision recorded; no new generation in this update
owner: Sean

## 目标

Reference 的交付目标是“高清细节 + 高度统一”，不是让一段低清 H3 视频同时承担所有职责。当前只讨论单个角色，不启动五对象并行。

## 已确认的职责分离

| 资产 | 真值来源 | 主要职责 | 当前状态 |
|---|---|---|---|
| `F0` / `F` | 已覆盖的高清唯一正脸流程 | 身份、五官、发型前侧；必要时扣出纯脸 | canonical 入口，待本轮单物体重接 |
| `W0` / `W` | 与 `F0` 同一身份源的高清全身图 | 服装、体态、装备、轮廓、鞋 | 必须单独高清确认 |
| `WB` | 从 `W0` 去脸/去头整理 | 降低脸与服装的条件竞争 | 在 `W0` 通过后生成 |
| `S/Q/B` | `W0` 驱动的 H3 turnaround 帧 | 侧面、3/4、背面和隐藏服装/装备 | H3 通过后再高清化 |
| H3 原视频/原始帧 | 单对象 H3 | 时序、转身、服装一致性证据 | Character A 已有 smoke |

关键原则：`F0` 不从低清 H3 视频硬裁脸；`W0` 不从低清 H3 全身帧冒充高清；`S/Q/B` 不独立随机生图。

## 采用的单物体流程

```text
F0 高清正脸
  → W0 高清全身
  → WB 去脸/去头服装图
  → H3 Ref2VA turnaround（只输入 W0）
  → H3 review
  → 选择 S/Q/B 原始帧
  → 直接图像超分 A/B
  → 必要时低 denoise 图像 latent 二采
  → package review / manifest
```

H3 视频的首要验收项是整体人物、侧面、背面、服装和配饰是否统一；它不承担远景小脸的高清恢复。完整视频 latent 二采作为整体视频交付路线保留，不纳入当前 reference 默认链，因为本地证据表明它主要保持结构/时序，不能保证恢复小脸身份细节。

## S/Q 高清化决策

1. 先保存 H3 原帧，原帧永远是证据和回滚源。
2. 第一对照使用直接图像超分：风险最低，先观察是否只增加纹理而不改变服装和脸。
3. 只有直接超分不足时，才对同一帧做低 denoise 图像 latent 二采；必须与原帧、直接超分并排 QC。
4. 任一高清化路线若改写身份、发型、衣服、配饰或视角，标记 `experimental`/`rejected`，不得覆盖原帧。
5. 只有通过 package review 的 S/Q 才能成为 `conditional`；B 同理，但要额外检查背部隐藏装备的一致性。

## 当前证据

- H3 输入主图：`/home/sean/projects/ComfyUI/input/sean_t47_1_ref_v1_character_a.png`
- H3 prompt：[`prompts/character_a_turnaround.txt`](prompts/character_a_turnaround.txt)
- H3 视频：[`character_a_silver_elf_archer/02_h3_turnaround/turnaround_test_00001_.mp4`](character_a_silver_elf_archer/02_h3_turnaround/turnaround_test_00001_.mp4)
- review 抽帧：[`character_a_silver_elf_archer/03_review_frames/turnaround_keyframes.png`](character_a_silver_elf_archer/03_review_frames/turnaround_keyframes.png)
- 参数：`768×448 / 192 frames / 8.000s / 24fps / 20 steps / res_multistep / seed=4701201`
- H3 prompt id：`3a07a19b-3536-4153-a931-8127020edbd3`

初步观察：Character A 的前、侧、背、回正结构和服装连续性基本可用，但该 smoke 分辨率导致细节偏软；因此当前没有生成最终 F/W/WB/S/Q/B，也没有合成组合图。

## 2026-09-26 高清静帧候选已生成

在 Character A H3 turnaround 通过 review 后，按本流程生成了两张待审查静帧；两张均使用同一主图 `/home/sean/projects/ComfyUI/input/sean_t47_1_ref_v1_character_a.png`，没有使用 H3 低清帧作为输入：

| 候选 | 尺寸 | 模式 | seed | prompt id | 文件 |
|---|---:|---|---:|---|---|
| `F0_front_hd` | 1344×1344 | `identity_portrait` | 4701202 | `8ed468e6-ece6-48d4-9b61-ec2f715dbe90` | `/home/sean/projects/ComfyUI/output/sean_t47_1_hd_stills_20260926/character_a/F0_front_hd_00001_.png` |
| `W0_full_body_hd` | 1024×1536 | `wardrobe_full_reference` | 4701203 | `f20949ea-35e4-4843-915d-3d917c288f39` | `/home/sean/projects/ComfyUI/output/sean_t47_1_hd_stills_20260926/character_a/W0_full_body_hd_00001_.png` |

两张候选的 SHA-256、参数和输出路径已写入 `manifest.json`。当前仅标记为 `awaiting_still_review`，不把它们提升为 canonical。

## 当前暂停点

等待 Sean 检查 `F0/W0` 是否统一。通过后才整理 `WB`，再从已通过的 H3 视频中选择 S/Q/B 帧并进行直接超分 vs 图像二采对照。此次尚未生成 WB、S/Q/B 或组合图。

## [Sean] 2026-09-28 H3 多角度一致性观察（待复核）

用户反馈：以前的 H3 视频多角度生成流程里，物品与场景无法稳定保持一致性。该观察先作为风险记录，不提升为普遍结论：目前未在本轮定位到对应的旧视频、输入图、prompt 与 manifest，也未对它们重新逐帧复核。

本批次 manifest 中的 scene 与 prop job 仍为 `blocked_until_character_a_review`；本批实际只跑过 Character A 的 8 秒 turnaround smoke。因此这里不能把本批当作物品/场景一致性的验证。后续如复查，应先定位旧产物和对应条件，再分别评估物品形态/配件及场景布局跨视角是否保持；通过 QC 前不能把该链路描述为可靠的物件或场景 Reference 生成器。
