# H3 文档系统审计（2026-10-21）

Owner: Sean

本文是修订前审计快照；后续设计、试点、采用修订及验证见 [实施记录](sean_document_health_implementation_20261021.md)。

## 结论与范围

H3 生成相关文档存在明显的系统性漂移：历史实验、现行参数和可执行操作建议混在一起，导航仍将旧档案提升为配置依据。风险已超出两处 CPU 句子的局部漏改，足以再次误导生成或共享服务操作。此次证据不足以断言整个项目文档均不可用。

本轮检查 docs/INDEX、comfyui-ops 索引及 H3/Ref2VA/环境/排错分册，定向搜索 docs 与项目技能中的 CPU、重启、量化和路线指令，核对模型清单、当前生成手册、节点更新记录、相关 ledger 及两份本地工作流。未进行 ComfyUI 服务操作、GPU 查询或视频生成；未逐篇验证所有文档和所有历史实验。

Task Center 只读查询成功；本轮未创建、接管或修改远程任务。发现既有多处未提交改动，以下均按审计时工作树判断。未把那些改动计为本轮修复。

## 高优先级发现

### 1. CPU 旧规则还有第三处残留，而且可由当前导航到达

- `docs/09_h3_test_plan.md:99` 和 `.pi/skills/comfyui-ops/references/params.md:168` 已有未提交纠正，改为默认设备。
- `.pi/skills/comfyui-ops/references/nodes.md:107` 仍写“视频参考必须 CLIPLoader device=cpu（否则显存爆）”。
- `.pi/skills/comfyui-ops/references/video/h3.md:13` 明确引导读旧 nodes.md。
- `.pi/skills/comfyui-ops/references/video/ref2va.md:12` 继续引导到 nodes.md 与 params.md。
- 本地 `workflows/minimax_h3_ref2va_img_vid_api.json` 与 `workflows/sean_h3_preview_pdd6_lightvae_api.json` 的 CLIPLoader.inputs.device 均为 `default`。这里只证明模板当前设置，不证明所有视频参考条件下均不会 OOM。

影响：只修用户指出的两句仍无法切断错误路径。应将 nodes 中该句标为已撤销的早期观察，并指向现行生成手册；旧观察不得触发自动改设备。

### 2. 历史测试文档仍被宣布为当前参数依据

- `references/video/h3.md:3` 将 docs/09、docs/34 和“旧版参数档案”并列为模型、版本、参数依据。
- `references/params.md:3` 仍宣称“本册收集所有参数结论”。
- `docs/INDEX.md:15` 在“H3 生成、提示词、参数”行并列挂出“测试数据”，但未明确其只能提供历史证据。
- docs/09 首页仍有 ComfyUI 0.30 环境、长期 output 落点和“保留全部定论”等文字，缺少文档整体的历史边界。

影响：新手册和旧档案拥有相似的指令权重。根因是事实权威关系失效，而不只是索引缺链接。

建议：普通 Ref2VA 操作参数归 docs/34；模型及禁止恢复项归 docs/02；提示词归对应模式 skill 与 docs/17；旧档案只提供带条件的证据，不与现行手册共同决定配置。

### 3. “跑批必须重启”仍以硬规则存在

- `docs/09_h3_test_plan.md:87,95` 从旧环境速度观察推出“长跑/批产前先重启”。
- `references/params.md:161` 写成“铁律：跑批前重启 ComfyUI”，并继续使用 start.sh 语境。
- `docs/breeze-tts-standard.md:19` 也把连续任务结束后的停止/重启作为释放显存步骤。

这些建议未带共享实例、队列及活动任务的判断边界，与当前 AGENTS 的共享服务纪律冲突。历史上重启后变快是观察，不能据此制定所有批次的重启前置条件。

建议：保留旧速度观察；撤销无条件重启指令；当前生命周期操作统一引用服务管理规则。Breeze 的流程也应补共享服务边界。

### 4. 旧参数册会把已删除模型重新带回选型

- `references/params.md:159` 将 fp8_scaled 写成 4090 画质更好、同速的推荐量化。
- `docs/02_models.md:9-12` 明确相关 FL2VA FP8 scaled 已删除，不得自动恢复；两个旧脚本需先改默认值。
- `docs/34_ref2va_generation_guide.md:59` 指定普通 Ref2VA int8 ConvRot。

旧数据可保留，但其 FL2VA/旧版本范围必须显式标注，不能被当作当前 Ref2VA 量化选择。此次未重新验证量化画质或性能。

## 中优先级发现

- `references/video/ref2va.md:14` 仍写“当前 T-comfy-ops-40 只研究可行性”，把某任务阶段投影到通用能力手册。当前项目已有 Reference 创建、编辑与架构文档；能力边界应指向现行主题手册，任务状态应由 Task Center 提供。
- `references/core/environment.md:8` 将 comfy-stack wrapper 作为主启动入口。当前 AGENTS 指定 comfyui.service，wrapper 只是兼容入口。wrapper 本身不等于第二实例，但主次关系需要对齐。
- `docs/34_ref2va_generation_guide.md:121` 仍以“当前”介绍 output 中的长期测试产物，与当前 experiments 归档纪律不一致。未核对那些历史文件的实际迁移状态，不能据此声称产物已丢失。
- skill 主入口和 docs/34 都维护了预览车道参数、耗时与选型长摘要；两处目前大体一致，但有重复维护风险。应让入口保留用途、限制和权威正文链接。

## 检查工具为何没有拦住

本轮运行 `bash scripts/docs_check.sh` 返回通过；其中检查了 663 个本地 Markdown 链接，并跳过 2 个仓库外绝对路径。

现有检查覆盖收录、路径存在性、编号、skill 格式和 Ledger ID；没有检查历史内容是否被当成现行指令，也没有检查设备、重启或模型选择与当前基线的语义冲突。链接存在不代表内容正确。

`scripts/docs_reference_check.py` 的链接解析不检查同页标题锚点；代码块被跳过，行内代码形式的路径也不等同于 Markdown 链接。这些属于覆盖边界，不能将“检查通过”描述为文档内容已验证。

## 建议实施顺序

1. 撤销 nodes 的残留 CPU 硬规则及旧文档中的无条件重启指令，保留原始观察和适用环境。
2. 修正 H3 分册的“以旧档案为准”措辞；docs/09 与旧 params/nodes 显式标历史范围和现行替代入口。
3. 将旧参数册中的量化、步数、时长、FaceRefine 等配置逐主题核对后降为历史参考，避免未经验证整册迁入新手册。
4. 对齐环境主入口、任务状态投影与 output 归档表述；只在核对真实迁移状态后改产物路径。
5. 为已明确撤销的指令增加定向回归检查；语义审计仍需核对证据、适用条件和采用决定，不能靠关键词或日期自动判定全部旧文档失效。

本轮仅新增本审计记录，未修改既有手册、工作流、服务或用户级文件。未提交或推送，避免混入工作区其他任务的改动。
