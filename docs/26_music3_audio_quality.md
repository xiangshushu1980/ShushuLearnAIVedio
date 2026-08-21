# MiniMax Music 3 音质与 Prompt 探索定论

> 关联任务：T-comfy-ops-16（Music3 评估）+ 2026-08-22 音质探索。结论由多轮试听实证（30+ 首）。

## 1. 模型与音质上限

- Music3 原生输出 **32kHz / 16bit 立体声**（SaveAudio 可重采样到 44.1k）；纯文本条件生成，无音频输入，不支持续写/拼接（music3lab 实证）。
- **音质规律定论**：Music3 生成**高频持续音**（笛/长音管乐等）时音色不纯净、带颗粒杂音——这是模型对这些音色的频谱建模本征缺陷。**非高频、短促瞬态乐器（低频/打击/拨弦/吉他/人声）干净**。
- 实测结论：此杂音**后期不可根治**（超分/母带/demucs 分离/重混均无法消除，因源头在生成）。
- 应用：选材避雷——避免"高频持续音"当主角，用低频/打击/短促拨弦/人声为主。

## 2. Lyrics prompt 坑（台词问题，已验证修复）

**坑**：lyrics 区的非歌词文字（如 `no vocals`、`Instrumental. xxx` 描述）会被 Music3 当**台词念/唱**出来，导致"有人读提示词"。纯器乐指令（caption 写 No vocals）遵守也不完全。

**修复**（已验证有效）：纯器乐曲子**歌词区只留方括号标签**（`[Intro]` `[Section 1]` ...），不写任何会被念的文字；全部乐器/编曲描述放进 caption 的 Arrangement。详见 `*.fix_input.json`。

## 3. 其他 prompt 经验

- **乐器指定不严格**：会插入未指定乐器（string_quartet 要求纯弦乐却出小号；testinst 写 NO wind 仍出笛子）。
- 中文/中英混合歌词、单主声线稳定；双平级主唱不稳（意外涌现）；圆括号角色标注 `((男·中文))` 比 caption 抽象 Singer A/B 可靠（详见 T-16 control_baseline）。

## 4. 音质提升链路（工具手册）

```
Music3 输出 mp3 (44.1k) 
  → FlashSR 超分到 48kHz 补高频  (scripts/upscale_music3.py)
  → ffmpeg 母带 (-14 LUFS/-1dBTP/去浑浊)  (scripts/master_music.py)
  → 可选 demucs 分离 stems → 乐器轨增强重混  (scripts/remix_music_stems.py)
```
- 全部在 `comfy-ops/scripts/`，批量用 `batch_music.sh`（改 GEN 数组）。
- **注意**：超分对高频持续音杂音无帮助（甚至会加重），该链路主要提人声/低频/整体响度；乐器杂音靠选材规避。

## 5. 产出文件

- `output/audio/*_mastered.wav`：30+ 首各国风格测试曲（48kHz），含 `_fix` 版（无台词）。
- 世界音乐覆盖：日本/印度/爱尔兰/中东/巴西/非洲/俄罗斯/墨西哥/意大利/德国/北欧/夏威夷/土耳其/希腊/苏格兰/越南 + 中式/WOW 等。
- 输入 prompt：`scripts/*_input.json`（`_fix` 为纯标签无台词版）。

## 6. 待续事项

- 关注 MiniMax H3 / Music 后续更新；需要真正成片时再继续探索。
- 未做：ACE-Step（48kHz）高频纯净度对比；高频持续音去噪实验（预期伤音色，未做）。
