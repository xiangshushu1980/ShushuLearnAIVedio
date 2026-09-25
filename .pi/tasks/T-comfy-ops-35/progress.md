# T-comfy-ops-35：H3 提示词生成器主线

## 2026-09-15 外部更新复核

- 官方 `MiniMax-AI/MiniMax-H3` 的 `h3-prompt-writing` 核心契约未变：五种模式、三核心段/Ref2VA 六段式、标签与字段顺序仍以官方 reference 文件为准。
- 官方 skill 当前补充的结果提示已并入本地镜像：目标时长匹配 4–15 秒、引用标签跨段稳定、优先具体视觉/声音细节、I2VA/FL2VA/L2VA 明确首尾帧与时间线的连接。
- 官方 9 个 skill 的宿主边界再次确认：只有 `h3-prompt-writing` 是 agent-portable；其余风格 skill 依赖 MiniMax Hub-native 能力，不纳入本地提示词生成器运行时。
- 新候选 `T8mars/minimax-h3-prompt-skill-T8` 已发展为 Creative DNA 案例/Skill 库（README 标注 v1.4.2、225 个可安装目录）。定位为精选案例源，不替代官方格式，也不整库接入生成器。
- `awesome-minimax-h3-integration`、`mmx-h3-video` 等新集成 skill 主要解决 API/本地生成、媒体预检、提交与下载，不是新的提示词契约；暂不并入本任务核心。

## 决策与后续

1. 保持 A/B 生成器架构和官方字段契约不变。
2. 在案例采集阶段从 T8 Creative DNA 精选 3–5 个与短剧/多角色/对白/产品镜头直接相关的案例，提炼机制后写入 `docs/11`/`docs/17`，不复制模板全文。
3. 为官方 4–15 秒、标签一致、首尾帧连接建立共享回归向量，并同步 Python 校验器与 web-shotlist 的 zod schema。
4. 外部 skill 后续若要安装，先做 license、运行宿主和输入输出契约审查；本轮不新增运行时依赖。
