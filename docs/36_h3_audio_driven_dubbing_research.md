# H3 音频驱动配音与 Ref2VA 输入音频研究

> 状态：研究中（T-comfy-ops-34）
> 
> 建立日期：2026-09-15

## 1. 当前研究对象

近期 B 站视频 [AI声音带电无法听！人物情绪不到位？最强短剧模式音频驱动解决！](https://www.bilibili.com/video/BV1ecbG6wE85/) 展示了一条与“逐句 TTS 后逐镜头驱动”不同的短剧路线：先用豆包 Audio 根据参考音频、文本和情绪提示生成一段完整的戏剧音频，再把同一内容拆成镜头提示词交给 MiniMax H3，通过 `Audio 1` 作为音频参考驱动镜头推进。

该路线的核心不是单句音质，而是把对白、停顿、呼吸、情绪、打断和多角色互动先固化为一条连续表演音频。视频提示词负责画面中的人物、镜头、动作和场景。

## 2. 当前方案分层

### A. 音频优先的探索路线

```text
剧本/情绪/参考音频
    ↓
豆包 Audio：完整场景或连续对话音频
    ↓
按 shot 切分并作为 Ref2VA Audio 参考
    ↓
H3 Ref2VA：同一内容的镜头提示词 + 角色/场景参考
    ↓
H3 生成视频和原生音频
```

这里的 `ref_audio` 是参考条件，不等于原始波形锁定。H3 可能重新生成声音，因此仍可能出现台词变化、声线漂移或多角色串音。适合快速探索完整戏剧感、环境声和动作声。

### B. 当前生产基线

```text
豆包 Audio / Breeze / 演员音频：最终对白 master
    ↓
按镜头切分，加入必要 pre-roll
    ↓
H3 Ref2VA：角色、场景、动作、镜头
    ↓
NativeAudioLock：锁定最终对白音频并驱动口型
    ↓
Motion Context：连接连续镜头
    ↓
独立环境音、音乐、Foley 和最终混音
```

该路线把“台词真值”和“画面表演”分开：外部音频决定实际说了什么，H3 负责根据该波形生成口型、表情和动作。台词修改后，必须用新音频重新生成对应视频，不能继续使用旧口型。

### C. 混合声音路线

音频 master 可以包含对白、呼吸和关键动作声；H3 原生音频或后期 Foley 负责环境声、物理音效和音乐。最终以独立 stems 混音。若先得到 H3 混合音频，再做语音/音乐/环境分离，只作为抢救手段，不作为主链；项目已有 AudioSep/FlowSep 不可靠的实测记录。

## 3. 重要边界

1. **Ref2VA 音频参考不等于音频锁定。** 官方 H3 Ref2VA 的音频输入是参考信号；每段参考音频通常需要落在 2–15 秒范围，总参考时长也有限。B 站演示中约 40 秒的连续音频不能简单作为一个原始 Ref2VA 输入，应按 shot 切片，或由 Extender 做分段调度。
2. **同一提示词不能替代音频锁定。** 音频和文本都描述对白时，二者必须逐字一致；若不一致，H3 有可能在音频参考和文本对白之间选择不同结果。
3. **MC 只解决连接，不解决声线真值。** Motion Context/Extender 可改善镜头、 latent、缓存和音频接缝，但普通 `ref_audio` 仍可能发生角色声音漂移。持续声线应依赖同一条连续角色音频或 NativeAudioLock。
4. **长音频切片必须保留上下文。** 每个片段需要在 H3 帧网格和音频时间线上对齐，并保留 pre-roll；最终成片音频应以原始 master 为准，避免片段重新编码造成接缝。

## 4. 候选扩展和工具

- [ComfyUI MiniMax H3 Extender](https://github.com/tritant/ComfyUI_MiniMax_H3_Extender)：Ref2VA 多片段、Motion Context、音频按时间线切片、缓存、验证、断点恢复和接缝处理。它改善长序列工程性，但不是声音身份锁定器。
- `ComfyUI-H3-NativeAudioLock`：将外部音频编码后锁入 H3 音频 latent，适合把豆包 Audio 或 Breeze master 作为对白真值。
- 项目内部标准：[H3 Ref2VA + NativeAudioLock + MC 工程流程](33_h3_mc_engineering.md)。

## 5. 后续实验矩阵

用同一角色、同一镜头和同一段多角色对白，对比：

| 组别 | 输入音频 | H3 音频路径 | 目的 |
|---|---|---|---|
| A | 豆包 Audio 连续表演音频 | Ref2VA `ref_audio` | 验证社区音频参考路线 |
| B | 豆包 Audio 连续表演音频 | NativeAudioLock | 验证对白真值、口型和情绪保持 |
| C | Breeze 多句拼接音频 | NativeAudioLock | 与当前已测试 TTS 路线比较 |
| D | 豆包 Audio 连续表演音频 | Ref2VA + MC 多段 | 验证长片段的连续声线和接缝 |
| E | 豆包 Audio：对白+呼吸 | NativeAudioLock + 后期 Foley | 验证混合声音生产链 |

每组记录：逐字准确率、角色声线、口型同步、情绪连续性、环境音质量、片段接缝、改一句台词后的重生成范围。

## 6. 当前结论

当前不再把问题表述为“豆包 Audio 是否替代 Breeze”。更准确的判断是：

> 豆包 Audio 提供的是连续戏剧表演轨道；Breeze 更适合可控、可编辑的对白音频；H3 Ref2VA 提供画面和原生声音参考；NativeAudioLock 提供对白真值；MC/Extender 提供长镜头连接。

短剧主线优先测试“豆包 Audio 连续表演音频 + NativeAudioLock + Ref2VA + MC”，同时保留普通 `ref_audio` 路线作为 H3 原生环境音和快速探索基线。

## 7. 证据入口

- MiniMax H3 官方仓库：[MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3)
- 社区工作流视频：[BV1ecbG6wE85](https://www.bilibili.com/video/BV1ecbG6wE85/)
- 长序列扩展：[ComfyUI_MiniMax_H3_Extender](https://github.com/tritant/ComfyUI_MiniMax_H3_Extender)
- 声音串台公开问题：[ComfyUI #15454](https://github.com/Comfy-Org/ComfyUI/issues/15454)、[MiniMax-H3 #17](https://github.com/MiniMax-AI/MiniMax-H3/issues/17)
