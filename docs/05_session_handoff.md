# 05 会话交接（2025-08-01 下午）

> 本文件是会话起点：新对话从 `docs/INDEX.md` + 本文件 + `.pi/skills/comfyui/SKILL.md` 开始即可无缝继续。
> 上次交接记录（07-31→08-01 上午）已完成项已归档清理，未完成项合并进下方待办。

## 一、当前环境状态（已就绪）

| 项 | 状态 |
|----|------|
| ComfyUI | ✅ 运行中 http://127.0.0.1:8188（0.29.0，`--enable-assets --enable-asset-hashing` 已固化进 start.sh）|
| 模型栈 | ✅ Wan2.2 I2V Lightning（GGUF Hi/Lo + 4步LoRA）+ ANIMA 生图 + KREA 2 turbo 全就绪 |
| CivitAI token | ✅ 已写入 .mcp.json env（但 pi MCP 不读新 env，**下载用 curl 绕行**，见 SKILL troubleshooting）|
| comfyui-browser | ✅ 已装且用户验收通过（顶部菜单 Browser → Outputs 页签）|
| 资源分类 | ✅ output/input 已按规范子目录化（见 SKILL 资源分类规范）|
| 磁盘 | ✅ 710GB 可用 |
| 队列 | ✅ 空闲 |

## 二、本次会话（08-01 下午）成果

