# T-comfy-ops-14: ALLinONE / Extender / Easy 集成形态横向对比

- 任务线: comfy-ops-allinone
- 状态: 已完成（2026-08-17）
- 开始: 2026-08-17

## 目标
读三个社区集成节点仓库 README/工作流，与现有主力工作流对比，出选型结论（替代/借鉴/忽略）：
1. LeonQ8/ComfyUI-ALLinONE-MinimaxH3（163★，Beta，单节点全管线）
2. tritant/ComfyUI_MiniMax_H3_Extender（106★，链式多片段 + motion context + disk cache）
3. nkxx188/ComfyUI-MiniMaxH3-Easy（436★，单紧凑工作流 T2V/I2V/首尾帧）

## 负责文件
- 无文档变更（结论大概率走 mem0 / 或追加 docs 已有分册）

## 进度
- [x] 开场：recall 经验 + state 对账
- [x] 抓取三仓库 README/工作流结构（README + workflows + config + prompt_guides manifest）
- [x] 与现有主力（minimax_h3_i2v_api.json 等）对比
- [x] 出选型结论 → mem0 retain（4 条，agent=comfy-ops-allinone）
- [x] 收尾：progress + [STATE] 更新 + scoped commit

## 选型结论（详版在 mem0）
- **ALLinONE（163★, Beta, GPL-3.0）→ 忽略**：单节点黑盒，加速预设全为本机已有包组合；Audio Drive/Chain 依赖他系包（vrgamegirl / seitanism MultiRef，与本机 NikoDemon80 MC 栈非一家）
- **Extender（106★）→ 借鉴不装**：长视频链式正解（disk cache 78KB 自研 + 逐片段 Validated 验证 + 音频 declick）；subject_definitions 惯例本项目 docs/17 已覆盖；与本机 MC 栈功能重叠，留作未来 30s+ 长片任务线评估
- **Easy（436★, MIT）→ 推荐安装作 UI 交互面**：4 节点 + 采样解码全在节点外（16 节点结构与官方原生 15 节点同构，不破坏脚本化跑批）；Media 多链路端口 + @ 引用编辑器 + <d> 对话块 + API 优化器 + Pass2 两阶段放大；**prompt_guides 与本项目 8 skill 深度同源**（h3_general guide 与 h3-prompt-writing SKILL frontmatter 逐字一致）

## 遗留待办
- 安装 Easy 后验证 ComfyUI 0.33 兼容
- 对照其 guide 升级本项目 skill 分层（通用+场景）机制

## 卡点 / 决策记录
- 无卡点；结论已落 mem0 供后续任务线检索
