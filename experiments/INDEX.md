# 实验资料索引与维护规则

> 本文件只做实验资料导航和生命周期管理，不复制实验结论。实验结论以 `docs/`、`.pi/ledger/` 和 Mem0 为准；实验目录保存可追溯证据。

## 生命周期

| 状态 | 含义 | 处理规则 |
|---|---|---|
| `planned` | 已登记、尚未完成 | 保留目录和 manifest；开始生成前补齐输入与输出契约 |
| `active` | 当前正在运行或持续追加 | 不移动、不删除；结果和 QC 持续追加 |
| `review` | 生成完成，等待人工或质量验收 | 保留原始证据；结论未确认前不能提升为 canonical |
| `completed` | 实验已定论 | README 写清结论和边界；可清理重复派生产物 |
| `reference` | 稳定的历史样本或可复用资料 | 保留关键证据；若被新资料替代则转为 `archived` |
| `blocked` | 因资源、质量或外部依赖无法继续 | README 记录阻塞原因；解除后回到 `active`，否则归档 |
| `archived` | 被新实验替代，但仍需追溯 | 移到 `experiments/archive/`，并在 `docs/archive/README.md` 登记 |
| `deletable` | 已确认没有追溯价值或为可再生缓存 | 先查引用和 manifest，再删除；不要仅凭目录日期删除 |

状态以实验目录内的 `manifest.json` 为准；没有 manifest 的历史资料以 README、任务记录和本索引为准。目录的修改时间不代表生命周期。

## 当前资料

| 资料 | 状态 | 用途 / 维护动作 |
|---|---|---|
| `qwen_image_2_1_multiref_20261001/` | `review` | Qwen-Image-2.1 角色编辑测试；双人脸朝向、剑盾配合动作和帽子/王冠测试已完成 |
| `krea2_turnaround_sheet_batch_20260926_v1/` | `planned` | 当前 Krea2 turnaround sheet 批次；生成后更新 manifest 的 `results`、QC 和状态 |
| `krea2_front_back_consistency_20260926_v2/` | `review` | v1 的输入与对照证据；保留 raw、QC 和失败边界 |
| `krea2_front_back_consistency_20260926/` | `completed` | v2 的旧规格基线；仅在追溯旧方案时使用 |
| `krea2_turnaround_sheet_test_20260926/` | `review` | 首个单角色 turnaround sheet 先导实验 |
| `krea2_multi_reference_20261001/` | `review` | Krea2 双脸、场景和物品多参考图合成；逐图结论见目录内 `QC.md` |
| `krea2_single_character_refs_20261001/` | `review` | Krea2 单角色脸、服装、装备和场景参考对照；逐图结论见 QC.md |
| `krea2_shared_costume_weapon_20261002/` | `review` | Krea2 双人同款制服、武器的一致性对照实验；逐图结论见 QC.md |
| `qwen_image_2_1_shared_costume_weapon_20261002/` | `review` | 使用与 Krea2 相同的人物、制服和武器参考对照双人统一装备；逐图结论见 QC.md |
| `qwen_image_2_1_bare_face_uniform_20261002/` | `review` | 对比含服装脸部 crop 与裸肩头部身份图对双人制服/手部的影响，短提示词、暂不加物品；逐图结论见 QC.md |
| `qwen_image_2_1_duo_proportion_20261002/` | `review` | 对比数值 8 头身提示词与双人灰衣比例参考图；目视看比例图两 seed 都改善头身比，逐图结论见 QC.md |
| `qwen_image_2_1_text_proportion_height_20261002/` | `review` | 不加比例图，三组文字控制对照；相对身高差表现清晰，8/9 头身差未稳定显现，逐图见 QC.md |
| `qwen_image_2_1_single_body_type_20261002/` | `review` | 单人物固定脸/制服/武器/场景，文字能区分三种体型但姿势/画幅仍漂移；逐图见 QC.md |
| `qwen_image_2_1_charactersheet_v3_domain_validation_20261003/` | `review` | V3 角色脸部+正侧背、盾牌、提灯与场景多视图验证；Katana 跨视图结构仍不稳定，见 QC.md |
| `h3_reference_pipeline/` | `review` | T47-1 设定图与 H3 reference 管线；按 manifest 的 gate 推进 |
| `h3_character_reference_test/` | `reference` | 已完成的 H3 角色参考组织测试；文字清单与 prompts 已迁入，生成结果见 [ComfyUI output 归档索引](comfyui_output_archive_20260928.md) |
| `h3_face_solution/` | `completed` | 远景小脸修复当前基线与边界；稳定结论同步到 `docs/39`、`docs/40`、`docs/43` |
| `h3_vae_upgrade/` | `active` | Sean 的 H3 VAE / Ref2VA / FaceRefine 复测；结论确认后提炼到 docs/ledger |
| `h3_ref2v/` | `reference` | Ref2VA 批量案例和结果证据 |
| `h3_digital_human/` | `reference` | 数字人、MC、NativeAudioLock 等历史/对照案例 |
| `breeze_tts/` | `reference` | Breeze TTS 当前保守基线和 POC 记录 |
| `prompt_compare/` | `reference` | 提示词模型对照样本；新批次继续使用现有脚本入口 |
| `mc_test/` | `reference` | MC 历史测试输入和结果 |
| `spectrum_ab/` | `reference` | H3 spectrum 速度/画质对照证据 |
| `ir_samples/`、`community_samples/` | `reference` | 官方 IR 与社区 prompt 参考样本 |
| `shotlist/`、`speech-video/` | `reference` | 分镜和音频+文字视频管线的可复用资料 |
| `archive/` | `archived` | 已完成、被替代但仍需追溯的实验；进入前需更新归档索引 |
| `comfyui_output_archive_20260928.md` | `archived` | 2026-09-28 ComfyUI output 快照的外部归档位置和旧路径映射 |

