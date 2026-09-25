# H3 模型/可行性结论谱系

> 模型选型与可行性定论演进史。规则见 README.md。append-only。

## 条目索引

| C-ID | 主题 | 状态 | 备注 |
|---|---|---|---|
| C-20260816-20 | Hybrid b25-49（fl2va+ref2va merge） | 🟡待验证 | 已拆 T-20260815-09 深度测试 |
| C-20260816-21 | 防 OOM flags 全退 | ✅现行 | 灾难性慢 3.7x |
| C-20260816-22 | SageAttention v2 无需 patch | ✅现行 | int8QK+fp8PV kernel |
| C-20260816-23 | Sol Engine 未开源 | ✅现行 | 组件拆解 |
| C-20260816-24 | fal H3 定价 | ✅现行 | $0.16/s@768p，未注册 |
| C-20260816-25 | FaceRefine 精修参数铁律 | ✅现行 | 官方参数原样不可改 |
| C-20260816-26 | Cache-DiT 加速（官方宣称） | 🟡待验证 | T-20260815-10 待实测 |
| C-20260816-27 | H3 能力边界（固定音频同步） | ✅现行 | 数字人方案弃用 |
| C-20260825-01 | H3 TE 精度选型（NVFP4 维持定论） | ✅现行 | 高精度 INT8 无收益/放不下/不支持参考流 |
| C-20260825-02 | v4-600EMA 无法跨用 ref2va pruned（LoRA 键名不匹配） | ✅现行 | 518 键未加载/0 加载 |
| C-20260917-01 | VDN Ref2VA 1024×576/20s + NativeAudioLock 验收基线 | ✅现行 | T-comfy-ops-VDN-01 |
| C-20260922-01 | H3 FaceRefine 远景小脸稳定性与分辨率边界 | ✅现行 | T-comfy-ops-47 |
| C-20260922-02 | VOSR2 本地安装与图像/短批次 smoke | 🟡待验证 | 图像质量通过；长视频时序未验收 |

---

### C-20260922-01 | H3 FaceRefine 远景小脸稳定性与分辨率边界
- 状态：✅现行（valid_from 2026-09-22）
- 现行值：**当前默认采用局部 latent FaceRefine + H3InjectVideoLatent + face-only rectangular stitch；ClipVision 负责非真人/插画角色身份跟踪，完整人物图只给 H3 object reference，face-only 图只给跟踪。** 保守参数为 768 crop、crop_factor 3.0、8 steps、base denoise 0.28、per-frame 0.65/.25、smooth 15。该链路在中景至正常远景能明显抑制劣化和跳脸；脸缩小到约 20–35px 后 face detector 掉检，不能恢复不存在的身份细节。
- 时间线：
  - 2026-09-22 提出：旧基线使用 768 crop、denoise 0.40、per-frame 1.0/.35、smooth 9。
  - 2026-09-22 修正：保守参数 0.28 / .65/.25 / 15 在 124 帧旧 1344 母片和 241 帧 10 秒远拉源片上更稳定；768 长片约 260.1s，1024x1024 约 610.3s 且未见明显锐度收益，native 1344x768 约 616.0s 也未解决软化，故更大画布不作为默认值。
  - 2026-09-22 边界确认：全人物 YOLO/mask 可把跟踪延伸到远景，但主要保证连续性；face-only 与人物 refine 的选择必须分开比较，不把人物 mask 当作细节恢复方案。
- 证据锚：`.pi/tasks/T-comfy-ops-47/progress.md`；产物 `/home/sean/projects/ComfyUI/output/face_solution/t47_face1344_10s_clipvision_faceonly_20260922_00001_.mp4`、`t47_person1344_10s_fullcrop_rect_20260922_00001_.mp4`；观测 `e38ecab4-ca30-4edb-9b30-a9219c9b360e`、`59967e24-1ba7-4345-a9a5-9520b66f7c2c`。

