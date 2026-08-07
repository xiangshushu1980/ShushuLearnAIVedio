#!/usr/bin/env python3
"""H3 A/B 测试提交：raw vs IR prompt，同 seed 同参数。
场景 A=温泉美人 / B=魔兽战斗；10s(240帧) 1024×576 20步 res_multistep/simple
"""
import json
import sys
import urllib.request
from pathlib import Path

BASE = json.load(open("/home/sean/projects/comfy-ops/workflows/minimax_h3_t2v_api.json"))
SEED = 20260808

CASES = [
    # (名字, prompt)
    ("A_raw", "年轻女性在日式温泉浴场享受水疗，白色水汽袅袅升腾，暖黄色灯光柔和，清水顺着肩颈流淌，氛围宁静唯美，镜头缓慢环绕拍摄"),
    ("A_ir", Path("/tmp/ir_ab_a.txt").read_text(encoding="utf-8")),
    ("B_raw", "魔兽世界风格战斗场景，兽人战士与人类圣骑士激烈对战，魔法特效华丽，刀光剑影，尘土飞扬，镜头快速移动跟拍"),
    ("B_ir", Path("/tmp/ir_ab_b.txt").read_text(encoding="utf-8")),
]


def submit(workflow) -> str:
    req = urllib.request.Request(
        "http://127.0.0.1:8188/prompt",
        data=json.dumps({"prompt": workflow}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["prompt_id"]


for name, prompt in CASES:
    wf = json.loads(json.dumps(BASE))  # deep copy
    wf["6"]["inputs"]["prompt"] = prompt
    wf["6"]["inputs"]["width"] = 1024
    wf["6"]["inputs"]["height"] = 576
    wf["6"]["inputs"]["length"] = 240
    wf["10"]["inputs"]["noise_seed"] = SEED
    wf["15"]["inputs"]["filename_prefix"] = f"video/h3_ab/{name}"
    pid = submit(wf)
    print(f"{name}: enqueued -> {pid}")
