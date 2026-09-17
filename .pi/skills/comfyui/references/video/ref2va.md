# H3 Ref2VA 与 Object ref

## 当前定位

Object ref 是视频镜头消费的参考资产，不等于首帧，也不自动等于构图锚点。正式接入时需要在工作流/提示词中明确每张图的角色：身份、服装、场景、道具或效果。

## 读取顺序

1. 视频测试、生成或提示词任务先读 [h3-prompt-writing/SKILL.md](../../../h3-prompt-writing/SKILL.md) 的 Ref2VA 官方参考与 [docs/17_h3_prompt_writing_rules.md](../../../../../docs/17_h3_prompt_writing_rules.md)。
2. [docs/34_ref2va_generation_guide.md](../../../../../docs/34_ref2va_generation_guide.md)：日常入口和资源。
3. [docs/33_h3_mc_engineering.md](../../../../../docs/33_h3_mc_engineering.md)：连续性、MC 和音画时间线。
4. 旧版 [nodes.md](../nodes.md) 和 [params.md](../params.md) 的节点实现与历史参数。

当前 `T-comfy-ops-40` 只研究 Object ref 的可行性，不建立正式资产生产工作流。