### C-20260922-02 | VOSR2 本地安装与图像/短批次 smoke
- 状态：🟡待验证（valid_from 2026-09-22）
- 现行值：VOSR2 1.4B 本地节点与权重已安装并被 ComfyUI 识别；`fp16 + wavelet + DiT 512/64 + VAE 1024/128` 下，1024² 输入 2x/4x 单图分别成功输出 2048²/4096²，约 12.9s/24.6s；3 帧 512x288 视频批次 2x 成功输出 3 张 1024x576 图像。当前结论仅覆盖安装、加载、显存可行性和短批次链路，不覆盖长视频帧间一致性。
- 时间线：
  - 2026-09-22：主 checkpoint、Qwen-Image 2D VAE、DINOv2-L 落盘；修正 `args.json` 层级并完成 DINO safetensors 转换；ComfyUI 重启后 object info 注册成功。
  - 2026-09-22：单图 2x、4x、seed 43 对照和 3 帧视频 batch smoke 全部成功；目视未见明显 tile seam，seed 改变会带来轻微生成细节变化。
- 适用边界：VOSR2 当前作为生成后图像/短批次细节重建候选；不能据此替代 H3 latent 二采或宣称长视频 temporal consistency，后续需用连续长段做闪烁、身份漂移和动作保持验收。
- 证据锚：`docs/39_h3_latent_upscale_face_research.md`；`.pi/tasks/T-comfy-ops-47/progress.md`；产物 `/home/sean/projects/ComfyUI/output/vosr2_quick_2x_00001_.png`、`vosr2_quick_4x_00001_.png`、`vosr2_quick_2x_seed43_00001_.png`、`vosr2_quick_clip_3frames_2x_00001_.png`–`00003_.png`。

### C-20260816-20 | Hybrid b25-49（fl2va+ref2va merge）
- 状态：🟡待验证（动画域已实测通过，写实域结论待深度测试 T-20260815-09）
- 现状（08-17 用户确认跟踪暂停）：模型在库（models/diffusion_models/，08-15 下载）；深度测试线 T-20260815-09 未在跑，暂挂起；非模型更新，勿当疑似更新排查
- 现行值：**动机 = ref2va 精度低 + fl2va 画质好 → 融合出精度可接受且仍受 ref 控制的版本**；动画域 ref2va 画质提升显著（Laplacian 43→**54，+26%** 清晰度，耗时 80s→60s）；写实域无优势（耗时打平 60s 且没脸待查）；dtype = int8 混合精度（F32/BF16/F16/I8/U8）20.97GB，24GB 可跑；权重选择 merge（非微调），Ref2VA drop-in 替换，作者推荐 b25-49
- 时间线：
  - 2026-08-15 提出：三方对比（ref2va_pruned_int8 80s/43 vs hybrid b25-49 60s/54 vs fl2va+RefPatch 56s/46；RefPatch 提升有限；来源任务 T-20260815-07）
  - 2026-08-15 补充：写实域耗时打平且"没脸"→ 拆 T-20260815-09 独立深度测试（写实域状态🟡）
- 证据锚：.pi/tasks/h3-new-findings-test/progress.md / output/compare/ref2va_vs_hybrid_vs_refpatch.png / TODO T-20260815-09

### C-20260816-21 | 防 OOM flags 全退
- 状态：✅现行（valid_from 2026-08-11）
- 现行值：`--disable-pinned-memory --disable-smart-memory` 实测**灾难**——1344×768 每步 394s（42min/条，默认 ~11.5min 慢 3.7x）、1024×576 239s vs 158s（慢 51%）；原因 = smart memory 禁用后强制 offload；yume 建议不适用本机（64GB RAM + 4090 默认配置更优），已恢复默认参数重启
- 时间线：
  - 2026-08-11 提出（T2 实测；来源任务 h3-today-testing）
- 证据锚：.pi/tasks/h3-today-testing/progress.md（T2 结论）

