# 任务进度：h3-ref2v-pilot

> 任务：2026-08-14 Ref2VA Turbo 4-step v0.1 实测（8-13 lightx2v 新发布 LoRA）
> 队列占用：已 [STATE] 声明占坑（2026-08-14），ComfyUI v0.33.0 空闲待跑批

## 任务
- 目标：Ref2VA Turbo 4-step v0.1（参考图/参考视频/参考音频 → 视频+音频，4 步蒸馏）实测：
  ① 官方工作流本地化跑通 ② 多参考图身份一致性（ref_lib 素材）③ 参考视频/音频条件（可选）④ 速度对比 F 档（v4-600EMA 8步@1024 = 158s）
- 当前状态：🟡 进行中（LoRA 下载中）
- 我负责的文件区：`.pi/tasks/h3-ref2v-pilot/`、`scripts/h3_download.py`、ComfyUI/models/loras/（ref2v LoRA）

## 进度日志（append-only，每条带日期）
### 2026-08-14
- 巡检：Ref2VA Turbo 4-step v0.1 昨日 15:17 发布（lightx2v/Minimax-h3-Turbo），ModelTC 同步 feat: ref2va (#8)；官方 ComfyUI 工作流 video_minimax_h3_ref2v_lightx2v_turbo.json（纯核心节点）
- 规格：544p 训练、shift 12/3、NFE 4、euler；ref_image_size 三策略（match 默认=训练一致 / max=2048 短边保身份 / diffusers=固定 2048 短边）
- 本地就绪：ComfyUI v0.33.0 ✅、MiniMaxH3ReferenceToVideo 节点 ✅、ref2va_pruned_int8_convrot 基础模型 ✅、qwen3vl_32b CLIP ✅、双 VAE ✅；缺 LoRA 1.9GB（ModelScope 未同步 → hf 直连 8 线程后台下载，~260KB/s 网络差）
- 官方工作流解析：UNETLoader(bf16 66GB→本地换 int8_convrot 21GB)、LoraLoaderModelOnly(strength 1)、ResolutionSelector 16:9@1MP→可选 960×544(0.5MP)/1024×576、BasicScheduler simple 4 步、MiniMaxH3SigmaShift 12/3、RandomNoise seed 42、prompt 六段式（subject_definitions/summary/retention_analysis/detailed_description/overall_soundscape/non_diegetic_music）
- 参考图素材：output/ref_lib/（ANIMA 60+ / KREA 50+ 张）可用
- **基线已跑（官方 20 步 res_multistep @960×544 124帧 shift12/3，无 LoRA）**：R1 三图(场景+两角色)=122.6s / R2 两图(场景+角色)=100.5s / R3 三图 seed2=100.0s；产物 output/video/h3_ref2v/R{1,2,3}_*.mp4；runner=scripts/h3_ref2v_runner.py、用例=experiments/h3_ref2v/cases_r1{,b}.json
- **下载受阻**：hf 直连 0.8-160KB/s 波动、代理更慢、hf-mirror 308 回源不代理 LFS；**最终解法：台湾节点 + 16 线程 hf 直连 = 1.8-2.1MB/s，~25 分钟下完**（07:35 完成，1956193000 字节校验 OK）
- **Turbo 4 步实测（07:36-37，同 prompt/seed 对照 20 步）**：T1 3图=40.0s / T2 3图seed2=40.0s / T3 2图=40.0s → **2.5-3x 提速**（20 步 100-122s）；对比图 output/compare/h3_ref2v_20vs4.png（同帧 2s 抽帧并排）；产物 output/video/h3_ref2v/T{1,2,3}_*.mp4
- 待用户：目视验收 4 步 vs 20 步画质/音频差异（身份一致性是否保留）

## 下一步
1. 用户目视验收 4 步 vs 20 步（对比图 output/compare/h3_ref2v_20vs4.png + 视频）
2. 可选：参考视频/音频条件测试、1024×576 档速度验证、音频质量对比
3. 结论入 mem0 + params.md 更新（待验收后）

## 关键链接
- HF LoRA: https://huggingface.co/lightx2v/Minimax-h3-Turbo/blob/main/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors
- 官方仓库: https://github.com/ModelTC/Minimax-H3-Turbo（README #1 Model specs / COMFYUI_SETUP_AND_INFERENCE.md）
- 官方工作流: example_workflows/video_minimax_h3_ref2v_lightx2v_turbo.json
- 本地节点: comfy_extras/nodes_minimax_h3.py（MiniMaxH3ReferenceToVideo）

### 2026-08-14（FaceRefine 线）
- **FaceRefine 实测（Carasibana 节点）**：装节点+face_yolov8m.pt 检测器（Bingsu HF 源 52MB）+NativeAudioLock；本地化官方示例工作流（GGUF→标准加载器 ref2va int8+qwen3vl）
- **v1-v3 改参数全部马赛克**（LoRA 换 v1.0 768p@1.0 + prompt 占位符 + 强度乱改）→ 用户目视确认特写被过度重绘
- **v4 官方参数原样 = 干净**（用户确认）：LoRA v0.1 comfy @0.75、er_sde 4 步 denoise 0.45、强度 0.8/0.35、原 prompt；30-45s/条
- 验证第二条 T2d（不同 seed）通过；对比图在 ~/projects/ComfyUI/output/compare/（用户要求放 ComfyUI output 目录，勿放仓库 output/compare）
- **Florence-2 反推装好**（Kijai 节点+base-ft 463MB）：GPU 1-3s/图、keep_model_loaded=False 不挤显存；粒度仅场景级，不能判脸部马赛克
- 经验入 mem0 + nodes.md/params.md
