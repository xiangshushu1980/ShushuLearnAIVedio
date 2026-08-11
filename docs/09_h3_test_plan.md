# 09 H3 系统化测试计划（2026-08-03 夜跑）

> 目标：MiniMax H3 能力与速度甜点系统化测试。结果持续落盘于此 + Mem0。
> 硬件：RTX 4090 24GB / 47GB RAM / ComfyUI 0.30 / fl2va+ref2va pruned int8 + nvfp4 TE
> 纪律：每批次前查内存；跑完清理；队列串行；视频统一存 `output/video/h3_*`
> **2026-08-11 瘦身**：已完结计划/被取代旧数据删除（git 历史可查），保留全部定论与数据表。

## 已完成数据（阶段 0：基线）

### 阶段 0 速度矩阵（旧数据，已被干净环境定论取代）

> ⚠️ 2026-08-11 瘦身：阶段 0-4 数据均受模型加载/内存压力干扰（偏保守，真实约为其一半多一点），**速度以「最终速度矩阵」（干净环境 + sage）为准**。旧表已删，git 历史可查。仅保留当时结论：5s 档 1024×576≈768×448 性价比最高；10s 档分辨率非线性放大；15s 档边际成本低；体积 1.3-1.9MB/条。产物在 `output/video/h3_res/` 与 `h3_res2/`。

### Ref2VA 首测
- R1 单图参考（1024×576 5s match）：163s，与 fl2va 同速 ✅
- R2 图+视频参考：**24GB 显存打爆 → 交换地狱卡死**（15min 0 推进）→ 杀
- R2b 修复：CLIPLoader device="cpu"（TE 在 CPU 编码参考视频，采样时扩散独占显存）→ 进行中

## 待测计划（阶段 1-5，已全部完成 → 结果见「结果记录区」与各定论节）

## 结果记录区（持续追加）
（每批次完成后在此追加小节）

### 阶段 0 补充：Ref2VA 视频参考（R2b，TE cpu 方案）
- R1 单图参考 1024×576 5s match：**163s**（=fl2va 同速，图参考零惩罚）
- R2 图+视频参考（TE 默认 GPU）：**卡死**（显存 24GB 打爆交换地狱，15min 0 推进）
- R2b 图+视频参考（CLIPLoader device="cpu"）：**756s** ✅ 出片 1.44MB
  - 开销构成：CPU 编码参考视频 ~10min（Qwen3VL-32B CPU 前向）+ 采样 ~3min
  - **教训：24GB 单卡上带视频参考必须 TE 走 CPU；纯图参考无需（TE 单图编码很快）**
- 文件：output/video/h3_ref2va/{r1_img_1024x576_5s,r2b_img_vid_te_cpu}_00001_.mp4

### 阶段 1：steps 扫描（fl2va 1024×576 5s，同 seed，文件 video/h3_steps/）
| steps | 耗时 | 备注 |
|-------|------|------|
| 10 | 110s | 含模型加载（队列首个）|
| 14 | 82s | |
| 16 | 95s | |
| 20 | 111s | 基线（此前 163s 含加载）|

**结论：steps 对速度影响小**（固定开销~50s 占大头，纯采样 ~7.5s/步；10 vs 20 步差 ~35s）。质量差异待目视；14-16 步或为甜点。

### 阶段 2：提示词响应（fl2va 1024×576 5s，同 seed 20260803，文件 video/h3_prompt/）
8 变体：p1 简单 / p2 详细(基线) / p3 六段式结构化 / p4 动作指定(转身挥手) / p5 镜头指定(推近) / p6 换场景(雨夜霓虹) / p7 中文 / p8 声音强调
（结果待回填）