### C-20260816-22 | SageAttention v2 无需 patch
- 状态：✅现行（valid_from 2026-08-11）
- 现行值：sageattention 2.2.0 sm89 走 int8QK+fp8PV CUDA kernel（日志无 launch-fail / 无 fallback，速度达标）；驱动 610.88（>580）+ CUDA 13.3 满足 int8_convrot；yume 的 patch/driver 建议针对旧环境，**不适用本机**
- 时间线：
  - 2026-08-11 提出（T4 实测；来源任务 h3-today-testing）
- 证据锚：.pi/tasks/h3-today-testing/progress.md（T4 结论）

### C-20260816-23 | Sol Engine 未开源
- 状态：✅现行（valid_from 2026-08-11）
- 现行值：Sol Engine 本体**未开源**（NVIDIA 内部，8×GB200 部署，nvlabs.github.io/Sana/Sol-Engine/H3/）；组件拆解 = First Block Cache（ParaAttention，等价 MotionCache 已测）+ Sol-Attn（arXiv:2607.24027，training-free 稀疏注意力，未来关注 ComfyUI 实现）+ kernel 融合（int8/convrot 已覆盖）；本地可落地部分已由现有栈覆盖 → 观望
- 时间线：
  - 2026-08-11 提出（T5 调研；来源任务 h3-today-testing）
- 证据锚：.pi/tasks/h3-today-testing/progress.md（T5 结论）

### C-20260816-24 | fal H3 定价
- 状态：✅现行（valid_from 2026-08-11）
- 现行值：fal H3 = **$0.16/秒 @768p、$0.26/秒 @2K**（vs 官方 0.8 元/秒）；规格 1440p / 7000 字符 / 15s；**用户未注册（无 key，未实测）**
- 时间线：
  - 2026-08-11 提出（T6 调研；来源任务 h3-today-testing）
- 证据锚：.pi/tasks/h3-today-testing/progress.md（T6 结论）

### C-20260816-25 | FaceRefine 精修参数铁律
- 状态：✅现行（valid_from 2026-08-14）
- 现行值：**官方参数原样不可改**（改任何一项 → 特写马赛克）：LoRA fl2v v0.1 comfy @0.75（非 v1.0 768p）、er_sde + simple 4 步 denoise 0.45、PerFrameDenoise 0.8/0.35、crop 512² factor 3、fallback none；必须传原视频原始 prompt（占位符劣化重生成）；管线 = Turbo 4 步（40s）+ FaceRefine（30s）= 70s 可验收；FaceRefine 是成片档工具不进快速档；**双人场景否决**（检测乱飞，T-20260814-10）；远处小脸改善方向未测（阈值 0.35→0.2 / crop 768 / 强度 1.0）
- 时间线：
  - 2026-08-14 提出：v1-v3 改参数全部马赛克 → v4 官方参数原样干净（用户目视确认）；第二条不同 seed 验证通过（来源任务 h3-ref2v-pilot FaceRefine 线）
- 证据锚：params.md §FaceRefine 精修参数 / .pi/tasks/h3-ref2v-pilot/progress.md（FaceRefine 线）/ output/compare/h3_facerefine_T1*.png（在 ~/projects/ComfyUI/output/compare/）

### C-20260816-26 | Cache-DiT 加速（官方宣称，待本地实测）
- 状态：🟡待验证（官方 same-seed 宣称，未本地实测）
- 现行值：ComfyUI-CacheDiT（Jasonzzt）2026.08 已加 H3 支持——官方 T2V/I2V/R2V same-seed 验证 **1.41-1.50x**，保立体声音频；H3 走 Pattern 3 DBCache 自适应（fn_blocks=8 / bn_blocks=0 / threshold 0.12 / warmup 3）；**warmup 3 步对 turbo8 快车道收益存疑**（README：<6 步不值得、low-step 未验证），慢车道 std14/20 收益最优；与 MotionCache/Motion-Context 同属 residual reuse 家族，叠加/重叠未测；底层 = vipshop/cache-dit（已集成 vLLM-Omni / SGLang / TensorRT-LLM / ComfyUI）
- 时间线：
  - 2026-08-15 提出：调研（vLLM-Omni 直播衍生；来源任务 vllm-h3-stream-analysis，git 3a6f3e6）→ 登记 T-20260815-10 待实测（挂链C EasyCache 后 / 可与 mc-test 线合并对比）
