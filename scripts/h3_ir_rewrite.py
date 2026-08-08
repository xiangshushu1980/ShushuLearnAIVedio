#!/usr/bin/env python3
"""H3-Context-IR 提示词增强脚本（CN 平台 platform.minimaxi.com）

流程：上传本地素材（mm_file 引用）→ 创建 IR 任务 → 轮询 → 输出六段式/三核心段增强提示词。
用法：
  # 纯文本（t2va）
  python3 scripts/h3_ir_rewrite.py --text "一只橘猫在窗台晒太阳" --duration 5 --ratio 16:9

  # 图生视频（首帧/尾帧，i2va）
  python3 scripts/h3_ir_rewrite.py --text "猫站起来伸懒腰" --duration 5 \
      --image first_frame=/path/start.png

  # 多模态参考（r2va，参考图/视频/音频可组合）
  python3 scripts/h3_ir_rewrite.py --text "保持人物形象，做一段海边散步" --duration 5 \
      --image reference_image=/path/char.png --video /path/ref.mp4 --audio /path/bgm.mp3

Key 位置：~/.config/minimax_key（明文，不进 git）
"""
import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

API_BASE = "https://api.minimaxi.com"
UPLOAD_URL = f"{API_BASE}/v1/files/upload"
IR_URL = f"{API_BASE}/v2/h3_context_ir"
QUERY_URL = f"{API_BASE}/v2/query/video_generation/{{task_id}}"

KEY_FILE = Path.home() / ".config" / "minimax_key"
POLL_INTERVAL = 3  # s
POLL_TIMEOUT = 300  # s


def get_key() -> str:
    if not KEY_FILE.exists():
        sys.exit(f"缺少 API key：请写入 {KEY_FILE}")
    key = KEY_FILE.read_text().strip()
    if not key:
        sys.exit(f"API key 为空：{KEY_FILE}")
    return key


def upload_file(key: str, path: str) -> str:
    """上传素材到平台，返回 mm_file://{file_id} 引用（有效期 7 天）。"""
    p = Path(path)
    if not p.exists():
        sys.exit(f"文件不存在: {path}")
    size_mb = p.stat().st_size / 1024 / 1024
    print(f"[upload] {p.name} ({size_mb:.1f}MB) ...", flush=True)
    with p.open("rb") as f:
        resp = requests.post(
            UPLOAD_URL,
            headers={"Authorization": f"Bearer {key}"},
            files={"file": (p.name, f)},
            data={"purpose": "video_generation_input"},
            timeout=120,
        )
    resp.raise_for_status()
    data = resp.json()
    base = data.get("base_resp", {})
    if base.get("status_code") != 0:
        sys.exit(f"[upload] 失败: {base.get('status_msg', data)}")
    file_id = data.get("file_id") or data.get("file", {}).get("file_id")
    if not file_id:
        sys.exit(f"[upload] 响应缺 file_id: {data}")
    print(f"[upload] OK -> mm_file://{file_id}", flush=True)
    return f"mm_file://{file_id}"


def create_ir_task(key: str, content: list, duration: int, ratio: str) -> str:
    body = {"model": "MiniMax-H3", "content": content, "duration": duration}
    if ratio:
        body["ratio"] = ratio
    resp = requests.post(
        IR_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=body,
        timeout=60,
    )
    data = resp.json()
    if resp.status_code != 200:
        err = data.get("error", {})
        sys.exit(f"[IR] 提交失败 HTTP {resp.status_code}: {err.get('type')} {err.get('message')}")
    task_id = data.get("task_id")
    if not task_id:
        sys.exit(f"[IR] 响应缺 task_id: {data}")
    print(f"[IR] 任务已创建: {task_id}", flush=True)
    return task_id


def poll_task(key: str, task_id: str, timeout: int = POLL_TIMEOUT) -> dict:
    url = QUERY_URL.format(task_id=task_id)
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        task = data.get("task", {})
        status = task.get("status")
        print(f"[IR] 状态: {status}", flush=True)
        if status == "succeeded":
            return task
        if status in ("failed", "cancelled"):
            sys.exit(f"[IR] 任务{status}: {json.dumps(data, ensure_ascii=False)[:500]}")
        time.sleep(POLL_INTERVAL)
    sys.exit(f"[IR] 轮询超时（>{timeout}s）")


def main():
    ap = argparse.ArgumentParser(description="H3-Context-IR 提示词增强")
    ap.add_argument("--text", required=True, help="目标视频描述（必填，非空 text 项）")
    ap.add_argument("--duration", type=int, default=5, help="目标时长 4-15s（默认 5）")
    ap.add_argument("--ratio", default="16:9",
                    help="宽高比 adaptive/21:9/16:9/4:3/1:1/3:4/9:16（t2va 必填非 adaptive）")
    ap.add_argument("--image", action="append", default=[],
                    help="图片素材，格式 role=path（role: first_frame/last_frame/reference_image；可多次）")
    ap.add_argument("--video", action="append", default=[], help="参考视频路径（可多次，≤3）")
    ap.add_argument("--audio", action="append", default=[], help="参考音频路径（可多次，≤3）")
    ap.add_argument("--output", help="增强提示词落盘路径（不填则打印到 stdout）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将提交的 content，不调 API")
    args = ap.parse_args()

    # 组装 content（媒体为嵌套结构：{type, <type>:{url}, role}，官方脚本格式）
    content = [{"type": "text", "text": args.text}]
    for item in args.image:
        role, _, path = item.partition("=")
        if not path:
            role, path = "first_frame", item  # 单图默认首帧
        content.append({"type": "image_url", "role": role, "image_url": {"url": path}})
    for path in args.video:
        content.append({"type": "video_url", "role": "reference_video", "video_url": {"url": path}})
    for path in args.audio:
        content.append({"type": "audio_url", "role": "reference_audio", "audio_url": {"url": path}})

    # 本地文件先上传（mm_file:// 引用；URL 原样透传）
    for item in content:
        if item["type"] == "text":
            continue
        holder = item[item["type"]]  # image_url / video_url / audio_url 对象
        url = holder["url"]
        if url.startswith(("http://", "https://", "mm_file://")):
            continue
        key = get_key()
        holder["url"] = upload_file(key, url)

    if args.dry_run:
        print(json.dumps(content, ensure_ascii=False, indent=2))
        return

    key = get_key()
    task_id = create_ir_task(key, content, args.duration, args.ratio)
    task = poll_task(key, task_id)
    prompt = task.get("content", {}).get("prompt")
    if not prompt:
        sys.exit(f"[IR] 成功但无 content.prompt: {json.dumps(task, ensure_ascii=False)[:500]}")

    usage = task.get("usage", {})
    print(f"[IR] 完成（tokens: {usage.get('total_tokens')}）", flush=True)
    if args.output:
        out = Path(args.output)
        out.write_text(prompt, encoding="utf-8")
        print(f"[IR] 提示词已写入 {out}（{len(prompt)} 字符）")
    else:
        print("=" * 60)
        print(prompt)
        print("=" * 60)


if __name__ == "__main__":
    main()
