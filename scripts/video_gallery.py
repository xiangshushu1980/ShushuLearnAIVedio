#!/usr/bin/env python3
"""
视频素材预览服务 - 独立 Web 页浏览 input/material 素材
用法: python3 video_gallery.py [--port 8000] [--input <ComfyUI input 路径>]
打开 http://127.0.0.1:8000 预览视频
"""
import os, sys, argparse, html, urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

INPUT_DIR = None  # ComfyUI/input 路径
ROOT_DIR = None   # 素材根目录(默认 input/material)

CATS = ["action", "portrait", "scene"]

def list_videos(subdir):
    """返回 {分类: [文件名]}"""
    base = os.path.join(ROOT_DIR, subdir)
    result = {}
    for cat in CATS:
        d = os.path.join(base, cat)
        if os.path.isdir(d):
            vids = sorted(f for f in os.listdir(d) if f.lower().endswith(('.mp4','.webm','.mov')))
            if vids:
                result[cat] = vids
    return result

def gallery_html():
    """生成素材库 HTML 页面"""
    material = list_videos("material")      # 原片
    material_b = list_videos("material_b")  # 预处理
    parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
             "<title>视频素材库</title>",
             "<style>body{font-family:sans-serif;margin:20px;background:#f5f5f5}",
             "h2{border-bottom:2px solid #ccc;padding-bottom:5px}",
             "h3{color:#555}",
             ".card{display:inline-block;margin:8px;padding:8px;background:#fff;border:1px solid #ddd;border-radius:6px;vertical-align:top}",
             "video{width:320px;height:180px;background:#000;border-radius:4px}",
             ".name{font-size:12px;margin-top:4px;max-width:320px;word-break:break-all}",
             ".banner{background:#eef;padding:10px;border-radius:6px;margin-bottom:15px}",
             "</style></head><body>",
             "<div class='banner'><b>视频素材库</b> | 原片: <code>material/</code> | Bernini预处理: <code>material_b/</code></div>"]

    def render_section(title, data):
        if not data:
            return ""
        s = [f"<h2>{title}</h2>"]
        for cat, files in data.items():
            s.append(f"<h3>{cat}/</h3>")
            for f in files:
                rel = f"media/{title}/{cat}/{urllib.parse.quote(f)}"
                s.append(f"<div class='card'><video controls src='{rel}'></video><div class='name'>{html.escape(f)}</div></div>")
        return "".join(s)

    parts.append(render_section("material", material))
    parts.append(render_section("material_b", material_b))
    parts.append("</body></html>")
    return "".join(parts)


class GalleryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            body = gallery_html().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def translate_path(self, path):
        """把 /media/<title>/<cat>/<file> 映射到对应磁盘目录"""
        if path.startswith("/media/"):
            # 格式: /media/material/action/<file> 或 /media/material_b/action/<file>
            rest = path[len("/media/"):].lstrip("/")
            # 前两段是 title/cat，剩余是文件名(可能含子路径)
            seg = rest.split("/", 2)
            if len(seg) >= 2:
                title, cat = seg[0], seg[1]
                fname = seg[2] if len(seg) > 2 else ""
                return os.path.join(ROOT_DIR, title, cat, urllib.parse.unquote(fname))
        # 静态(未用)走默认
        return super().translate_path(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--input", default=None, help="ComfyUI/input 绝对路径")
    args = ap.parse_args()

    global INPUT_DIR, ROOT_DIR
    if args.input:
        INPUT_DIR = args.input
    else:
        # 自动探测 ComfyUI input
        for cand in [os.path.expanduser("~/projects/ComfyUI/input"),
                     os.path.expanduser("~/ComfyUI/input")]:
            if os.path.isdir(cand):
                INPUT_DIR = cand
                break
    if not INPUT_DIR:
        print("找不到 ComfyUI/input，用 --input 指定")
        sys.exit(1)
    ROOT_DIR = INPUT_DIR

    os.chdir(INPUT_DIR)  # 让 media 相对路径可用
    srv = HTTPServer(("127.0.0.1", args.port), GalleryHandler)
    print(f"素材预览: http://127.0.0.1:{args.port}")
    print(f"素材根目录: {INPUT_DIR}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
