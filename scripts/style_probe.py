#!/usr/bin/env python3
"""风格对比板采样（story-e2e-v1）：同一场景 prompt × 多风格。
ANIMA 基座 5 变体（摘角色 LoRA）+ KREA 1 变体（游戏 stylized 写实对照）。
用法: python3 scripts/style_probe.py [--only A,B] [--dry-run]
"""
import argparse
import copy
import json
import os
import sys
import time
import urllib.request

SERVER = "http://127.0.0.1:8188"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SCENE = ("a young human villager adventurer in simple brown linen tunic and leather belt, "
         "standing on the main street of a small medieval abbey town, stone abbey with tall spire behind, "
         "timber-framed houses with thatched roofs, town guards in simple armor on patrol, "
         "golden morning light through trees, distant forested hills, warm cozy fantasy atmosphere")

NEG = ("dark face, shaded face, worst quality, low quality, score_1, score_2, score_3, artist name, "
       "blurry, jpeg artifacts, lowres, censor, bad anatomy, bad hands, extra fingers, "
       "extra limbs, missing fingers, extra digits, watermark, signature, text, logo")

STYLES = {
    "A_anime_cel": {
        "wf": "workflows/anima_alya_169_t2i.json",
        "pos": "masterpiece, best quality, score_9, score_8, score_7, official art, "
               "anime style, cel shading, vibrant saturated colors, clean lineart, detailed eyes, " + SCENE,
    },
    "B_ghibli": {
        "wf": "workflows/anima_alya_169_t2i.json",
        "pos": "masterpiece, best quality, score_9, score_8, score_7, "
               "studio ghibli inspired, watercolor painting, soft pastel palette, hand-painted background, "
               "gentle warm light, whimsical storybook feel, " + SCENE,
    },
    "C_painterly": {
        "wf": "workflows/anima_alya_169_t2i.json",
        "pos": "masterpiece, best quality, score_9, score_8, score_7, "
               "painterly fantasy concept art, thick impasto brushstrokes, dramatic golden lighting, "
               "oil painting texture, " + SCENE,
    },
    "D_american_cartoon": {
        "wf": "workflows/anima_alya_169_t2i.json",
        "pos": "masterpiece, best quality, score_9, score_8, score_7, "
               "american cartoon style, bold clean outlines, vibrant flat colors, "
               "stylized friendly proportions, " + SCENE,
    },
    "E_webtoon": {
        "wf": "workflows/anima_alya_169_t2i.json",
        "pos": "masterpiece, best quality, score_9, score_8, score_7, "
               "webtoon manhwa style, clean digital painting, soft cel shading, polished rendering, " + SCENE,
    },
    "F_game_stylized": {
        "wf": "workflows/krea2_t2i_test.json",
        "pos": ("stylized realistic AAA game art, painterly realism, high fidelity, cinematic lighting, "
                + SCENE.replace("villager adventurer", "villager adventurer character")),
    },
}


def submit(prompt: dict) -> str:
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(f"{SERVER}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["prompt_id"]


def wait_queue():
    while True:
        with urllib.request.urlopen(f"{SERVER}/queue", timeout=10) as r:
            q = json.load(r)
        if not q.get("queue_running") and not q.get("queue_pending"):
            return
        time.sleep(3)


def build_api(wf_path: str, pos: str, prefix: str) -> dict:
    wf = json.load(open(os.path.join(ROOT, wf_path)))
    # 摘除角色 LoRA（LoraLoaderModelOnly），KSampler model 直连 UNETLoader
    lora_nodes = [nid for nid, n in wf.items() if n["class_type"] == "LoraLoaderModelOnly"]
    for nid in lora_nodes:
        del wf[nid]
    for n in wf.values():
        if n["class_type"] == "KSampler":
            n["inputs"]["model"] = ["1", 0]
    for n in wf.values():
        if n["class_type"] == "CLIPTextEncode":
            n["inputs"]["text"] = pos
        if n["class_type"] == "SaveImage":
            n["inputs"]["filename_prefix"] = prefix
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="逗号分隔风格名子集，如 A,B")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    selected = list(STYLES)
    if args.only:
        selected = [s.strip() for s in args.only.split(",") if s.strip() in STYLES]

    for name in selected:
        cfg = STYLES[name]
        prefix = f"style_probe/{name}"
        wf = build_api(cfg["wf"], cfg["pos"], prefix)
        if args.dry_run:
            print(f"[dry-run] {name}: {cfg['wf']} pos_len={len(cfg['pos'])}")
            continue
        pid = submit(wf)
        print(f"[submitted] {name} pid={pid} -> output/{prefix}")
        wait_queue()
        time.sleep(1)
    print("ALL DONE")


if __name__ == "__main__":
    main()
