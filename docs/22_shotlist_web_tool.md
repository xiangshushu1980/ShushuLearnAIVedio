# 22. 拍摄本看板 Web 工具设计（web-shotlist-tool）

> 状态：设计稿 v0.1（2026-08-12 讨论确认，待实现）
> 任务线：.pi/agents/web-shotlist-tool/progress.md
> 定位：通用影片引擎的"剧本→拍摄本→提示词→渲染输入"可视化看板；V1 纯看板（只读为主）

## 一、架构决策（用户确认 2026-08-12）

### 1. 分层：审阅层与执行层分离
```
网页工具（审阅/决策层，全 TS 单栈）          ComfyUI（执行层，Python 服务，不动）
剧本 → 拍摄本 → 提示词                         组装 workflow（h3_gap_runner 逻辑重写）
        ↓ 审阅/选候选                            → 提交 /prompt API
        ↓ 输出"渲染意图"（输入源清单）            → 进度/产物回传（WebSocket）
```
- 不把工具做进 ComfyUI 节点：ComfyUI 是执行引擎不是审阅工作台（时间轴/卡片/标色/联动表达弱；分支是文档层概念不是执行流概念；LLM 环节要造大量自定义节点）
- 执行层继续深度复用 ComfyUI（h3_gap_runner 就是从拍摄本组装 workflow 提交，此路已通）

### 2. 全 TypeScript 单栈（用户确认：脚本重写不是问题）
| 层 | 选型 | 理由 |
|---|---|---|
| 运行时 | Node 22 LTS | 生态兼容最稳（不用 Deno/Bun） |
| 后端 | Fastify | 类型友好、快；API 面不大不引 NestJS |
| 前端 | React 19 + Vite 7 + TypeScript | tldraw（V2 画布）只支持 React；DirectorsConsole 同栈可参考 |
| 包管理 | pnpm | 快、省空间 |
| 状态 | Zustand + TanStack Query | DirectorsConsole 同款 |
| UI | Tailwind CSS + shadcn/ui | 现代克制可定制（用户嫌 seesee75 难看；Gemini 出稿易配合） |
| 校验 | zod（前后端共享 schema） | 替代 prompt_validator.py |
| 存储 | 项目=文件目录+JSON；实体图谱大了再引 better-sqlite3 | 对应现有 experiments/ 结构 |

### 3. Python-only 依赖边界
| 脚本 | 处置 |
|---|---|
| h3_shotlist_gen.py / h3_prompt_stage2.py / prompt_validator.py / h3_gap_runner.py / h3_concat.py | **重写进 TS**（模板文本直接搬，校验转 zod） |
| h3_demucs.py / h3_audio_sep.py（demucs/AudioSep，PyTorch 独立工具） | **保留 Python 独立 CLI**，TS child_process 调用（各 ~20 行封装）；与 ComfyUI 无关，借 venv 环境属历史习惯，后续可独立 venv |
| ComfyUI 本体 | 外部服务不动，HTTP 对接 |

## 二、产品形态（V1 看板）

### 页面布局：三段式 + 侧栏
```
┌─────────────┬────────────────────────────────┬──────────┐
│ ① 剧本区     │ ② 拍摄本区（竖排卡片流）         │ ③ 侧栏    │
│ 文本编辑框    │   顶部：时间轴概览横条（切点/景别）│ 渲染输入源 │
│ (粘贴/导入)   │   镜头 1 卡片：动作/台词/声音三层  │ 参考图墙  │
│ [生成拍摄本]  │   镜头 2 卡片：...               │ 音频卡    │
│             │   [生成提示词]                   │ 高级参数   │
├─────────────┴────────────────────────────────┴──────────┤
│ ④ 输出区：H3 提示词（语法高亮/标色，只读）+ 复制/保存       │
└─────────────────────────────────────────────────────────┘
```
- 拍摄本呈现 = **竖排卡片流**（信息密度高、好做清楚）+ 顶部**时间轴概览横条**（只显示切点/景别/运动，不承担主阅读）——用户确认
- V1 纯看板：只能改剧本重生成，无拖拽/无编辑（候选多选一后续加，**每镜候选**，整本候选=重拍无意义）
- 看板粒度：V1 单拍摄本；数据模型预留"成片=段列表"（agreement 三段教训）

