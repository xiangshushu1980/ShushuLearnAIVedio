# [Sean] H3 人脸预分析与多 reference 外部方案研究

> Owner: Sean
> 状态：资料落盘，作为 T-comfy-ops-47 的续开研究依据。
> 研究区：`vendor/sean_source_research/`

## 结论摘要

当前主线使用的是我们从视频/素材中截取的 face-only identity reference；H3 的完整人物 reference 仍只负责局部重绘时的角色与服装语义。正在制作的 H3 多视角人物 reference 不应直接替代视频身份跟踪 reference。

外部资料已经分别实现了本方案的若干部件，但没有发现一个同时覆盖以下全部内容的现成实现：风格化角色的多视角身份库、视频全量预分析、多人脸与人物框联合关联、道具/骷髅误检排除，以及结构化 manifest 驱动的 H3 局部 latent refine。

## 外部方案

### face-finder：最接近预分析缓存路线

仓库：[athuler/face-finder](https://github.com/athuler/face-finder)

已实现：

- 单张或多张 reference 图片；
- 多 reference consensus / `min-matches` / strict 模式；
- 视频连续出现片段；
- 视频 hash、checkpoint、断点恢复；
- reference embedding 缓存和自动失效；
- CSV 与带框帧导出；
- 快速预筛后再做较重的 embedding 比对。

可借鉴：reference gallery、视频哈希、参数指纹、候选分数、连续区间和人工审查导出。不直接使用：它的目标是找出某人出现的时间段，不是 H3 局部重绘。

### ComfyUI-faceExtractor：ComfyUI 多 reference 方向

资料页：[llikethat/ComfyUI-faceExtractor](https://github.com/llikethat/ComfyUI-faceExtractor)

资料显示其设计包含 Face Reference Embedding、视频 Face Extractor、多个 reference、similarity threshold、streaming/chunked 模式和 extraction log。其 GitHub clone 地址当前返回 repository not found，因此本地未下载，只保留网页资料，不把它作为已验证代码依赖。

### ComfyUI-H3-FaceRefine 上游

仓库：[Carasibana/ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine)

已有能力：`identity_reference` 按身份选脸、逐 shot 选目标、连续性跟踪、一次检测后通过 `face_pick` 传递候选框，以及多人逐人运行再串联合成。

与我们正在增加的部分相比，仍缺少持久化候选 manifest、人物辅助关联、全局/镜头级多视角 gallery，以及基于源脸像素高度的 H3 refine gate。

### ComfyUI-facefusion：多人 reference face 选择

仓库：[bjfrbjx/ComfyUI-facefusion](https://github.com/bjfrbjx/ComfyUI-facefusion)

其 `reference_face_image` 可以在多人视频中选择相似人脸，并支持切换 YOLOFace、RetinaFace、SCRFD 等检测器。这验证了“reference face + 多人选择 + 多检测器”是成熟组件思路。

但它的目标是换脸/脸部增强，不是保持原动作和 latent 时序的 H3 局部重绘；其模型和许可证也不应直接成为本项目默认依赖。

## 对当前设计的影响

```text
全局人物 gallery：正脸、3/4、侧脸、稳定外观
        ↓
当前镜头 gallery：从当前视频中挑选清晰、姿态匹配的脸
        ↓
预分析：候选框 + 身份分数 + 人物关联 + 时空连续性
        ↓
manifest：每帧 accepted / ambiguous / tracking_lost / refine
        ↓
H3 局部 latent refine
```

全局 gallery 防止认错角色；镜头 gallery 适应当前画风、光照和侧脸角度。两者不能只用第一帧图片代替。

manifest 应保存：源视频哈希、FPS、分辨率、帧数、检测器版本、reference gallery 文件哈希、每帧全部候选框、检测分数、身份分数、人物关联分数、选中轨迹、`face_px`、`refine_start_px`、`tracking_lost`，以及人工确认覆盖版本。

## 已下载研究源码

下载到 `vendor/sean_source_research/`，只作研究，不自动安装、不接入生产：

- `face-finder/`：已下载；
- `comfyui-facefusion/`：已下载；
- `h3-face-refine-upstream/`：已下载；
- `comfyui-face-extractor/`：因仓库地址返回 repository not found，未下载。

## 后续测试顺序

1. 安全 reload 后让现有 `H3FaceManifestSave` 实际写出 JSON；
2. 用第一帧侧脸 + 肩部骷髅的视频验证全片预分析；
3. 加入正脸/3/4/侧脸多个视频 reference，比较单 reference 与 gallery；
4. 加入双人物视频，验证人物框关联能否拒绝肩部骷髅；
5. 最后让第二阶段读取 manifest 并运行 H3 refine。

## 2026-09-23 续开实现状态

- `H3FaceManifestSave` 的 JSON 已作为第二阶段输入契约使用；`H3FaceSelect` 新增可选 `analysis_manifest`。
- 第二阶段传入 manifest 后，会先校验 `kind/version`、源视频帧数与分辨率，再复用候选框、shot picks、检测参数和身份结果；不会加载 detector，也不会重新做 identity selection。
- `tools/h3_face_crop_refine_runner.py --analysis-manifest <path>` 已接入该路径，并关闭 `H3FaceTrackCrop` 的二次 identity tracking，保证 refine 阶段只消费预分析结果。
- 当前只完成代码与 AST 静态校验；需在下一次获准的 ComfyUI reload 后，用已有双人侧脸 manifest 做一次“预分析 → manifest → refine”闭环实测，确认节点注册和输出视频。
