#!/usr/bin/env python3
"""批量 FaceRefine：对已生成视频逐条精修（官方参数 v4 模板）。

用法: python3 h3_facerefine_batch.py <cases.json> [--interval 15]
cases.json 复用 h3_ref2v 用例格式（name/prefix/prompt），视频路径按
output/video/h3_ref2v/<name>_00001_.mp4 约定。
"""
import json, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
TEMPLATE = json.load(open('/tmp/face_refine_api.json'))  # v4 官方参数模板

def api(path, data=None, timeout=30):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def queue_pids():
    q = api("/queue")
    return ([x[1] for x in q["queue_running"]], [x[1] for x in q["queue_pending"]])

def build_wf(c):
    wf = json.loads(json.dumps(TEMPLATE))  # deep copy
    name = c["name"]
    for nid, n in wf.items():
        t = n["class_type"]
        if t == "VHS_LoadVideoPath":
            n["inputs"]["video"] = f'/home/sean/projects/ComfyUI/output/video/h3_r2v/{name}_00001_.mp4'
        if t == "VHS_LoadAudioUpload":
            n["inputs"]["audio"] = f'{name}_audio.mp3'
        if t == "VHS_VideoCombine":
            n["inputs"]["filename_prefix"] = f'video/FaceRefined/{name}'
        if t == "MiniMaxH3ReferenceToVideo":
            n["inputs"]["prompt"] = c["prompt"]
            n["inputs"]["length"] = 124
    return wf

def main():
    cases = json.load(open(sys.argv[1]))
    interval = 15
    if "--interval" in sys.argv:
        interval = int(sys.argv[sys.argv.index("--interval") + 1])
    results = []
    for c in cases:
        pid = api("/prompt", {"prompt": build_wf(c)})["prompt_id"]
        t0 = time.time()
        while True:
            time.sleep(interval)
            hist = api("/history/" + pid, timeout=10)
            if pid in hist:
                st = hist[pid]["status"]
                status = "success" if st.get("completed") else ("error" if st.get("status_str") == "error" else "running")
                if status != "running":
                    results.append({"name": c["name"], "status": status, "secs": round(time.time() - t0, 1)})
                    print(f"[{c['name']}] {status} {round(time.time()-t0,1)}s", flush=True)
                    break
            if time.time() - t0 > 1800:
                results.append({"name": c["name"], "status": "timeout"})
                break
    out = sys.argv[1] + ".refine_results.json"
    json.dump(results, open(out, "w"), ensure_ascii=False, indent=1)
    print("results ->", out)

if __name__ == "__main__":
    main()
