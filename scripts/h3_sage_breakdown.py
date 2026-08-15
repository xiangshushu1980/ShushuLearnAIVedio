#!/usr/bin/env python3
"""单任务耗时构成实测（sage 节点开/关对比，cond-cache-node 任务线，2026-08-16）

跑生产配置（turbo v4 LoRA 8 步 @ 1024×576，int8 DiT）两次：
  plain = UNETLoader → (scheduler+guider) 直连（无注意力 patch）
  sage  = UNETLoader → PathchSageAttentionKJ → (scheduler+guider)
从服务端日志窗口提取：采样耗时（进度条 elapsed）+ 各模型加载标记 + 总耗时，
补全两阶段收益模型里缺失的「sage 采样真实值」。

用法（标准库 python3）：
  python3 /home/sean/projects/comfy-ops/scripts/h3_sage_breakdown.py
"""
import json, os, re, sys, time, urllib.request

HOST = "http://127.0.0.1:8188"
LOG = "/tmp/comfyui_start.log"


def _post(path, data):
    req = urllib.request.Request(HOST + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def load_wf(path):
    with open(path) as f:
        return json.load(f)


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


def urllib_request_get(path):
    with urllib.request.urlopen(HOST + path, timeout=30) as r:
        return json.loads(r.read())


def log_offset():
    try:
        with open(LOG, "rb") as f:
            f.seek(0, 2)
            return f.tell()
    except OSError:
        return 0


def read_window(start):
    try:
        with open(LOG, "rb") as f:
            f.seek(start)
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def parse_window(text):
    """采样耗时（进度条最大 elapsed）+ 模型加载标记。"""
    # 进度条形如 "100%|...| 8/8 [00:25<00:00, 3.16s/it]"，取最大 elapsed（采样段）
    elapsed = []
    for m in re.finditer(r"\[(\d+):(\d+)<", text):
        elapsed.append(int(m.group(1)) * 60 + int(m.group(2)))
    sampling = max(elapsed) if elapsed else None
    markers = {
        "TE 加载": text.count("Requested to load MiniMaxH3TEModel_"),
        "DiT 加载": text.count("Requested to load MiniMaxH3\n") + text.count("Requested to load MiniMaxH3 prepared"),
        "LoRA 加载": text.count("lora") > 0,
        "VAE 解码": text.count("Requested to load MiniMaxH3VideoVAE"),
    }
    m = re.search(r"Prompt executed in ([\d.]+) seconds", text)
    prompt_exec = float(m.group(1)) if m else None
    return sampling, markers, prompt_exec


def run(tag, wf_path):
    print(f"\n== {tag} ==")
    _post("/free", {"unload_models": True, "free_memory": True})
    time.sleep(3)
    off = log_offset()
    pid = _post("/prompt", {"prompt": load_wf(wf_path)})["prompt_id"]
    entry, dt = wait(pid)
    text = read_window(off)
    sampling, markers, prompt_exec = parse_window(text)
    print(f"  总耗时(wait): {dt:.1f}s | 日志 Prompt executed: {prompt_exec}s")
    print(f"  采样段(进度条): {sampling}s" if sampling else "  采样段: 未解析到")
    print(f"  标记: TE加载={markers['TE 加载']} DiT加载={markers['DiT 加载']} VAE解码={markers['VAE 解码']}")
    return dt, sampling, prompt_exec


def main():
    base = "/home/sean/projects/comfy-ops/workflows"
    r_plain = run("plain（无注意力 patch）", f"{base}/attn3way_dance_plain.json")
    r_sage = run("sage（PathchSageAttentionKJ 节点）", f"{base}/attn3way_dance_sage.json")
    print("\n== 对比 ==")
    for tag, r in (("plain", r_plain), ("sage", r_sage)):
        dt, smp, pe = r
        print(f"  {tag}: 总 {dt:.1f}s / 采样 {smp}s / 日志 {pe}s")
    if r_plain[1] and r_sage[1]:
        print(f"  sage 采样加速: {r_plain[1]/r_sage[1]:.2f}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
