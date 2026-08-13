# 任务进度：h3-today-testing

> 任务：2026-08-11 H3 今日动态测试（用户指令：依次测试直到出结果）
> 队列占用：2026-08-11 占用期间已在 [STATE] 声明（条目未建成，收尾补建），跑批已结束，队列已释放

## 任务
- 目标：依次测试 T1-T6（LightX2V Turbo LoRA v1.0 → 防 OOM flags → Ref2VA 纯音频 → Sage v2 Ada patch → Sol Engine → fal API）
- 当前状态：✅ 完成（2026-08-12 收尾）
- 我负责的文件区：`.pi/tasks/h3-today-testing/`、ComfyUI models/loras/（minimax_h3_turbo_v1.0 相关）

## 进度日志
### 2026-08-11
- 巡检确认今日动态：LightX2V Turbo LoRA v1.0 发布（HF lightx2v/Minimax-h3-Turbo，今天 14:28 UTC）、fal 上线 H3、README 放宽 Ref2VA 音频限制、官方转推 Sol Engine
- T1 执行（脚本 scripts/h3_v1_test_runner.py 新建）：从 ModelScope 下载 v1.0 LoRA ×2（HF/hf-mirror 仅 0.3-1.7MB/s，ModelScope 10-21MB/s 秒下，大小校验 ✓）
- **第一轮 768×448@8s fp8（同 seed 20260811 花田首帧）**：A v4-4步=53s(响度-12.8/运动38.3) / B v4-8步=68s(-16.6/39.7) / C v1-8step 8步=67s(**清晰度57.8最高**，但响度-27.2异常安静/运动36.1) / D v1-8step 4步=53s(-32.6/33.6) / E v1-4step768p 4步=52s(49.1/25.5 明显弱)
- **第二轮 1024×576@8s int8_convrot**：F v4-8步=158s(-11.2/34.5) / G v1-8step res+shift12/3=144s(57.0 清晰度最高，**响度-14.8 正常**/32.8) / H v1-4step768p 4步=**65s**(51.1/23.9/-19.0 画质偏弱但速度2x) / I v1-8step TurboSampler=96s(**响度-24.9 崩**/24.9)
- **T1 结论**：v1-8step 正确用法 = res_multistep + SigmaShift(12/3) + **1024×576**（768×448 下音频异常安静 12dB）；TurboSampler 只配 v4/v0.1 4步，对 v1-8step 音频崩；H 档 65s 极速候选待用户目视；G 144s vs 基线 125s 需复测确认
- **T2 结论（flags 全退）**：--disable-pinned-memory --disable-smart-memory 实测灾难：1344×768 每步 394s（42min/条，默认 ~11.5min 慢 3.7x）、1024×576 239s vs 158s（慢 51%）；原因=smart memory 禁用后强制 offload。yume 建议不适用于本机（64GB RAM+4090 默认配置更优），已恢复默认参数重启
- **T3 结论（纯音频参考可用 ✅）**：Ref2VA 仅 ref_audios（voice_seed_male.wav）无图无视频，20步成功生成：音频 -11.3 LUFS 有真实语音（无静音段）；对照同 prompt 无音频参考 = -31.3 LUFS 几乎静音 → 纯音频参考今天起可用且是语音生成必要条件（README 放宽实测验证）。L 清晰度 48.9 vs M 47.7
- **T4 结论（无需 patch）**：sageattention 2.2.0 sm89 走 int8QK+fp8PV CUDA kernel，日志无 launch-fail/无 fallback，速度达标；驱动 610.88（>580）+ CUDA 13.3，int8_convrot 正常；yume 的 patch/driver 建议针对旧环境，不适用
- **T5 结论（观望）**：Sol Engine 本体未开源（NVIDIA 内部，8×GB200 部署，nvlabs.github.io/Sana/Sol-Engine/H3/）；组件=First Block Cache(ParaAttention，等价我们 MotionCache 已测) + Sol-Attn（论文 arXiv:2607.24027 训练-free 稀疏注意力，未来关注 ComfyUI 实现）+ kernel 融合（int8/convrot 已覆盖）
- **T6 结论（定价探明，实测待 key）**：fal H3 = $0.16/秒@768p、$0.26/秒@2K（vs 官方 0.8 元/秒）；1440p/7000 字符/15s；实测需用户注册+API key
- 产物：output/video/h3v1/（A-K+L/M 共 12 条）+ output/compare/h3v1_round1_768.png、h3v1_round2_1024.png
- 待用户：目视验收（T1 对比图/视频）、决定是否注册 fal（T6）
- **用户目视定案（2026-08-11）**：F 细节多 > G 画面简单（v1.0 8step 蒸馏抹细节）；H/D/E 全部糊淘汰；**成片档维持 F（v4-600EMA 8步@1024）不动**，G 留作干净风格备用；fal 未注册（无 key）

### 2026-08-12（收尾）
- **全部完成**：T1-T6 结论 + 用户目视定案（2026-08-11）已在上面日志；定案 = 成片档维持 F（v4-600EMA 8步@1024）不动、G 留作风备选、H/D/E 糊淘汰、fal 未注册（无 key）
- **产物清点**：视频 13 条完好 —— `~/projects/ComfyUI/output/video/h3v1/`（A-K+L/M，ComfyUI 运行时输出不进 git）；对比图 2 张在仓库 `output/compare/`（git 跟踪）曾遭删除，已从 git restore 恢复；结论数据完整保留在本文档 + mem0（条目 34c933c9 等）
- [STATE] 补建：本线当初“已声明队列”实际未落库，收尾时 retain 补建 ✅ 条目
- 交接提示：本线 T1 实测已覆盖 h3-turbo-pilot 的“新武器试点”计划（v1.0/v4 均已测并定案），该线建议合并收口

## 下一步
- 无（本线收口）

## 关键链接
- HF LoRA: https://huggingface.co/lightx2v/Minimax-h3-Turbo
- 官方规格: https://github.com/ModelTC/Minimax-H3-Turbo#model-specs
- 相关 mem0：经验条目 34c933c9（v1.0 LoRA 测试结论）、4d53abcd（成片档定案）；[STATE] 2026-08-12 agent=h3-today-testing（✅）
