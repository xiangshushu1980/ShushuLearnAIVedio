# 空间 job 文字验收

Owner: Sean

## 结论

**FAIL（结果可用作草稿，需完成下列小范围文字修订）**。job `b2d8117c-a7a8-4719-89c4-660754b9f94f` 状态为 `succeeded`，输出 revision 20。五镜顺序、ID、提示词内时长、对白和大部分角色/道具状态都正确；尚有明确的方位越界、可见道具缺少 reference 绑定、Ref2VA 格式错误与服装落点歧义。空间产物本身还把部分本轮授权的虚构调度误称为权威实体事实，并留下本可由输入优先级直接消解的确认问题。

## 验收范围与证据

- 唯一检查对象：`experiments/sean_film_pi_20261005/native-write-test/spatial-job.json`，只读取 `job.input.content.shots`、`job.input.spatialNotes/directorNotes` 与 `job.result` 的结构化文字；没有读取图片、调用生成/GPU，也没有改数据库或任务。
- job：`b2d8117c-a7a8-4719-89c4-660754b9f94f`，`kind=spatial`、`status=succeeded`、输入和输出 revision 均为 20。
- 按 `.pi/skills/h3-prompt-writing/references/ref-en.txt`、`docs/17_h3_prompt_writing_rules.md` 审核 Ref2VA 六段格式、英语输出、音频 retention 类型和对白标注。

## 通过项

- **镜头 ID、顺序和时长：通过。** `job.result.shots` 依次保持输入 ID：`51b9d957…`、`9478d1bf…`、`1e97e13e…`、`6df199fc…`、`5f220d41…`。结果对象不重复写 `durationSec` 字段，但五条提示词分别声明 exact six-, seven-, four-, six-, seven-second duration，与输入 `6/7/4/6/7s` 对应；合计 30 秒。
- **台词：通过。** 五镜 `<d>` 内的中文与对应输入 `dialogue[].text` 逐字一致、次序一致，语言标签均为 `[Chinese]`。无声镜 3 正确写 `No dialogue`。S1/S2 按实际每镜说话次序分配，跨同一镜内台词稳定。
- **多数素材绑定与声音来源：通过。** 已定义的 Library、角色 A/B、刀、休闲服、派生外观图片标签按各镜输入图片顺序匹配实体；Audio 标签与该镜说话者匹配。派生声音资产继承角色 A 的源音频 hash；镜 5 复用 S1，结果还说明角色 A 穿上休闲服后成为派生状态，未把它写成第三个剧情人物。
- **主要跨镜状态：通过。** 全镜共用 T1；A 位于近侧 C1，B 位于远侧 C2；刀在 M1，先留在桌面、镜 4 被 B 带走、镜 5 不在桌面；B 的休闲服在 M2 留到镜 5 再被 A 穿上。B 在镜 3 脱衣后仍坐 C2，镜 4 起身取刀离场，符合当前 `content.shots` 动作。

## 必须修正的问题

1. **绝对方位违背本轮约定。** `job.result.scenePlan` 将机位写成“P1 南侧向北看”，并给书墙指定“北侧与西侧”；镜 1 的 detailed description 也重复北/西墙。job 输入约定明确禁止东南西北方位。本轮虽授权 T1/C1/C2/M1/M2/P1 虚构调度，但没有授权绝对方向。改用 camera-side/near-side/far-side 等相对桌面关系，并删去所有 north/south/east/west 位置。

2. **镜 2、镜 3 的刀缺少图像 Subject 绑定。** 这两镜的 prompt 在 detailed description 中把刀作为可见物放在 M1，但相应 `subject_definitions` 没有刀，且这两镜的输入 `imageAssetIds` 也不含刀的 reference（实体/图片仅出现在镜 1、镜 4）。不能声称这两镜能按“同一参考刀的大小与形态”保持视觉连续。最小修订是让镜 2、3 的生成输入包含已有刀参考图，并增加刀的稳定 Subject 绑定；否则 prompt 应避免宣称按参考图锁定尺寸/外形。

3. **镜 5 的 M2 同时指向两处服装。** 场景计划把 M2 定义为远侧桌面的 B 服装点；镜 5 prompt 又写 A 把自己的衣服“放在近侧的 M2”，再从远侧同一 M2 取 B 的衣服。结果 start/end state 和 `questions` 也暴露此位置冲突。选定一个明确的 A 衣物暂放位置，使其与仍在 M2 的 B 衣物分开；不增加新家具、衣物或尺寸，也不要复用 M2 表示两个同时占用的位置。

4. **Ref2VA 输出格式不合规则。** 多处 `subject_definitions` 是中文标签速记（如 `<Subject 1> 图书馆 (Picture 1)`），并非规范要求的英文定义句；`retention_analysis` 也是无镜次、无说明的中文名加状态列表。全部段落应写英文，中文只保留在 `<d>[Chinese]…</d>` 和确需显示的原始画面文字；retention 行按规范引用 `<Subject N>` / `<Audio N>`、出现镜次及保留理由。

