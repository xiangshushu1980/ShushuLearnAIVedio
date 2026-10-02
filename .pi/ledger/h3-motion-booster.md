# H3 Motion Booster 结论谱系

Owner: Sean。独立记录本次新测试，避免修改其他任务正在维护的 h3-models.md。

### C-20261003-01 | Motion Booster V0.2 REF2VA 可加载、可生成；侧步单例存在白边代价
- 状态：🟡质量待用户验收；技术兼容性已验证（2026-10-03）。
- 现行值：Civitai 2840146 / version 3246346，`ref2VA_Motion_v2.safetensors`，触发 `dynv2`，与本机 Ref2VA INT8 ConvRot 底模的 208 组目标名称和矩阵形状匹配，ComfyUI 原生解析 208/208 补丁；0.7 和 0.8 两档均完整生成，运行日志无未加载键警告，无 OOM。
- 条件：ComfyUI 0.37.0、RTX 4090 24GB、单角色全身参考、正常侧步、同 seed 和完整六段式 prompt、768×448 / 124 帧 / 24fps、20 steps / res_multistep / simple、无加速 LoRA、原生 attention、INT8 video VAE / FP32 audio VAE / tiled decode。
- 质量边界：两档均出现白色左右留白；0.8 横向红色区域质心变化相对基线约 1.26×，0.7 约 1.08×。这是运动代理指标，受服装与姿势影响，不等同于动作正确率或普遍质量提升；保留现行生产基线。
- 时间线：2026-10-02 首次匿名下载明确 401；用户配置 API Key，2026-10-03 认证下载并核对 SHA256 后完成无 LoRA / 0.7 / 0.8 对照。无远程任务立项，用户质量验收待定。
- 当前模型登记：[docs/02_models.md](../../docs/02_models.md)。
- 证据锚：[实验 README](../../experiments/sean_h3_motion_booster_ref2va_20261002/README.md)、[QC](../../experiments/sean_h3_motion_booster_ref2va_20261002/QC.md)、manifest.json、lora_header_compatibility.json、lora_native_parser_check.json、两档 runtime.log 与 history、motion_metrics.json、audio_levels.json。视频与模型留本机。
- 覆盖关系：不覆盖 Turbo/PDD、FaceRefine 或 Ref2VA 生产结论；本次没有叠加这些路线。

### C-20261003-02 | 横幅参考解除0.7白边；修正固有1:1限制的归因
- 状态：✅单例修正已验证；普适质量和仅比例因果仍待验证。
- 当前操作：参考图优先采用接近目标输出比例的完整场景图。本例用原无LoRA视频解码首帧作768×448参考，0.7生成的124帧均为完整768×448有效画面，无白色侧边。
- 补测：原竖图1344×1536经match缩为544×640。输出文件宽高一直正确；原有效区域约442×448。0.7仅关闭参考VAE仍448×448，0.7仅加强横幅prompt仍448×448，0.7仅换横幅参考后有效区域768×448。各case保持seed、模型、采样与输出画布一致。
- 归因边界：结果支持参考构图/图像条件与LoRA交互，不支持LoRA只能生成1:1。横幅参考同时改变布局及渲染外观，因此尚未独立证明比例是唯一原因。新参考下的运动提升需要配对的新无LoRA基线，未扩大该矩阵。
- 时间线：2026-10-03 用户指出画面近1:1，核对容器、全帧白边、节点源码后完成三条消融。补测耗时67.476/70.375/69.487秒，全部成功，GPU已释放。
- 覆盖关系：细化C-20261003-01的白边适用条件；不能把原竖图单例的白边和暂不替换建议推广为所有参考输入下的固有限制。技术兼容、原始测量和声音记录不变。
- 证据锚：[QC](../../experiments/sean_h3_motion_booster_ref2va_20261002/QC.md)、aspect_diagnosis.json、aspect_check.py、三个补测workflow/history/ffprobe以及motion_07_landscape_ref.mp4；本地视频与参考图留实验目录。

