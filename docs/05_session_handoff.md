# 05 会话交接（2025-08-02）

> 本文件是会话起点：新对话从 `docs/INDEX.md` + 本文件 + `.pi/skills/comfyui/SKILL.md` + `docs/07_video_material.md` 开始即可无缝继续。
> 上次交接（08-01）已完成项归档，本次聚焦 08-02 的 Bernini 编辑 / 素材库 / SageAttention 探索。

## 一、当前环境状态（已就绪）

| 项 | 状态 |
|----|------|
| ComfyUI | ✅ 运行中 http://127.0.0.1:8188（0.29.0，start.sh 含 --enable-assets）|
| 模型栈 | ✅ Wan2.2 I2V Lightning（GGUF Q4_K_S Hi/Lo）+ Bernini-R int8（视频编辑用）+ ANIMA/KREA |
| mem0 | ✅ HTTP 常驻（http://127.0.0.1:8899/mcp），重启 pi 后走 HTTP 连接正常 |
| 素材库 | ✅ Pexels 管线（下载+预处理+分类）+ 预览插件 |
| 素材预览插件 | ✅ comfyui-material-gallery（ComfyUI 菜单"素材库"按钮 → http://127.0.0.1:8000）|
| SageAttention | ✅ 已装 2.2.0 但 start.sh 当前**未启用**（测试结论待定）|
| 队列 | ✅ 空闲 |

## 二、本次会话（08-02）核心成果

### 1. Bernini 编辑能力验证（重点）✅
- **6 类编辑测试**（基础视频 nosage480_combo，81帧/480²，int8 模型）：动作/人物/镜头/表情/环境 **5 类效果都很好**；第 6 类"图片参考"**未测**（待办）
- **真人素材编辑**（woman_walking→golden hour）成功，效果好
- **Bernini 是编辑器**（in-context 软参考）非生成器：改动作/人物/镜头/表情/环境都能精确控制，人物保持好
- ⚠ **显存教训**：832×480 编辑显存冲 24009MiB 满载 → 触发 offload 能跑但慢(261s)；**480² 安全(15.7GB,122s)**；**640×360 最优(20.2GB,100s)**

### 2. Bernini 编辑速度（已实测）⭐
| 分辨率 | 显存峰值 | 耗时 | 结论 |
|--------|---------|------|------|
| 640×360 | 20.2GB | **100s** | 最优（16:9，最快安全）|
| 480² | 15.7GB | 122s | 安全 |
| 832×480 | 24.0GB满载 | 261s | offload 变慢，避免 |

### 3. Wan2.2 分辨率-速度/动作探索
- **720p（1280×720, 81帧）= 300s**，显存 19.4GB（Q4_K_S 可跑，无需降量化）
- **832×480 = 102s**（官方甜点，ComfyUI 默认）
- **分辨率-动作复杂度阶梯**：token 越多动作越丰富（512走路→960自然转身），但高分辨率有细节漂移风险
- **起始图比例须匹配生成分辨率**（否则拉伸/裁切丢细节）→ 生成 16:9 与 1:1 的 alya 起始图
- **Wan 单次生成 >81帧 动作退化**（241帧平均帧差0.54 vs 81帧1.79）；>120帧循环/停顿

### 4. SageAttention 探索（测试进行中，未定论）
- 已编译安装 2.2.0（WSL 踩坑：需 conda cuda-nvcc 13.0 匹配 torch cu130 + 完整 cuda-toolkit + 头文件符号链接）
- ComfyUI 0.29 原生支持 `--use-sage-attention` 启动参数（当前 start.sh 未启用）
- 初步：832×480 加速 26%（102.7→75.9s），画质目视无损
- ⚠ **但用户观察到 sage 可能让动作变单调**（nosage 更丰富）→ **待进一步多动作对比验证**

### 5. 素材库管线（新建）✅
```
Pexels 下载 → 预处理(832×480/81帧) → Bernini 编辑
```
- `scripts/pexels_download.py`：节制下载（max-width=1280 防超大中断，自动清0字节）
- `scripts/prep_bernini.py`：预处理成 Bernini 规格
- `docs/07_video_material.md`：素材索引+规范
- 素材分类：input/material/{action,portrait,scene}（原片）+ input/material_b/（Bernini预处理版）

### 6. 素材预览插件（新建）✅
- `custom_nodes/comfyui-material-gallery/`：菜单"素材库"按钮 → 启动/检测预览服务 → 跳转 http://127.0.0.1:8000
- `scripts/video_gallery.py`：独立素材浏览 Web 页（标准库，不碰 ComfyUI 源码）
- 已验证：路由 /material-gallery/start 工作，前端 JS 加载成功

### 7. 其他
- mem0 锁问题：因 pi 会话连接方式（需重启 pi 走 HTTP 8899），server 本身健康
- input 根目录散文件已全部归类（start/ test/ 等）

## 三、待办（新对话优先级）

1. **Bernini 第6类"图片参考"编辑测试**：用参考图引导编辑（未做，补全能力图谱）
2. **SageAttention 定案**：多动作对比（转身/跳跃/组合 × sage on/off）确认是否影响动作丰富度 → 决定 start.sh 是否启用
3. **Bernini 真人素材更多编辑测试**：动作/表情在真人上（已测环境，待测其他）
4. **优化 Bernini 速度**：640×360 已测最快(100s)，可考虑并行/其他
5. **Wan 长视频分块方案**（可选）：Community 方案 context window 81帧+overlap，或装 Kijai WanVideoWrapper
6. **素材库扩展**：更多素材分类/下载（Pexels API 已就绪）

## 四、常用链接/命令
- 素材预览：http://127.0.0.1:8000（或 ComfyUI 菜单"素材库"按钮）
- 下载素材：`python3 scripts/pexels_download.py "<关键词>" --count N`
- 预处理：`python3 scripts/prep_bernini.py`
- mem0：`scripts/mem0.sh status|start|stop`
- Bernini 编辑模板：`workflows/bernini_edit_81_base.json`（480²）/ int8 版 `bernini_edit_81_int8.json`
