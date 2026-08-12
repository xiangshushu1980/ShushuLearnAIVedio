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
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wait", action="store_true", help="提交后轮询等待完成（默认提交即返回）")
    args = ap.parse_args()

    tpl = json.loads(TPL.read_text(encoding="utf-8"))
    ch = CHARACTERS[args.character]
    for i, scene in enumerate([s.strip() for s in args.scenes.split(",")]):
        if scene not in SCENES:
            print(f"⚠️ 未知场景 {scene}，跳过")
            continue
        wf = json.loads(json.dumps(tpl))  # 深拷贝
        wf["4"]["inputs"]["lora_name"] = ch["lora"]
        wf["5"]["inputs"]["text"] = ("masterpiece, best quality, score_9, score_8, score_7, official art, "
                                     "1girl, solo, clean lineart, detailed eyes, soft shading,\n" + ch["base"] +
                                     ",\n" + SCENES[scene])
        wf["7"]["inputs"]["width"] = 768
        wf["7"]["inputs"]["height"] = 448
        wf["8"]["inputs"]["seed"] = args.seed_base + i
        prefix = f"anima/{args.character}169_{scene}"
        wf["10"]["inputs"]["filename_prefix"] = prefix
        if args.dry_run:
            print(f"[dry-run] {args.character} x {scene}: seed={wf['8']['inputs']['seed']} prefix={prefix}")
            print("   prompt:", wf["5"]["inputs"]["text"][:150].replace("\n", " ") + " ...")
            continue
        pid = queue_prompt(wf)
        print(f"[{args.character} x {scene}] submitted {pid} (seed {wf['8']['inputs']['seed']})")
        if args.wait:
            wait_done(pid)


if __name__ == "__main__":
    main()
