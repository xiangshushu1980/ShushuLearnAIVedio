"""Small Windows Tk UI for browsing ComfyUI videos and running DLSS5."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from dataclasses import asdict, dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "comfy-ops" / "dlss5"
CONFIG_PATH = APP_DIR / "ui.json"


def default_video_dir() -> str:
    configured = os.environ.get("COMFYUI_VIDEO_DIR")
    if configured:
        return configured
    distro = os.environ.get("WSL_DISTRO_NAME", "")
    if not distro:
        try:
            result = subprocess.run(["wsl.exe", "-l", "-q"], capture_output=True, text=True, timeout=5)
            names = [line.replace("\x00", "").strip() for line in result.stdout.splitlines() if line.replace("\x00", "").strip()]
            distro = names[0] if names else "Ubuntu"
        except (OSError, subprocess.SubprocessError):
            distro = "Ubuntu"
    return rf"\\wsl$\{distro}\home\sean\projects\ComfyUI\output\video"


def default_output_dir() -> str:
    return os.environ.get("DLSS5_OUTPUT_DIR", str(Path.home() / "Videos" / "DLSS5-enhanced"))


@dataclass
class Settings:
    comfy_video: str = ""
    engine_root: str = ""
    engine_python: str = ""
    output_dir: str = ""
    style: int = 1
    preset: int = 0
    scale: float = 1.0
    intensity: float = 0.7
    detail: float = 0.7
    codec: str = "hevc_nvenc"
    cq: int = 19
    bit_depth: int = 10


def load_settings() -> Settings:
    values = asdict(Settings(default_video_dir(), find_engine_root(), find_engine_python(), default_output_dir()))
    try:
        values.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        pass
    return Settings(**{key: values[key] for key in asdict(Settings())})


def find_engine_root() -> str:
    configured = os.environ.get("VIDEO2DLSSNR_ROOT", "")
    candidates = [configured, r"D:\dlss5\video2dlssnr", r"C:\dlss5\video2dlssnr",
                  str(Path.home() / "dlss5" / "video2dlssnr"),
                  str(Path.home() / "Downloads" / "video2dlssnr"),
                  str(Path.home() / "Desktop" / "video2dlssnr")]
    for candidate in candidates:
        if candidate and (Path(candidate) / "nr_video.py").exists():
            return candidate
    return configured


def find_engine_python() -> str:
    configured = os.environ.get("VIDEO2DLSSNR_PYTHON", "")
    root = find_engine_root()
    if root:
        for relative in (r".venv\Scripts\python.exe", r"venv\Scripts\python.exe", r"python_embeded\python.exe"):
            candidate = Path(root) / relative
            if candidate.exists():
                return str(candidate)
    return configured or sys.executable


def save_settings(settings: Settings) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")


def find_videos(root: Path) -> list[Path]:
    if not root.exists():
        return []
    try:
        return sorted(
            (p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return []


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ComfyUI → DLSS5 视频增强")
        self.geometry("1120x700")
        self.minsize(900, 560)
        self.settings = load_settings()
        self.videos: list[Path] = []
        self.selected: Path | None = None
        self.process: subprocess.Popen[str] | None = None
        self.stop_requested = False
        self._build_ui()
        self._load_form()
        self.after(300, self.refresh)
        self.after(2500, self.auto_refresh)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="ComfyUI video 目录").grid(row=0, column=0, sticky="w")
        self.video_dir = ttk.Entry(top, width=82)
        self.video_dir.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(top, text="浏览", command=lambda: self.choose_dir(self.video_dir)).grid(row=0, column=2)
        ttk.Label(top, text="引擎目录").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.engine_dir = ttk.Entry(top, width=82)
        self.engine_dir.grid(row=1, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(top, text="浏览", command=lambda: self.choose_dir(self.engine_dir)).grid(row=1, column=2, pady=(6, 0))
        ttk.Label(top, text="引擎 Python").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.engine_python = ttk.Entry(top, width=82)
        self.engine_python.grid(row=2, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(top, text="浏览", command=lambda: self.choose_file(self.engine_python)).grid(row=2, column=2, pady=(6, 0))
        ttk.Label(top, text="增强输出目录").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.output_dir = ttk.Entry(top, width=82)
        self.output_dir.grid(row=3, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(top, text="浏览", command=lambda: self.choose_dir(self.output_dir)).grid(row=3, column=2, pady=(6, 0))
        top.columnconfigure(1, weight=1)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        left = ttk.Frame(body, padding=4)
        right = ttk.Frame(body, padding=12)
        body.add(left, weight=1)
        body.add(right, weight=3)

        toolbar = ttk.Frame(left)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="刷新", command=self.refresh).pack(side="left")
        self.count_label = ttk.Label(toolbar, text="0 个视频")
        self.count_label.pack(side="right")
        self.listbox = tk.Listbox(left, activestyle="dotbox", exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True, pady=(8, 0))
        scroll = ttk.Scrollbar(left, command=self.listbox.yview)
        scroll.pack(side="right", fill="y", pady=(8, 0))
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.bind("<<ListboxSelect>>", self.select_video)

        self.title_label = ttk.Label(right, text="请选择一个视频", font=("Segoe UI", 15, "bold"))
        self.title_label.pack(anchor="w")
        self.info_label = ttk.Label(right, text="", justify="left")
        self.info_label.pack(anchor="w", pady=(8, 12))
        form = ttk.LabelFrame(right, text="DLSS5 参数", padding=10)
        form.pack(fill="x")
        self.style = ttk.Combobox(form, values=["0 Default", "1 Natural", "2 Cinematic"], state="readonly", width=18)
        self.preset = ttk.Combobox(form, values=["0", "1", "2", "3"], state="readonly", width=8)
        self.scale = ttk.Combobox(form, values=["1", "1.5", "2", "3"], state="readonly", width=8)
        self.intensity = ttk.Entry(form, width=8)
        self.detail = ttk.Entry(form, width=8)
        self.codec = ttk.Combobox(form, values=["hevc_nvenc", "av1_nvenc", "h264_nvenc", "prores", "ffv1"], state="readonly", width=14)
        self.cq = ttk.Entry(form, width=8)
        self.bit_depth = ttk.Combobox(form, values=["8", "10"], state="readonly", width=8)
        fields = [("风格", self.style), ("NR preset", self.preset), ("放大倍数", self.scale), ("强度", self.intensity),
                  ("细节", self.detail), ("编码", self.codec), ("CQ", self.cq), ("位深", self.bit_depth)]
        for index, (label, widget) in enumerate(fields):
            row, col = divmod(index, 4)
            ttk.Label(form, text=label).grid(row=row * 2, column=col, sticky="w", padx=(0, 8), pady=(0, 2))
            widget.grid(row=row * 2 + 1, column=col, sticky="w", padx=(0, 18), pady=(0, 8))

        buttons = ttk.Frame(right)
        buttons.pack(fill="x", pady=12)
        self.preview_button = ttk.Button(buttons, text="预览原片", command=self.preview_source)
        self.preview_button.pack(side="left")
        self.process_button = ttk.Button(buttons, text="开始处理", command=self.start_process)
        self.process_button.pack(side="left", padx=8)
        self.stop_button = ttk.Button(buttons, text="停止", command=self.stop_process, state="disabled")
        self.stop_button.pack(side="left")
        self.open_output_button = ttk.Button(buttons, text="打开增强结果", command=self.open_output)
        self.open_output_button.pack(side="left", padx=8)

        self.status = ttk.Label(right, text="就绪")
        self.status.pack(anchor="w")
        self.log = tk.Text(right, height=15, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True, pady=(8, 0))

    def _load_form(self) -> None:
        s = self.settings
        for widget, value in [(self.video_dir, s.comfy_video), (self.engine_dir, s.engine_root), (self.engine_python, s.engine_python), (self.output_dir, s.output_dir),
                              (self.style, f"{s.style} {'Default' if s.style == 0 else 'Natural' if s.style == 1 else 'Cinematic'}"),
                              (self.preset, str(s.preset)), (self.scale, str(s.scale)), (self.intensity, str(s.intensity)),
                              (self.detail, str(s.detail)), (self.codec, s.codec), (self.cq, str(s.cq)), (self.bit_depth, str(s.bit_depth))]:
            if isinstance(widget, ttk.Entry):
                widget.insert(0, value)
            else:
                widget.set(value)

    def choose_dir(self, entry: ttk.Entry) -> None:
        selected = filedialog.askdirectory(initialdir=entry.get() or str(Path.home()))
        if selected:
            entry.delete(0, "end")
            entry.insert(0, selected)
            self.refresh()

    def choose_file(self, entry: ttk.Entry) -> None:
        selected = filedialog.askopenfilename(
            initialdir=entry.get() or str(Path.home()),
            filetypes=[("Python", "python.exe"), ("所有文件", "*.*")],
        )
        if selected:
            entry.delete(0, "end")
            entry.insert(0, selected)

    def refresh(self) -> None:
        root = Path(self.video_dir.get())
        self.videos = find_videos(root)
        current = self.selected
        self.listbox.delete(0, "end")
        for path in self.videos:
            try:
                label = str(path.relative_to(root))
            except ValueError:
                label = path.name
            self.listbox.insert("end", label)
        self.count_label.configure(text="目录不可用" if not root.exists() else f"{len(self.videos)} 个视频（含子目录）")
        if current in self.videos:
            index = self.videos.index(current)
            self.listbox.selection_set(index)
            self.listbox.see(index)
        elif self.videos:
            self.listbox.selection_set(0)
            self.select_video()

    def auto_refresh(self) -> None:
        self.refresh()
        self.after(2500, self.auto_refresh)

    def select_video(self, _event: object = None) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        self.selected = self.videos[selection[0]]
        path = self.selected
        try:
            stat = path.stat()
            info = f"路径：{path}\n大小：{stat.st_size / 1024 / 1024:.1f} MB\n修改：{time.ctime(stat.st_mtime)}"
        except OSError as exc:
            info = f"路径：{path}\n无法读取：{exc}"
        self.title_label.configure(text=path.name)
        self.info_label.configure(text=info)
        if not Path(self.engine_dir.get()).joinpath("nr_video.py").exists():
            self.status.configure(text="已选择；请安装或设置 video2dlssnr 引擎")
        else:
            self.status.configure(text="已选择")

    def read_settings(self) -> Settings:
        style = int(self.style.get().split()[0])
        return Settings(self.video_dir.get(), self.engine_dir.get(), self.engine_python.get(), self.output_dir.get(), style, int(self.preset.get()),
                        float(self.scale.get()), float(self.intensity.get()), float(self.detail.get()), self.codec.get(),
                        int(self.cq.get()), int(self.bit_depth.get()))

    def output_for(self, source: Path, settings: Settings) -> Path:
        return Path(settings.output_dir) / f"{source.stem}.dlss5{source.suffix.lower()}"

    def build_command(self, source: Path, destination: Path, settings: Settings) -> list[str]:
        script = Path(settings.engine_root) / "nr_video.py"
        python = settings.engine_python or sys.executable
        command = [python, str(script), "--in", str(source), "--out", str(destination)]
        command += ["--nr-scale", str(settings.scale), "--nr-style", str(settings.style), "--nr-preset", str(settings.preset),
                    "--nr-intensity", str(settings.intensity), "--nr-detail", str(settings.detail), "--nr-color", "0",
                    "--nr-sr-preset", "default", "--codec", settings.codec, "--cq", str(settings.cq), "--bit-depth", str(settings.bit_depth)]
        return command

    def append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def preview_source(self) -> None:
        if self.selected:
            os.startfile(str(self.selected))

    def open_output(self) -> None:
        if not self.selected:
            return
        try:
            settings = self.read_settings()
            output = self.output_for(self.selected, settings)
            if output.exists():
                os.startfile(str(output))
            else:
                messagebox.showinfo("尚未生成", f"增强结果不存在：\n{output}")
        except (ValueError, OSError) as exc:
            messagebox.showerror("打开失败", str(exc))

    def start_process(self) -> None:
        if not self.selected or self.process is not None:
            return
        try:
            settings = self.read_settings()
            engine = Path(settings.engine_root)
            script = engine / "nr_video.py"
            if not script.exists():
                raise FileNotFoundError(f"找不到 nr_video.py：{script}")
            settings_path = CONFIG_PATH
            save_settings(settings)
            destination = self.output_for(self.selected, settings)
            destination.parent.mkdir(parents=True, exist_ok=True)
            command = self.build_command(self.selected, destination, settings)
        except (ValueError, OSError) as exc:
            messagebox.showerror("参数错误", str(exc))
            return
        self.append_log(f"\n> {' '.join(command)}\n")
        self.status.configure(text="处理中…")
        self.process_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.stop_requested = False
        threading.Thread(target=self._run_process, args=(command, engine, settings_path), daemon=True).start()

    def _run_process(self, command: list[str], cwd: Path, _settings_path: Path) -> None:
        try:
            self.process = subprocess.Popen(command, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace", bufsize=1)
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.after(0, self.append_log, line)
            returncode = self.process.wait()
            self.after(0, self._process_finished, returncode)
        except OSError as exc:
            self.after(0, self._process_failed, str(exc))

    def _process_finished(self, returncode: int) -> None:
        self.process = None
        self.process_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status.configure(text="处理完成" if returncode == 0 else f"处理失败（{returncode}）")
        self.refresh()

    def _process_failed(self, error: str) -> None:
        self.process = None
        self.process_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status.configure(text="启动失败")
        self.append_log(f"[error] {error}\n")

    def stop_process(self) -> None:
        if self.process is None:
            return
        self.stop_requested = True
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(self.process.pid), "/T", "/F"], capture_output=True, text=True)
        else:
            self.process.terminate()
        self.status.configure(text="正在停止…")

    def close(self) -> None:
        if self.process is not None:
            self.stop_process()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