### 实体系统（用户需求核心，V1 基础版）
```
实体（Entity）= 世界观设定单元：角色/物件/场景/技能/组织/地点……
属性：id | 名字 | 类型 | 类型色 | 重要程度 | 详细设定(md) | 来源（V2：剧本/世界观手册/多份材料）
存储：experiments/entities/*.md + 注册表（entities/index.json）
```
- **颜色体系（用户确认方案）**：类型定色（角色=蓝系/场景=绿系/物件=橙系/技能=紫系）+ 重要程度加边框（核心实线/次要虚线）
- **UI 交互链**：
  ```
  拍摄本内引用 → chip（名字+类型色+重要度）
    → tooltip 1 级（摘要+来源数）
    → 点击 → 详情面板（完整设定+关系列表）
    → 关系条目 → 二级 tooltip（关系类型）
    → 点击 → 跳另一实体详情 → 返回栈（面包屑一键回跳）
  ```
- V2 扩展：来源追踪、关系图谱（tooltip 标关系+二级跳转）、多份材料溯源
- 承接"类型偏向设定"：类型预设 = 实体类型体系的一部分（后续）

### 剧本获取（工具 A0，V2 候选）
实体库+世界观手册 → DeepSeek（模板 prompt）→ 剧本 YAML（参数头+正文）→ 人工微调 → 工具 A。无现成开源工具值得引，模板 prompt 即方案。

## 三、标色方案（H3 提示词高亮）

| 元素 | 染色/符号 |
|---|---|
| `<Subject N>` / `<Picture N>` / `<Video N>` / `<Audio N>` | 高亮 chip + 彩色徽章（S1 蓝/S2 粉…与实体色对应） |
| `[Shot N] At MM:SS` 时间戳 | 深色底 + ⏱ |
| `<d>[Chinese] 台词</d>` | 引号样式 + 说话者实体色 |
| 镜头运动语法（push_in/static…） | 斜体 + 🎥 |
| 声音三层（ambient/fx/bgm） | 环境=绿 / fx=橙 / bgm=紫 + 🔊 |
| non_diegetic_music 决策 | N/A=灰（特意行为徽章）/ 配乐描述=紫 |

## 四、渲染输入源（侧栏，用户确认方案 A）

- 参考图卡片墙（缩略图→点击放大；标注用途："Subject 1 Alya 角色卡 canon"）
- 音频卡片（波形+播放+角色名）
- 参数表：**折叠为"高级参数"**（seed/steps/分辨率/时长/模式 ref2va/i2va/unet）
- **与拍摄本联动**：hover 拍摄本 `<Subject N>` → 对应卡片高亮；点击 chip → 跳到输入源本体（滚动+高亮 1s）；输入源点击 → 跳回引用处
- V1 只显示清单（解析自拍摄本 audio_refs / 提示词 <Picture N> 引用），不做提交——**提交 ComfyUI + 进度（WebSocket）为 V2**，JobGroup/ChildJob 状态机参考 DirectorsConsole Orchestrator

## 五、数据模型与项目格式

### 项目 = 一个目录（对应现有 experiments/shotlist/ 结构）
```
<项目名>/
├── script.yaml          # 剧本（参数头+正文）
├── shotlist.yaml        # 拍摄本（工具 A 输出，schema 见下）
├── prompt_ref2va.txt    # 提示词（工具 B 输出）
├── inputs.json          # 渲染输入源清单（解析产物）
└── meta.json            # 项目元信息（created/entities 引用/成片归属 V2）
```
- **导入**：V1 支持导入已有剧本/拍摄本/提示词文件（粘贴或文件选择器），把 experiments/shotlist/ 现有内容包成项目（用户确认）
- 剧本 schema（现有）：参数头（title/style/ratio/scene/duration/sound/role_cards/chain/audio_refs/no_bgm）+ 正文；**预留 branch 扩展点**（分支剧情 V2：决策点标记→路径展开，拍摄本保持线性）

### 拍摄本 schema（工具 A 现有输出，web 只读展示）
```yaml
title/style/ratio/scene/duration_total/chain/role_cards/audio_refs
shots:
  - id: 1
    duration_s: 3.0
    framing: 全景        # 特写|近景|中景|中全景|全景|大远景
    camera: {type: push_in, amplitude: small, speed: slow}
    subject: yuki_v1, alya_v1
    action: 本镜主导动作（中文，一镜一动作）
    dialogue: [{speaker: alya_v1, text: "台词 verbatim"}]
    sound: {ambient: …, fx: …, bgm: N/A（导演特意决策）}
    continuity: 锚定与跨镜延续
```

