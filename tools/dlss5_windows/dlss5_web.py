"""Local Windows web service for browsing ComfyUI videos and running DLSS5."""

from __future__ import annotations

import hashlib
import ctypes
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
APP_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "comfy-ops" / "dlss5"
CONFIG_PATH = APP_DIR / "web.json"
PID_PATH = APP_DIR / "web.pid"
THUMB_DIR = APP_DIR / "thumbs"


def wsl_distro() -> str:
    try:
        result = subprocess.run(["wsl.exe", "-l", "-q"], capture_output=True, text=True, timeout=5)
        names = [line.replace("\x00", "").strip() for line in result.stdout.splitlines() if line.replace("\x00", "").strip()]
        return names[0] if names else "Ubuntu"
    except (OSError, subprocess.SubprocessError):
        return "Ubuntu"


def default_video_dir() -> str:
    return os.environ.get("COMFYUI_VIDEO_DIR", rf"\\wsl$\{wsl_distro()}\home\sean\projects\ComfyUI\output\video")


def find_engine_root() -> str:
    configured = os.environ.get("VIDEO2DLSSNR_ROOT", "")
    candidates = [configured, r"D:\dlss5\video2dlssnr", r"C:\dlss5\video2dlssnr",
                  str(Path.home() / "dlss5" / "video2dlssnr"), str(Path.home() / "Downloads" / "video2dlssnr"),
                  str(Path.home() / "Desktop" / "video2dlssnr")]
    for candidate in candidates:
        if candidate and (Path(candidate) / "nr_video.py").exists():
            return candidate
    return configured


def find_engine_python(root: str) -> str:
    configured = os.environ.get("VIDEO2DLSSNR_PYTHON", "")
    if root:
        for relative in (r".venv\Scripts\python.exe", r"venv\Scripts\python.exe", r"python_embeded\python.exe"):
            candidate = Path(root) / relative
            if candidate.exists():
                return str(candidate)
    return configured or sys.executable


def default_config() -> dict:
    root = find_engine_root()
    return {"video_dir": default_video_dir(), "engine_root": root, "engine_python": find_engine_python(root),
            "output_dir": str(Path.home() / "Videos" / "DLSS5-enhanced"), "style": 1, "preset": 0,
            "scale": 1.0, "adapter": 1, "intensity": 0.7, "detail": 0.7, "codec": "hevc_nvenc", "cq": 19, "bit_depth": 10}


def load_config() -> dict:
    config = default_config()
    try:
        config.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        pass
    return config


CONFIG = load_config()
STATE = {"running": False, "input": "", "output": "", "status": "就绪", "phase": "idle", "progress": None,
         "returncode": None, "log": [], "pid": None}
PROCESS: subprocess.Popen[str] | None = None
STOP_REQUESTED = False
STATE_LOCK = threading.Lock()


def save_config() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")


def video_root() -> Path:
    return Path(CONFIG["video_dir"])


def safe_video_path(relative: str) -> Path:
    root = video_root().resolve()
    candidate = (root / unquote(relative)).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("视频路径不在配置的 ComfyUI video 目录内")
    if candidate.suffix.lower() not in VIDEO_EXTENSIONS:
        raise ValueError("不是支持的视频格式")
    return candidate


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(video_root().resolve()).as_posix()


def list_videos() -> list[dict]:
    root = video_root()
    if not root.exists():
        return []
    result = []
    for path in root.rglob("*"):
        try:
            if not path.is_file() or path.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            stat = path.stat()
            rel = relative_path(path)
            result.append({"path": rel, "name": path.name, "size": stat.st_size, "mtime": stat.st_mtime,
                           "url": "/media?path=" + quote(rel, safe="/")})
        except OSError:
            continue
    return sorted(result, key=lambda item: item["mtime"], reverse=True)


def ffmpeg_path() -> str | None:
    root = Path(CONFIG.get("engine_root", ""))
    candidates = [shutil.which("ffmpeg"), str(root / "out" / "ffmpeg.exe"),
                  str(root / "bin" / "ffmpeg" / "bin" / "ffmpeg.exe"), str(root / "ffmpeg" / "bin" / "ffmpeg.exe")]
    return next((item for item in candidates if item and Path(item).exists()), None)


