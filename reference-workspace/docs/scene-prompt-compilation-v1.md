# 已有场景提示词编译 v1

Owner: Sean

已有场景的 Agent 图片方案使用 `sceneIntent`，由服务端从持久化实体资料和项目设定编译提示词。Agent 的自由提示词、保持不变及未知项被编译结果替换，避免补写未经登记的材质、灯光与几何。

## 数据与调用

`sceneIntent: {focusText, anchorIds, cameraAnchorId?}`：focusText 必须是当前介绍或外观原文片段；锚点和可选相机位置只能引用本场景已确认锚点。细节必须有目标。角度及细节必须依赖本场景主图、基础场景主图或明确选择本场景参考图。

`POST /api/authoring/:projectId/entities/:entityId/scene-image-preview` 接收完整图片步骤，返回编译后的步骤；不保存、不生成。PC 界面支持选择文字目标、已确认锚点、预览及保存新版本。编译提示词和规则只读。

返回 `scenePromptBasis` 包含 compilerVersion=1、entityId、textHash、spatialHash、spatialStatus、projectRulesHash。项目哈希覆盖 worldRules、visualStyle、decisions。登记介绍、外观、确认空间及项目规则原文进入提示词；未确认空间不会升级成事实。相邻、连通不推断共线；未知也不意味着禁止参考图中的布局。取景位置和临时人物行为不会写回固定空间。

源资料改变后，工作流预览、输入准备、匹配该步骤的草稿生成和预备批次提交均拒绝旧版本，需按当前资料修订。编译来源超过 16000 字符会明确报错，不静默截断。

## 兼容与边界

旧步骤及手工自由提示词继续兼容；新场景初始设计仍是设计提案。Agent 提交已有场景方案必须使用此结构。编译不改实体资料、不自动确认空间，也不自动运行生成。原文片段匹配并非语义审核，已有错误设定仍需人工修订。受约束文字不能保证图像模型不自行补全未知细节。

## 验证

73 项自动化测试通过；Vite 构建通过。隔离 PC 页面完成目标从长凳区改为入口、预览、保存新版本、应用与刷新持久化检查。

真实 Pi 单次接续实验保存在本地 experiments/sean_reference_authoring_goal_20261004/real-authoring-scenarios-1791107859766.json：模型选择入口和长凳区，服务端提示词未保留模型先前补写的木材、磨损和灯光。该实验运行于开发中的编译器，早于最终 projectRulesHash 命名和可选相机字段；这些最终字段由自动化测试覆盖。没有提交 ComfyUI，没有证明实际图像空间一致性。
