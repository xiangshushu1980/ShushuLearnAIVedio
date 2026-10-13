# Qwen-Image-2.1 多参考图本地测试

> Owner: Sean。状态：review。

## 目的

验证本地 Qwen-Image-2.1 对角色概念图的多参考控制：人物身份、服装、武器、姿势/表情、变身、环境、多物品和多人物。

## 结果概览

- 双参考人物 + 服装，以及三参考人物 + 服装 + 武器均成功。
- 后续六项生成全部完成：姿势/表情、精灵战士变身、衬衫换色、添加场景、剑盾双物品、两个人物同框。
- 四张 ref 的多物品与多人物 case 均成功；输出和边界见 [QC](QC.md)。
- 这是每项单 seed 的可行性测试，不作为跨人物/复杂场景的稳定性基线。

## 文件

- `manifest.json`：模型、素材哈希、参数、运行记录和结果路径。
- `api_workflows/`：各 case 的 ComfyUI API 工作流。
- `prompts/`：case 专属提示词。
- `inputs/`、`outputs/`：参考图与选定输出。

## 本轮追加测试（静态动作 / 场景 / 发型）

- `test09_sword_slash`：明显的横向挥剑动作。
- `test10_forward_run`：向前奔跑动作。
- `test11_replace_scene`：把灰蓝摄影棚背景换成夕阳城堡庭院。
- `test12_hair_finetune`：只微调卷发顶部体积和两侧 taper。

Qwen 输出的是静态帧；动作案例比较关键姿势是否改变，不表示生成了连续运动。四项已完成，结论追加在 QC。

## 双人面向与配合动作复测

- `test13_face_to_camera`：先把两人的脸转向镜头并保留身份。
- `test14_duo_coordinated_headwear`：基于修正后的合照，让男主挥剑、女同伴举盾掩护，并分别加帽子和王冠。

- `test15_duo_action_pose_refined`：加入独立挥剑姿势 ref，再加强剑击/盾护配合。
