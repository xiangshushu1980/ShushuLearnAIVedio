#!/usr/bin/env python3
"""双轨盲区补测后处理：客观指标提取（2026-08-09 h3-prompt-agent）

对每个 case 产物:
- ffprobe: 时长/分辨率/帧率/码率
- ffmpeg volumedetect: mean_volume / max_volume（音频响度, dB）
- 文件大小
帧链分析（若提供 --chain A2 C2）:
- A2 产物末帧 vs C2 产物首帧 → MSE/SSIM（跨段连续性客观代理）

用法: python3 h3_gap_analyze.py <results.json> [--chain <src_case> <dst_case>] [--out <md>]
"""
import json, os, subprocess, sys

def ffprobe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=width,height,r_frame_rate,codec_name,codec_type",
        "-of", "json", path], capture_output=True, text=True)
    return json.loads(r.stdout)

def volume(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af", "volumedetect",
        "-f", "null", "-"], capture_output=True, text=True)
    out = r.stderr
    mean = None; mx = None
    for line in out.splitlines():
        if "mean_volume" in line: mean = line.split(":")[1].strip().split(" ")[0]
        if "max_volume" in line: mx = line.split(":")[1].strip().split(" ")[0]
    return mean, mx

def frame(path, index_or_last, out_png):
    """index_or_last: int 帧号或 'last'"""
    if index_or_last == "last":
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
            "-count_frames", "-show_entries", "stream=nb_read_frames",
            "-of", "csv=p=0", path], capture_output=True, text=True)
        n = int(r.stdout.strip() or 0) or 120
        expr = f"eq(n\\,{n-1})"
    else:
        expr = f"eq(n\\,{index_or_last})"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
        "-vf", f"select={expr}", "-frames:v", "1", out_png], check=True)

def img_metrics(a, b):
    from PIL import Image
    import math
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    # 统一尺寸
    w, h = min(ia.size[0], ib.size[0]), min(ia.size[1], ib.size[1])
    ia, ib = ia.resize((w, h)), ib.resize((w, h))
    pa, pb = list(ia.getdata()), list(ib.getdata())
    n = len(pa)
    mse = sum(sum((x - y) ** 2 for x, y in zip(pa[i], pb[i])) for i in range(n)) / (n * 3)
    # SSIM 简化版（亮度+对比度+结构，窗口=全图）
    def stats(px):
        vals = [v for p in px for v in p]
        mu = sum(vals) / len(vals)
        var = sum((v - mu) ** 2 for v in vals) / len(vals)
        return mu, var
    ma, va = stats(pa); mb, vb = stats(pb)
    cov = sum(sum((pa[i][k] - ma) * (pb[i][k] - mb) for k in range(3)) for i in range(n)) / (n * 3)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * ma * mb + c1) * (2 * cov + c2)) / ((ma**2 + mb**2 + c1) * (va + vb + c2))
    return mse, ssim

def main():
    results = json.load(open(sys.argv[1]))
    chain = None
    if "--chain" in sys.argv:
        i = sys.argv.index("--chain")
        chain = (sys.argv[i + 1], sys.argv[i + 2])
    out_md = None
    if "--out" in sys.argv:
        out_md = sys.argv[sys.argv.index("--out") + 1]

    rows = []
    for r in results:
        v = r.get("video")
        if not v or r.get("error"):
            rows.append({"name": r["name"], "seconds": r.get("seconds"), "error": r.get("error")})
            continue
        try:
            p = ffprobe(v)
            vs = [s for s in p["streams"] if s["codec_type"] == "video"][0]
            mean, mx = volume(v)
            dur = float(p["format"]["duration"])
            size_mb = float(p["format"]["size"]) / 1048576
            rows.append({
                "name": r["name"], "seconds": r.get("seconds"), "peak_vram_gb": r.get("peak_vram_gb"),
                "dur_s": round(dur, 2), "res": f"{vs['width']}x{vs['height']}",
                "fps": vs.get("r_frame_rate"), "mean_vol_db": mean, "max_vol_db": mx,
                "size_mb": round(size_mb, 1),
            })
        except Exception as e:
            rows.append({"name": r["name"], "seconds": r.get("seconds"), "error": f"analyze: {e}"})

    lines = ["| case | 耗时s | 显存峰值GB | 时长s | 分辨率 | 帧率 | mean dB | max dB | 大小MB |", "|---|---|---|---|---|---|---|---|---|"]
    for x in rows:
        if x.get("error"):
            lines.append(f"| {x['name']} | {x.get('seconds','?')} | - | - | - | - | - | - | ❌ {x['error'][:50]} |")
        else:
            lines.append(f"| {x['name']} | {x['seconds']} | {x.get('peak_vram_gb')} | {x['dur_s']} | {x['res']} | {x['fps']} | {x['mean_vol_db']} | {x['max_vol_db']} | {x['size_mb']} |")
    out = "\n".join(lines)
    print(out)

    if chain:
        src, dst = chain
        s = next((x for x in results if x["name"] == src), None)
        d = next((x for x in results if x["name"] == dst), None)
        if not s or not d or not s.get("video") or not d.get("video"):
            print(f"\n帧链分析: 缺产物 {src}/{dst}")
        else:
            fa = "/tmp/gap_chain_a.png"; fb = "/tmp/gap_chain_b.png"
            frame(s["video"], "last", fa)
            frame(d["video"], 0, fb)
            mse, ssim = img_metrics(fa, fb)
            print(f"\n帧链 {src}末帧 vs {dst}首帧: MSE={mse:.1f} SSIM={ssim:.3f}（SSIM 0.9+≈视觉几乎相同, 0.7-0.9=连续性好, <0.6=有明显跳变）")
            print(f"帧图: {fa} / {fb}")

    if out_md:
        with open(out_md, "w") as f:
            f.write("# 19 H3 双轨盲区补测（2026-08-09）\n\n> 数据来源: /tmp/h3_gap_cases.json + results.json\n\n## 速度/显存/产物表\n\n")
            f.write(out + "\n")
            if chain:
                f.write(f"\n## 帧链分析\n\n{src} 末帧 vs {dst} 首帧: MSE/SSIM 见上\n")
        print(f"\n已写: {out_md}")

if __name__ == "__main__":
    main()