### 阶段 2 结果（8/8 完成，~150-157s/条 稳定）
| 变体 | 耗时 | 说明 |
|------|------|------|
| p1 简单 | 150s | "a young woman in a flower field at sunset" |
| p2 详细基线 | 151s | 场景+动作+镜头+氛围+音乐 |
| p3 六段式结构化 | 155s | [Shot 1][Camera][Sound][Music] 分节 |
| p4 动作指定 | 152s | 转身+挥手+微笑 |
| p5 镜头指定 | 153s | 缓慢推近 |
| p6 换场景 | 155s | 雨夜霓虹街道（完全换场景）|
| p7 中文 | 157s | 中文 prompt |
| p8 声音强调 | 154s | 风/鸟鸣/钢琴 声音指定 |

提示词不影响速度（全部 ~152s±3s）。内容差异待目视（同 seed 下提示词变体的响应效果是核心观察点）。

### 阶段 3 结果（ref2va 参考图响应，6/6，~143-163s/条）
| 变体 | 耗时 | 说明 |
|------|------|------|
| r_forest | 154s | 森林场景参考图 |
| r_dessert | 143s | 静物参考图 |
| r_night | 152s | 夜景参考图（2048px 大图）|
| r_alya_action | 151s | 人物图+动作指定（跳转/旋转）|
| r_multi2 | 158s | **双图参考**（人物+森林融合）|
| r_alya_max | 157s | ref_image_size=max（参考图 1280×720 不触发放大，与 match 几乎同速）|

**结论**：不同题材参考图 + 双图 + max 模式速度都 ~150s 稳定（1024×576 5s）；max 对 ≤1280 参考图无速度惩罚。

### 阶段 4：fp8 vs int8 量化对比（1024×576 5s，同 seed/prompt，文件 video/h3_quant/）
| 模型 | 显存驻留 | offload | 采样速度 | 总耗时 |
|------|---------|---------|----------|--------|
| int8_convrot（现用）| 13.9GB | 6.1GB | ~4.5-5s/it | 123s（队列第2，加载已缓存）|
| fp8_scaled | **17.1GB** | 2.9GB | ~4.5-5s/it | 196s（队列第1，冷加载）|

**结论：采样速度几乎相同**；fp8 驻留多 3.2GB 但无速度收益（本环境）；画质待目视（fp8 理论更优）。fp8 冷加载更慢（int8 有页面缓存）。GGUF 路线不可行（ComfyUI-GGUF 不支持 H3 架构，2026-08-03 时点）。

### 阶段 5：干净环境速度确认（int8，1024×576，同 seed，文件 video/h3_clean/）
| 时长 | 耗时 | 备注 |
|------|------|------|
| 5s | ~123s | 含模型加载（队列第2）|
| 10s | 295s | 含加载 |
| 15s | 503s | 模型已驻留，纯生成 |

**重要修正**：ComfyUI 重启 + 内存干净后，采样速度从 7.5-9.5s/it 提升到 **4.5-5s/it**（近 2 倍）。此前阶段 0-3 的速度数据（1344×768 5s=291s、1024×576 5s=163s 等）均偏保守，真实速度约为旧数据的一半多一点。**测试纪律：长跑测试前先重启 ComfyUI 清内存**。

## 最终甜点总结（2026-08-04 凌晨）

### 速度甜点（干净环境）
- **1024×576（16:9）为甜点分辨率**：5s≈123s、10s≈295s、15s≈503s
- 768×448 更快但内容细节损失；1344×768 10s+ 成本非线性飙升（不推荐长视频）
- steps 10-20 差异仅 ~35s，14-16 步为速度质量平衡候选
- **跑测试/批产前先重启 ComfyUI**（内存压力会让速度慢一倍）

### 能力结论
- Ref2VA 单图参考：零速度惩罚（~150s），题材任意（人物/场景/静物/夜景/双图）
- Ref2VA 视频参考：**必须 CLIPLoader device="cpu"**（否则显存打爆卡死）；代价 +600s（CPU 编码）
- max 参考模式对 ≤1280px 图无惩罚
- 提示词（简单/详细/结构化/中文/声音指定）不影响速度，内容响应待目视