- 证据锚：.pi/tasks/vllm-h3-stream-analysis/progress.md（调研① Cache-DiT）/ TODO T-20260815-10

### C-20260816-27 | H3 能力边界（固定音频同步）
- 状态：✅现行（valid_from 2026-08-07）
- 现行值：**H3 只能生成自带语音的画面，无法同步用户固定音频**（音频与画面联合生成不可注入）；本机无口型模型 → 固定音频解说/演讲类视频弃用 H3/数字人路线，走「KREA 图 + zoompan 微动 + 烧字幕」静态管线（speech-video 交付 1024×576 8MB 验证）
- 时间线：
  - 2026-08-07 提出：debate 演讲视频方案选型（来源任务 speech-video）
- 证据锚：docs/12_speech_to_video_pipeline.md / .pi/tasks/speech-video/progress.md（方案节）

### C-20260825-01 | H3 TE 精度选型（NVFP4 维持定论）
- 状态：✅现行（valid_from 2026-08-25）
- 现行值：**H3 TE 维持官方 Qwen3-VL-32B NVFP4/AWQ（15.7GB）**，不换高精度 INT8。理由：① 能放入 24GB 显存的 INT8 备选（SearchingMan pruned-24 15.2GiB / recovered-8B 6.2GiB）均为文本 T2V only，**不支持 image/I2V/first-/last-frame/reference 输入**——与本地 Ref2VA/Ref2V/I2V 主力流不兼容；② 支持参考流的完整 32B INT8（官方 27.1GB / linjian257 25.77GB）超 24GB VRAM，encode 需 spill；③ 同架构 INT8 vs NVFP4 条件连续一致性 cosine **0.99999**（≈无精度收益）；④ NVFP4 在 Ada(4090) 无原生硬件加速（Blackwell 专属），但该代价每次生成只付一次（非逐 step），且 16GB 是唯一能塞进的参考兼容档
- 时间线：
  - 2026-08-25 提出：全面排查 INT8 备选（官方/linjian257-uncensored/SearchingMan pruned-24+recovered-8B）+ 量化一致性数据，定论维持 NVFP4（来源：H3 内容巡检会话；上游 ComfyUI 0.33 更新验证顺带）
- 证据锚：ledger README §INT8 排查 / SearchingMan/MiniMax-H3-Text-Encoders（release_manifest + evidence 表）/ Comfy-Org/MiniMax-H3（TE 体积 15.7/27.1/51.5GB）/ linjian257 repo（license=personal-entertainment-use-only）

### C-20260825-02 | v4-600EMA 无法跨用 ref2va pruned（LoRA 键名不匹配）
- 状态：✅现行（valid_from 2026-08-25）
- 现行值：**larryvrh `minimax_h3_turbo_v4_step600_ema` LoRA 无法跨用到本机 `minimax_h3_ref2va_pruned_int8_convrot`**：ComfyUI LoraLoader 实测 **518 条 `lora key not loaded` / 0 条加载**，键名（`blocks.0.adaln_proj/attn.qkv_proj/mlp.*`、`token_refiner.*`、`final_layer.*`）与 pruned int8_convrot 重打包模型的张量名全不匹配。原因：v4 是为非 pruned 标准 FL2VA bf16 布局训练（PulpCut 所称“两 transformer 张量同名同形”仅适用未 pruned 版）。→ ref2v 快车道**跨用通用 LoRA 走不通**，须走整模型 turbo（如 PulpCut Ref2VA Turbo / lightx2v ref2v LoRA）
- 时间线：
  - 2026-08-25 提出：零下载交叉实测（v4 8步 单图片参考 ref2v，prompt_id 613dd160，5s/1024×576）；首次提交 OOM 崩（20GB+LoRA 峰值+未释放），去视频引用分支后成功
