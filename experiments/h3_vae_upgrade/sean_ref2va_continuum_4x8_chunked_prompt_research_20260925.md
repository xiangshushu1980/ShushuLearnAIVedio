# Sean — Continuum 社区研究与 4×8s 提示词重写

owner: Sean
date: 2026-09-25

## 研究结论

1. Continuum 官方 V3.4 文档要求 Timeline header 单独占行，格式为 `[0-8s]`、`[8-16s]`；时间范围通常应匹配 `chunk_seconds`。Inline 的 `[0-8s] prompt` 不会被可靠识别，无法解析时会回退到 Fixed 或其他可用模式。
2. Fixed 是一个 prompt 重复给所有 chunk；List 用 `---` 分隔，每段对应一个 chunk；Timeline 按物理时间范围选择对应 chunk prompt。
3. 官方示例强调下一段从上一段的 exact final state 继续，而不是只重复角色外观。Continuum 负责 prompt routing，Native Masked 负责精确 AV latent continuation。
4. 社区 Motion Context Auto-Chain 采用 shared style + numbered per-clip prompts，每个 clip 独立保存、续接和重渲染；H3 Multishot 工作流也使用 one prompt per shot，并用 `---` 分隔。
5. 社区经验更适合把一个 chunk 设计成一个连续 shot；如果一个 chunk 内放多个 shot，模型仍可能执行，但 chunk 边界和 shot 边界会混在一起，难以判断接缝来源。

## 本版设计

- 4 个 chunk × 8 秒，总计约 32 秒。
- 每个 `[start-end]` header 单独一行。
- 每个 chunk 内只有一个连续 shot。
- 每个 chunk prompt 自包含六段式 Ref2VA，避免依赖全局文本被错误重复或丢失。
- Chunk 2 明确从 Chunk 1 的人物位置、罗盘右手状态继续，并在本段完成右手→左手转交。
- Chunk 3 明确从已完成的左手持罗盘状态继续，开始唯一青色法术。
- Chunk 4 明确从已激活法术状态继续，不重新生成法术。
- Native Masked Strong 39；暂不使用 Motion Context、Plus 二采或 Sylvanas。

## 来源

- 官方 Plus README：<https://github.com/xmarre/ComfyUI-H3-Continuum-Plus>
- Continuum 上游 README/社区 fork：<https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum>
- Motion Context Auto-Chain 社区说明：<https://comfyui-wiki.com/en/news/2026-08-25-h3-motion-context-auto-chain>
- H3 Multishot 社区工作流：<https://huggingface.co/joeygambino/MiniMax-H3-Multishot-Workflow>

## 当前状态

提示词已按真实 Continuum Timeline 语法重写，但尚未提交生成。下一步先检查每个 chunk 的最终 prompt routing，再运行 4×8s。
