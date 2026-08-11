# 视频素材库索引

> 素材来源：Pexels（免费，节制下载）。供 Bernini v2v 编辑 / Agent 自动取用。

## 目录规范

```
input/
├─ material/           ← Pexels 原片（未预处理）
│   ├─ action/         ← 动作类（走路/跳舞/挥手/转身/跑步...）
│   ├─ portrait/       ← 人像/表情/特写
│   └─ scene/          ← 场景/环境（雨夜街道/城市/室内...）
├─ material_b/         ← Bernini 预处理版（832×480 / 81帧 / 16fps，与 material/ 一一对应）
│   ├─ action/
│   ├─ portrait/
│   └─ scene/
├─ start/              ← 起始图（alya 等生图起始图）
│   └─ 169/            ← 16:9 首帧图库（H3 i2v 首帧必须 16:9，35 张，规则见 docs/21 §首帧锚定规律）
├─ ref_lib/            ← H3 ref2va 参考图库（realistic/ 写实 59 + illustration/ 插画 62，共 121 张，来源见 docs/09 底图库）
├─ test/               ← 测试用临时文件
└─ 3d/                 ← 3D 相关
```

## 命名规则
- 原片：`<动作_主体_分辨率>.mp4`（来自 Pexels 自动命名）
- 预处理版：`<原片名>_b81.mp4`（832×480/81帧）
- 分类判断关键词：action=walking/dancing/waving/turning/running；portrait=portrait/smiling/face；scene=rainy/city/street/night/interior

## 素材清单

### action/（动作）
- girl_turning_around_6976383_960x506.mp4 / _b81
- man_walking_street_6002525_960x540.mp4 / _b81
- woman_dancing_8039424_960x506.mp4 / _b81
- woman_dancing_8929498_960x540.mp4 / _b81
- woman_walking_3251840_960x540.mp4 / _b81
- woman_walking_7570173_960x540.mp4 / _b81
- woman_waving_4492700_960x540.mp4 / _b81

### portrait/（人像）
- woman_portrait_smiling_6684246_960x540.mp4 / _b81
- woman_portrait_smiling_7049300_540x960.mp4 / _b81

### scene/（场景）
- rainy_city_street_night_35153704_360x640.mp4 / _b81

## 使用方法（Agent）
- 检索：`ls input/material/<分类>/` 或读本索引
- 下载新素材：`python3 scripts/pexels_download.py "<关键词>" --count N`
- 预处理：`python3 scripts/prep_bernini.py`（转到 832×480/81帧）
- Bernini 编辑：LoadVideo 用子目录路径 `material_b/action/xxx.mp4`（已验证可读）
- ⚠ Bernini 显存：优先 640×360（100s）或 480²（122s），勿用 832×480（24GB 满载触发 offload 变慢 261s）

## 预览服务
- 网页预览：http://127.0.0.1:8000（scripts/video_gallery.py）
- ComfyUI 菜单按钮："素材库"（插件 comfyui-material-gallery，点击启动并跳转）
- 刷新 ComfyUI 页面后菜单出现按钮
