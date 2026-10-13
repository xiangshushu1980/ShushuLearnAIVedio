# Sean Continuum 4×8 分段提示词 v2 实测

- owner: Sean
- date: 2026-09-25
- route: H3 Ref2VA → Continuum V3.4 → Native Masked Strong 39
- hardware: RTX 4090 24GB
- runtime: ComfyUI `--fast fp16_accumulation`、INT8 VAE、Sage Attention、PDD Acc 8-step
- prompt mode: `Timeline`
- chunks: 4 × 8s
- references: 5 张，分别承担角色 A、角色 B、场景、法术、道具；避免重复的人物身份板
- output: `/home/sean/projects/ComfyUI/output/video/sean_ref2va_chunked_prompt_v2_4x8_00001_.mp4`

## 结果

- 状态：success
- 视频：31.999s，1024×576，768 帧；音频 1001 帧
- 生成耗时：537.679s，约 8 分 57.7 秒（按 Coordinator execution start/success 时间戳）
- 显存：约 23.1GiB 峰值采样，未发生 OOM
- 主机内存：采样峰值约 48.0GB used，最低约 11.2GB available
- 结束状态：ComfyUI healthy，队列为空，GPU 利用率回落，GPU lease 已释放

## 与此前 32 秒实验对比

| 对照 | 结构/负载 | 耗时 | 本次差异 |
|---|---|---:|---:|
| `sean_ref2va_standard_shot_boundaries_4x8` | 4×8、5 张参考、全局 Shot 边界提示词 | 约 508.2s | 本次慢 29.479s，约 **5.80%** |
| `sean_ref2va_continuum_4x8_1024` | 4×8、2 张参考 | 约 399.6s | 本次慢 138.079s，约 **34.55%** |

因此，本次变慢主要应归因于“每个 chunk 都使用完整独立六段式 Ref2VA prompt + 5 张职责型参考图”的负载增加；相对于同样 5 张参考图的 32 秒诊断实验，只增加约半分钟，不能归因于视频长度本身。两次均为 1024×576、4×8、Sage、PDD Acc 8-step、Native Masked、INT8 VAE 和 `--fast fp16_accumulation`。

## 关键经验

1. Continuum 的 `Timeline` 标题必须独占一行，使用 `[0-8s]`、`[8-16s]` 这类与 `chunk_seconds` 对齐的范围；每个 chunk 的正文必须是完整、可独立执行的六段式 Ref2VA prompt。
2. `[Shot 1]` 之类不带时间范围的文本不能作为本地 Continuum Timeline 的可靠路由格式，可能回退到 Fixed/默认分配。
3. 当前已验证的稳妥长视频基线是 4×8s；第一遍使用 Native Masked 传递前一段尾部，二采尚未完成 4×8 长视频验收。
4. 4090 上长视频的主要边界不是单次 VAE 显存，而是每段采样的约 23GiB 显存占用、主机内存、拼接/解码以及多参考图带来的运行时间。
5. 7×8 测试是用户主动中止，不应记录为 OOM 或机器上限。

## 后续验证边界

`refine_state` 应按 chunk 处理，不能直接理解成一次把完整 32s latent 做全局二采。适合的后续实验是：先对单个 8s chunk 做 refine smoke，再对 4×8 中选定 chunk 做二采并重新组装；暂不把完整 32s 二采作为 4090 基线。
