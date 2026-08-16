#!/usr/bin/env python3
"""ComfyUI 出图 → 线上 VL 识图联测脚本（img-qc-api-test 任务）。

用法：
    python3 scripts/img_qc_test.py gen --prompt "..." --seed 42 [--workflow workflows/anima_alya_768_t2i.json]
    python3 scripts/img_qc_test.py gen --prompt "..." --workflow workflows/krea2_t2i_test.json

生图后打印输出图片绝对路径，供 vision_chat 识别比对。
"""
import json
import sys
import time
import uuid
import urllib.request

SERVER = "http://127.0.0.1:8188"


def _post(path, data):
    req = urllib.request.Request(
        f"{SERVER}{path}", data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def _get(path):
    with urllib.request.urlopen(f"{SERVER}{path}", timeout=60) as resp:
        return json.loads(resp.read())


def gen_image(prompt, seed, workflow="workflows/anima_alya_768_t2i.json",
              prefix="anima/anima_apirecog_test", lora=None, lora_strength=None):
    """加载 API 格式工作流，替换正/负提示词与 seed，提交并轮询，返回输出图绝对路径。"""
    with open(workflow) as f:
        wf = json.load(f)

    # 正提示词统一替换（CLIPTextEncode 节点 text 字段）
    pos_done = False
    for nid, node in wf.items():
        if node.get("class_type") == "CLIPTextEncode":
            txt = str(node["inputs"].get("text", ""))
            if not pos_done and ("1girl" in txt or "score_9" in txt or txt == "" or "masterpiece" in txt or "best quality" in txt):
                node["inputs"]["text"] = prompt
                pos_done = True
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = int(seed)
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = prefix
        if node.get("class_type") in ("LoraLoader", "LoraLoaderModelOnly"):
            if lora:
                node["inputs"]["lora_name"] = lora
            if lora_strength is not None:
                node["inputs"]["strength_model"] = float(lora_strength)

    client_id = str(uuid.uuid4())
    res = _post("/prompt", {"prompt": wf, "client_id": client_id})
    pid = res["prompt_id"]
    print(f"已提交: {pid}")

    start = time.time()
    while True:
        time.sleep(3)
        try:
            hist = _get(f"/history/{pid}")
        except Exception:
            continue
        if pid not in hist:
            continue
        status = hist[pid].get("status", {})
        if status.get("status_str") == "error":
            print("生成失败:", json.dumps(status, ensure_ascii=False)[:500])
            sys.exit(1)
        if status.get("completed"):
            elapsed = time.time() - start
            print(f"生成完成，耗时 {elapsed:.0f}s")
            for nid, out in hist[pid].get("outputs", {}).items():
                if "images" in out:
                    for img in out["images"]:
                        path = f"/home/sean/projects/ComfyUI/output/{img['subfolder']}/{img['filename']}"
                        print(f"输出图: {path}")
                        return path
            print("未找到图片输出:", json.dumps(hist[pid], ensure_ascii=False)[:500])
            sys.exit(1)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--prompt", required=True)
    g.add_argument("--seed", type=int, default=42)
    g.add_argument("--workflow", default="workflows/anima_alya_768_t2i.json")
    g.add_argument("--prefix", default="anima/anima_apirecog_test")
    g.add_argument("--lora", default=None)
    g.add_argument("--lora-strength", type=float, default=None)
    a = ap.parse_args()
    if a.cmd == "gen":
        gen_image(a.prompt, a.seed, a.workflow, a.prefix, a.lora, a.lora_strength)
