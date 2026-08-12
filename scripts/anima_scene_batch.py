#!/usr/bin/env python3
"""anima t2i 角色场景底图批量生成（h3-prompt-agent 线，图库扩充）

模板 = workflows/anima_alya_169_t2i.json（anima-base + qwen_3_06b + 角色 LoRA），
按 角色×场景 生成 768×448 16:9 首帧底图，落盘 ComfyUI/output/anima/<prefix>.png。

用法：
  python3 scripts/anima_scene_batch.py --character yuki --scenes beach,stage,night --dry-run
  python3 scripts/anima_scene_batch.py --character yuki --scenes beach,stage,night
"""
import argparse
import json
import time
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:8188"
BASE = Path(__file__).resolve().parent.parent
TPL = BASE / "workflows" / "anima_alya_169_t2i.json"
I2I_TPL = BASE / "workflows" / "anima_alya_169_i2i.json"

# 角色 LoRA 与正提示词模板（{scene_block} 由场景块替换）
CHARACTERS = {
    "alya": {
        "lora": "alisa_mikhailovna_kujou_roshidere.safetensors",
        "base": ("alisa mikhailovna kujou (roshidere), long hair, silver hair, ahoge, hair between eyes, "
                 "hair ribbon, blue eyes, school uniform, grey blazer, brown lapels, white collared shirt, "
                 "red bowtie, black vest, long sleeves, pleated skirt, white thighhighs, black loafers"),
    },
    "yuki": {
        "lora": "yuki_suou_v1120706.safetensors",
        "base": ("yuki suou, long pinkish-purple hair, twin braids (twin tails), large ponytails, amber eyes, "
                 "playful smirk, cat-like mischievous smile, school uniform, dark sailor uniform, dark blazer, "
                 "pleated skirt, white thighhighs, dark shoes"),
    },
}

SCENES = {
    "beach": ("standing at the center of the frame, eye-level frontal view, looking directly at the camera, "
              "straight-on composition, no high angle, beach at sunset, golden hour light, gentle waves behind, "
              "warm orange sky, soft sea breeze"),
    "stage": ("standing at the center of the frame, eye-level frontal view, looking directly at the camera, "
              "straight-on composition, no high angle, dark concert stage, dramatic spotlight from above, "
              "rim lighting, blurred stage lights bokeh in background"),
    "night": ("standing at the center of the frame, eye-level frontal view, looking directly at the camera, "
              "straight-on composition, no high angle, night campus street, warm street lamp light, "
              "bokeh city lights background, cool blue night tone"),
    # 中性背景通用站姿（跨段复用安全：场景特征弱，由 prompt 定场景）
    "portrait": ("standing at the center of the frame, eye-level frontal view, looking directly at the camera, "
                 "straight-on composition, no high angle, warm dusk light, soft blurred background, "
                 "gentle golden hour ambience"),
}

# 服装变体（覆盖角色 base 的服装描述；None = 用角色 base 默认服装）
OUTFITS = {
    "uniform": {
        "alya": "school uniform, white jacket with gold trim worn open over a dark navy top with white collar and red bow, black pleated skirt, white thighhighs, black loafers",
        "yuki": "school uniform, dark navy sailor school uniform top, black sailor blouse, white sailor collar and red neckerchief, black pleated skirt, white thighhighs, dark shoes",
    },
}

NEG = ("dark face, shaded face, worst quality, low quality, score_1, score_2, score_3, artist name, blurry, "
       "jpeg artifacts, lowres, censor, bad anatomy, bad hands, extra fingers, text, watermark, top-down view")


def queue_prompt(workflow: dict) -> str:
    req = urllib.request.Request(f"{API}/prompt",
                                 data=json.dumps({"prompt": workflow, "client_id": "anima-scene-batch"}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["prompt_id"]


def wait_done(prompt_id: str, timeout: int = 300) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(f"{API}/history/{prompt_id}", timeout=10) as r:
            h = json.loads(r.read())
        if prompt_id in h:
            status = h[prompt_id].get("status", {})
            if status.get("completed"):
                print(f"  ✅ {prompt_id} 完成")
                return
            if status.get("status_str") == "error":
                raise SystemExit(f"❌ {prompt_id} 失败: {status.get('messages')}")
        time.sleep(3)
    raise SystemExit(f"⏱️ {prompt_id} 超时 {timeout}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", required=True, choices=list(CHARACTERS))
    ap.add_argument("--scenes", required=True, help="逗号分隔场景（beach,stage,night）")
    ap.add_argument("--seed-base", type=int, default=20260811)
    ap.add_argument("--outfit", default="", help="服装变体（uniform=学园制服，覆盖 base 服装描述）")
    ap.add_argument("--i2i", default="", help="img2img 输入图（相对 input/ 或绝对路径）；改服装/构图时保留面容")
    ap.add_argument("--denoise", type=float, default=0.6, help="i2i 重绘强度（改服装 0.5-0.7）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wait", action="store_true", help="提交后轮询等待完成（默认提交即返回）")
    args = ap.parse_args()

    tpl = json.loads((I2I_TPL if args.i2i else TPL).read_text(encoding="utf-8"))
    ch = CHARACTERS[args.character]
    outfit = OUTFITS.get(args.outfit, {}).get(args.character) if args.outfit else None
    for i, scene in enumerate([s.strip() for s in args.scenes.split(",")]):
        if scene not in SCENES:
            print(f"⚠️ 未知场景 {scene}，跳过")
            continue
        wf = json.loads(json.dumps(tpl))  # 深拷贝
        wf["4"]["inputs"]["lora_name"] = ch["lora"]
        char_desc = outfit if outfit else ch["base"]
        wf["5"]["inputs"]["text"] = ("masterpiece, best quality, score_9, score_8, score_7, official art, "
                                     "1girl, solo, clean lineart, detailed eyes, soft shading,\n" + char_desc +
                                     ",\n" + SCENES[scene])
        if args.i2i:
            wf["11"]["inputs"]["image"] = args.i2i
            wf["7"]["inputs"]["denoise"] = args.denoise
            seed = args.seed_base + i
            wf["7"]["inputs"]["seed"] = seed
        else:
            wf["7"]["inputs"]["width"] = 768
            wf["7"]["inputs"]["height"] = 448
            seed = args.seed_base + i
            wf["8"]["inputs"]["seed"] = seed
        prefix = f"anima/{args.character}169_{scene}"
        if args.outfit:
            prefix += f"_{args.outfit}"
        if args.i2i:
            prefix += f"_i2i{int(args.denoise*100)}"
        wf["10"]["inputs"]["filename_prefix"] = prefix
        if args.dry_run:
            print(f"[dry-run] {args.character} x {scene}: seed={seed} prefix={prefix}")
            print("   prompt:", wf["5"]["inputs"]["text"][:150].replace("\n", " ") + " ...")
            continue
        pid = queue_prompt(wf)
        print(f"[{args.character} x {scene}] submitted {pid} (seed {seed})")
        if args.wait:
            wait_done(pid)


if __name__ == "__main__":
    main()
