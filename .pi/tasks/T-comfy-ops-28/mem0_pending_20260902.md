# Mem0 待补写内容

> 状态：待 Mem0 proxy 恢复后导入。项目池：`comfy-ops`；建议 `agent_id=codex`。

## H3 结构与方案边界

- [定论候选][2026-09-02][T-comfy-ops-28] H3 原生是单模型联合视频/音频扩散，不是“草稿+精修”两阶段；FL2VA/Ref2VA 是条件分支，video/audio 是双流。
- PDD 8-step 是 H3 内部单阶段采样加速，使用 PDD head bank 和专用 SIGMA/Euler，直接输出最终 H3 视频，不包含 LTX 精修。
- NVIDIA H3 Super Acceleration 是额外的两模型流水线：H3 4-step LightX2V 低分辨率草稿 → latent upscale → LTX-2.5 3-step 视频精修 → 复用 H3 音频。GB200 热服务、排除加载/warmup 的宣传速度不能外推到 RTX 4090。
- 当前不做高清/修补时，4090 主线优先使用：外部粤语音频 + FL2VA + PDD 8-step；NVIDIA H3+LTX 两阶段方案后置。

## 外部音频与数字人实测

- FL2VA 可以通过 `MiniMaxH3NativeAudioLock` 使用预先生成的外部音频；该节点把音频编码进 H3 audio latent，并锁住音频，只去噪视频。
- 外部音频测试使用真人高清上半身首帧和完整粤语音频 `hk_a_30s.wav`，768×448，FL2VA INT8，14 steps；10 秒配置总耗时 306 秒，输出 10.833 秒，音频为 32kHz 双声道 AAC，基础链路成功。
- PDD FL2VA 外部音频短测：5.167 秒配置耗时 145 秒，成功；未使用 MC。
- PDD FL2VA 长段：4090 24GB、INT8、768×448、NativeAudioLock、PDD 8 nfe；10 秒配置耗时 255 秒、输出 10.833 秒；15 秒配置耗时 315 秒、输出 15.792 秒；均成功无 OOM/节点错误，峰值显存约 22.2GB，结束后可用内存约 7.2GB。
- H3 输出帧网格会使容器时长略长，批量拼接前要按视频帧数统一裁切并对齐音频。

## MC 实测

- 基础 FL2VA 14 steps + NativeAudioLock + MotionCache，768×448、5.167 秒，耗时 155 秒；日志显示 `skipped 0/14 model calls`，估算 1.00x，无实际收益。
- 结论：MC 在短段/14 steps 下无收益，暂不作为默认方案；长段或更高步数可另行评估。

## Codex CLI 恢复信息（如需放 global 记忆）

- [2026-09-02] Codex 主包 `@openai/codex@0.152.1` 存在，但 Linux x64 optional native dependency 缺失/损坏。
- 显式安装 `@openai/codex-linux-x64@npm:@openai/codex@0.152.1-linux-x64` 后恢复；验证输出为 `codex-cli 0.152.1`。
- 若终端缓存旧命令，执行 `hash -r` 或重新打开 WSL 终端。
