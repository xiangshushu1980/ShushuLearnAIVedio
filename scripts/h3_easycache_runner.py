#!/usr/bin/env python3
"""EasyCache 成片档实测 runner（T-20260814-01 easycache-test 任务线）

对比：成片档（int8_convrot + v4-600EMA + PathchSageAttentionKJ auto, 8步 @1024×576 124帧）
      baseline（无 EasyCache）vs EasyCache(reuse_threshold=0.30, start_percent=0.20, end_percent=0.90)
同 seed，度量：总耗时(wait) + 采样段(进度条) + EasyCache 跳步日志（verbose=True）

用法（标准库 python3）：
  python3 scripts/h3_easycache_runner.py [--seed 20260814] [--scene wave|dance]
"""
import json, re, sys, time, urllib.request

HOST = "http://127.0.0.1:8188"
LOG = "/tmp/comfyui_start.log"
BASE = "/home/sean/projects/comfy-ops/workflows"
EC_PARAMS = {"reuse_threshold": 0.30, "start_percent": 0.20, "end_percent": 0.90}


def _post(path, data):
    req = urllib.request.Request(HOST + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def urllib_request_get(path):
    with urllib.request.urlopen(HOST + path, timeout=30) as r:
        return json.loads(r.read())


def wait(pid, timeout=3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        h = urllib_request_get(f"/history/{pid}")
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed"):
                return h[pid], time.time() - t0
            if st.get("status_str") == "error":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        raise RuntimeError(m[1].get("exception_message", "?"))
                raise RuntimeError(str(st))
    raise TimeoutError("超时")


def log_offset():
    with open(LOG, "rb") as f:
        f.seek(0, 2)
        return f.tell()


def read_window(start):
    with open(LOG, "rb") as f:
        f.seek(start)
        return f.read().decode("utf-8", "replace")


def parse_window(text):
    """采样耗时（进度条最大 elapsed）+ EasyCache 跳步日志 + 总耗时。"""
    elapsed = []
    for m in re.finditer(r"\[(\d+):(\d+)<", text):
        elapsed.append(int(m.group(1)) * 60 + int(m.group(2)))
    sampling = max(elapsed) if elapsed else None
    # EasyCache 跳步日志
    ec = {}
    m = re.search(r"EasyCache enabled - threshold: ([\d.]+), start_percent: ([\d.]+), end_percent: ([\d.]+)", text)
    if m:
        ec["params"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    m = re.search(r"EasyCache - skipped (\d+)/(\d+) steps \(([\d.]+)x speedup\)", text)
    if m:
        ec["skipped"] = int(m.group(1))
        ec["total"] = int(m.group(2))
        ec["speedup"] = float(m.group(3))
    m = re.search(r"Prompt executed in ([\d.]+) seconds", text)
    prompt_exec = float(m.group(1)) if m else None
    return sampling, ec, prompt_exec


def build_workflow(template_path, ec_enable, seed):
    """从 attn3way_*_sage.json 派生：改 seed + 前缀；ec_enable=True 时插 EasyCache 节点。"""
    wf = json.load(open(template_path))
    # 改 seed
    for node in wf.values():
        if node["class_type"] == "RandomNoise":
            node["inputs"]["noise_seed"] = seed
        if node["class_type"] == "SaveVideo":
            node["inputs"]["filename_prefix"] = node["inputs"]["filename_prefix"].replace("attn3way", "easycache_test")
    if not ec_enable:
        return wf
    # 插 EasyCache：model 链 UNETLoader→(LoraLoader)→PathchSageAttentionKJ → EC → guider/scheduler
    # 找 sage 节点输出给谁（BasicGuider / BasicScheduler）
    sage_id = None
    consumers = {"guider": None, "scheduler": None}
    for nid, node in wf.items():
        if node["class_type"] == "PathchSageAttentionKJ":
            sage_id = nid
    assert sage_id is not None, "未找到 PathchSageAttentionKJ 节点"
    for nid, node in wf.items():
        if node["class_type"] == "BasicGuider" and node["inputs"]["model"] == [sage_id, 0]:
            consumers["guider"] = nid
        if node["class_type"] == "BasicScheduler" and node["inputs"]["model"] == [sage_id, 0]:
            consumers["scheduler"] = nid
    ec_id = str(max(int(x) for x in wf) + 1)
    wf[ec_id] = {"class_type": "EasyCache", "inputs": {
        "model": [sage_id, 0], "reuse_threshold": EC_PARAMS["reuse_threshold"],
        "start_percent": EC_PARAMS["start_percent"], "end_percent": EC_PARAMS["end_percent"],
        "verbose": True}}
    for k, nid in consumers.items():
        if nid:
            wf[nid]["inputs"]["model"] = [ec_id, 0]
    return wf


def run(tag, wf, scene):
    print(f"\n== {scene} {tag} ==")
    _post("/free", {"unload_models": True, "free_memory": True})
    time.sleep(3)
    off = log_offset()
    pid = _post("/prompt", {"prompt": wf})["prompt_id"]
    entry, dt = wait(pid)
    text = read_window(off)
    sampling, ec, prompt_exec = parse_window(text)
    print(f"  总耗时(wait): {dt:.1f}s | 日志 Prompt executed: {prompt_exec}s")
    print(f"  采样段(进度条): {sampling}s" if sampling else "  采样段: 未解析到")
    if ec:
        print(f"  EasyCache: params={ec.get('params')} skipped={ec.get('skipped')}/{ec.get('total')} "
              f"({ec.get('speedup')}x speedup)")
    else:
        print("  EasyCache: 无跳步日志（可能未启用或未解析）")
    # 产物文件名
    for node in wf.values():
        if node["class_type"] == "SaveVideo":
            print(f"  产物前缀: {node['inputs']['filename_prefix']}")
    return dt, sampling, prompt_exec, ec


def main():
    seed = 20260814
    scenes = ["wave", "dance"]
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])
    if "--scene" in sys.argv:
        scenes = [sys.argv[sys.argv.index("--scene") + 1]]
    results = {}
    for scene in scenes:
        tmpl = f"{BASE}/attn3way_{scene}_sage.json"
        r_base = run(f"baseline", build_workflow(tmpl, False, seed), scene)
        r_ec = run(f"easycache", build_workflow(tmpl, True, seed), scene)
        results[scene] = {"baseline": r_base, "easycache": r_ec}
    print("\n== 汇总 ==")
    for scene, r in results.items():
        rb, re_ = r["baseline"], r["easycache"]
        print(f"  {scene}: baseline 总{rb[0]:.1f}s/采样{rb[1]}s | easycache 总{re_[0]:.1f}s/采样{re_[1]}s"
              f" | 跳步 {re_[3].get('skipped','?')}/{re_[3].get('total','?')}"
              f" ({re_[3].get('speedup','?')}x)")
        if rb[1] and re_[1]:
            print(f"    采样加速: {rb[1]/re_[1]:.2f}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
