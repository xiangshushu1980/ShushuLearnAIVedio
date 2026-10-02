# H3 Motion Booster REF2VA 对照测试

Owner: Sean。日期：2026-10-02。

用户指定版本：V0.2 REF2VA（3246346），不是页面标题所示的 Anime Edition（3299686）。一手来源为 [Civitai 模型版本 API](https://civitai.com/api/v1/model-versions/3246346) 和 [模型 API](https://civitai.com/api/v1/models/2840146)；仅核对作者说明和机器元数据，未使用社区评价。

模型：`ref2VA_Motion_v2.safetensors`，约 148 MiB，触发词 `dynv2`，SHA256 `B48CF96EBB14985789528449FE61985BABF786FEB658740A82A88AC685167FD9`。作者推荐 V2 权重 0.6–0.8，起点 0.7；REF2VA 版本说明认为身份一致性更好，但画质和稳定性可能有代价，此处尚未实测。

首次匿名下载返回 HTTP 401，作者要求登录。用户配置本机 Civitai API Key 后，2026-10-03 完成认证下载、SHA256 核验与安装；Key 不进入本实验记录。模型位于 `/home/sean/projects/ComfyUI/models/loras/ref2VA_Motion_v2.safetensors`。三档已完成，见 [QC](QC.md)、[并排视频](comparison.mp4) 与 [抽帧对照](comparison_contact.png)。没有创建远程任务，现行生产基线保持不变。

## 实验设计

- Ref2VA，已有红发法师全身角色图；正常连续左右侧步训练，单镜、固定机位、原生环境与动作声。
- 768×448，124 帧，24 fps，目标约 5.167 秒；20 steps，res_multistep，simple，BasicGuider，denoise 1，seed 2026100201。
- 原生 Ref2VA INT8 ConvRot 底模，AWQ 文本编码器，INT8 视频 VAE，FP32 音频 VAE，tiled decode。
- 三档仅改变 Motion LoRA：0（基线）、0.7、0.8。全部使用同一个完整六段式 prompt（基线也包含 dynv2），避免将触发词变化与权重变化混杂。无加速 LoRA 或模型 patch。
- 单 seed 探索，不能据此建立普适优胜结论。画质、参考身份、动作方向、循环次数、位移幅度、回弹、次级运动与音画一致性均须复核。

`manifest.json` 记录真实执行状态；`workflows/` 可直接由 ComfyUI API 加载。恢复执行前需校验模型 SHA256。`reference.png` 保留输入快照；`prompt.txt` 是三档唯一提示词正文。生成成功后将视频、history、QC 和分析保存在本目录，并仅清理当前批次 ComfyUI output 文件。

## 复现与交付

Owner: Sean。`run_cases.py --lease <lease-id>` 在既有共享实例上串行跑未成功的两个 LoRA case；事先检查队列并获得绑定实际 ComfyUI PID 的 GPU lease，脚本持续 heartbeat 并在自身队列清空后 observe/release。`analyze.py` 仅在 CPU 上生成三档运动代理指标和抽帧对照。

视频、参考图、contact sheet 和模型保留本机，Git 仅交付脚本、工作流、提示词、元数据与 QC。并排视频为静音，原始三档视频保留各自原生音频。三档耗时受冷热加载和条件缓存影响，不能解释为 LoRA 加速。

验证：三档视频 hash、帧数、尺寸与音频流均通过；两个 Python 脚本编译通过。`bash scripts/docs_check.sh` 在已有 `47_h3_reference_workbench_redesign.md` INDEX 收录问题上失败；本次新增引用检查通过，未修改该任务线文档。
