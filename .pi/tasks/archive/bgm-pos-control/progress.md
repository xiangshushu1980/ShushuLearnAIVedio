# 任务进度：bgm-pos-control（BGM 正向控制实测，T-20260812-02）

> 项目级私有进度（只有本任务线读写）。
> 关联：prompt-audio 线已定论负向抑制无效（N/A/none/否定句），本线测正向方向——显式音乐事件描述能否触发/控制 BGM。
> 判定权威 = 用户试听（频谱谐波误报多，判音乐必须试听）。

## 任务
- 目标：实测 H3 显式音乐指令的正向控制能力：① 无音乐区（单镜头中性）能否正向触发；② diegetic vs non_diegetic 写法差异；③ 时间 cue 是否可控（TODO 预期不可控待实测）；④ 多镜头中性区 + 显式配乐能否触发
- 当前状态：✅ 完成（2026-08-12 收尾）
- 我负责的文件区：.pi/tasks/bgm-pos-control/、/tmp/bgmpos_*.txt|json、产物 video/h3_bgm_pos/
- TODO 编号：T-20260812-02（无认领人，用户指示跟进）

## 实验设计（2026-08-12）
- 基准（已定论无音乐）：V6 = 337字单镜头海边中性（/tmp/h3_sfx_prompt.txt）；C2 = 写实多镜头中性（/tmp/c_real.txt）
- 全部同规格：i2v std20 8s(192帧) 768×448 seed 20260810，与 V/C 批可比
- 测试矩阵：

| # | 名称 | 首帧 | 变量 | 测什么 |
|---|---|---|---|---|
| P1 | pos_ndm_single | alya169_roshidere | 337字版 + non_diegetic_music 显式钢琴（慢/疏/轻，官方写法） | 单镜头无音乐区：正向触发能力 |
| P2 | pos_diegetic | alya169_roshidere | 337字版 + soundscape 加远处海滩酒吧钢琴（diegetic 写法） | diegetic vs non-diegetic |
| P3 | pos_ndm_timecue | alya169_roshidere | P1 + "fades in at 4s, swells at 6s" | 时间 cue 可控性 |
| P4 | pos_ndm_multishot | wow_real_768.png | c_real.txt 多镜头中性 + non_diegetic 显式钢琴 | 多镜头不触发区：正向触发 |

- 官方写法参考：docs/17 第 51 行（non_diegetic_music 写配器/速度/节奏/力度，不写情绪词）——P1/P3/P4 遵守，P2 用 diegetic 对照

## 进度日志（append-only，每条带日期）
### 2026-08-12
- 上下文收集：prompt-audio 定论（负向四写法全无效仅 8 步档、触发条件=多镜头×温情/舞台、单镜头免疫、触发态≈纯音乐）+ docs/17 官方 non_diegetic 写法
- 基准确认：V6（337字单镜头）/ C2（写实多镜头中性）均无音乐，首帧与 cases 结构已核实（h3_verify2_submit.py 可复用）
- 4 条测试 prompt 落盘：/tmp/bgmpos_p1~p4.txt + /tmp/bgmpos_cases.json
- 等待队列：ComfyUI 有另一 agent 任务在跑（h3_dialogue 批），跑完即声明 [STATE] 占用并执行

### 2026-08-12（结果 + 收尾）
- **跑批完成**：4 条全成功（各 160s，std20 8s 768×448 seed 20260810）；踩坑：169/ 已按场景归档（roshidere 图在 start/169/beach/），P1-P3 首次提交失败后修正路径重跑
- **用户试听定论（判定权威）**：
  - P1 单镜头+显式配乐（官方写法）→ **4s 起钢琴**：正向触发 ✓（单镜头无音乐区可被显式配乐描述触发）
  - P2 diegetic 写法（远处海滩酒吧钢琴）→ **有场景内感，与 P1 听感有区别**：diegetic 写法有效且与配乐层可区分
  - P3 +时间 cue（4s 入/6s 强）→ **2.5s 开始、无变强**：开始时间近似响应、动态变化不可控 → 时间 cue 半可控
  - P4 多镜头中性+显式配乐 → **有音乐**：多镜头不触发区正向触发 ✓（对照 C2 无音乐）
- **核心结论：负向抑制无效但正向控制有效**——要音乐→显式写配器描述；不要音乐→维持单镜头/多镜头中性客观描述
- 落盘：docs/17 音乐策略节新增“正向控制有效（2026-08-12 实测）”；mem0 retain 经验；[STATE] 更新 ✅
- 响度参考：P1 -22.4 / P2 -27.5 / P3 -24.5 / P4 -19.2 dB vs V6 基准 -32.2 dB（仅参考，判定以试听为准）

## 下一步
- 无（本线收口）

## 关键链接
- 关联文档：docs/17_h3_prompt_writing_rules.md（§音乐策略/§soundscape）
- 基准 prompt：/tmp/h3_sfx_prompt.txt（337字）、/tmp/c_real.txt（多镜头中性）
- 提交脚本：/tmp/h3_verify2_submit.py（C 批同款，164s/条）
- 相关 mem0：[STATE] prompt-audio（BGM 调研 2.0）、「H3 去 BGM 最终方案」2026-08-12
