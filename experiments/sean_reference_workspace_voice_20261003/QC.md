# Reference 声音阶段 PC 与运行记录

Owner: Sean。2026-10-03。任务 remote-1eae8efb-cdeb-416b-8bee-7daf781801af。

## 真实运行

文字声音设计 run `698812b4-38b6-4c12-b91a-0877b23955f4`，Comfy prompt `dda9827f-5108-4832-84cf-04881b38202c`。中文、日常交流、三段情绪试听，声音描述“成年女性，声音清晰温和，普通话自然，语速适中，正常说话，不唱歌。”，seed 42、CFG 1.5。

使用已有 BreezeTTS2LoadModel/BreezeTTS2Speaker/BreezeTTS2MultiSpeaker/SaveAudio；BF16、CUDA、SDPA、cuda_graphs，download_if_missing=false。三段共用种子、各自附加系统情绪引导。输出 FLAC 回收后转为 24kHz、单声道、16 位 WAV。

| 台词类型 | 时长 | 本地证据 |
| --- | --- | --- |
| 平静 | 3.92s | sean_voice_1.wav |
| 喜悦 | 3.84s | sean_voice_2.wav |
| 认真 | 4.24s | sean_voice_3.wav |

运行成功，创建到结果登记约 31.18 秒（含模型准备/生成/回收，不是纯推理性能基线）。完整输入、工作流和输出 metadata 见同目录 JSON。WAV 留本机忽略，应用业务音频另存在 reference-workspace/.data。

## PC 检查

1440×1000 页面：声音独立入口可用，描述/目的/台词范围可保存；三段可加载，audio readyState=4，duration 与文件匹配，error=null。实际播放首段，currentTime=1.26 秒、paused=false，其余播放器暂停。无横向溢出，浏览器 console 0 errors/warnings。

将刚生成的 3.92 秒 WAV 导入，统一保存为新 voice-source，音源播放与转写输入可用；勾选确认后可生成，修改转写立即清除确认并禁用生成。后端拒绝 transcriptConfirmed=false（HTTP400），没有新增 run；见 sean_api_checks.json。该导入只检查管线，检查后删除音源并保留墓碑，没有用它生成克隆声音。

点击声音历史恢复 design、三段系统台词、描述、seed 42/CFG 1.5 和 sourceRunId；保存后重启应用，原草稿和三段结果仍在。历史工作流兼容状态为 true。样例未确认当前声音，留给用户试听。主形象和视图仍保持之前选择。

本批 ComfyUI output 文件已回收清理；GPU 租约释放。只重载 Reference 应用，ComfyUI 未重启，未新增模型/依赖。未新增/运行单元测试。

## 限制

- 没有人工发音、自然度、情绪强度和跨段音色质量验收，布局标签不是效果保证。
- 真实录音的克隆/声音引导、英文输出尚未实跑。
- 当前声音版本保护/替换代码已接入；样例不由开发者代替用户定稿。
- BGM、环境音、自动转写、H3 下游和手机未接入。

## 2026-10-03 固定基础音色修正（Owner: Sean）

原 v1 三段文字设计分别生成，种子相同不能证明身份一致。v2 先设计或从录音建立一段中性基础样音，选定后情绪阶段引用同一音源与准确转写。情绪输出不可定稿成基础声音，不可再作为基础引用；输入和产物保留 anchor ID/hash/转写。

构建成功；1440×1000 PC 模板填入、特征自定义、旧历史载入、已有当前基础声音选择、未确认禁用生成检查通过，无横向溢出及浏览器 console error。12 声音模板／8 类特征／5 台词题材。只读构图见 sean_voice_v2_workflow_review.json：三段 Speaker 全连接 [2,0] 且转写完全相同，设计和录音建立基础样音各一段。该文件不是提交记录，未送入 ComfyUI；借已有样音检查输入连接，不判断克隆质量。

本轮没有生成新音频、运行单元测试或改变用户定稿和业务草稿。跨情绪音色实际一致性、v2 录音建立基础样音与英文仍待真实试听验证。
