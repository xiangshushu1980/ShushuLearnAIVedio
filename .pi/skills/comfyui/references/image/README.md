# 图像生成能力

## 路由

| 目标 | 入口 |
|---|---|
| Qwen 场景/物件参考图、编辑、三视图 | 用户级 `/home/sean/.pi/agent/skills/comfyui/SKILL.md`；当前调用契约只在该处维护 |
| KREA 2 基础生图 | [krea2.md](krea2.md)；人物身份/提示词管线见项目 [docs/40](../../../../../docs/40_krea2_prompt_and_identity_pipeline.md) |
| ANIMA 基础生图 | 旧版 [workflows.md](../workflows.md) 的 ANIMA 小节 |
| 统一世界观/风格提示词 | [prompt-style.md](prompt-style.md) |
| 图片分析和批量对比 | [workflows/batch-qc.md](../workflows/batch-qc.md) |
| 放大、抠图、局部处理 | 旧版 [nodes.md](../nodes.md) 的图像编辑/超分小节，按需验证 |

日常 Qwen 生成走共享入口；KREA 2 / ANIMA 等专题按明确需求进入。不默认安装 ControlNet、IPAdapter 或大型扩展。
