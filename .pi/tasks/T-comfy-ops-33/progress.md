# 任务进度：T-comfy-ops-33 H3 Ref2VA 对照：PDD 5s 与标准 20-step 5s

> 项目级私有进度（只有本任务线读写；多 PI Agent 并行时互不干扰）。
> 状态标记：🟡进行中 / ⏸暂停 / ✅完成。
> 共享状态（焦点/活跃决策/全局待办）在 `[STATE]`（hive-state），不写在这里。

## 任务
- 目标：在同一 Ref2VA 配置下严格对照 PDD Acc 8-step 与原版 20-step 的 5 秒片段（速度 + 质量），用于决定 PDD 能否作为 Ref2VA 日常快车道。
- 当前状态：🟡 跑批完成，等用户目视/试听验收
- 我负责的文件区：`experiments/h3_ref2v/cases_pdd_vs_std20_5s_20260914.json`、`experiments/h3_ref2v/pdd_vs_std20_5s_20260914/`、`scripts/h3_ref2v_runner.py`（新增 PDD 支持）

## 进度日志（append-only，每条带日期）

### 2026-09-15
- 开局 recall/对账：T-comfy-ops-33 未在 `docs/34` 定论，仅有一条「后续单独测试 PDD 5s 与无 LoRA 标准 20-step 5s，不能与 VDN Turbo 1024×576 结果混记」的边界说明；`[STATE]` 已有本任务认领（准备严格 5 秒对照跑批）。ComfyUI 在 8188 运行、队列空、GPU 空闲（约 0.4/24GB）。
- 环境事实：`input/` 已清理，历史 `h3_avatar/` 参考音频不在；改用 `vdn_audio_test/hk_a_30s.wav` 截取前 5.000s，副本落 `experiments/h3_ref2v/pdd_vs_std20_5s_20260914/audio/hk_a_5s.wav` 保证可复现。
- 脚本改造：`scripts/h3_ref2v_runner.py` 新增 `pdd` 支持（`MiniMaxH3PDDAccApply` → `MiniMaxH3SigmaShift` → `NativeAudioLock`，采样器自动切 `euler`、sigmas 取自 PDD 节点），并给 results.json 记录 `exec_ms`。
- 严格对照（除采样路线外全同参）：同一参考图 `ref2va_refs/digital_human/01_host_blank_gray_16x9.png`、同一 5.000s 粤语音频、同一六段式 prompt、同一 seed `20260914`、768×448、124 帧、shift 12/3、NativeAudioLock；A=无 LoRA `res_multistep` 20 steps，B=Ref2VA PDD Acc nfe 8 + `euler`。
- 结果：A 端到端 90.0s（ComfyUI 内部 86.50s，采样 20 步 53s）；B 端到端 40.0s（内部 33.38s，采样 8 步 19s，PDD 加载/打补丁约 2s）。两者均为 124 帧 / 5.167s / 768×448 / 24fps，音频流 163 帧，无冻结帧。
- 指标：整片 SSIM A-vs-B 0.867；运动能量（帧差）A face 0.70 / body 0.50，B face 0.84 / body 0.36；逐帧面部运动序列相关 0.616；音频包络 vs 面部运动代理相关 A 0.061、B −0.04（弱，只能当异常筛查，不能当口型结论）。
- PDD 侧日志确认走对通道：`partition check ok: ref2va file on ref2va model (fl2va 0.0504, ref2va 0.0017)`、`steps=8 blocks=4,4,4,4,4,4,4,4, heads fused`、`50 adaln modules rebased onto the ref2va curve basis`。
- 卡点：本机视觉质检通道不可用（DashScope VL 免费额度耗尽、LM Studio 未启动），**画质/口型结论只能由用户目视**。已备接触表 `contact_AB.png` + 8 张单帧。

## 下一步
1. 用户目视/试听 A（标准 20 步）与 B（PDD 8 步）成片，判定身份/构图/口型/稳定性是否可接受。
2. 若质量可接受 → 把 PDD 8-step 记为 Ref2VA 日常快车道；若不可接受 → 保留 20-step 质量基线，PDD 降级为预览档。
3. 可选延伸：同条件补 4-step 档（`nfe=4`）与更长时长（10s/15s）验证 PDD 在 Ref2VA 上的斜率是否与 FL2VA 一致。

## 关键链接
- 对照配置：`experiments/h3_ref2v/cases_pdd_vs_std20_5s_20260914.json`
- 结果与抽帧：`experiments/h3_ref2v/cases_pdd_vs_std20_5s_20260914.json.results.json`、`experiments/h3_ref2v/pdd_vs_std20_5s_20260914/`
- 成片：`/home/sean/projects/ComfyUI/output/video/h3_ref2va_pdd_vs_std20_5s/{A_std20_5s_00001_,B_pdd8_5s_00001_}.mp4`
- 相关文档：`docs/34_ref2va_generation_guide.md`、`docs/35_vdn_h3_ref2va_route.md`
- 相关 ledger：`.pi/ledger/h3-speed.md`（C-20260915-01）
