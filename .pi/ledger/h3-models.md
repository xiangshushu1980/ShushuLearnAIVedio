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

---

### C-20260816-20 | Hybrid b25-49（fl2va+ref2va merge）
- 状态：🟡待验证（动画域已实测通过，写实域结论待深度测试 T-20260815-09）
- 现行值：动画域 ref2va 画质提升显著（Laplacian 43→**54，+26%** 清晰度，耗时 80s→60s）；写实域无优势（耗时打平 60s 且没脸待查）；dtype = int8 混合精度（F32/BF16/F16/I8/U8）20.97GB，24GB 可跑；权重选择 merge（非微调），Ref2VA drop-in 替换，作者推荐 b25-49
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
