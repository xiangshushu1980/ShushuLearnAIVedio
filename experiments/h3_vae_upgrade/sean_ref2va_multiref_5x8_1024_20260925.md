# Sean — 多高清 Ref2VA + Continuum 5×8 秒上限测试

owner: Sean
date: 2026-09-25

## 配置

- 5 张参考图，`reference_size=Max Identity`
  - `sean_t2_a_character_board.png`
  - `sean_t2_a_identity_front.png`
  - `sean_t2_a_face_closeup.png`
  - `sean_t2_scene_observatory.png`
  - `object_scene_refs/observatory_side_orbit.png`
- Continuum V3.4，5 chunks × 8 秒
- 1024×576，Ref2VA，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：960 帧 / 39.999 秒 / 1024×576
- 峰值显存采样：约 23086 MiB / 24564 MiB
- 主机内存峰值采样：约 57907 MiB；最低可用约 1352 MiB
- 执行时间：约 663 秒
- 输出：[sean_ref2va_multiref_5x8_1024_00001_.mp4](../comfyui_output_archive_20260928.md)
- 抽帧检查：角色的银发、深青斗篷、弓和观测台结构保持稳定；长时间段中人物主要保持背/侧面，未对正脸身份稳定性做充分覆盖检查

## 结论

5×8 秒、5 张高清参考图在本机仍可完成，但已经逼近主机内存上限：最低可用内存约 1.35 GiB，风险明显高于 4×8 秒的约 5 GiB。显存仍约 23.1 GiB，没有成为这次失败点；下一步若继续测试，应优先做 6×8 秒并保留相同 5 张参考图，预计真正的失败点会出现在 Assemble/解码阶段的主机内存。