## 新实验的最小文件

```text
experiments/<experiment_id>/
├── README.md       # 目的、输入、结论、边界、证据链接
└── manifest.json   # 机器可读状态、参数、输入/输出路径、来源关系
```

manifest 至少包含：`owner`、`experiment` 或 `batch_id`、`status`、目的、输入/输出路径，以及 `source_manifest` 或 `supersedes`（如果存在前序实验）。Sean 新增实验按项目约定写入 `owner: Sean`。

## 日常维护流程

### 1. 创建或开始实验

- 新建目录和最小 README/manifest。
- `status` 从 `planned` 开始；正在生成时改为 `active`。
- 输入图、模型、prompt、ComfyUI 输出路径写入 manifest，不把大模型或可再生缓存复制进仓库。

### 2. 追加结果

- 结果文件放在实验目录内，或在 manifest 中记录外部输出的绝对/项目相对路径。
- QC 通过/失败、人工复核和阻塞原因写入 README 或 `QC_NOTES*.md`。
- 不用重命名覆盖旧结果；新一轮使用新的 `experiment_id` 或明确的 v2/v3。

### 3. 收尾

- 结论稳定后，先把当前结论提炼到对应 `docs/` 或 `.pi/ledger/`。
- manifest 改为 `completed`、`review` 或 `blocked`，并记录 `canonical_doc` / `evidence`。
- 重复拼图、临时帧、可再生缓存可以删除；原始输入、关键输出和失败证据保留。

### 4. 移动或删除

移动前在项目根执行：

```bash
rg -n 'experiments/<旧路径>' docs .pi scripts workflows tools
```

同步修改脚本、任务记录、manifest 和本索引。归档实验移入 `experiments/archive/<topic>/`，并更新 `docs/archive/README.md`。只有状态为 `deletable` 且无引用时才直接删除。

### 5. 定期检查

维护时重点检查：

- 索引路径是否存在；
- manifest 中的 `source` / `supersedes` / `output` 是否仍可追溯；
- 是否有“当前结论只存在实验 README、尚未进入 docs/ledger”的情况；
- 是否有已经完成却仍标记 `active` 的目录；
- 是否有大体积、可再生、无引用的派生文件。

未来如果重复出现这些检查，再补一个只读校验脚本；在此之前不引入数据库或常驻管理服务。
