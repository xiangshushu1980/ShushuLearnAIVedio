# FaceRefine 1.1.2 升级与回归验收（Owner: Sean）

- Task Center：`T-comfy-ops-facerefine-upgrade-20260925`；状态由当前 Codex 会话领取。
- 范围：将 `/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-H3-FaceRefine` 纳入官方 `Carasibana/ComfyUI-H3-FaceRefine` 的 `v1.1.2` 历史，并复跑 T47 已验证的保守局部 FaceRefine 基线。

## 升级

- 上游 `origin/main` 的 `d8521d1`（tag `v1.1.2`）已合并为本地 merge commit `f8d3beb`。官方示例工作流一并纳入。
- 合并前本地 `nodes.py` 未提交的 T47 分析/manifest 增强已保留；可回滚补丁：`/tmp/facerefine-local-nodes-before-upstream-20260925.patch`。
- `python3 -m py_compile nodes.py` 通过。队列为空时仅结束已有 `main.py`，由既有 `/home/sean/projects/ComfyUI/start.sh` 守护自动重启；没有创建第二个实例。
- 重启后 `H3FaceSelect`、`H3FaceTrackCrop`、`H3InjectVideoLatent`、`H3PerFrameDenoise`、`H3FaceStitch`、`H3FaceManifestSave` 均在 `/object_info` 注册。

## 验收复跑（2026-09-25）

- 母片：`/home/sean/projects/ComfyUI/output/face_solution/sylvanas_hero_pullback_1344_final8_00001_.mp4`（1344x768、124 帧、24fps、5.167 秒）。
- 参数：分离的人脸身份图与完整人物 H3 reference，`clip_vision` 阈值 `0.20`，768x768 crop、crop factor 3、8 steps、base denoise 0.28、per-frame 0.65/0.25、smooth 15、`face_only` stitch、`skip` 未检测帧。
- 预分析 prompt `a6a104b2-661f-4b1a-b5f0-b87087b6db7d`：124/124 帧跟踪，零丢检，源脸高 45.2--90.0px；报告位于 `ComfyUI/output/face_solution/analysis/sean_facerefine_112_preflight_20260925_*`。
- 首次提交误设阈值 `0.80`，prompt `41504051-e03d-4b69-bce3-f6ebe76fd841` 在 `H3FaceTrackCrop` 正确地将所有镜头判 absent，未进入采样。这重现 T47 已知边界（此角色真目标最高约 0.768），不是升级回归。
- 正确基线 prompt `7ff13f46-d7d4-46b3-a880-d3d2af8b31f5`：`success`，125.1 秒，无 OOM。输出：`/home/sean/projects/ComfyUI/output/face_solution/sean_facerefine_112_upgrade_20260925_00001_.mp4`。
- 输出为 H.264 1344x768、124 帧、24fps、5.167 秒，含 AAC 音频；首/中/末帧对照未见构图重绘或明显贴回边界。与母片的全帧平均 PSNR 为 44.04dB，符合仅局部保守精修的预期。
- GPU 租约 `6187db71-337e-46ff-b1f2-a4351ea99023` 已释放；观测 `0241717c-e40f-4ceb-9933-8863f19c1dd0` 记录峰值采样约 23042MiB、100% 利用率。队列恢复为空。

## 结论

官方 FaceRefine v1.1.2 已规范合入且可加载；T47 现行 768 局部 FaceRefine 基线在升级后的 ComfyUI 0.37.0 单实例上完整通过。基线参数不变；ClipVision 阈值仍须按角色校准，Sylvanas 这一组使用 0.20，不能硬编码为通用建议值 0.80。