### 全部产物（34 个视频）
- h3_res/（分辨率矩阵 5）+ h3_res2/（时长矩阵 5）+ h3_steps/（4）+ h3_prompt/（8）+ h3_ref/（6）+ h3_quant/（2）+ h3_clean/（2）+ h3_ref2va/（2）
- 对比拼图：output/compare/h3_res_compare.png

### 补测批 A：steps 干净环境（1024×576 5s，同 seed，文件 video/h3_steps2/）
| steps | 耗时 |
|-------|------|
| 10 | 145s（含加载）|
| 14 | **121s** |
| 16 | 135s |
| 20 | 165s |

**修正结论：干净环境下 steps 差异明显（14 vs 20 差 44s）**。此前"差异仅 35s"受内存压力掩盖。14 步为速度最优候选，画质待目视。

### 补测批 B：seed 稳定性 + fp8 多组（1024×576 5s 或注明，文件 video/h3_seed/ + h3_quant/）
| 任务 | seed | 模型 | 分辨率 | 耗时 |
|------|------|------|--------|------|
| sd1 | 20260801 | int8 | 1024×576 | 163s |
| sd2 | 20260802 | int8 | 1024×576 | 165s |
| sd3(复用 s20) | 20260803 | int8 | 1024×576 | 165s |
| fp8_sd1 | 20260801 | fp8 | 1024×576 | 210s（冷加载）|
| fp8_768 | 20260803 | fp8 | 768×448 | 140s |

**结论：seed 不影响速度（163/165/165s 稳定）**。fp8 冷加载代价 ~47s，采样本身同速（页面缓存后差异缩小）。768×448 fp8 140s。

### 补测批 C：FL2VA 首尾帧 + 768×448 全时长矩阵（干净环境 int8 20步，文件 video/h3_fl2va/ + h3_clean/）
| 任务 | 规格 | 耗时 |
|------|------|------|
| firstlast | 1024×576 5s 首帧+尾帧(双 keyframe) | 217s（比单帧 +52s，双帧编码+注入开销）|
| 768×448 5s | — | **115s** |
| 768×448 10s | — | 234s |
| 768×448 15s | — | 403s |

## 最终速度矩阵（干净环境，int8，20 步，含模型加载）
| 分辨率 | 5.2s | 10.1s | 15.1s |
|--------|------|-------|-------|
| 768×448 | **115s** | 234s | 403s |
| 1024×576 | ~165s | 295s | 503s |
| 1344×768 | ~290s | ~690s | — |

**甜点定论**：
- 速度优先：768×448（5s≈2min / 15s≈6.7min）
- 画质均衡：1024×576（5s≈2.7min / 15s≈8.4min）
- steps 用 14（121s vs 20 步 165s，省 27%）
- 768×448 × 14 步 5s ≈ **1.6 min/条**，可支撑批量迭代

### 社区加速节点调研（2026-08-04）
- **MiniMax H3 MotionCache**（starsFriday，论文方法，无核心 patch）：运动感知去噪缓存，跳过变化小的 denoiser 调用
  - 实测（同条件对照）：768×448 5s 115s→105s（skip 4/20，1.25x）；1024×576 5s 165s→~138s（skip 5/20，1.33x）
  - 加速 ~9-16%，参数可调更激进（reuse_threshold↑/warmup↓）但画质风险（复用残差可能糊，**需目视**）
- **ComfyUI-MiniMaxH3-Cache**（lihaoyun6，16⭐）：⚠️ patch ComfyUI 核心文件，未装
- 其他：ComfyUI-MiniMax-H3-Guide（提示词准备节点，13⭐）、Director（多段导演）、H3-Tools（prompt 校验/画布规划/audio reroll）、minimax-h3-prompt-skill（Claude skill 写官方格式 prompt，**与提示词智能体计划相关**）
- asset-hashing 说明：计算 blake3 内容哈希（未来资产去重/跨机解析），默认关闭，大目录开销大 → 已从 start.sh 移除

