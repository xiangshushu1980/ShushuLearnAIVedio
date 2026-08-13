# context-opt — 首轮对话上下文优化

- 状态：进行中
- 目标：新对话静态上下文 10K 削减（工具裁剪 + AGENTS 压缩 + skill 描述精简）
- 已确认决策（用户 2026-08-05）：A 黑名单排除 76 个 comfyui 工具（comfy-cli 先排、音频 2 个待定、civitai 记 TODO）；B/C 一起做
- 负责文件：.mcp.json、~/.pi/agent/AGENTS.md、comfy-ops/AGENTS.md、3 个 skill frontmatter
- 卡点：无

## 收尾记录（2026-08-05）

- 全部落地：.mcp.json excludeTools（76 工具）、AGENTS×2 压缩、3 skill 描述精简、双仓库 commit、mem0 通告（global + comfy-ops [STATE] + 经验）
- **待验证**：excludeTools 需 `/reload` 后生效，重连 comfyui 应显示 105 工具（当前 181 是旧配置）
- 后续 TODO：T1 TTS 方案调研、T2 模型源调研（已入 [STATE] 全局待办）
