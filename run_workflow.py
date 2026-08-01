#!/usr/bin/env python3
"""将 UI 格式工作流转换为 API 格式并提交到 ComfyUI 运行。"""
import json
import sys
import time
import urllib.request

SERVER = "http://127.0.0.1:8188"

# 每个节点类型的 widget 参数名顺序（对照节点定义）
WIDGET_NAMES = {
    "UNETLoader": ["unet_name", "weight_dtype"],
    "CLIPLoader": ["clip_name", "type", "device"],
    "VAELoader": ["vae_name"],
    "CLIPVisionLoader": ["clip_name"],
    "CLIPTextEncode": ["text"],
    "ModelSamplingSD3": ["shift"],
    "KSampler": ["seed", "control_after_generate", "steps", "cfg", "sampler_name", "scheduler", "denoise"],
    "WanImageToVideo": ["width", "height", "length", "batch_size"],
    "CLIPVisionEncode": ["crop"],
    "VAEDecode": [],
    "CreateVideo": ["fps"],
    "SaveVideo": ["filename_prefix", "format", "codec"],
    "LoadImage": ["image", "image_upload"],
}

UI_ONLY = {"control_after_generate", "image_upload"}


def build_api(workflow: dict) -> dict:
    """把 LiteGraph UI 工作流转换为 API 格式。"""
    node_map = {n["id"]: n for n in workflow["nodes"]}

    # 建立 link: id -> (src_node, src_slot, dst_node, dst_slot)
    links = {}
    for link in workflow.get("links", []):
        link_id, src, src_slot, dst, dst_slot, _ = link
        links[link_id] = (src, src_slot, dst, dst_slot)

    api = {}
    for node in workflow["nodes"]:
        nid = node["id"]
        ntype = node["type"]
        # 跳过纯 UI 注释节点
        if ntype == "MarkdownNote" or (not node.get("inputs") and not node.get("outputs")):
            continue
        api[str(nid)] = {"class_type": ntype, "inputs": {}}

        # 收集该节点的输入连接: 输入名 -> [src_node, src_slot]
        connected = {}
        for inp in node.get("inputs", []):
            link_id = inp.get("link")
            if link_id is not None and link_id in links:
                src, src_slot, _, _ = links[link_id]
                connected[inp["name"]] = [str(src), src_slot]

        api[str(nid)]["inputs"].update(connected)

        # widget 值按参数名顺序填充（UI 专用控件和已连接输入同样消费值，但不写入 API）
        widget_names = WIDGET_NAMES.get(ntype, [])
        widgets = list(node.get("widgets_values", []))
        wi = 0
        for wname in widget_names:
            if wi >= len(widgets):
                break
            if wname in UI_ONLY or wname in connected:
                wi += 1
                continue
            api[str(nid)]["inputs"][wname] = widgets[wi]
            wi += 1

    return api


def queue_prompt(prompt: dict) -> dict:
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(f"{SERVER}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode()}")


def get_history(prompt_id: str) -> dict:
    with urllib.request.urlopen(f"{SERVER}/history/{prompt_id}") as resp:
        return json.loads(resp.read())


def main():
    wf_path = sys.argv[1] if len(sys.argv) > 1 else "workflows/wan2.1_i2v_480p.json"
    with open(wf_path) as f:
        workflow = json.load(f)

    api = build_api(workflow)
    print(f"✅ 已转换 {len(api)} 个节点，提交任务...")

    result = queue_prompt(api)
    prompt_id = result["prompt_id"]
    print(f"✅ 任务已提交: {prompt_id}")

    # 轮询进度
    start = time.time()
    while True:
        time.sleep(5)
        try:
            hist = get_history(prompt_id)
        except Exception:
            continue
        if prompt_id in hist:
            status = hist[prompt_id].get("status", {})
            if status.get("completed"):
                elapsed = time.time() - start
                print(f"\n🎉 任务完成！耗时 {elapsed:.0f} 秒")
                for node_id, out in hist[prompt_id].get("outputs", {}).items():
                    print(f"  节点 {node_id}: {json.dumps(out, ensure_ascii=False)[:300]}")
                return
            if status.get("status_str") == "error":
                msgs = status.get("messages", [])
                for m in msgs:
                    if m[0] == "execution_error":
                        err = m[1]
                        print(f"\n❌ 错误: {err.get('exception_message', '')}")
                        print(f"   节点: {err.get('node_type')} ({err.get('node_id')})")
                        if err.get("traceback"):
                            print("   " + "".join(err["traceback"][-3:]).strip())
                return
        elapsed = time.time() - start
        print(f"⏳ 运行中... 已耗时 {elapsed:.0f}s", end="\r")


if __name__ == "__main__":
    main()