- 证据锚：ComfyUI /tmp/comfyui_start.log（lora key not loaded 518 条）/ output/video/h3_ref2va/v4EMA_x_ref2va_8step_test_00001_.mp4 / 上游 PR #15808 会话

### C-20260917-01 | VDN Ref2VA 1024×576/20s + NativeAudioLock 验收基线
- 状态：✅现行（valid_from 2026-09-17）
- 现行值：RTX 4090 单卡上，VDN Ref2VA + 三张参考图 + INT8 ConvRot + 8 steps + `stream/retain_buffers=off/grouped` + NativeAudioLock 可稳定完成 1024×576、约20秒视频；当前端到端约380–411秒。Breeze 固定声线严格约20秒对白作为外部音频真值，视频/音频同步正常。
- 时间线：
  - 2026-09-16 提出：清理后严格20秒 VDN成功，431秒（来源任务 T-comfy-ops-VDN-01）
  - 2026-09-16 修正：简化中远景 prompt 复测成功，380秒；确认CPU staging是主要资源边界（来源任务 T-comfy-ops-VDN-01）
  - 2026-09-17 验收：标准 H3 Ref2VA 六段式 + NativeAudioLock 成功410秒；分段镜头/特效 prompt 成功411秒，特效时序有效但景别仍为软约束（来源任务 T-comfy-ops-VDN-01）
