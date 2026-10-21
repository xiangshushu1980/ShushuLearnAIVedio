# [Sean] H3 FaceRefine 当前状态与续开入口

> 更新时间：2026-09-26  
> 任务主线：`T-comfy-ops-47`  
> 适用范围：ComfyUI-H3-FaceRefine 1.1.2、H3 局部人脸精修、远景小脸防劣化、预分析 manifest 与分段执行。

## 一句话结论

FaceRefine 当前应作为“近景/中景或明确需要修脸的短片段慢车道”：它能稳定跟踪、保留动作并防止跳脸/贴回劣化，但不能从 20–35px 的源脸凭空恢复身份细节。全片结构与分辨率优先走 latent 二采；FaceRefine 只对选定人物、选定镜头、选定 8 秒窗口启用。

## 当前唯一推荐链路

```text
H3 母片
  → 预分析/ROI/坐标锚点（优先 manifest）
  → 单人物独立轨迹
  → 768×768 crop，crop_factor=3
  → 原视频 crop latent + H3InjectVideoLatent
  → H3PerFrameDenoise
  → H3 8-step 局部采样
  → face_only stitch，丢检帧保留原像素，原音频不变
```

当前保守基线：`res_multistep`、8 steps、base denoise 0.28–0.40；最新 T47/1.1.2 验收使用 `0.28 + per-frame 0.65/0.25 + smooth 15`，早期 T44 动态基线为 `0.40 + 0.35/1.0 + smooth 9`。两者都是已验证配置，后续对照需注明使用哪一档，不要混写成一个参数。

## Reference 职责（硬规则）

| 输入 | 唯一职责 |
|---|---|
| 完整人物/object reference | H3 局部重绘的身份、脸、服装、轮廓和总体外观 |
| face-only identity reference | 只判断“是哪一个人”，优先 CLIP Vision/CCIP；非真人/3D/插画不要默认 InsightFace |
| 源视频当前帧 crop latent | 保留当前帧动作、头部角度、表情、光照、发型位置和时间连续性 |
| 环境 reference | 环境、建筑、布局与光照，不承担 FaceRefine 身份跟踪 |

face-only 图不能同时充当 H3 object reference。多人必须每人独立 reference、独立轨迹、独立 refine，再串行 stitch；不能靠 `face-index=1` 在双人远景中可靠选择第二个人。

## 已验证结果与边界

- 4090 上 768 局部 FaceRefine 已通过单人动态侧脸、抬头/低头/转身、稳定双人串行，以及 1344×768 中景→远景 pull-back 的稳定性验收。
- 1344 母片中脸约 40–60px 后，清晰度收益快速消失；严格 30–50px 远景主要收益是“不跳脸、不抖、不错误补正”。降到约 20–35px 时检测会掉检，必须保留源像素。
- T47/1.1.2 升级验收：124 帧、1344×768、约 125.1 秒、峰值约 23GB、无 OOM，平均 PSNR 44.04dB；官方 v1.1.2 已加载，基线仍成立。
- VOSR2 只定位为可选末端优化：接在局部 H3 decode 后再增强 crop；旧 1344 中景 H3-only 137.1 秒，H3+VOSR2 2x 635.4 秒（约 4.6×），中景略锐但没有恢复 20–35px 远景可读脸。
- 2026-09-26 Continuum 4×8 实测：32 秒全片 FaceRefine 因主机内存压力主动中止；改为 8 秒/192 帧窗口，单脸 228.2–275.1 秒成功。红发角色 c1/c2 有效，精灵 c2 因 `face-index=1` 仍锁到红发角色，结果作废，禁止拼回成品。
- 2026-09-26 长度基准：清缓存后 8 秒/192 帧单脸完成 222.3 秒；采样阶段显存约 23.1GiB，系统可用内存最低约 375MiB。16 秒/384 帧进入采样后系统可用内存降至约 300–500MiB并开始使用 swap，为避免主机 OOM 主动中止；因此当前 8 秒是已验证安全分段，16 秒是风险边界，不继续直接扩大到 20/24 秒。
- 2026-09-26 源长度对照：`H3FaceSelect` 会先完整解码源视频，再应用 `frame_load_cap`；因此 32 秒源即使只处理前 5 秒，仍比物理裁成 5.17 秒的源慢约 12.4%（140.6s vs 125.1s）。8 秒物理裁剪源处理 8 秒成功（180.2s），未出现 16 秒测试那种可用内存降至数百 MiB的危险状态。生产前应先物理裁剪，再进入 FaceRefine。

## 相关任务与证据主题

以下只用于定位历史任务；生命周期、controller/generation 与验收状态实时查询远程 Task Center，本页不维护状态投影。

| T-ID | 证据主题 |
|---|---|
| `T-comfy-ops-47` | 远景/中景 FaceRefine 防劣化与目标锁定 |
| `T-comfy-ops-facerefine-upgrade-20260925` | 官方 v1.1.2 升级回归 |
| `T-comfy-ops-facerefine-output-tidy-20260925` | 输出整理与升级审计 |
| `T-comfy-ops-45` | 完整 latent 二采 |
| `T-comfy-ops-46` | H3 二采与远景脸方案 |

## 研究执行建议（任务范围以远程系统为准）

1. **P0：先解决目标选择**。用 `H3FaceManifestSave` 生成并复用 manifest；优先坐标/ROI + identity gate，验证红发/精灵双人 8 秒窗口。验收必须有 tracking preview、每帧目标框和错误目标否决。
2. **P1：做同源短窗口 A/B**。同一源片、同一帧数比较原片 / FaceRefine / latent 二采 / latent 二采后 FaceRefine；分开记录稳定性与细节恢复，记录实际输出网格（1344 请求可能得到 1376×800）。
3. **P2：再做加速**。依次测试更少 steps、更小 crop、稀疏帧+时序传播；任何速度收益都必须经过身份、闪烁、贴回边缘和动作保持检查。
4. **可选：VOSR2**。只在目标脸已有可靠 refine 且确有中景锐度需求时启用；不把它当 detector、身份选择或远景恢复方案。

## 证据入口

- 主实验与参数演进：`experiments/h3_face_solution/README.md`、`experiments/h3_face_solution/T47_face_refine_research.md`
- 预分析与 manifest：`docs/42_h3_face_preanalysis_external_research.md`
- latent 二采与 FaceRefine 分工：`docs/39_h3_latent_upscale_face_research.md`、`docs/40_h3_far_face_second_pass_strategy.md`
- 升级回归：`.pi/tasks/T-comfy-ops-facerefine-upgrade-20260925/progress.md`
- 2026-09-26 分段实测：`experiments/h3_vae_upgrade/sean_ref2va_continuum_dialogue_4x8_1344_face_20260926.md`
- 2026-09-26 长度/资源基准：`experiments/h3_vae_upgrade/sean_facerefine_duration_benchmark_20260926.md`
- 执行器：`tools/h3_face_crop_refine_runner.py`
