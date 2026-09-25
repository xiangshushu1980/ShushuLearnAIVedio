# FaceRefine 输出整理与待升级审计（Owner: Sean）

- Task Center：`T-comfy-ops-facerefine-output-tidy-20260925`。
- 清理目标：`/home/sean/projects/ComfyUI/output/face_solution`。

## 输出整理（2026-09-25）

- 盘点后将 46 个重复试验、重复 tracking 预览、已停用 Krea2 参考和已被代表结果覆盖的产物移入系统回收站（`gio trash`），不是永久删除；释放约 119,970,487 bytes（约 120MB）。
- 目录由约 178.7MB 收敛到 58.7MB，保留 23 个文件：FaceRefine 1.1.2 验收成片、T47 1344 主母片/精修对、第二条 headshake 对照、10 秒远景源与 face-only/gate 对照、H3-only/VOSR2 对、人物 mask 安全失败样本、latent 二采代表样本、像素阈值 contact sheet，以及 ClipVision 0.20/0.80 预分析证据。
- 关键升级验收产物：`/home/sean/projects/ComfyUI/output/face_solution/sean_facerefine_112_upgrade_20260925_00001_.mp4`。

## 待升级审计

- **NativeAudioLock**：本地与 `origin/master` 为 2 ahead / 1 behind；上游唯一待合并提交 `11a95f6` 为“optimized H3 chained workflows with Spectrum acceleration”。这是实际使用的节点，但由于分叉，必须先人工 diff/合并并用 NativeAudioLock 基线回归，不能直接 pull。
- **H3 ContactSheet**：本地与官方 `origin/main` 为 1 ahead / 1 behind；上游 `f4868b4` 是 v1.1.3。需要人工比较本地提交后再决定是否合并；当前并非 FaceRefine 或日常 VDN/音频链路的阻塞项。
- **Qwen-TTS**：落后 4 提交（XPU 适配、训练节点选项、SDPA 无可用 CUDA kernel 时的 fallback 等）。本地工作流未使用 Qwen-TTS，继续暂缓。
- **Ref-Patch**：本地 1 ahead / 上游 1 behind；上游仅 README 更新，暂不处理。
- **Breeze/VDN**：仍保持现状；原 Saganaki22 上游不可用，已登记官方参考仓，但其代码路线不适合直接覆盖当前验证的 24GB 工作流。

## 2026-09-25 复核修正：ContactSheet / NativeAudioLock

- 上一版审计将两者的 Git 分叉误写为“需人工合并”。复核后确认：两者均**没有待合并的本地节点逻辑修改**。
- **H3 ContactSheet**：本地是原始独立的五视角角色卡节点包，仅含 `H3ContactSheet`、`H3ContactSheetDecode`、示例脚本和说明。所谓上游 `v1.1.3` 是已迁移的 `matlowai/ComfyUI-MAINodes` 大包：ContactSheet 节点被保留，但额外引入 Motion Lab、时间线、去抖/修复、低显存实验、alpha 节点、示例与资产，约 225 个文件/13 万行。它是迁移到不同产品边界，不是本地 ContactSheet 的增量更新；默认保持独立节点，不迁移。
- **NativeAudioLock**：本地文件是上游 monorepo 中 `custom_nodes/ComfyUI-H3-NativeAudioLock/__init__.py` 的提取副本；源码 blob hash 均为 `77e4d7f446570480f8dc623058e82e1bd80d3551`，逐字一致。上游所谓 Spectrum 链式工作流提交是一次性加入 NativeAudioLock、Spectrum、Multishot 与模板的打包提交，没有后续 NativeAudioLock 节点逻辑更新。工作树的 `__pycache__/__init__.cpython-313.pyc` 只是运行时缓存，忽略即可。
- **Sean H3 人物参考流的实际使用**：ContactSheet 历史上用于 `workflows/h3_shushu_object_ref_probe.json`、`workflows/turnaround_test.json` 和 FaceRefine 研究脚本，作为“一张身份图 → 五视角风格化角色卡”的可选资产生产实验。当前正式 Sean Ref2VA 人物参考测试/生成流不调用 ContactSheet；它直接消费职责拆分的普通参考图（face identity、wardrobe/body、按镜头需要加入侧/背视图）。只有未来把 ContactSheet 产出的角色卡选作普通 object reference 时，才会间接使用其产物。
