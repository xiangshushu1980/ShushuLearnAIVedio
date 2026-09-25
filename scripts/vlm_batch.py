#!/usr/bin/env python3
"""批量图片/PDF 视觉识别脚本 — 调 LM Studio 本地 VLM (qwen3.6-35b-a3b-mtp)

用法:
  python vlm_batch.py <图片或PDF文件或目录>... [选项]

选项:
  --out DIR            输出目录 (默认: ./vlm_out, 按时间戳建子目录)
  --prompt TEXT        识别提示词 (默认: 详细描述图片内容, 中文)
  --model NAME         模型 (默认: qwen3.6-35b-a3b-mtp)
  --base-url URL       API 地址 (默认: http://127.0.0.1:12134/v1)
  --max-tokens N       输出上限 (默认: 2048)
  --pdf-dpi N          PDF 转图 DPI (默认: 150)
  --pdf-max-pages N    PDF 最多识别页数 (默认: 50)
  --ext EXT            图片扩展名, 可多次 (默认: png jpg jpeg webp bmp)
  --retry N            失败重试次数 (默认: 2)
  --json               输出 JSON 汇总 (默认 markdown 汇总)

示例:
  python vlm_batch.py ~/pics/photo.png
  python vlm_batch.py ~/docs/manual.pdf --prompt "提取文档中的关键信息, 结构化输出"
  python vlm_batch.py ~/pics/ --json
"""
import argparse, base64, json, os, sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import urllib.request
except ImportError:
    pass

def render_pdf(pdf_path: Path, out_dir: Path, dpi: int, max_pages: int):
    """PDF 每页渲染为 PNG, 返回图片路径列表 (路径含页码, 供结果合并)."""
    import pymupdf
    doc = pymupdf.open(pdf_path)
    total = min(doc.page_count, max_pages)
    pages = []
    for i in range(total):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=dpi)
        img = out_dir / f"{pdf_path.stem}_p{i+1:03d}.png"
        pix.save(img)
        pages.append((i + 1, img))
    doc.close()
    return pages

def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()

def ask_model(base_url, model, prompt, image_b64, max_tokens, retry):
    payload = {
        "model": model,
        "reasoning_effort": "none",          # 关思考, 图片识别不需要
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
        ]}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    url = base_url.rstrip("/") + "/chat/completions"
    last_err = None
    for attempt in range(retry + 1):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            content = d["choices"][0]["message"]["content"]
            usage = d.get("usage", {})
            return content, usage
        except Exception as e:
            last_err = e
            if attempt < retry:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"请求失败: {last_err}")

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("inputs", nargs="+", help="文件或目录")
    ap.add_argument("--out", default=None)
    ap.add_argument("--prompt", default="请详细描述这张图片的内容：画面里有什么、什么风格、构图、颜色、光线。用中文回答。")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-mtp")
    ap.add_argument("--base-url", default="http://127.0.0.1:12134/v1")
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--pdf-dpi", type=int, default=150)
    ap.add_argument("--pdf-max-pages", type=int, default=50)
    ap.add_argument("--ext", action="append", default=[], help="图片扩展名")
    ap.add_argument("--retry", type=int, default=2)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    exts = {e.lower().lstrip(".") for e in (args.ext or ["png", "jpg", "jpeg", "webp", "bmp"])}
    if args.out:
        out_root = Path(args.out)
    else:
        out_root = Path("vlm_out") / time.strftime("%Y%m%d_%H%M%S")
    out_root.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_root / "_pages"
    tmp_dir.mkdir(exist_ok=True)

    # 收集任务: (label, image_path)
    tasks = []
    for inp in args.inputs:
        p = Path(inp)
        if p.is_dir():
            for f in sorted(p.iterdir()):
                if f.suffix.lower().lstrip(".") in exts:
                    tasks.append((f.stem, f))
        elif p.is_file():
            if p.suffix.lower() == ".pdf":
                pages = render_pdf(p, tmp_dir, args.pdf_dpi, args.pdf_max_pages)
                tasks.extend((f"{p.stem}_p{pn:03d}", img) for pn, img in pages)
                print(f"[pdf] {p.name}: {len(pages)} 页 -> {len(pages)} 张图")
            elif p.suffix.lower().lstrip(".") in exts:
                tasks.append((p.stem, p))
            else:
                print(f"[skip] 不支持的类型: {p}")

    if not tasks:
        print("没有可识别的文件")
        sys.exit(1)

    print(f"共 {len(tasks)} 个任务, 模型 {args.model} (reasoning_effort=none)")
    results = []
    t0 = time.time()
    for i, (label, img) in enumerate(tasks, 1):
        ts = time.time()
        try:
            content, usage = ask_model(args.base_url, args.model, args.prompt,
                                       encode_image(img), args.max_tokens, args.retry)
            results.append({"file": str(img), "label": label, "ok": True,
                            "content": content, "usage": usage})
            status = f"[{i}/{len(tasks)}] {label}: OK ({time.time()-ts:.1f}s, in={usage.get('prompt_tokens')}, out={usage.get('completion_tokens')})"
        except Exception as e:
            results.append({"file": str(img), "label": label, "ok": False, "error": str(e)})
            status = f"[{i}/{len(tasks)}] {label}: FAIL ({e})"
        print(status)

    # 汇总输出
    if args.json:
        out_file = out_root / "results.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"prompt": args.prompt, "results": results}, f, ensure_ascii=False, indent=2)
    else:
        out_file = out_root / "results.md"
        lines = [f"# VLM 批量识别结果", "", f"prompt: {args.prompt}", ""]
        for r in results:
            lines.append(f"## {r['label']}")
            lines.append(f"- file: {r['file']}")
            if r["ok"]:
                lines.append("")
                lines.append(r["content"])
            else:
                lines.append(f"- ERROR: {r['error']}")
            lines.append("")
        out_file.write_text("\n".join(lines), encoding="utf-8")

    ok = sum(1 for r in results if r["ok"])
    print(f"\n完成: {ok}/{len(results)} 成功, 总耗时 {time.time()-t0:.0f}s")
    print(f"结果文件: {out_file}")

if __name__ == "__main__":
    main()