def thumbnail_path(video: Path) -> Path:
    stat = video.stat()
    key = hashlib.sha256(f"{video}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()
    return THUMB_DIR / f"{key}.jpg"


def make_thumbnail(video: Path) -> Path:
    target = thumbnail_path(video)
    if target.exists():
        return target
    ffmpeg = ffmpeg_path()
    if not ffmpeg:
        raise FileNotFoundError("找不到 ffmpeg，无法生成缩略图")
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp.jpg")
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", "00:00:01", "-i", str(video),
               "-frames:v", "1", "-vf", "scale=360:-2", "-y", str(temp)]
    subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    if not temp.exists():
        raise RuntimeError("ffmpeg 未能生成缩略图")
    os.replace(temp, target)
    return target


def output_for(video: Path) -> Path:
    root = Path(CONFIG["output_dir"])
    rel = video.resolve().relative_to(video_root().resolve())
    return root / rel.parent / f"{rel.stem}.dlss5{rel.suffix.lower()}"


def output_for_relative(relative: str) -> Path:
    rel = Path(unquote(relative).replace("/", os.sep))
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() not in VIDEO_EXTENSIONS:
        raise ValueError("结果路径无效")
    return Path(CONFIG["output_dir"]) / rel.parent / f"{rel.stem}.dlss5{rel.suffix.lower()}"


def build_command(video: Path, output: Path) -> list[str]:
    engine = Path(CONFIG["engine_root"])
    return [CONFIG.get("engine_python") or sys.executable, str(engine / "nr_video.py"), "--in", str(video), "--out", str(output),
            "--nr-scale", str(CONFIG["scale"]), "--adapter", str(CONFIG.get("adapter", 1)), "--nr-style", str(CONFIG["style"]), "--nr-preset", str(CONFIG["preset"]),
            "--nr-intensity", str(CONFIG["intensity"]), "--nr-detail", str(CONFIG["detail"]), "--nr-color", "0",
            "--nr-sr-preset", "default", "--codec", CONFIG["codec"], "--cq", str(CONFIG["cq"]), "--bit-depth", str(CONFIG["bit_depth"])]


def append_state_log(line: str) -> None:
    with STATE_LOCK:
        STATE["log"].append(line.rstrip())
        STATE["log"] = STATE["log"][-200:]
        percent = re.search(r"(?:^|\s)(\d{1,3}(?:\.\d+)?)%", line)
        if percent:
            STATE["progress"] = min(100.0, float(percent.group(1)))
        frames = re.search(r"(?:frame|frames|帧)\s*[:=]?\s*(\d+)\s*/\s*(\d+)", line, re.I)
        if frames and int(frames.group(2)):
            STATE["progress"] = min(100.0, int(frames.group(1)) * 100.0 / int(frames.group(2)))


def process_video(video: Path) -> None:
    global PROCESS, STOP_REQUESTED
    output = output_for(video)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = build_command(video, output)
    with STATE_LOCK:
        STOP_REQUESTED = False
        STATE.update({"running": True, "input": relative_path(video), "output": str(output), "status": "启动处理中…", "phase": "starting", "progress": 0.0, "returncode": None,
                      "log": ["> " + " ".join(command)]})
    try:
        PROCESS = subprocess.Popen(command, cwd=str(Path(CONFIG["engine_root"])), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace", bufsize=1)
        with STATE_LOCK:
            STATE["pid"] = PROCESS.pid
            STATE["status"] = "处理中…"
            STATE["phase"] = "processing"
        assert PROCESS.stdout is not None
        for line in PROCESS.stdout:
            append_state_log(line)
        returncode = PROCESS.wait()
        with STATE_LOCK:
            stopped = STOP_REQUESTED
            STATE.update({"running": False, "phase": "stopped" if stopped else ("completed" if returncode == 0 and output.exists() else "failed"), "returncode": returncode,
                          "progress": 100.0 if returncode == 0 and output.exists() else STATE.get("progress"),
                          "status": "已停止" if stopped else ("处理完成" if returncode == 0 and output.exists() else f"处理失败（{returncode}）"), "pid": None})
    except Exception as exc:
        append_state_log(f"[error] {exc}")
        with STATE_LOCK:
            STATE.update({"running": False, "phase": "failed", "status": "启动失败", "pid": None})
    finally:
        PROCESS = None


def stop_process() -> None:
    global STOP_REQUESTED
    if PROCESS is None:
        return
    STOP_REQUESTED = True
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(PROCESS.pid), "/T", "/F"], capture_output=True, text=True)
    else:
        PROCESS.terminate()


