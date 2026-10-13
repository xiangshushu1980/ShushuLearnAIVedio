# Sean Material Gallery

Owner: Sean

这是一个本地 ComfyUI 视频素材预览插件。它在 ComfyUI 菜单中添加“素材库”按钮，启动随包附带的 `gallery.py` 并打开浏览器页面。

页面读取 ComfyUI `input` 下的两个目录：

- `material/{action,portrait,scene}/`：原始视频
- `material_b/{action,portrait,scene}/`：预处理视频

插件只预览目录中的视频，不包含素材，也不提供上传、编辑或 ComfyUI 模型资产管理功能。素材目录为空时，页面会显示标题但没有视频卡片。

## 安装

1. 将 `sean_material_gallery` 目录复制到 `ComfyUI/custom_nodes/`。
2. 重启 ComfyUI 并刷新页面。
3. 按上述目录结构放置视频，点击“素材库”。

预览服务默认使用本机 `127.0.0.1:8000`。若端口上已有服务，插件会假定它就是 Gallery 并打开该端口；安装前请确认 8000 端口空闲，或已运行 Gallery。

## 文件

- `__init__.py`：ComfyUI 菜单入口和预览服务启动接口
- `web/index.js`：菜单按钮
- `gallery.py`：独立本地视频预览服务
