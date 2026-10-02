# H3 Motion Booster 结论谱系

Owner: Sean。独立记录本次新测试，避免修改其他任务正在维护的 h3-models.md。

### C-20261003-01 | Motion Booster V0.2 REF2VA 可加载、可生成；侧步单例存在白边代价
- 状态：🟡质量待用户验收；技术兼容性已验证（2026-10-03）。
- 现行值：Civitai 2840146 / version 3246346，`ref2VA_Motion_v2.safetensors`，触发 `dynv2`，与本机 Ref2VA INT8 ConvRot 底模的 208 组目标名称和矩阵形状匹配，ComfyUI 原生解析 208/208 补丁；0.7 和 0.8 两档均完整生成，运行日志无未加载键警告，无 OOM。
- 条件：ComfyUI 0.37.0、RTX 4090 24GB、单角色全身参考、正常侧步、同 seed 和完整六段式 prompt、768×448 / 124 帧 / 24fps、20 steps / res_multistep / simple、无加速 LoRA、原生 attention、INT8 video VAE / FP32 audio VAE / tiled decode。
- 质量边界：两档均出现白色左右留白；0.8 横向红色区域质心变化相对基线约 1.26×，0.7 约 1.08×。这是运动代理指标，受服装与姿势影响，不等同于动作正确率或普遍质量提升；保留现行生产基线。
- 时间线：2026-10-02 首次匿名下载明确 401；用户配置 API Key，2026-10-03 认证下载并核对 SHA256 后完成无 LoRA / 0.7 / 0.8 对照。无远程任务立项，用户质量验收待定。
- 当前模型登记：[docs/02_models.md](../../docs/02_models.md)。
- 证据锚：[实验 README](../../experiments/sean_h3_motion_booster_ref2va_20261002/README.md)、[QC](../../experiments/sean_h3_motion_booster_ref2va_20261002/QC.md)、manifest.json、lora_header_compatibility.json、lora_native_parser_check.json、两档 runtime.log 与 history、motion_metrics.json、audio_levels.json。视频与模型留本机。
- 覆盖关系：不覆盖 Turbo/PDD、FaceRefine 或 Ref2VA 生产结论；本次没有叠加这些路线。