### 目测反馈整理（2026-08-04 用户评估）
**A. MotionCache**：视频画质差异小，但**音频明显变弱**（768 更明显）→ 需音频专项对比后定启用与否
**B. steps**：画面 16-20 接近；**眼睛 14-16 崩；声音 20 步明显更好** → 双档：14 步快速看效果 / 20 步成片
**C. fp8 vs int8**：fp8 头发动态更好、更清晰；但同 seed 内容不可比（量化差异致采样路径不同）→ 需多案例统计
**D. 提示词**：p3 结构化"内容更多但人物完全变了"（提示词主导>seed 锚定）；p4/p5/p6 全部生效；**p7 中文 prompt 未产出中文元素**；**p8 鸟鸣未生成**（风生效、钢琴本就有）
**E. 参考图**：r_alya_action（动作指定+保长相）✅ r_multi2（双图融合）✅；max 模式对 1280px 图无增益
**F. 长视频**：15s 稳定但动作简单（token 分配限制）
**G. firstlast**：双帧控制测试通过（工作流见上文记录）

## 后续测试建议（2026-08-04 列，已全部完成；2026-08-11 删明细）

1. MotionCache 音频专项 → 已做（见下补测：响度差 0.7 LU，主观差异归因 MC 残差复用）
2. fp8 多案例统计 → 已做（见下补测批 B：3 场景 × 2 量化）
3. 中文 prompt 专项 → 已做（zh_dialog 已生成；p7 中文未产出中文元素结论在目测反馈 D）
4. 声音细粒度边界 → 已做（C22 loud birdsong 强指令）
5. 15s 动作丰富度 → 已做（C24 15s 多动作）
6. 声音对比基线 → 已做（voice_nocache vs voice_motioncache LUFS 对比）

## 待确认的默认参数（已被生产双轨定论取代，2026-08-11 删明细）

> 最终双轨配置：快车道 fl2va fp8 + turbo（docs/19）、慢车道 ref2va std14/20（docs/19）、全链路验收（docs/21）、活跃决策（mem0 [STATE]）。

### 补测：MotionCache 音频专项（2026-08-04，文件 video/h3_audio/）
- voice_nocache vs voice_motioncache（同 prompt 含人声+钢琴+鸟鸣，同 seed）
  - 响度：-18.8 vs -19.5 LUFS（差 0.7，<1 LU 人耳难辨阈值）
  - LRA：5.4 vs 5.6（动态几乎同）
- **结论：响度差异客观很小，但用户主观感知"声音变弱"明显 → 差异可能来自音频内容/清晰度（残差复用致高频或细节丢失），需听感确认**
- zh_dialog（<d>标签中文对话测试）、bird_strong（强声音指令）已生成待听测

## review 对比目录已建（output/review/，40 视频 37MB，复制不移动）
A_motioncache/ B_steps/ C_quant/ D_prompt/ E_ref/ F_long/ G_res/（文件名语义化+前缀排序，方便对比）

### 补测批 B 完成：fp8 vs int8 多案例（3 场景 × 2 量化，同 seed 20260820，1024×576 5s）
| 场景 | int8 | fp8 | 备注 |
|------|------|-----|------|
| forest | 183s | 215s | fp8 冷加载 |
| night | 205s | 205s | 同速 |
| dessert | 206s | 208s | 同速 |

采样同速确认（队列后段无加载差异）。3 组可控画质对比已入 review/C_quant/（C4-C6 同场景相邻命名），待目测。

### 讨论定论（2026-08-04）
1. **量化默认改为 fp8_scaled**（int8 备选）：
   - 架构：fp8 e4m3 是 Hopper/Ada 原生格式；4090 (Ada) 原生支持 → 画质更好速度不输；30系 (Ampere) 无原生 fp8 → int8 更优（符合用户听闻）
   - 实测：fp8 采样 ≈ int8 同速；显存驻留更多（17.1 vs 13.9GB）
   - 社区：ComfyUI issue "INT8 ConvRot slower than FP8 on A100" 佐证 fp8 通用性
