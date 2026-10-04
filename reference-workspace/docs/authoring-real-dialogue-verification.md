# 自然语言创作：真实对话验证与文字检查范围

Owner: Sean。2026-10-04。

## 本轮真实证据

通过本机 Reference 已配置的 Pi deepseek/deepseek-flash 完成三次真实对话，使用私有临时数据库：

| 请求 | 实际保存结果 | 已证明范围 |
|---|---|---|
| 已有林岚增加脸部＋正／背／侧，已有候车厅增加回看角度和长凳细节 | 两份接续方案，三图片步骤；V3 布局正确；都等待本实体主图 | 不重复创建实体，临时库应用前后项目上下文完全一致 |
| 林岚增加腕伤变体，白色绷带独立物品 | 两个新候选、两个概念步骤、设定关系；变体等待基础主图 | 独立变体 ID、基础来源、不变量和关系保存 |
| 检查导入的电子腕表与禁止电子设备的世界规则 | 读取全部五个实体；保存两条 conflict 和缺失／建议项 | 识别物品和携带关系的规则矛盾；场景方向／尺度和声音不足未误判为错误；没有图像核验声明 |

真实对话结构验证不是语义质量通过。人工审阅发现第一轮接续提示词把未确定的共线关系写成“禁止共线”，还给基础人物加了无依据的完好／无伤断言。变体与物品提示词也添加了具体棉布、卷装、配件排除等设计；新设计可以建议，但不能冒充来源观察事实。

收紧 entity-workflow 方法后，仅重跑接续请求，避免重复全部消耗。人物提示词改为保持参考图已有配饰，不从伤势资料空缺推出“确定无伤”；场景明确取景无人只属于本图、不是永久空间事实。但场景仍出现未经提供的墙地材质、磨损与夜间照明描述，甚至与自己列出的材质待补充矛盾；空间排列的否定措辞也仍有歧义。因此**场景提示词的事实约束尚未通过完整语义验证**，不能取消人工审阅或声称流程已可靠自动完成。

本轮生成运行数均为0，无 ComfyUI、GPU 或视觉模型请求；未验证真实图片一致性／反馈修正效果。原始证据留在本地 experiments/sean_reference_authoring_goal_20261004/real-authoring-scenarios-1791071365516.json 与 real-authoring-scenarios-1791071571977.json，不包含凭据。

## 文字报告的服务端约束

project consistency 报告的问题引用实体时，必须在本轮完整读取该实体；索引摘要、在上一轮读过、或仅打开该实体的对话不能算本轮检查证据。get_project_entity 算完整读取；get_project_context/get_scene_context 返回的 currentEntity 若是完整记录，也可算当前实体已读。其他索引实体不算。项目字段自身的缺失可以用空 entityIds，不强行指向未读实体。

沿用 session 返回中的 projectProposals，coverage 新增：

```json
{
  "reviewedEntityIds": ["<本轮完整读取 ID>"],
  "projectEntityCount": 2,
  "unreviewedEntityIds": ["<仅索引 ID>"],
  "entityCoverage": "partial",
  "selectedImageAssetIds": [],
  "viewedImageAssetIds": []
}
```

全部实体完整读取时 entityCoverage=complete，但只表示文字读取范围，不代表逻辑结论正确、人工审核通过或图文一致。网页展示实际读取数量和未检查范围；旧报告缺少新字段时按原计数显示，不重写旧报告。引用未读实体返回400，项目／实体依据变化仍返回409。报告不直接修改资料。

## 复现与界限

- `npm test`：67 tests 通过，新4项覆盖未读实体、跨轮读取、选择实体不能充当读取、partial/complete 的精确范围以及全项目字段缺失。
- `npm run build`：通过。
- `REFERENCE_PROJECT_REVIEW_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`：临时库和模拟 Agent；PC 展示完整文字1/2，明确不能代表全部检查，控制台0错误／警告，无横向溢出。证据 project-review-partial-pc.png / project-review-partial-session.json。
- `node scripts/verify-authoring-scenarios.mjs`：实际调用已配置模型，消耗额度；执行接续、变体、文字检查三场景。每轮上限5分钟，终止与结束清理私有临时库／应用凭据副本，不改本机登录。
- `REFERENCE_VERIFY_CONTINUATION_ONLY=1 node scripts/verify-authoring-scenarios.mjs`：只跑第一场景，用于限定复测费用。

真实脚本只检查结构、引用、临时库应用和基本冲突分类；即使输出 verified，仍需逐句审阅 prompts/invariants/unknowns 的语义矛盾。当前完整目标保持 active；下一步需要让来源核对和修订形成更可靠的闭环，并在得到生成授权后验证真实图片。

## 具体关系引用：真实 Pi 验证（2026-10-04）

Owner: Sean。`REFERENCE_VERIFY_RELATIONS_ONLY=1 node scripts/verify-authoring-scenarios.mjs` 限定运行关系检查。新增临时电子腕表、角色携带的设定关系及角色值守场景的项目剧情关系，均不是生产资料。

真实 deepseek/deepseek-flash 已完整读取三个实体，在报告中以 relationIds 引用实际关系，并由服务端保存两种 scope 的 relationSources。报告正确识别电子设备与世界规则的冲突，将无固定空间资料列为 missing，没有声称看图；提出机械替代或规则例外的建议，均未自动采用。项目上下文前后相同、生成运行数 0。

原始本地证据：experiments/sean_reference_authoring_goal_20261004/real-authoring-scenarios-1791109090087.json。该测试请求明确给出关系 ID 与禁止电子设备的矛盾线索，不证明模型能在大型项目中独立找出全部问题。

此前场景自由提示词的补写问题已有后续来源编译，见 [场景提示词编译](scene-prompt-compilation-v1.md)；图像模型实际结果仍未验证。

## 同一对话：报告 → 规则提案 → 人工接受 → 重检

`REFERENCE_VERIFY_RELATION_REPAIR=1 node scripts/verify-authoring-scenarios.mjs` 在同一项目、同一 session 连续运行三轮真实 Pi 对话。测试用户明确决定把世界规则修改为「普通现实城市，无魔法；允许现实存在的机械、手工和电子设备；伤势不改变人物身份与已有服装。」这是测试资料的主动设定变更，不是 Agent 自行放宽规则。

真实结果：

1. 完整读取三个实体，保存电子腕表与原规则冲突的报告，引用设定及剧情关系。
2. 只保存 worldRules 项目修改提案，内容与测试用户要求逐字一致；未自动应用。测试脚本调用与网页相同的 applyProjectProposal 模拟人工接受，未操作真实用户项目。
3. 接受后旧报告因上下文变化标为 stale；同一对话再完整读取三个实体，新报告不再列电子设备冲突。前后实体及项目剧情关系完全相同；其他不足继续标为 missing 或 suggestion。

本地证据：experiments/sean_reference_authoring_goal_20261004/real-authoring-scenarios-1791109177957.json。全部三轮 succeeded、同一 session、0 生成运行。脚本现在按 runId 切分保存的报告，避免把上一轮报告误当作本轮结果。生产应用与凭据未修改；临时数据库及凭据副本已清理。

范围限制：只有一个三实体、两关系、明确提示冲突线索的受控案例。报告中的建议仍需人工判断；读取证据不等于全部语义正确。此次不含真实图片观察、再生成、多个实验变体的视觉比较。
