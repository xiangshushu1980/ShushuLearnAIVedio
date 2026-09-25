#!/usr/bin/env python3
"""多线程分片下载 HuggingFace 大文件（直连，失败重试）。

用法: python3 h3_download.py <url> <output> [threads] [chunk_mb]
"""
import os, sys, threading, time, urllib.request

URL = open(sys.argv[1]).read().strip() if sys.argv[1].endswith(".txt") else sys.argv[1]
OUT = sys.argv[2]
THREADS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
CHUNK = int(sys.argv[4]) if len(sys.argv) > 4 else 4  # MB per segment
SEG = CHUNK * 1024 * 1024

def get_size():
    req = urllib.request.Request(URL, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        return int(r.headers["Content-Length"])

def fetch(part, lo, hi):
    for attempt in range(5):
        try:
            req = urllib.request.Request(URL, headers={"Range": f"bytes={lo}-{hi}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(f"{OUT}.part{part}", "wb") as f:
                f.write(data)
            return
        except Exception as e:
            time.sleep(3 * (attempt + 1))
            if attempt == 4:
                print(f"FAIL part{part}: {e}", flush=True)

def main():
    size = get_size()
    total_seg = (size + SEG - 1) // SEG
    print(f"size={size/1e6:.0f}MB segments={total_seg} threads={THREADS}", flush=True)
    threads = []
    for i in range(total_seg):
        lo, hi = i * SEG, min((i + 1) * SEG - 1, size - 1)
        t = threading.Thread(target=fetch, args=(i, lo, hi))
        t.start()
        threads.append(t)
        if len(threads) >= THREADS:
            for t in threads: t.join()
            threads = []
    for t in threads: t.join()
    # merge
    with open(OUT, "wb") as out:
        for i in range(total_seg):
            with open(f"{OUT}.part{i}", "rb") as p:
                out.write(p.read())
            os.remove(f"{OUT}.part{i}")
    got = os.path.getsize(OUT)
    print(f"DONE {OUT} {got/1e6:.0f}MB {'OK' if got == size else 'SIZE-MISMATCH'}", flush=True)

if __name__ == "__main__":
    main()
