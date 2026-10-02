# H3 Motion Booster：长发、根须、飘带

Owner: Sean。2026-10-03；用户授权短片测试，未新建远程任务。用户认为0.7与基线接近，随后要求补权重1.0；新结果待查看。

采用新制作的树灵横幅参考：银色长发、棕色细根须、红色肩部飘带。参考由 **built-in imagegen** 生成，保存为 [reference.png](reference.png)，原始图像提示词见 [reference_prompt.txt](reference_prompt.txt)。生成结果偏写实幻想渲染，视频提示词按实际参考外观描述。根须按附着在角色身上的植物根须解释。

每个场景固定参考图、seed、六段式提示词和采样参数，仅比较无 LoRA 与 Motion Booster V0.2 REF2VA 0.7。两组都保留 `dynv2`，无加速 LoRA。单 seed 探索性结果，不是重复性能或物理模拟 benchmark。

| 场景 | 同步对照（左 0 / 右 0.7，静音） | 完整六段式视频提示词 | 原始视频（带生成音频） |
| --- | --- | --- | --- |
| 站立风吹 | [wind_comparison.mp4](wind_comparison.mp4) | [prompt_wind.txt](prompt_wind.txt) | [0](wind_base.mp4) / [0.7](wind_motion.mp4) |
| 大幅转体 | [move_comparison.mp4](move_comparison.mp4) | [prompt_move.txt](prompt_move.txt) | [0](move_base.mp4) / [0.7](move_motion.mp4) |
| 转体提高至1.0 | [三档同步对照：0 / 0.7 / 1.0](move_strength_comparison.mp4) | 同一份 [prompt_move.txt](prompt_move.txt) | [1.0](move_motion10.mp4) |

1.0补测仅提高LoRA权重，其他输入完全相同。实际仍以转身和材料拖尾为主，尚未见稳定的飘带幅度大幅增益；并出现约150–151像素的左右黑边，有效画面约466–468×448（接近1:1）。输出容器仍768×448；原图未裁切，工作流未改画布参数，三档同步对照保留生成的边栏。横幅参考对0.7有效的白边修正，不能推广为1.0也必然全幅。

用户后续观看反馈：0.7动作有穿帮，1.0动作还好。该反馈与“飘带增益有限”分别记录；没有确认具体故障由LoRA还是底模不稳定引发。作者对REF版已有画质/稳定性代价说明，版本区分及更针对连续性的作者项目见[作者资料复核](author_notes.md)。

风吹提示词安排左向右阵风：0–2 秒增强，2–6 秒持续，6–8 秒减弱；人物站立，三种材质按不同刚度响应。转体提示词安排连续的大幅左右交替 pivot，弱环境风，观察身体带动后的拖尾与回摆。实际转体执行偏向较大范围连续转身，未严格实现指定的左右交替周期。

固定参数：Ref2VA INT8 ConvRot 底模；Qwen3VL NVFP4/AWQ 文本编码；768×448、192 帧、24fps、8 秒；20 步 `res_multistep/simple`，BasicGuider、denoise 1、seed 2026100302；reference VAE 开启、`ref_image_size=match`；INT8 video VAE、FP32 audio VAE、tiled decode、原生 attention。未重启共享 ComfyUI。

本例无 LoRA 已能生成显著的长发与飘带动态。风吹时 0.7 的头发在选取帧中更早、较持续地展开；飘带两组均明显，根须增益不明显。转体两组均有大幅拖尾，0.7 改变节奏与轨迹，未观察到三种材质都稳定放大的效果。风向一致性和动作执行仍有限，详见 [QC.md](QC.md)。这些结果支持将该 LoRA 视为运动倾向调整，尚不足以作为本项目默认配置。

所有原视频已从 ComfyUI output 哈希校验迁入本目录，并清理本批次原落点。图、视频和日志留本机；文本、工作流、manifest、history、ffprobe、QC 可随 scoped commit 交付。权威证据是 [manifest.json](manifest.json)、[integrity.json](integrity.json)、各 case 的 history/runtime.log；[qc_secondary.py](qc_secondary.py) 可重建对照与接触表。运行环境使用 `/home/sean/projects/ComfyUI/venv/bin/python`（包含 OpenCV）。`setup.py` 已有 manifest 时拒绝重置；复跑用新实验目录，续跑用 `run_cases.py` 配新的 GPU lease。