2. **MC 节省机制**：固定跳步数（skip 4-5/20）→ 绝对节省 = 跳步数×每步耗时，随分辨率/时长放大（768 5s 省10s/9%，1024 5s 省27s/16%）；**抽卡可用 MC（声音劣化不影响选片），成片不用**
3. **review 目录**：保持复制现状（分组自包含利于对比，37MB 可忽略）

### ⚠️ 重大发现：SageAttention 是关键加速（2026-08-04）
中途无意的对照实验：手动启动漏带 --use-sage-attention，所有速度慢一截：
| 1024×576 | sage 开 | sage 关 | 加速 |
|----------|--------|---------|------|
| 5s | ~165-177s | 207-217s | ~20% |
| 10s | 295-303s | 498-499s | ~40% |
| 15s | 491-503s | 941s | ~48% |

**sage 加速随时长增大而增大**（长序列 attention 占比高）；768 系列影响小（234/236、403/395 几乎一致）。确认：**必须开 --use-sage-attention**（start.sh 已含）。此前"干净环境"数据（115/165/295/503）均为 sage 下，有效。

### 时间矩阵最终确认（sage 开，int8，含加载）
| 分辨率 | 5s | 10s | 15s |
|--------|----|----|----|
| 768×448 | ~115s | 234s | 403s |
| 1024×576 | ~165s | 295-303s | 491-503s |

### 加速组合最终数据（1024×576 10s，int8）
| 组合 | 耗时 | vs 全关 |
|------|------|---------|
| 全关（无 sage 无 MC）| 498s | — |
| sage 开 | 303s | -39% |
| sage + MC | **225s** | -55% |

- fp8 + sage 10s = 372s（含冷加载，与 int8 303s 同档）→ **fp8 与 int8 速度等价确认（sage 下）**
- MC + sage 可叠加（跳步 4/20 × 每步 ~19s）；MC 音频劣化只影响抽卡档
- **最终管线建议**：fp8 + sage（成片）/ fp8 + sage + MC（快速抽卡）

### sage/MC 画面影响测试（1024×576 5s，同 seed/prompt，四状态，review/I_sg_mc/）
| 状态 | 文件 | 耗时 |
|------|------|------|
| 全关 | I1_full_off | ~210s |
| sage only | I2_sage_only | 165s |
| mc only（无 sage）| I3_mc_only | 138s |
| sage+MC | I4_sage_mc | 129s |
| 768 sage+MC | I5 | 161s |
| 768 sage only | I6 | 115s |

**待目测**：四状态画面主体/结构是否一致（细节/声音允许差异）。若主体一致 → 抽卡管线 = fp8+sage+MC+14步，预计 768×448 5s <1min/条。

### sage/MC 10s 放大测试（1024×576 10s，同 seed/prompt）
- I7 sage+MC 10s（301s，MC 跳 4/20 正常）
- I8 sage only 10s（303s）
- **待用户确认异常表现**；MC 跳步复用残差对运动场景（10s 运动多）可能产生伪影/闪烁，需目测

### 画面/声音判定（2026-08-04 用户确认）
- **三状态（全关/sage/sage+MC）20 步同 seed：画面一致** → sage/MC 对画面主体无影响，可放心用于加速
- **声音差异大**（MC 跳步复用音频残差为主因；sage 对声音影响待专项听测）
- **管线固化**：
  - 快速抽卡：fp8 + sage + MC + 14 步 @ 768×448（画面安全，声音差无所谓）→ 预计 <1.5min/条
  - 正式成片：fp8 + sage + 20 步 @ 1024×576（画面+声音双保）→ 5s≈2min / 10s≈5min / 15s≈8min
- 声音专项（后续）：sage/MC 对音频频谱影响、成片档声音基线