### 1. Browser 面板验收 ✅
- 用户确认正常：顶部菜单 Browser → Outputs 页签可浏览历史文件
- 后端验证：`/browser/files` 目录树、`/browser/config`、`/browser/web/index.html` 全部 200
- 已向用户说明：面板无"新建文件夹"入口（插件 2024-11 停更）→ 目录管理用 Windows 资源管理器（`\\wsl.localhost\Ubuntu\home\sean\projects\ComfyUI\output\`）或 agent

### 2. Alya 768² 起始图标准化 ✅
- 从 `output/anima/anima_alya_20step_00001_.png` 的 **PNG metadata 恢复完整原 prompt**（alisa LoRA 触发词 + 20步/euler/cfg4 + seed 1931893149）
- 新建 `workflows/anima_alya_768_t2i.json`（仅改 768×768）→ `output/anima/anima_alya_768_00001_.png` → `input/start/alya_768.png`
- 768² → I2V 全链路 ✅ `output/video/alya768_i2v_33f_4step_00001_.mp4`（64s，201KB，比原 1024² 版 157KB 信息量更高）

### 3. 资源分类整理 ✅（之后沿用）
- output 按模型/用途分目录：`anima/ krea/ compare/ video/ img_anima/ img_krea/ res_test/`
- input 公用素材语义化：`start/`（alya_768.png / night_street_2048.png…）、`test/`
- SaveImage/SaveVideo 的 filename_prefix 直接带子目录；LoadImage 支持子目录路径（已验证）
- 移动文件后重启 ComfyUI → asset_seeder(prune_first=True) 自动清理旧路径（无需手动清库）
- 所有工作流引用已同步更新

### 4. 网络工作流通路验证 ✅
- `comfyui_run_workflow_url` 实测：拉取 Comfy-Org 官方 `wan2.1_fun_camera_14B.json`（15 节点，相机运镜控制）→ 完整解析+校验
- 摸清资源：本地 blueprints 80+、官方 templates 506、MCP 内置 56 packs + 35 skills
- 质量门禁四关：validate → check_runtime → 本机栈对比 → 实跑量化（详见 SKILL learning.md）

### 5. 知识体系重构 ✅
- SKILL.md 从单文件集合体（104 行）→ 主干 + references/ 分册（params/workflows/troubleshooting/learning）
- docs/02_models.md 重写（旧版停留在 Wan2.1 四件套 23.7GB）；docs/04 更新为当前栈
- 用户确认"官方示例 + MCP 内置 = 高质量基线"的质量观

### 6. 起始图选优（进行中）
- ANIMA vs KREA Alya 768² 同题对比已生成：`output/compare/alya768_compare_anima_vs_krea.png`
- 量化：ANIMA 清晰度805/中心比1.60/饱和111 vs KREA 1356/1.65/74
- **结论倾向**：ANIMA 角色 LoRA 还原精确（主角色用）；KREA 平滑/写实（场景氛围用）

### 6. 2.2 多底图×多帧数基准（2025-08-01）
- 18 视频（6 底图 × 17/33/49 帧，6 步）：`output/video/sweep_*`
- 结论：帧数不影响清晰度；动作随帧数增长；底图内容决定清晰度基线（机甲 3938 > 森林 2765 > 甜点 2170 > 夜景 1421 > 人物 1029 > 太空猫 179）
- **5 秒视频标准定为 41帧@8fps**（生成 ~24s，比 81帧@16fps 快一半）
- 生成时间由帧数决定（30fps×2s = 10fps×6s = 60帧同耗时）；帧数-耗时近线性（~0.54s/帧）

### 7. Wan2.1 vs Wan2.2 对比（2025-08-01）
- 简单提示词/33帧：2.1 清晰度略胜（1219 vs 991），动作持平；2.2 快 2.5 倍
- 复杂提示词/49帧：Alya 图 2.1 清晰度 +29%；写实夜景图 2.2 清晰度 2.3 倍（1384 vs 606）、2.1 动作 35.8 vs 20.7
- 综合：2.2 更均衡；2.1 仅在动漫人像清晰度领先；对比产物 `output/compare/cmp2_49f_grid.png`
- Wan2.1 也有官方 4 步蒸馏（lightx2v/Wan2.1-Distill-Models），但需整模型替换（~15GB），2.2 用 LoRA 免费

### 8. 多人视频测试（2025-08-01）
- 用户上传图（3 张多人 + 2 张单人）全部可生成视频：`output/video/userimg_*`（5.1s）
- ANIMA 自生成多人图（2人左右/3人一排/2人对话）→ 视频：`output/video/genmulti_*`，清晰度 3409-5408（高于上传图），动作 2人 24.0 > 对话 9.1 > 3人 5.3
- **多人可行性**：能生成，但动作分配随人数下降（2人互动最好）；需目视确认是否“独立运动 vs 糊一体”
- 多人图生成强调分离构图：提示词写明人物位置/特征/间距

### 9. 底图分辨率严格实验（2025-08-01，关键修订）
- 骑士图 5 档（512/768/1024/1536/1792²）同 seed 同提示词：**底图分辨率 → 视频清晰度线性 +82%**（539→979）；**不影响动作**（18.1-19.0 持平）；**不影响耗时**（21-30s）
- **修订旧“768² 性价比最高”结论 → I2V 起始图用原图分辨率直接跑**（1024-1792² 增益持续）
- 产物：`output/video/resk_{512,768,1024,1536,1792}_00001_.mp4`

## 三、待办（新对话优先级）

0. **✅ Bernini 深度探索完成（2025-08-02）**：
   - **核心结论**：Bernini 是"编辑器"（in-context 软参考）非"生成器"（concat 硬锁）→ 生成模式（r2v/t2v）脸部漂移，编辑模式（v2v/i2i）保持好
   - **✅ 最终管线（推荐）**：`Wan2.2 I2V（脸部锁定）→ Bernini v2v 编辑 → RIFE补帧 → ClearReality超分`，工作流 `pipeline_wan22_bernini_golden.json`，全链路验证通过（脸部/动作/风格保持，120s）
   - **static2v 技巧**：单帧→RepeatImageBatch→source_video 伪装视频（风格保持✅ 脸部漂移⚠️）
   - **rv2v 双参考**：source_video+reference_images 脸部保真✅ 但慢（370s）
   - 官方参数：832×480 横屏 / fps16 / 40步（ComfyUI 用 Turbo 6步替代）；提示词技巧（image0 引用/动作序列/负面词防写实）
   - 详细见 docs/06_extras_install.md；Bernini 视频生成（t2v 一致性）后续再探索
1. **起始图选优拍板**：ANIMA vs KREA Alya 768²（对比图 output/compare/）→ 用户拍板主角色管线
2. **多动作管线探索**：artokun-flow **已完成结构评估**（需 WanVideoWrapper 生态 ~30GB，成本高）→ 降级方案优先 `wan-longer-videos`（同 GGUF 栈，适配成本低）待评估
3. **更多测试**（可选）：Yuki 角色 LoRA、KREA 画 Alya、不同场景 I2V、Wan2.1 Fun Camera 相机运镜（需下载专用模型 ~30GB，暂缓）
4. **资源索引脚本**（可选）：sqlite 登记 prompt/参数/文件，按角色/题材检索
5. **Mem0 共享记忆系统（已落地 2025-08-02）**：MCP server（scripts/mem0_mcp.py）+ 20 条经验入库（docs/06 迁移）+ AGENTS.md 决策树 + mem0 skill（.pi/skills/mem0/）。会话开始先 memory_recall，结束时 memory_retain。**后续优化**：① 记忆中文输出（custom_instructions）② Codex 接入（~/.codex/config.toml 声明同一 MCP server）③ docs/06 实测部分精简（头注已约定）④ BM25 混合检索（pip install "mem0ai[extras]"，当前仅 dense 单路）
6. **Bernini int8 vs fp8 对比（2025-08-02 已测，已 retain 入 Mem0）**：视频任务 int8 快 21% 画质无损 → 低配加速选项，完整结论在 Mem0 检索

## 本次追加（2025-08-02 晚，Bernini 收尾）

### 已完成
- ✅ **int8_convrot 已下载并实测**：视频任务 int8 快 21%（105s vs 133s/81帧）画质无损（清晰度 1023 vs 999）；图像单帧 int8 反而慢 18%（加载开销）；结论入 `bernini_int8_findings.md` + docs/06 + params.md
- ✅ **cfg/fps 三版对比**：cfg1.0@16fps（81帧 480²）清晰度最高 1320，动作最连贯；cfg1.5 压低清晰度 + 步伐乱；**cfg1.0 是编辑任务甜点**
- ✅ **10s 组合管线验证（关键）**：`wan22_alya_10s_f16`（Wan2.2 161帧@16fps 832×480，280s）→ `bernini_v2v_10s_f16`（Bernini 编辑，1310s）→ 清晰度 732→870，**用户目视确认 10s 全程自然连贯**
- ✅ **时长匹配铁律**：源视频时长必须 == Bernini 输出时长（10s→10s 匹配；10s→5s 脑补/步伐混乱）
- ✅ **WSL 内存 32GB→48GB**：Bernini 任务 python 峰值 ~30GB 两次 OOM 崩溃 → `.wslconfig` 加 `memory=48GB`（已生效，免费 45GB）；重启命令 setsid
- ✅ **ComfyUI 模型缓存机制确认**：NORMAL_VRAM 任务间不释放（空闲显存 ~11.8GB 驻留），同模型连跑快、互切才重载
- ✅ **新工作流**：`bernini_int8_cfg10_fps16.json` / `bernini_v2v_10s_f16.json` / `wan22_alya_10s_f16.json`

### 待办（重开对话优先级）
1. **10s 甜点定案**：161帧@832×480 = 1310s 太慢（非线性 12×）；待测 **640×360** 降面积方案（预计 ~500s）——若接受则固化 10s 组合管线
2. **5s 甜点定案**：待测 **81帧@832×480（官方横屏）** vs 480² 的画质/耗时权衡 → 确定后固化默认管线
3. **产物对比图**：`output/compare/bernini_3way_fps_cfg.png`（cfg/fps 三版）、`bernini_v2v_10s_f16_compare.png`（10s 源/编辑）
4. **目视确认遗留**：cfg1.0@16fps 5s 版步伐是否自然（用户已确认 10s 版连贯）

## 四、常用链接

- Alya 768² 起始图：`http://localhost:8188/view?filename=anima_alya_768_00001_.png&subfolder=anima&type=output`
- Alya 768² I2V 视频：`http://localhost:8188/view?filename=alya768_i2v_33f_4step_00001_.mp4&subfolder=video&type=output`
- Alya 对比拼图：`http://localhost:8188/view?filename=alya768_compare_anima_vs_krea.png&subfolder=compare&type=output`
- 工作流：`comfy-ops/workflows/`（anima_alya_768_t2i / anima_t2i / krea2_t2i / wan2.2_lightning / wan2.2_standard_multiaction）