def open_folder(kind: str) -> Path:
    paths = {"video": Path(CONFIG["video_dir"]), "output": Path(CONFIG["output_dir"]),
             "engine": Path(CONFIG.get("engine_root", ""))}
    if kind not in paths:
        raise ValueError("未知目录类型")
    path = paths[kind]
    if not str(path):
        raise ValueError("目录尚未配置")
    if kind == "engine" and not path.exists():
        raise FileNotFoundError("引擎目录不存在，请先配置 engine_root")
    if kind == "video" and not path.exists():
        raise FileNotFoundError("视频目录不存在，请检查 video_dir")
    if kind == "output":
        path.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        raise OSError("打开文件夹功能需要在 Windows Python 中运行")
    subprocess.Popen(["explorer.exe", str(path)])
    # Explorer may open behind the browser when launched from a local web request.
    # Bring the newly opened Cabinet window to the foreground after its shell view exists.
    def focus_explorer() -> None:
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW("CabinetWClass", None)
            if hwnd:
                user32.ShowWindow(hwnd, 5)
                user32.SetForegroundWindow(hwnd)
        except (AttributeError, OSError):
            pass
    threading.Timer(0.35, focus_explorer).start()
    return path


class Handler(BaseHTTPRequestHandler):
    server_version = "ComfyOpsDLSS5/1.0"

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/":
                body = (WEB_DIR / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/api/videos":
                self.send_json({"root": str(video_root()), "videos": list_videos()})
            elif parsed.path == "/api/config":
                self.send_json(CONFIG)
            elif parsed.path == "/api/status":
                with STATE_LOCK:
                    self.send_json(dict(STATE))
            elif parsed.path == "/thumb":
                body = make_thumbnail(safe_video_path(query.get("path", [""])[0])).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/media":
                self.serve_media(safe_video_path(query.get("path", [""])[0]))
            elif parsed.path == "/result":
                self.serve_media(output_for_relative(query.get("path", [""])[0]))
            elif parsed.path == "/api/result":
                relative = query.get("path", [""])[0]
                result = output_for_relative(relative)
                self.send_json({"exists": result.exists(), "path": str(result),
                                "url": "/result?path=" + quote(unquote(relative), safe="/")})
            else:
                self.send_error(404)
        except FileNotFoundError as exc:
            self.send_json({"error": str(exc)}, 404)
        except (ValueError, OSError, RuntimeError) as exc:
            self.send_json({"error": str(exc)}, 400)

    def serve_media(self, path: Path) -> None:
        if not path.exists():
            self.send_error(404)
            return
        size = path.stat().st_size
        start, end = 0, size - 1
        header = self.headers.get("Range")
        if header and header.startswith("bytes="):
            value = header[6:].split(",", 1)[0]
            left, right = (value.split("-", 1) + [""])[:2]
            start = int(left) if left else max(0, size - int(right))
            end = int(right) + start if left and right else min(size - 1, start + 4 * 1024 * 1024 - 1)
            end = min(end, size - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        length = max(0, end - start + 1)
        self.send_header("Content-Type", mimetypes.guess_type(str(path))[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        with path.open("rb") as source:
            source.seek(start)
            remaining = length
            while remaining:
                chunk = source.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/api/config":
                CONFIG.update(payload)
                save_config()
                self.send_json({"ok": True, "config": CONFIG})
            elif self.path == "/api/process":
                with STATE_LOCK:
                    active = STATE["running"]
                if PROCESS is not None or active:
                    self.send_json({"error": "已有任务正在处理"}, 409)
                    return
                video = safe_video_path(payload.get("path", ""))
                if not Path(CONFIG.get("engine_root", ""), "nr_video.py").exists():
                    self.send_json({"error": "未找到 video2dlssnr/nr_video.py，请先设置引擎目录"}, 400)
                    return
                with STATE_LOCK:
                    STATE.update({"running": True, "input": relative_path(video), "output": str(output_for(video)),
                                  "status": "排队中…", "phase": "queued", "progress": 0.0, "returncode": None, "log": []})
                threading.Thread(target=process_video, args=(video,), daemon=True).start()
                self.send_json({"ok": True, "status": "排队中"})
            elif self.path == "/api/stop":
                stop_process()
                with STATE_LOCK:
                    if STATE["running"]:
                        STATE.update({"status": "正在停止…", "phase": "stopping"})
                self.send_json({"ok": True})
            elif self.path == "/api/open-folder":
                path = open_folder(str(payload.get("kind", "")))
                self.send_json({"ok": True, "path": str(path)})
            else:
                self.send_error(404)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)


def main() -> int:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PID_PATH.write_text(str(os.getpid()), encoding="ascii")
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("[dlss5] http://127.0.0.1:8765", flush=True)
    try:
        if "--no-browser" not in sys.argv:
            threading.Timer(0.7, lambda: webbrowser.open("http://127.0.0.1:8765")).start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_process()
        server.server_close()
        try:
            PID_PATH.unlink()
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