- 适用条件：启动前系统可用内存至少约40GiB、Swap基本空闲；采样峰值约23.9/24.6GiB显存、约52GiB已用系统内存。VDN v1.5.2保障adapter metadata兼容，不等同于显存/内存优化。
- 证据锚：`docs/35_vdn_h3_ref2va_route.md` §2026-09-17；`.pi/tasks/T-comfy-ops-VDN-01/progress.md`；产物 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/breeze_clone_1024x576_20s_shot_timed_effects_20260917_00001_.mp4`；git `ComfyUI-VDN-H3` commit `3eb6349`。

### C-20260920-02 | H3 完整视频 latent 两阶段放大远景脸验证
- 状态：🟡待验证（链路和资源通过；远景保真相对当前 FaceRefine 的最终选型仍需更长动作对照）
- 现行值：本地 RTX 4090 可运行 `MinimaxH3LatentUpscaler3DRefineHandoff`：768×448 一采完整视频 latent → 本地 BF16 learned 3D latent upscale → 4 步、denoise 0.40 H3 二采 → 输出视频；49 帧 smoke 约 130.5s，124 帧/5.17s 正式对照约 125.1s，峰值观测约 22.9/24.6GiB，无 OOM。目标 1344×768 在当前 H3 latent/VAE 对齐路径实际输出 1376×800。
- 时间线：
  - 2026-09-20 提出：根据社区复核，将“完整视频 latent 两阶段”列为第一优先测试（来源 T-comfy-ops-45）。
  - 2026-09-20 实测：节点注册、BF16 权重、49 帧 smoke、124 帧正式生成均成功；同正向提示词的一采源片与二采成片均保持远景构图，二采未出现明显跳脸/错误近景重画，远景细节提升有限（来源 T-comfy-ops-45）。
- 证据锚：`docs/39_h3_latent_upscale_face_research.md`；`.pi/tasks/T-comfy-ops-45/progress.md`；脚本 `scripts/h3_ref2v_latent_two_pass_runner.py`；产物 `/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_latent_two_pass_768_to_1344_full_00001_.mp4`、`sylvanas_hero_latent_two_pass_768_to_1344_smoke_00001_.mp4`。

### C-20260922-03 | FaceRefine + VOSR2 远景阈值与最终优化定位
- 状态：🟡待验证（当前生成优化手段已确定，阈值门控仍需受控视频 A/B）
- 现行值：VOSR2 作为**可选最终生成优化**接在局部 H3 FaceRefine decode 后，仅增强已 refine 的局部 crop，再缩回 stitch 画布；不替代人脸跟踪、不修复 detector 丢失、不增强背景。旧 1344 中景实测 H3-only 137.1s，H3+VOSR2 2x 635.4s（约 4.6x），有轻微中景眼缘/边缘锐化，远景尾段未恢复可读脸细节。
- 阈值初测：同一 1344×768、10s 拉远片的 `face_yolov8m` 原始检测显示，约 35–40px 仍可靠；约 30px 开始进入劣化/降置信区；25–27px 置信度快速下降；约 20px 主要为低置信或误检；<20px 不应继续依赖脸部 refine。候选门控：`>35–40px` 不 refine或极低强度，`30–35px` 开始 refine，`25–30px` 保守 refine，`<25px` 停止脸部 refine并保留原帧，`<20px` 如需连续性改用人物框/人物 mask。
- 关键限制：当前 `H3FaceStitch=fade_out` 并不停止 H3 计算，丢检帧仍进入采样，只是贴回权重淡出；实现真正节省计算的 per-frame/segment gate 是下一步测试内容。`H3PerFrameDenoise.face_px_small=30` 只是 denoise 曲线阈值，不是识别截止线。
- 证据锚：`.pi/tasks/T-comfy-ops-47/progress.md`（2026-09-22 VOSR2/threshold）；产物 `/home/sean/projects/ComfyUI/output/face_solution/t47_old1344_faceonly_vosr2_2x_no_preview_20260922_00001_.mp4`、`t47_far_tail_person_vosr2_20260922_00001_.mp4`。
- 补充：同一长拉远片中，用户标定的开始劣化第94帧对应源脸高约68px/原图VAE约8.5 latent px，但此时 detector confidence约0.82、跟踪稳定；真正默认人脸跟踪停止约第156帧，对应约26px/3.25 latent px。因此 `refine_start` 与 `face_track_stop` 必须是两个独立阈值，不能用丢脸检测作为首次劣化指标。证据：`experiments/h3_face_solution/t47_face_threshold_metrics_20260922.csv`。
- 跨分辨率初测：同一内容缩放到 1344×768、960×548、768×438 后，第94帧脸高 68/48/38px，但占画面高度均约 8.7–8.9%；跟踪终点附近脸高 26/18/14px，占画面高度约 3.2–3.4%。因此跨分辨率候选指标应是 `face_h/frame_height`，不是固定px，也不是原图VAE latent px（后者随输出分辨率变化）。初始候选：比例约 0.088 启动 refine；跟踪失败硬停止并保留原帧。仍需真正不同分辨率生成片复核。

### C-20260907-01 | Ref2VA 中文口型测试必须接 NativeAudioLock
- 状态：🟡待验证（有效组合已跑通，最终口型/接缝待用户目视确认）
- 现行值：Ref2VA 仅把外部 Breeze WAV 作为 `ref_audios` 参考时，最终回挂同一母带不能保证逐帧口型；有效对照组合为 **Ref2VA + NativeAudioLock + Motion Context**。该组合在中文 Breeze 30 秒 A/B/C 测试中三段成功，标准 20 步，峰值显存约 20.0–20.6GB。
- 时间线：
  - 2026-09-07 提出：Ref2VA+MC 30s 初版用户确认口型未对上（来源 T-comfy-ops-28）
  - 2026-09-07 修正：补接 NativeAudioLock 并修复 runner 节点编号冲突，A/B/C 全部完成；后续转 T-comfy-ops-31 验证 Extender 2.0 的多参考连续性
- 证据锚：`.pi/tasks/T-comfy-ops-28/progress.md`；`experiments/h3_digital_human/zh_breeze_ref2va_audio_lock_mc_30s_cases.json.results.json`；产物 `/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_ref2va_audio_lock_mc_30s/joined_30s_master_audio_timeline_fixed.mp4`
