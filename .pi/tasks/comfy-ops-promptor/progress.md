# T-comfy-ops-03: H3 Promptor + prompt-enhancer-T8 对比（任务线 comfy-ops-promptor）

状态：🟡 产出完成，待用户验收（2026-08-17）

## 做什么
对比两个提示词自动化工具（1038lab ComfyUI-MiniMax-H3-Promptor 138★ V1.2.0 + T8mars comfyui-minimax-h3-prompt-enhancer-T8 132★）与现有 17 号规则/工具 B 合成，吸收可用模式进 11 案例库/17 规则。

## 做了什么（2026-08-17 一次性完成）
1. **读两仓库结构**：README + 1038lab templates/（system_base + 8 个模式文件）+ vision_prompts.json + T8 nodes.py（COMMON_SYSTEM_RULES / OFFICIAL_CORE_ADDENDUM 冻结契约 @093f3129 / 8 场景 skill / TASK_RULES）+ case_templates/catalog.json（112 项）
2. **抽样输出对比**：同一输入（汉服少女×灯笼街雨夜 I2VA 8s）× 三契约 × deepseek-chat：
   - A 1038lab：3 镜叙事 + Audio:/Music: 两行收尾，Music: N/A，无虚构（1393 tok）
   - B T8 兼容/balanced：1 镜中文三字段，**balanced 档擅自加配乐**（1676 tok）
   - C 我方 base-en：1 镜英文三字段，**虚构了未请求的 (S1) 台词**+自动加 guzheng（3958 tok）
   - 归档：experiments/promptor_compare/（README + 3 抽样 + system_base + t8_case_catalog.json）
3. **吸收落盘**：
   - docs/17：模式专属（FL2VA 单镜偏好/I2V 首帧强对齐不引新角色）+ 防虚构句 + Ref2VA 防误判 4 条 + 验证清单 2 项
   - docs/11：模式 7（两行声音收尾）/模式 8（结构标签程序注入）/模式 9（外部案例条目格式+精选锚点表）+ ⚠ 冲突 3 条 + 速查表
   - docs/16：§四.1 对抗幻觉机制 6 条（结构注入/防虚构句/优先级链/三档改写默认 strict/参考模板融合边界/指南冻结哈希）

## 关键结论
- 1038lab = 架构参考（视觉分析解耦 + 结构标签代码注入 + 两行声音契约）；T8 = 内容参考（官方 skill 冻结哈希 + 110 案例 selector 条目格式）
- 我方 base-en 契约最大的坑是**幻觉台词**，17 号已补禁止句
- T8 balanced/creative 档违反 17 号无 BGM 决策 → 生成器默认 strict 档
- T8 的 8 个官方场景 skill = 本地 8 个 skill 同源（MV v0.6.6 已同步），无新内容

## 负责文件
docs/17_h3_prompt_writing_rules.md、docs/11_h3_case_library.md、docs/16_prompt_generator_plan.md、experiments/promptor_compare/

## 未做（如需后续）
- 视频实测两工具输出（需 ComfyUI + API key，未跑）
- T8 catalog 110 selector 全文翻译/逐条吸收（已归档备查，按需取用）
