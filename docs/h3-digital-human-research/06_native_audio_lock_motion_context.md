# H3 NativeAudioLock 与 Motion Context 经验总结

更新时间：2026-09-03

## 1. NativeAudioLock 的实际机制

`MiniMaxH3NativeAudioLock` 不是普通的音频参考输入，而是对 H3 联合音视频 latent 做定向替换和掩码：

```text
外部音频 → Audio VAE 编码 → 替换 AV latent 的 audio 部分
原 video latent → 保留
video noise mask = 1 → 视频继续去噪
audio noise mask = 0 → 音频保持干净，不再被 H3 重写
```

节点同时给模型写入 `minimax_h3_lock_audio_clean = True`。因此它的效果是：外部音频保持真值，H3 仍然根据这条音频时间轴生成匹配的嘴型、表情和动作；它不是画面锐化或分辨率放大节点。

代码证据：`ComfyUI/custom_nodes/ComfyUI-H3-NativeAudioLock/__init__.py`。

## 2. AV latent、参考音频和 Motion Context 的分工

```text
参考图/参考视频       → 身份、服装、构图、视觉动作条件
普通参考音频          → 声音/节奏的软参考，H3 仍可重新生成音频
NativeAudioLock       → 外部音频编码后的强约束，视频分支适配它
初始 AV latent        → 整段视频的时空生成画布和起始状态
Motion Context latent  → 上一段尾部状态到下一段的连续性条件
```

H3 的初始 latent 不是只决定第一帧。它覆盖整段视频的时空位置；采样过程中，prompt、参考条件、音频条件和 Motion Context 会共同参与每一步更新。

## 3. `context_length=22` 的当前理解

根据当前实际测试，`context_length=22` 应按 22 个视频 frame 理解：

```text
上一段视频的最后 22F
→ Motion Context
→ 下一段视频的生成条件
```

它不是上一段视频的前 22F，也不能按 `22 / 24fps` 简单换算成 0.9 秒。音频上下文是独立参数，当前默认使用：

```text
context_length = 22
audio_context_length = 24
```

22F 共同形成一个连续时序窗口，不是 22 张互相独立的参考图。模型使用时序位置编码和注意力处理它们，因此不能假设每一帧权重完全相同。

当前合理的工程假设是：

- 最后几帧最接近续接边界，通常对下一段开头影响最大；
- 中间帧提供动作、姿态和镜头运动趋势；
- 第一帧仍提供窗口起点和较长上下文，但不应被视为唯一关键帧；
- 以上是机制推断，不等于已测得的严格注意力权重。

## 4. 对话分段方式

对话应尽量在自然停顿、换气或语义边界切分，保存上一段结尾的连续 22F，而不是随意截取 22F：

```text
上一段：……说话动作 → 换气/停顿 → 句尾
                              └─ 取最后 22F
下一段：从真实音频时间轴的下一位置开始
```

不要为了凑 22F 重复或截断粤语音频。视频 context 和音频 context 要按各自节点及真实时间轴对齐。

## 5. Trim 约定

常见做法是保留第一段完整内容，删除第二段开头与第一段重叠的部分：

```text
第一段：A A A A B B
第二段：      B B C C C C
              ↑ 重叠区
输出：  A A A A B B C C C C
```

当前项目的 `MiniMaxH3MotionContextTrim` 也是修剪第二段前部，`match_tail=True` 用于按上一段尾部对齐。

## 6. 尚未定论的验证项

还没有证据证明 22F 内部存在固定的线性权重，也没有证据证明最后 1F 永远比前 21F 更重要。应使用同 seed、同 prompt、同音频做消融：

```text
A：完整 22F
B：替换/删除第 1F
C：替换/删除第 22F
D：只保留末尾 6F 或中间 6F
```

比较下一段开头 1 秒的接缝、嘴型、姿态和运动方向，才能把“边界帧更重要”从合理推断升级为实测结论。

