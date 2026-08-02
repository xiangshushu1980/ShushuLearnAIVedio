#!/usr/bin/env python3
"""
Pexels 视频素材批量下载脚本
用法:
  python3 pexels_download.py "woman dancing" --count 5 --quality hd --min-width 720 --out ../../ComfyUI/input/video_material
"""
import json, os, sys, time, urllib.request, urllib.parse, argparse, re

API_KEY = "VA4xzH96mrVZn7Nekf41gcB5ugfeLn18eD5UV0BDl96kDCx1t9fltYp7"
BASE = "https://api.pexels.com/videos/search"


UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def api_search(query, per_page, page=1):
    h = dict(UA)
    h["Authorization"] = API_KEY
    req = urllib.request.Request(f"{BASE}?query={urllib.parse.quote(query)}&per_page={per_page}&page={page}",
                                 headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return os.path.getsize(dest)


def pick_file(video, quality, min_width, max_width):
    """从 video_files 挑选合适的文件"""
    best = None
    for f in video.get("video_files", []):
        w = f.get("width") or 0
        q = (f.get("quality") or "").lower()
        # 匹配质量偏好
        if min_width and w < min_width:
            continue
        if max_width and (w > max_width):
            continue
        if quality == "hd" and q != "hd":
            continue
        if quality == "sd" and q != "sd":
            continue
        if best is None or w > best.get("width", 0):
            best = f
    # 若没有合适, 回退到最小可用(不会太大)
    if best is None:
        best = min(video.get("video_files", []), key=lambda f: f.get("width") or 0)
    return best


def slugify(text, maxlen=60):
    s = re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()
    return s[:maxlen]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--quality", choices=["hd", "sd"], default="hd")
    ap.add_argument("--min-width", type=int, default=0)
    ap.add_argument("--max-width", type=int, default=1280, help="跳过超过此宽度的文件(避免超大下载中断)")
    ap.add_argument("--out", default=".")
    ap.add_argument("--min-duration", type=float, default=0)
    ap.add_argument("--max-duration", type=float, default=30)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    tag = slugify(args.query)
    downloaded = 0
    page = 1

    print(f"搜索: '{args.query}' | 目标 {args.count} 个 | {args.quality} | min-width {args.min_width}")

    while downloaded < args.count:
        data = api_search(args.query, per_page=min(10, args.count * 2), page=page)
        videos = data.get("videos", [])
        if not videos:
            print("没有更多结果")
            break

        for v in videos:
            if downloaded >= args.count:
                break
            dur = v.get("duration", 0)
            if dur < args.min_duration or dur > args.max_duration:
                continue
            f = pick_file(v, args.quality, args.min_width, args.max_width)
            if not f or not f.get("link"):
                continue
            w, h = f.get("width", 0), f.get("height", 0)
            fname = f"{tag}_{v.get('id')}_{w}x{h}.mp4"
            dest = os.path.join(args.out, fname)
            if os.path.exists(dest) and os.path.getsize(dest) > 0:
                print(f"  已存在: {fname}")
                downloaded += 1
                continue
            print(f"  下载[{downloaded+1}/{args.count}] {fname} ({dur}s) ...", flush=True)
            try:
                size = download(f["link"], dest)
                if size == 0:
                    print(f"    ✗ 0字节, 删除")
                    os.remove(dest)
                else:
                    print(f"    ✓ {size/1e6:.1f}MB")
                    downloaded += 1
            except Exception as e:
                print(f"    ✗ 失败: {e}")
                if os.path.exists(dest) and os.path.getsize(dest) == 0:
                    os.remove(dest)
            time.sleep(0.5)

        page += 1
        time.sleep(1)  # Pexels 限流

    print(f"\n完成: 下载 {downloaded} 个视频到 {args.out}")


if __name__ == "__main__":
    main()
