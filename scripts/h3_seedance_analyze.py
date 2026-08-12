#!/usr/bin/env python3
"""Seedance 经验验证 — 客观量化分析（帧差/运动/稳定性）+ 关键帧拼图
用法: python3 analyze.py <results.json>
输出: experiments/seedance_verify/analysis.json + compare_<case>.png（每 case 8 帧横条）
"""
import json
import os
import sys

import cv2
import numpy as np

OUT = "/home/sean/projects/ComfyUI/output"
ANALYZE = "/home/sean/projects/comfy-ops/experiments/seedance_verify"
N_FRAMES = 8  # 拼图帧数


def analyze(video_path):
    cap = cv2.VideoCapture(video_path)
    prev = None
    diffs = []
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idx = 0
    picks = sorted(set(int(i * (n - 1) / (N_FRAMES - 1)) for i in range(N_FRAMES)))
    tiles = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        g = cv2.resize(g, (192, 112))  # 统一小尺寸算帧差
        if prev is not None:
            diffs.append(float(np.mean(np.abs(g.astype(np.int16) - prev.astype(np.int16)))))
        prev = g
        if idx in picks:
            tiles.append(frame)
        idx += 1
    cap.release()
    d = np.array(diffs)
    osc = np.abs(np.diff(d))  # 帧差二阶差分：高频振荡（来回抖动）检测
    stats = {
        "frames": n,
        "mean_frame_diff": round(float(d.mean()), 2),
        "max_frame_diff": round(float(d.max()), 2),
        "std_frame_diff": round(float(d.std()), 2),
        "jumpy_frames_pct": round(float((d > 8).mean()) * 100, 1),  # 帧差>8 占比（剧烈变化）
        "osc_mean": round(float(osc.mean()), 2),        # 振荡均值（越高=越抖）
        "osc_high_pct": round(float((osc > 4).mean()) * 100, 1),  # 强振荡帧占比
        "motion_energy": round(float((d * d).sum()), 1),
    }
    return stats, tiles, d


def _save_curve(name, curve, w=800, h=200):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=100)
    ax.plot(curve, lw=1)
    ax.set_ylim(0, max(curve.max() * 1.1, 1))
    ax.set_title(name, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(ANALYZE, f"curve_{name}.png"))
    plt.close(fig)


def main():
    results = json.load(open(sys.argv[1]))
    analysis = {}
    for r in results:
        if r.get("error") or not r.get("video"):
            analysis[r["name"]] = {"error": r.get("error", "no video")}
            continue
        stats, tiles, curve = analyze(r["video"])
        analysis[r["name"]] = stats
        _save_curve(r["name"], curve)
        h = max(t.shape[0] for t in tiles)
        row = np.hstack([cv2.resize(t, (int(t.shape[1] * h / t.shape[0]), h)) for t in tiles])
        out_png = os.path.join(ANALYZE, f"compare_{r['name']}.png")
        cv2.imwrite(out_png, row)
    json.dump(analysis, open(os.path.join(ANALYZE, "analysis.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in analysis.items():
        if "error" in v:
            print(f"{k}: ❌ {v['error']}")
        else:
            print(f"{k}: mean={v['mean_frame_diff']} max={v['max_frame_diff']} "
                  f"std={v['std_frame_diff']} jumpy%={v['jumpy_frames_pct']} "
                  f"osc={v['osc_mean']} osc_high%={v['osc_high_pct']} motion={v['motion_energy']}")


if __name__ == "__main__":
    main()