### 社区做法调研：提示词控制强度 / 参考图强度 / 导演台（2026-08-04）
**关键洞察：H3 无 CFG → 控制强度没有数字权重参数，全靠语言量化控制**
- 镜头运动：类型 + 幅度（small/large amplitude）+ 速度（slow/fast）写进自然语言
- 动作强度：形容词梯度（gently → strongly）
- 参考保留（ref2va retention_analysis）：`fully_preserved` → `partially_preserved` → `attribute_transfer` → `weak_reference`
- 音频保留：`fully_copy` → `partially_copy` → `reference` → `weak_reference`
- 官方 IR 输出格式（开源指南 base 222 行/ref 341 行，HF 仓库 docs/）：base=指令+三段核心字段；ref=六段式

**社区 4 流派**：
1. **导演台插件**：AIMixer/ComfyUI_MiniMaxH3_Director ★15（多段时间轴/智能分镜 PySceneDetect/多任务 t2v~rv2v/参考素材组/选择运行/原生立体声）——我们的首选导演台
2. **Prompt Skill**：babicat4242/minimax-h3-prompting ★5（Codex skill+确定性校验器：schema 顺序/时长/7000 字符硬限）、kuronzzhan/minimax-h3-prompt-skill ★2（Claude skill）
3. **案例库**：imagineVid/Awesome-minimax-h3-prompts-and-skills ★4（28 个验证案例+真实结果片段+6 类工作流）、joeVenner/awesome-minimax-h3 ★3
4. **ComfyUI 内工具**：Rinne414/ComfyUI-MiniMaxH3-Tools ★1（prompt 校验/画布规划/audio reroll）

**我们的测试方案（拟）**：
- 提示词强度：同 seed 下语言梯度（镜头幅度/速度、动作强度形容词、详细度 10→100 词→六段式、约束强调词 must/strictly）
- 参考强度：retention marker 梯度（fully→weak 同图）、描述占比（详细 vs 简略）、双图主次分配
- 导演台：装 AIMixer Director + 自建 pi prompt skill（system=官方指南）+ 校验器（借鉴 babicat 规则）

### 底图库建设（2026-08-04，78 张）
- **KREA2 写实 39 张**（8步/cfg1.0/er_sde）：人物 15 + 场景 8 + 静物 7 + 5 样张 + HD 2(1344×768) + 快速 2(768×448)
- **ANIMA 插画 39 张**（20步/cfg4.0 + turbo LoRA）：人物 15 + 奇幻场景 10 + 风格化 5 + 5 样张 + HD 2 + 快速 2
- 位置：`output/ref_lib/sample_{krea,anima}/`（45MB）；已复制到 `input/ref_lib/{realistic,illustration}/` 供 LoadImage 直接引用
- 预览拼图：`output/compare/ref_lib_preview.png`
- 用途：H3 ref2va 参考图库（单主体聚焦，16:9 匹配视频比例）+ 提示词强度/参考强度测试素材
- 批量脚本：`/tmp/gen_ref.py`（可复用，LINE=krea|anima 参数化）

### 底图库扩充 2（2026-08-04，+43 张，共 121 张）
- **KREA2 写实 +20**：清凉美女 12（bikini/pool/surfer/sundress/yoga/volleyball 等）+ 文化特色 8（hanfu/qipao/kimono/tibetan/opera/inkwash/lanterns/dunhuang）
- **ANIMA 插画 +23**：人物扩充 15（swimsuit/cowgirl/punk/knight/mermaid/samurai 等）+ 文化特色 8（hanfu/cheongsam/liondance/dragon/torii/thangka 等）
- **新 LoRA**：Anima Highres/Aesthetic Boost（CivitAI ★1821，135MB）已下载并挂载（strength 0.6 + turbo LoRA 1.0 串联）
- **LoRA 调研结论**：CivitAI 泳装 LoRA 仅 2 个小众 Krea2 的（★109/★91 质量存疑未下）；文化类无 Anima/Krea2 现成 LoRA（Illustrious/SDXL 生态的汉服旗袍 LoRA 架构不兼容）→ 清凉/文化全靠 prompt（Qwen3-VL 文本编码器理解强）
- 位置：`input/ref_lib/{realistic:59, illustration:62}`；预览：`output/compare/ref_lib_preview2.png`
- 批量脚本：`/tmp/gen_ref2.py`（KREA 8步 / ANIMA 20步+双LoRA）