### C-20261003-03 | 初测三档20步采样时间基本一致；总耗时差不能视为LoRA加速
- 条件：同C-20261003-01原竖幅参考三档，20-step res_multistep/simple；非重复随机化benchmark。
- 现行值：服务器最后20/20 tqdm均显示采样01:00；无LoRA与0.7为3.03秒/步，0.8为3.04秒/步。秒级日志下未见明显采样速度变化，不能推断所有场景零开销。总耗时94.296/67.257/66.890秒包含不同冷热加载与缓存，不能作为加速比。
- 职责边界：这是动作倾向LoRA，无减少采样步数或替换调度器。作者V2宣称主体动作、节奏、接触回弹、次级跟随与动作音频；独立飘带/风驱动布料动态未实测。
- 时间线：2026-10-03 用户询问速度影响，补取原baseline执行窗口日志，与0.7/0.8进度原文核对。
- 证据锚：sampling_timing.json、baseline_runtime.log、motion_07_runtime.log、motion_08_runtime.log；归档于同一实验目录。

### C-20261003-04 | 横幅长发/根须/飘带的风吹与转体配对；次级轨迹变化不等于普遍幅度增益
- 状态：✅四条技术验证完成；质量待用户查看同步视频。
- 条件：新 imagegen 树灵横幅参考（1642×958），银发、棕色附着根须、红飘带；各组同 prompt/seed 2026100302，权重0 vs0.7；768×448 / 192帧 / 24fps / 8秒，native Ref2VA INT8、20-step res_multistep/simple，无加速LoRA、原生attention、INT8 video VAE / FP32 audio VAE / tiled decode。
- 现行值：保持生产默认；基础H3已有长发/飘带动态，0.7在风吹抽帧中头发更早或更持续展开，转体改变节奏和轨迹，但根须和飘带未观察到稳定普遍增益。根须细且易遮挡；风吹的逆风侧飘带仍向外扬，转体两组均偏连续转身而未严格左右交替。未做物理评分、多seed或强度曲线。
- 性能证据：风吹0/0.7采样121/122秒（6.08/6.12秒每步），转体均122秒（6.11/6.13）；一次配对日志不能给出普遍精确开销。两组峰值23116→23804MiB。全任务154.446/130.697/135.951/131.314秒受加载缓存影响，不作加速比。
- 完整性：全部8秒音视频完整解码，所有192帧无白色侧边，无OOM/未加载键警告；0.7日志208 patches attached。产物哈希核对迁移至实验目录，本批output清理，lease释放。
- 覆盖关系：补足C-20261003-03当时“风/飘带未实测”的范围，进一步支持C-20261003-02横幅可全幅生成；不覆盖Turbo/PDD/FaceRefine基线、不宣称服装物理专用能力。
- 证据锚：[README与同步视频](../../experiments/sean_h3_motion_booster_secondary_20261003/README.md)、[QC](../../experiments/sean_h3_motion_booster_secondary_20261003/QC.md)、manifest.json、integrity.json、四条workflow/history/ffprobe/runtime.log、wind_contact.png与move_contact.png。视频和图留本机。

### C-20261003-05 | 同图同转体权重1.0：飘带未见稳定大幅增益，黑边重现
- 触发：用户认为0.7两张图差不多，明确要求权重1.0、人物动作与飘带补测。
- 条件：继承C-20261003-04的8秒转体prompt、横幅参考、seed与采样；唯一模型变化为0.7→1.0。工作流归一化后按组一致，参考SHA256校验通过。
- 现行值：暂不采用为默认。1.0改变早期朝向、转身节奏与飘带轨迹，抽帧尚未见稳定大幅增强；所有192帧出现150–151像素左右黑边，有效宽466–468、高448，容器仍768×448。没有裁切/拉伸交付原片。0/0.7四条同批均无黑白侧栏。
- 时间/完整性：总执行130.545秒，20步进度02:02 / 6.10秒每步，峰值23804MiB；8秒音视频完整解码，无OOM/未加载键警告、208 patches attached；原片迁移哈希一致，output清理、lease释放。
- 覆盖关系：限制C-20261003-02/04横幅全幅正常的权重适用范围；横幅参考并不保证1.0全幅。黑边与参考/权重交互具体机制未隔离，不断言所有1.0都方形。单参考单seed、动作执行偏连续转身，不构成飘带物理或单调幅度曲线。
- 证据锚：同一[实验README](../../experiments/sean_h3_motion_booster_secondary_20261003/README.md)、QC.md、manifest.json、integrity.json、move_motion10工作流/history/ffprobe/runtime.log、move_strength_comparison.mp4与move_strength_contact.png。新增媒体留本机。
