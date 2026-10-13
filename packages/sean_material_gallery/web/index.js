// Owner: Sean
import { app } from "../../scripts/app.js";

// 素材预览服务入口: 点击启动并跳转
async function openGallery() {
  try {
    const res = await fetch("/material-gallery/start");
    const data = await res.json();
    if (data.error) {
      alert("素材预览启动失败: " + data.error);
      return;
    }
    const url = `http://127.0.0.1:${data.port}`;
    window.open(url, "_blank");
  } catch (e) {
    alert("素材预览请求失败: " + e);
  }
}

app.registerExtension({
  name: "ComfyUI.MaterialGallery",
  async setup() {
    const menuContainer = app.ui.menuContainer;
    if (!menuContainer) return;

    const btn = document.createElement("button");
    btn.textContent = "素材库";
    btn.style.marginLeft = "5px";
    btn.style.padding = "0 8px";
    btn.title = "打开视频素材预览服务";
    btn.onclick = openGallery;

    // 尝试加到菜单(兼容新旧布局)
    try {
      if (app.menu?.settingsGroup) {
        app.menu.settingsGroup.element.after(btn);
      } else {
        menuContainer.appendChild(btn);
      }
    } catch (e) {
      menuContainer.appendChild(btn);
    }
  },
});
