# T-comfy-ops-34 Ref2VA 输入音频与短剧配音方案研究

## 2026-09-15

### 本轮完成

- 建立研究任务，任务入口为 B 站视频 BV1ecbG6wE85。
- 核对视频元数据：标题为“AI声音带电无法听！人物情绪不到位？最强短剧模式音频驱动解决！Minimax H3 海螺H3 新LORA去油”，UP 主为阿硕讲ai；视频描述提供 SHUO-Canvas 和 RunningHub 的 H3 音频驱动多参考入口。
- 观察视频流程：先生成约 40 秒级的完整音频波形，再配合同内容的 shot1/shot2 提示词和参考素材驱动 H3 生成视频。
- 形成方案分层：
  1. 豆包 Audio 连续表演音频 → Ref2VA `ref_audio` → H3 原生音视频；
  2. 豆包 Audio/Breeze master → Ref2VA → NativeAudioLock → H3 口型表演；
  3. 对白/呼吸锁定，环境音、音乐、Foley 独立生成和混音。
- 新建研究文档：[docs/36_h3_audio_driven_dubbing_research.md](../../docs/36_h3_audio_driven_dubbing_research.md)。
- 已将研究候选结论 retain 到 `comfy-ops` Mem0 池，标记为待实验确认；`scripts/docs_check.sh` 已通过。

### 当前判断

- 视频展示的关键不是单句 TTS 音质，而是完整音频先固化了对白、停顿、情绪、多角色互动和时间轴。
- `ref_audio` 是参考条件，不等于复制或锁定音频；需要用 NativeAudioLock 才能把外部对白作为最终台词真值。
- 约 40 秒完整音频需要切为 H3 可接受的 shot 级片段，并处理 24 fps 帧网格、pre-roll 和 MC 接缝。
- H3 Ref2VA 多角色声音泄漏和声音失真仍有公开 Open Issue，不能把最新 ComfyUI 节点更新视为模型级声线问题已解决。

### 待做实验

- [ ] 同一段连续豆包 Audio：普通 `ref_audio` vs NativeAudioLock。
- [ ] 豆包 Audio 连续表演 vs Breeze 多句拼接，比较声线、情绪、口型和改词成本。
- [ ] 3–5 个 shot 的 NativeAudioLock + MC 连续链，记录音频接缝和角色声线漂移。
- [ ] Extender 长音频自动切片与当前手工 pre-roll 切片对照。
- [ ] 对白+呼吸锁定，后期补环境音/Foley 的混合声音链路。

### 证据

- B 站：[BV1ecbG6wE85](https://www.bilibili.com/video/BV1ecbG6wE85/)
- H3 官方：[MiniMaxAI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3)
- Extender：[tritant/ComfyUI_MiniMax_H3_Extender](https://github.com/tritant/ComfyUI_MiniMax_H3_Extender)
- 声音串台：[ComfyUI #15454](https://github.com/Comfy-Org/ComfyUI/issues/15454)、[MiniMax-H3 #17](https://github.com/MiniMax-AI/MiniMax-H3/issues/17)