5. **音色参考的 retention 类型错误。** 所有 voice-timbre `<Audio N>` 在 retention_analysis 写作 `fully_preserved`。官方 Ref2VA 对只参考音色、不复制音频规定用 `reference`；应在所有含声音参考的镜头逐处改正。

6. **空间计划误报权威来源，并残留不必要确认。** 本轮输入明确说明 T1/C1/C2/M1/M2/P1 属于用户授权的虚构调度约定，不是实体中心确认事实；结果却称“权威空间事实（来自图书馆实体与 currentFilmSpaceInstructions，不增不减）”，容易把虚构布局升格为实体事实。应改称“本轮授权的 proposed blocking”，实体外观与调度提案分开。结果 `questions` 中“B 全程落座 vs 镜 4 离场”及旧空间稿镜次划分冲突，可按输入第 7 条直接以当前 `content.shots` 为真值消解，不再要求人工确认；服装内层和具体拆件同样可以在提示词中继续保持未说明，不构成阻塞问题。

## 最小修订清单

- 全文删去绝对方位，统一使用近侧/远侧/机位侧。
- 对镜 2、3 加入已有刀图的 Subject reference 绑定；镜 5 明确 A 衣物暂放位置与 B 服装 M2 分开。
- 将 Ref2VA 的 subject definitions / retention analysis / description prose 改成英语；所有音色引用的 retention 标记改为 `reference`。
- 将布局标作本轮授权提案，并按当前拍摄本消解旧空间稿冲突；保留服装细节未知，不等待人工补设定。

验收只涉及文本、引用绑定与状态连续性；没有做视觉或影片质量验收。

## Corrected spatial draft 复验

修订稿位于 `evidence/corrected-spatial-result.json`，顶层只保留 `scenePlan`、`questions`、`shots` 这组空间结果字段，可作为离线 review draft 检视；本轮没有将它写入数据库或采用。

- **格式与内容：通过。** 五镜 prompt 均按 `subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape`、`non_diegetic_music` 顺序写成英文冒号字段；对白仅在 `<d>[Chinese]…</d>` 中保留原文。音色参考的 retention 统一标记为 `reference`。
- **逐镜对白、ID、顺序、时长：通过。** 对照原 job 输入逐镜验得 ID 与顺序一致；对白逐字、次序和 `[Chinese]` 标签一致。时长分别为 6、7、4、6、7 秒，总计 30 秒。五段 `detailed_description` 实际词数分别为 **420、378、413、395、430**，均在 Ref2VA 的 350–500 词范围内。
- **空间约定：通过。** 只写用户授权的 proposed blocking 与近侧/远侧/机位侧关系；同一 T1、C1/C2、M1/M2、P1 的道具和角色状态连续，不再将提案说成实体中心确认事实，也没有写绝对方位。
- **未解决项：未采用。** 镜 2 与镜 3 的 source `imageAssetIds` 缺少现有“一把刀”图像；review result 不含也不能修改输入绑定，因此没有伪造 `<Picture N>` 标签。该项仍留在中文 `questions`。B 的内层服装、A 自身衣物组成、休闲服构成件数也都只标为资料缺失，没有替用户做取舍。以上问题未解决，故该 corrected result 仍是审阅草稿，未提交/采用。

词数复验采用每段 `detailed_description` 的空白分词；ID、台词、语言标签、字段顺序、时长和方向限制通过只读脚本核对。没有读图、调用 GPU 或写入影片/任务状态。


## Clip 内 Shot 标签复核（追加）

Owner: Sean

服务端验收提醒指出上一版使用全片镜次编号，须在每个独立 clip 内从 `[Shot 1]` 开始。对当前离线 `corrected-spatial-result.json` 逐 prompt 及 `retention_analysis` 检查后，五个 clip 均只出现 `[Shot 1]`，没有 `[Shot 2]` 至 `[Shot 5]`；因此当前文件已满足该项，外层 shot ID、顺序、对白和时长未改。

尝试对原空间 job `b2d8117c-a7a8-4719-89c4-660754b9f94f` 调用只读 `validate-spatial` 时，服务返回 HTTP 409「空间修订稿不可编辑」；随后只读查询发现该 job ID 在当前服务项目导出中不存在，项目当前 revision 为 18，与验收稿的 revision 20 不符。因此本次不能把当前服务端 API 验证记为通过，也未对数据库执行保存或采用；当前离线格式复核不能替代 business 对实际目标项目版本的服务端验证。

## 最终服务端复验（Owner: Sean）

原生 PI 已实际保存修订稿并保留原 result/影片 revision20。首次文字自检漏了 detailed_description 内的 [Shot 1]；标签只在 retention，服务校验正确报告5条警告。Root补齐时间线标记后又修正镜5派生外观 Subject 的实际说话标签，通过共用 validate-spatial/spatial-draft 接口复验并保存：warnings=[]，questions=4，valid=false，未采用。最终证据 sean_final_spatial_validation.json；资料缺口真实保留，不将格式通过宣称为视频效果通过。