### A 提示词控制强度测试（2026-08-04，fp8+sage 20步 1024×576 5s，同 seed，review/J_prompt_strength/）
| 文件 | 变体 | 耗时 | 动作量 |
|------|------|------|--------|
| J0 p2 (int8 参照) | 基线 slow pans right | 151s | 4.17 |
| J1 A1 基线 (fp8) | 同上 | 177s | 4.07 |
| J2 pan fast large | 大幅快移横摇 | 178s | **12.59 (3.1x)** |
| J3 push fast large | 剧烈推近 | 175s | **14.25 (3.5x)** |
| J4 wave gentle | 轻柔挥手 | 174s | 4.06 (≈基线) |
| J5 wave strong | 强烈挥手 | 176s | **6.96 (1.7x)** |
| J6 preserve face | 严格保留脸/服装 | 175s | 3.97 |
| J7 keep scene | 必须保持场景不变 | 176s | 5.98 |

**结论（客观）**：
1. **镜头语言控制强度最高**：幅度+速度写清楚（large amplitude at fast speed）→ 动作量 3-3.5x；J2/J3 差异说明镜头类型（Pan vs Push）也可控
2. **动作指令中等**：strong vs gentle 1.7x vs 1x——形容词梯度生效但弱于镜头
3. **约束指令（strictly/must）**：动作量层面无显著压制，**需目测画面**是否真保脸/保场景
4. 提示词不影响速度（全部 ~175s±3）

**用户目测确认（2026-08-04）**：
- J1-J5 速度/强度全部符合指令 → **镜头语言（幅度+速度）和动作形容词（gentle→strong）都是可靠控制手段**
- J6 保脸/服装**有效** → 主体锚定约束可用（I2V 参考图锚定强）
- J7 保场景**无效** → 判断为**提示词内部矛盾**（"keep scene unchanged" vs "camera pans right" 冲突，模型优先镜头）→ 约束指令不与运动指令同句混用

### B 参考图强度测试（2026-08-04，ref2va int8 20步 1024×576 5s，参考=krea_bikini_beach + krea_forest，review/K_refstrength/）
| 文件 | 变体 | 耗时 |
|------|------|------|
| B1 fully+详细 | fully preserved + 完整特征描述 | 155s |
| B2 weak+简略 | weak reference + 风格近似 | 153s |
| B3 一句话 | 只说 "the woman in <Picture 1>" | 171s |
| B4 人物主图 | bikini 详 + 森林 <Picture 2> 提场景 | 384s(含加载) |
| B5 场景主图 | 森林详 + 人物简 | 176s |
| B6 partially | 同脸换白色连衣裙 | 187s |

**待目测**：参考保真梯度（fully vs weak vs 一句话）、双图主次（B4 vs B5 谁主导）、换装保留（B6 是否同脸换衣）

### 补测批 D：快速档端到端 + fp8 矩阵 + sage 音频对照（2026-08-05 凌晨，文件 video/h3_patch/）

**背景**：快速抽卡档（fp8+sage+MC+14步 @768×448）自定论以来从未以完整组合干净实测（C21 的 315s 疑脏数据）；成片档 10s/15s 数据全为 int8；sage 对音频影响未量化。本次补齐。

