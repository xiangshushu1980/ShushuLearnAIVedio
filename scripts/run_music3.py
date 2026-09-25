#!/usr/bin/env python3
"""提交 MiniMax Music 3 测试：读 API 模板 + 输入 JSON，替换 caption/lyrics，提交并等结果。
用法: python3 run_music3.py --input <in.json> [--duration 秒] [--seed N] [--tag 标签]
"""
import json, sys, time, argparse, urllib.request

SERVER = "http://127.0.0.1:8188"

def queue_prompt(prompt):
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(f"{SERVER}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"提交失败 HTTP {e.code}: {e.read().decode()[:500]}")

def get_history(pid):
    with urllib.request.urlopen(f"{SERVER}/history/{pid}", timeout=30) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--template", default=".pi/tasks/T-comfy-ops-16/minimax_music3_api_template.json")
    ap.add_argument("--duration", type=float, default=120.0)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--tag", default="wow")
    args = ap.parse_args()

    inp = json.load(open(args.input))
    tpl = json.load(open(args.template))
    import random
    seed = args.seed if args.seed is not None else random.randint(0, 2**31)

    # 注入
    for nid, node in tpl.items():
        if node["class_type"] == "MiniMaxMusic3TextEncode":
            node["inputs"]["caption"] = inp["caption"]
            node["inputs"]["lyrics"] = inp["lyrics"]
            node["inputs"]["seed"] = seed
            node["inputs"]["max_duration"] = args.duration
        elif node["class_type"] == "EmptyMiniMaxMusic3LatentAudio":
            node["inputs"]["seconds"] = args.duration
        elif node["class_type"] == "KSampler":
            node["inputs"]["seed"] = seed
        elif node["class_type"] in ("SaveAudioAdvanced", "SaveAudioMP3", "SaveAudio"):
            node["inputs"]["filename_prefix"] = f"audio/minimax_music3_{args.tag}"

    print(f"➡️  提交 Music3: tag={args.tag}, duration={args.duration}s, seed={seed}")
    print("   模型: dit_fp16 + TE_pruned_int8 + DAV")
    res = queue_prompt(tpl)
    pid = res.get("prompt_id")
    print(f"✅ 已提交: {pid}")
    if "error" in res or not pid:
        print("⚠️  服务响应:", json.dumps(res, ensure_ascii=False)[:400])
        sys.exit(1)

    # 轮询
    start = time.time()
    last_status = ""
    while True:
        time.sleep(5)
        try:
            hist = get_history(pid)
        except Exception as e:
            print("   (查询中断, 重试)", e); time.sleep(3); continue
        if pid in hist:
            status = hist[pid].get("status", {})
            s = status.get("status_str", "")
            completed = status.get("completed", False)
            if not last_status or s != last_status:
                print(f"   [{int(time.time()-start)}s] 状态: {s}"); last_status = s
            if completed:
                outputs = status.get("outputs", {})
                for nid, o in outputs.items():
                    for k, v in o.items():
                        if isinstance(v, list):
                            print(f"✅ 输出 [{nid}]: {v}")
                break
            if s == "error":
                msgs = status.get("messages", [])
                for m in msgs:
                    print("   ❌", m)
                sys.exit(1)
        if time.time() - start > 3600:
            print("⚠️  超时 1h，放弃轮询（可能仍在跑）")
            break
    print(f"完成，总耗时 {int(time.time()-start)}s")
