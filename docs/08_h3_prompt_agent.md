# 08 H3 提示词增强方案调研（2026-08-03）

> 用途：MiniMax H3 复杂多模态指令的"上下文预处理"方案决策与落地文档。
> 背景：官方强烈建议生成前把输入过 H3-Context-IR 系统；IR 未开源但**输出格式规范已开源**。

## 一、官方 H3-Context-IR 是什么

- 托管预处理/编排系统：解析指令、跨模态关联（图/视频/音频↔生成目标）、时序理解、逻辑推理
- 把自由多模态输入序列化为 H3-Base 能理解的**结构化表示（六段式 rewrite）**
- 会补全缺失/欠指定的语义细节（官方特性）
- 未开源（多阶段 + 多个托管模型），提供 API：`POST /v2/h3_context_ir`（异步任务，轮询 `GET /v2/query/video_generation/{task_id}`，结果在 `.task.content.prompt`）
- 素材需上传海螺 CDN（隐私数据出境）
- 文档：EN `platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir`，CN `platform.minimaxi.com/docs/api-reference/video-generation-v2-h3-context-ir`

## 二、官方开源的提示词写作指南（自建方案的底气）

仓库 `MiniMaxAI/MiniMax-H3` 的 `docs/`：
- `VIDEO_PROMPT_WRITING_GUIDE_base_en.md` — T2VA/I2VA/FL2VA/L2VA 基础模式
- `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` — Ref2VA 全参考模式（341 行）

**六段式 rewrite 输出格式**（ref 版，全部用英文写，`<d>` 内对话/歌词/画面文字保留原语言）：
1. `subject_definitions` — 参考内容抽象定义 + 标签：`<Subject N>`（可复用内容）/ `<Picture N>`（图=目标帧/分镜锚点）/ `<Video N>`（视频=编辑源/延续/节奏结构）/ `<Audio N>`（音频=复制/风格/音色）
2. `summary` — 任务类型、目标视频、主要参考关系
3. `retention_analysis` — 参考内容保留/转移/复用位置与方式
4. `detailed_description` — 逐镜头：构图/主体外观位置/环境光照/动作状态变化/镜头运动/当前声音/参考生效点（越详细越好，避免剧情摘要式）
5. `overall_soundscape` — 环境音与实体声汇总
6. `non_diegetic_music` — 背景音乐（仅观众可闻）

**标签规则要点**：
- 视频与音频独立编号，不隐含配对；同一素材可同时是 `<Video 1>` 和 `<Audio 2>`
- 图只用于定义角色/场景时并入 `<Subject N>` 引用，不单列 `<Picture N>`
- 音频对应目标说话人时用全局说话人 ID `(Sx)`
- 标签在全部六段中保持一致含义

## 三、方案对比与推荐

| | A: 官方 IR API | B: 自建提示词智能体 |
|---|---|---|
| 质量上限 | 官方多阶段最强 | 取决于本地视觉 LLM（LM Studio Qwen3.6-35B-A3B-MTP）|
| 成本/隐私 | 按量付费+素材上云 | 零成本全本地 |
| 集成 | 差（上传→API→prompt 回传）| 无缝（pi + comfyui_mcp）|
| 迭代 | 黑盒 | 六段式=明确评测标准 |

**结论：先自建（B），官方 IR 当对照基准**。理由：格式规范开源=非黑盒；本地素材为主；积木齐全（LM Studio 视觉模型/pi/mem0/ComfyUI MCP）；六段式指南即评测标准。

## 四、落地计划

```
输入（prompt + 参考图/视频/音频素材）
  → [提示词增强 Agent]（pi skill: prompt-rewriter，system=官方六段式指南）
  → [规则校验]（标签一致性/六段齐全/时长帧数/语言规范）
  → ComfyUI Ref2VA/I2V 工作流（comfyui_mcp 提交）
  → 成片回评 → 经验存 mem0
```

步骤：
1. 精读 ref/base 指南 → 写成 pi skill（单一写者，放 `.pi/skills/`）
2. LM Studio 视觉模型最小可用版（单参考图 → 六段式）
3. A/B 评测：直接 prompt vs 增强 prompt 各 2-3 条（同 seed 同素材）
4. 复杂案例调官方 IR 对照校准（需要时再申请 API）

## 五、IR API 接入落地（2026-08-08 更新）

> 用户拍板 2026-08-08：**接入官方 H3-Context-IR API 为主路径**（在线，本地视觉 LLM 方案关闭——GPU 切换成本 3-6min/次，对 2min/条成片不可接受）；同时装官方 9 个 skill（`.pi/skills/`，见下）。

### 已装官方资产
- **9 个官方 skill** → `.pi/skills/`（h3-prompt-writing 核心 + 8 风格生成 skill，含 SKILL.cn.md）；源 = `vendor/minimax-h3`（sparse 克隆仅 skills/，跟踪 commit 8d8824e，更新时 `cd vendor/minimax-h3 && git pull` 后重新复制）
- 官方安装命令（备用）：`npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`

### IR API 细则（CN 平台实测文档 2026-08-08）
- **创建**：`POST https://api.minimaxi.com/v2/h3_context_ir`，Bearer key；body = model + content[] + duration(4-15) + ratio
- **content 元素**：text（必填非空）/ image_url / video_url / audio_url，role 标用途：`first_frame`/`last_frame`/`reference_image`/`reference_video`/`reference_audio`；首尾帧与 reference_* 互斥
- **素材引用**：先传 `POST /v1/files/upload`（multipart，purpose=`video_generation_input`）→ 返回 file_id → content 里用 `mm_file://{file_id}`（7 天有效）；请求体 ≤64MB，大文件用 URL
- **限制**：图 ≤30MB/≤9 张（首尾帧各 1）；视频 ≤50MB/≤3 个/段 2-15s 总 ≤15s；音频 ≤15MB/≤3 个/段 2-15s
- **查询**：`GET /v2/query/video_generation/{task_id}` → 成功 `task.content.prompt`（六段式/三核心段）；`task_type=h3_context_ir`
- **计费**：按 tokens（示例 4s 任务 ~9090 tokens）；错误 402=余额不足
- **调用脚本**：`scripts/h3_ir_rewrite.py`（上传→提交→轮询→落盘；key 读 `~/.config/minimax_key`，不进 git）

### 待办
- 账户充值后跑冒烟测试 → A/B 实测（自写 vs IR，同 seed 同素材 2-3 条）
- 规则校验层优先级重估（IR 输出天然合规；校验主要留给本地 skill 路径）

## 六、相关资料
- 模型卡：`hf-mirror.com/MiniMaxAI/MiniMax-H3`（README 含 IR/2K workflow 章节）
- IR 调用示例：`scripts/readme/full-2k-{t2va,i2va,ref2va}-h3-context-ir.sh`
- 本地已存：`/tmp/h3_card.md`（模型卡全文）、`/tmp/guide_ref.md`（ref 版指南全文）
- ComfyUI 侧参考：`workflows/minimax_h3_r2v.json`（官方内联模板，标签提示词用法见节点注释）