| 任务 | 配置 | 耗时 | 说明 |
|------|------|------|------|
| P1 | fp8+sage+**MC默认**+14步 @768×448 5s | 195s | 冷加载；**MC 只跳 1/14（1.08x）** |
| P2 | fp8+sage+14步 @768×448 5s（无MC） | **75s** | 驻留；**快速档真实速度 ✅** |
| P3 | ref2va int8+sage+MC+14步 @768×448 5s | 90s | 换模型含加载；C21 干净复测（C21 的 315s 确认脏数据） |
| P4 | fp8+sage+20步 @1024×576 10s | 391s | 换模型含加载 |
| P5 | fp8+sage+20步 @1024×576 15s | 615s | 驻留；**内存压力（45GB used）** |
| P6 | fp8+sage+20步 @1024×576 5s 音频基线 | 255s | 内存压力；音频文件有效（sage on 基线） |
| V1 | fp8+sage+20步 @1024×576 5s | ~180s | 内存压力（重启脚本踩坑后复跑，耗时弃用） |
| V2 | fp8+sage+**MC激进**+14步 @768×448 5s | 337s | 内存压力；**跳步 4/14（1.40x）有效** |
| W1 | fp8+sage+20步 @1024×576 5s | **195s** | 干净冷加载；**权威 fp8 5s**（int8=165s，差 30s=加载） |
| W2 | fp8+sage+MC激进+14步 @768×448 5s | **106s** | 干净驻留；**MC 净收益仅 ~3-4s** |
| W3 | fp8+sage+20步 @1024×576 10s | 405s | 冷加载（int8=295s） |
| W4 | fp8+sage+20步 @1024×576 15s | 615s | 驻留；内存压力（44GB used；int8=503s） |
| P7 | **无 sage** fp8+20步 @1024×576 5s | 255s | 冷加载；sage off 音频对照 |

**结论（定论级）**：
1. **快速抽卡档 = fp8 + sage + 14 步 @768×448（去掉 MC）**：实测 75s/条（驻留），比带 MC 更快且声音更好。MC 在 14 步无实用价值——默认参数只跳 1/14（1.08x，warmup 4 占比大）；激进参数（warmup 2 / threshold 0.25 / maxskip 3）跳 4/14（1.40x）但 score 计算开销 ~0.7s/it，净收益 ~3-4s，还带音频劣化。**MC 仅保留为 20 步画质档加速选项**（1.25-1.33x 实测于 08-04）
2. **sage 对音频零影响**：W1（sage on）-10.9 LUFS vs P7（sage off）-11.1 LUFS（差 0.2 LU，人耳不可辨）；"声音变弱"100% 归因 MC 跳步复用音频残差 → 成片档（无 MC）声音安全 ✅
3. **fp8 速度矩阵（干净环境）**：5s=195s（含加载）、10s=405s（含加载）、15s=615s（驻留）vs int8 165/295/503s。5s 差 30s=加载；**10s/15s 差异受内存压力干扰**（fp8 驻留 17.1GB+TE 15.7GB 顶到 44-45GB used，WSL 47GB 极限），15s 差 112s 是否 fp8 长序列真实开销待流程优化（提内存上限）后复测
4. **内存压力规律**：fp8 模式下批量跑 2-3 条后内存即顶满（44-45GB used），长任务（10s+）速度波动大（P5/W4 均 615s vs 干净期望 ~500s）；int8（13.9GB 驻留）宽裕。**流程优化方向：WSL 内存上限 / TE 瘦身 / 批间内存回收**
5. C21（315s）确认为脏数据；ref2va 干净快速档 = 90s（含换模型加载）

**补测过程踩坑（流程优化素材）**：
- 重启脚本 pgrep 匹配到 bash 包装自身 → 误杀 shell、ComfyUI 没死 → 后续任务全在内存压力下跑（V1/V2 数据污染）+ 新实例端口冲突静默失败
- 手动启动忘 source venv（sqlalchemy ModuleNotFoundError）
- 重启过渡期提交任务 → runner 轮询误判"完成"（15s 假数据），实际排队执行
- 重启后 history 持久化（comfyui.db），"无 err 无 videos"是 outputs 解析键错（images 不是 videos）