## 六、API 设计（Fastify，前缀 /api）

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | /api/projects | 新建项目（导入剧本/文件包） |
| GET/PUT | /api/projects/:id | 读/存项目（script/shotlist/prompt） |
| POST | /api/projects/:id/generate-shotlist | 调工具 A 逻辑（DeepSeek，参数：model/effort/fewshot/review） |
| POST | /api/projects/:id/generate-prompt | 调工具 B 逻辑（mode: i2va/ref2va） |
| GET | /api/projects/:id/inputs | 解析渲染输入源清单 |
| GET | /api/entities | 实体注册表（含类型色/重要度） |
| GET | /api/entities/:id | 实体详情（md 渲染） |
| POST | /api/render/preview | V2：组装 workflow 预览 |
| POST | /api/render/submit | V2：提交 ComfyUI + WebSocket 进度 |
| GET | /api/projects/:id/prompt | 提示词文件 |

LLM 调用统一走服务内 client（DeepSeek API，OpenAI 兼容），key 从环境/配置读（不进 git）。

## 七、已知约束/经验（进工具后为默认规则）

- **BGM 三件套是特意行为**：non_diegetic_music 跟随拍摄本 bgm 字段；bgm=N/A 时 N/A+soundscape no music+中性词（2026-08-12 修订，不再是硬性默认）
- **镜头主体绑定写死**：特写必须写"主体+配角在画面边缘"（seg1 教训，"facing toward X" 有歧义）
- **环境音不随台词变轻**：不写 "grow lighter" 类描述（seg2 教训；持续考察）
- **站位 = prompt 主导**：Ref2VA 同参考图+翻转站位描述→产物跟随 prompt（T-01 已验收）；跨段站位全局约定写进剧本
- **BGM 触发组合**：多镜头×温情/氛围词或舞台语义；单镜头免疫（prompt-audio 线实测）
- 链式连续性（Motion Context）是 V2+ 候选，不进 V1

## 八、扩展路线（V2+，按优先级）

1. **候选多选一**（每镜候选；工具 A 带"表现方向参数"生成 2-3 版：日系清新/冷峻纪实/舞台戏剧 → 对应类型偏向预设）
2. **渲染提交**：ComfyUI 提交+WebSocket 进度（JobGroup/ChildJob 状态机）；后期线上服务只换 render 接口
3. **多段成片**：段列表管理（成片=段），时间轴跨段概览
4. **分支剧情**：剧本 branch 扩展点→路径展开（每路径一份线性拍摄本）；交互式（观众选择）为远期
5. **tldraw 画布模式**：实体/镜头/提示词变节点自由组合（探索视图；主视图仍三段式）
6. **工具 A0 剧本生成**：实体库+世界观→剧本模板
7. 实体关系图谱/来源追踪；音频工具集成（去 BGM 按钮）

## 九、参考项目（已调研 2026-08-12）

| 项目 | 借什么 |
|---|---|
| seesee75/ComfyUI-MiniMaxH3-Director（⭐179） | 时间线范式+编译 prompt 实时预览（shot 数/帧数/引用统计/警告）——UI 重设计 |
| j955229/Motion-Director（⭐23） | Prompt chip 可视化、Common+Local refs 分层 |
| NickPittas/DirectorsConsole（⭐318） | JobGroup/ChildJob 状态机、多后端抽象、WebSocket 进度 |
| huangserva/h3-film-studio | story→framework→storyboard 三层协议、用途驱动参考协议、质量两阶段审查（结构参考） |
| 不采用 | 无限画布（V1）；CPE 真实摄影规则引擎；ComfyUI 内嵌实现 |

## 十、开发计划（建议顺序）

1. 脚手架：pnpm + Vite + React + Fastify + Tailwind/shadcn；TS 共享类型包（entities/shotlist/prompt schema + zod）
2. 后端：项目 CRUD + 工具 A/B 重写（prompt 模板搬运）+ LLM client + 校验
3. 前端：三段式骨架 + 拍摄本卡片流 + 标色组件（chip/tooltip 1 级）
4. 输入源解析 + 侧栏联动（hover/跳转/返回栈）
5. 实体注册表 + 详情面板（V1 基础版）
6. 收尾：导入导出、项目 meta、样式打磨
