#!/usr/bin/env python3
"""迁移 docs/06 经验类内容 → Mem0（user_id=comfy-ops 共享池）
执行后这些经验可被任意 agent 会话通过 MCP memory_recall 检索。"""
import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("MEM0_TELEMETRY", "false")
from mem0 import Memory

config = {
    "llm": {"provider": "deepseek", "config": {"api_key": os.environ["DEEPSEEK_API_KEY"], "model": "deepseek-chat"}},
    "embedder": {"provider": "huggingface", "config": {"model": "BAAI/bge-m3"}},
    "vector_store": {"provider": "qdrant", "config": {
        "path": "/home/sean/projects/comfy-ops/.mem0/qdrant", "embedding_model_dims": 1024}},
}
m = Memory.from_config(config)

# docs/06 经验类内容（实测数据/踩坑/提炼认知/用户偏好）
EXPERIENCES = [
    # --- RMBG 抠图 ---
    "RMBG 抠图实测（BiRefNet_toonout）：768² PNG → RGBA，背景 68% 全透明、四角干净、中心主体 97.8% 保留，耗时 3.6 秒",
    "ComfyUI-RMBG 的正确仓库是 1038lab/ComfyUI-RMBG（kijai 的仓库不存在）；依赖需装 onnxruntime-gpu、opencv-python-headless、timm（缺 timm 报 No module named timm）",
    # --- ClearReality 超分 ---
    "ClearReality 超分实测：768²→3072²（4x）耗时 3.3 秒；推荐用于 480/720p 生成 → 超分 → 1080p 成品的流程",
    # --- Bernini 管线参数 ---
    "Bernini-R 图像/视频编辑管线关键参数：LoRA Hi=3.0/Lo=1.5（T2V distill 版），采样器 res_multistep，6 步 split 3/3，cfg=1.0，分辨率必须 16 的倍数（如 928×1280、832×480），帧数 4n+1",
    # --- Bernini 踩坑 ---
    "Bernini 不能用 GGUF text encoder（Q5_K_S），必须完整 fp8（umt5_xxl_fp8_e4m3fn_scaled，6.7GB）；不能用 euler 采样器；不能走 img2img VAEEncode 半程去噪（会花屏），必须 BerniniConditioning in-context 注入从头采样；WanImageToVideo 不适合（那是 I2V concat 条件）",
    "Bernini LoadVideo 只能读 input/ 下文件（不能 output/ 路径）；SaveVideo 需显式 format/codec",
    # --- Bernini 实测数据 ---
    "Bernini v2v 视频编辑实测：Alya 金色时刻重打光 5 秒（41帧@8fps），动作保留（14.1→15.6），耗时约 120 秒",
    "Bernini 任务耗时对比：v2v 单参考 120s < static2v 230s < rv2v 双参考 370s（v2v 最快，2 次 forward）",
    # --- Bernini 核心认知 ---
    "Bernini 是编辑器不是生成器：Wan2.2 I2V 是 concat 硬锁（第一帧噪声=0，脸部保真天然好）；Bernini 是 in-context 软参考（VAE 编码 token 参考但不锁定）→ 从静态图生成新内容会重绘细节（脸部漂移）",
    "Bernini 保真度排序：i2i（单帧小改）≈ v2v（真实视频参考）> static2v（静态帧无运动）> r2v/t2v（自由生成）",
    "Bernini static2v 技巧：单帧 → RepeatImageBatch×81 → source_video 伪装成视频（风格保持二次元、动作自然、脸部有漂移）",
    "Bernini rv2v 脸部保真：source_video + reference_images 双参考 + 脸部细节提示词 + 换脸/变脸负面词（保真但慢 370s）",
    # --- 推荐管线 ---
    "推荐的完整管线（已验证）：参考图 → Wan2.2 I2V（第一帧锁定，脸部/风格保真）→ Bernini v2v（重打光/风格化编辑）→ RIFE 补帧×3 → ClearReality 超分×4 → 1080p 成品",
    # --- 提示词技巧 ---
    "Bernini 提示词技巧：用 image0/image1 引用参考图（每图独立 token）；结构=主体引用→外貌保持→场景→动作序列（start/then/after/throughout）→镜头固定；负面词加 photorealistic/3D render/different face 防写实漂移",
    # --- 资源规范/约束 ---
    "output/ 按用途分子目录（anima/krea/compare/video/img_*/res_test），filename_prefix 直接带子目录，生成时命名绝不再重命名；LoadImage 支持子目录路径",
    # --- MCP/工具状态 ---
    "comfyui-mcp 工具状态：remove_background、upscale_image 可用；generate_with_ip_adapter 缺 ComfyUI_IPAdapter_plus 节点不可用；训练 train_* 需要 docker-GPU+HF_TOKEN 不可用；ComfyUI-Manager 是 3.x 旧版，Manager API 操作不可用（装节点用 git clone 或手动）",
    # --- 用户偏好/决策 ---
    "用户偏好：不用付费云服务（排除 RunPod/Comfy 云/付费 API）；不装 lossy 加速器（SageAttention/TeaCache，会改变视频结果）；本地优先，能本地跑的不上云",
    "用户网络环境：Clash Rule 模式+TUN 接管（无 system proxy），GitHub 走代理节点/国内直连；遇到网络异常先与用户确认，不要擅自改配置",
]

added = 0
for exp in EXPERIENCES:
    r = m.add(exp, user_id="comfy-ops")
    mems = r.get("results", [])
    added += len(mems)
    print(f"  +{len(mems)} | {exp[:50]}...")

total = m.get_all(filters={"user_id": "comfy-ops"})
print(f"\n迁移完成：新增 {added} 条记忆，库中共 {len(total.get('results', []))} 条")
