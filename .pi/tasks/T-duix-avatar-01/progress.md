# T-duix-avatar-01 进度：DuixAvatar 本地数字人部署与效果验证（用户单独推进）

> 用户单独推进任务。上下文：4090 WSL2+Docker 起 Lite(仅口型服务)，粤语口型实测为验收项；调研见 comfy-ops docs/27_DUIX_Avatar_数字人评估.md

## 状态总览
- [ ] ① 起 Duix-Avatar Lite compose（仅口型服务 duix.avatar-gen-video:8383）
- [ ] ② 跑通 submit/query，用现成音频+参考视频校准速度
- [ ] ③ 粤语口型验证（需本人出镜 ~10s 参考视频）

## 会话日志
### 开场 2026-09-01
- 任务由用户拍板创建（单独推进）。待办源 Todo.md T-duix-avatar-01。
- 参考：comfy-ops docs/27_DUIX_Avatar_数字人评估.md（架构/硬件/API/粤语/三方案对比）；Mem0 comfy-ops 池。

## 待办/备注
- **参考视频已备（2026-09-01，Pexels 免费可商用）**，存 `assets/duix_ref/`：
  - `candidate-a_8135207.mp4` 12.9s "woman talking while looking at camera" 360×640（首选：正脸说话）
  - `candidate-b_8814493.mp4` 12.5s "woman talking and looking at camera" 360×640
  - `candidate-c_36931662.mp4` 9.8s "expressive woman speaking indoors" 360×640
- C: 360p 偏糊，DUIX 最终出品分辨率受参考视频限制 → 若需更高清后续到 Pexels 详情页手动下 hd 档。
- 粤语测试音频：`/tmp/eleven-cantonese-test.mp3` 2.6s。
- **在线预览（看效果再自托管）**：硅基元镜免费每日5分钟（与 Duix 同源，嘴型>98%），先在线看效果再决定是否部署。可灵数字人 API 0.12元/s 可作对照。详见 comfy-ops docs/28_数字人在线方案_对比与价位.md。
- LongCat 已放弃（产能），不影响本任务。
