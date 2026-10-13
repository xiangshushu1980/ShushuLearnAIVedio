"""Owner: Sean. Local video-material preview entry point for ComfyUI."""

import os, subprocess, socket, time, sys
from aiohttp import web

import server

WEB_DIRECTORY = "web"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

PORT = 8000
GALLERY_SCRIPT = os.path.join(os.path.dirname(__file__), "gallery.py")


def _is_port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def _start_gallery():
    """启动素材预览服务(若未运行)"""
    if _is_port_open(PORT):
        return {"running": True, "port": PORT, "started": False}

    if not os.path.isfile(GALLERY_SCRIPT):
        return {"error": f"gallery 脚本不存在: {GALLERY_SCRIPT}"}

    log = open("/tmp/material_gallery_node.log", "a")
    subprocess.Popen(
        [sys.executable, GALLERY_SCRIPT, "--port", str(PORT)],
        stdout=log, stderr=log,
        start_new_session=True,
    )
    # 等待端口就绪(最多 5s)
    for _ in range(10):
        if _is_port_open(PORT):
            return {"running": True, "port": PORT, "started": True}
        time.sleep(0.5)
    return {"error": "启动超时，见 /tmp/material_gallery_node.log"}


async def api_start(request):
    try:
        result = _start_gallery()
        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


routes = web.RouteTableDef()
routes.get("/start")(api_start)

# 用 aiohttp Application + add_subapp 挂到 server（同 browser 做法）
_material_app = web.Application()
_material_app.add_routes(routes)
server.PromptServer.instance.app.add_subapp("/material-gallery/", _material_app)
