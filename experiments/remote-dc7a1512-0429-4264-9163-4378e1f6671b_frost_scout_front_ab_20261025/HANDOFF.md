# 新对话恢复入口

任务：remote-dc7a1512-0429-4264-9163-4378e1f6671b，当前 controller generation4；以 Task Center 最新 info/checkpoint 为准。用户将于新对话修订整体流程，本轮仅先设置通用默认。

## 当前默认

`Create a finished image of the same subject. Preserve the subject design and rendering style.`

入口：`prompt_cause_20261025/candidate/`，包含 prompt、schema、API graph 和 `run_single_view.py`。默认无站姿、手臂、全身/脚部可见、居中、视角、背景、光照或角色色名要求。view 改为可选；显式传 front/left_profile 才追加视角句，须与当前意图和深度输入一致。模型/采样参数本轮未重订。

## 证据边界

- 发灰诊断已完成：相同输入/seed/图接线下，B目标画面提示正常，B加旧两句灰度深度说明后的C在两seed变近单色灰；见 prompt_cause_20261025/QC.md 和 parent_cause_audit.json。
- 之前14张新增图（原因对照、正侧面验证及单图入口回归）使用的是带站立全身要求的旧模板。新通用默认未出图、未视觉验证；不能继承旧模板的通过状态。
- 旧prompt已存 candidate/historical/standing_full_body_prompt_v1.txt；旧代码/模板版本见 da6ae98。历史请求、输出、回执、hash、QC不改写。
- 工作流未保证初始参考图双臂离躯干，不能把这一姿势当通用前置条件。新对话需重新审查参考图、3D、深度和目标输出的整体合同。
- 弓/建模/参考图问题属于原 qwen-character-sheet 主任务 remote-ff12d609-9b58-4c0a-8760-0a8017eabfa3，本轮不修改其状态或QC。
- 本轮仅本任务内配置，不更新共享skill/preset，无GPU生成或资源租约。

新对话先 task-center info，再按正常 handoff 接管（本任务 checkpoint 就绪，控制权尚未转移）；读本文件与 candidate/README.md 后继续整体修订。
