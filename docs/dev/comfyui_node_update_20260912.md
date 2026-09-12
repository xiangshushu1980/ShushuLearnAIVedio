# ComfyUI 节点来源与更新记录（2026-09-12）

## ComfyUI 核心

- ComfyUI：`v0.35.0-16-g7193f562`
- 前端包：`1.52.7`
- 工作流模板：`0.11.59`
- Transformers：`5.14.1`
- H3 相关核心更新已包含：PDD LoRA、H3 Fun ControlNet model patch、H3 Max、Reference 节点增强、H3 denoise mask 修复。

## 已有 Git 节点

2026-09-12 已将此前的非 Git 目录建立本地 Git 基线；有上游的目录同时配置了 `origin` 并抓取上游。

| 目录 | 来源/性质 | 本次状态 | 当前定位 |
|---|---|---|---|
| `ComfyUI-H3-NativeAudioLock` | `Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow` 子目录 | 已同步上游；提交 `18424e6` | 当前数字人基础链，保持启用 |
| `ComfyUI-H3-FaceRefine` | `Carasibana/ComfyUI-H3-FaceRefine` | 已同步 `v1.1.1`；提交 `e891d2a` | 后期小脸精修；历史效果差，暂不进基础链 |
| `ComfyUI-H3-ContactSheet` | 旧仓库已迁移至 `matlowai/ComfyUI-MAINodes` | 建立本地基线并绑定迁移后的上游；未覆盖旧目录 | 五视图/转身 LoRA 辅助，暂不替换 |
| `ComfyUI-MiniMax-H3-CondCache` | 本项目自有节点 | 建立本地基线；提交 `a947666` | 批量条件缓存，可选 |
| `ComfyUI-MiniMaxH3_Ref-Patch` | `lihaoyun6/ComfyUI-MiniMaxH3_Ref-Patch` | 与上游一致；建立基线 `ed2d172` | 参考图兼容补丁，按工作流需要 |
| `ComfyUI-SolAttn_triton` | `kijai/ComfyUI-SolAttn_triton` | 与上游最新主分支一致；基线 `c8d99b9` | 实验性/已弃用，不进正式链 |
| `comfyui-material-gallery` | 本项目自有修改 | 建立本地基线；提交 `213a8d5` | 本地素材库入口 |

## SolAttn 回归

- 工作流：`workflows/attn3way_dance_sol.json`
- 配置：H3 FL2VA int8、Turbo v4、1024×576、124 帧、8 步、无 SageAttention
- 结果：成功，H.264/AAC，124 帧，24fps，5.167 秒；输出 `dance_sol_00001_.mp4`
- 静态检查：`compileall` 通过，SolAttn 节点导入通过
- 结论：兼容性通过；抽帧未见明显崩坏，但没有足够证据推翻历史“高动态/低步数收益差、正式链不采用”的结论。上游 README 已标记 DEPRECATED，原因是新版 ComfyUI/comfy-kitchen 已内置优化 Sparse Attention。

## 加载检查

- 更新后 ComfyUI 日志显示 NativeAudioLock、FaceRefine、ContactSheet、CondCache、Ref-Patch、SolAttn、Spectrum 均成功加载。
- RMBG 的 SAM 可选模块仍缺 `segment_anything`、`iopath`；不影响 H3 基础链。
- 启动时存在 `user/comfyui.db` 锁竞争；不影响当前 HTTP 生成，但后续应避免多实例同时使用同一数据库。

## 后续纪律

- 更新前先保留本地提交；更新后用 `git log` / `git diff` 对照。
- NativeAudioLock 跟随上游更新后必须跑基础数字人回归。
- FaceRefine 只在基础成片稳定后做独立后期 POC。
- SolAttn 仅保留为历史复现，不作为新生产路线。
