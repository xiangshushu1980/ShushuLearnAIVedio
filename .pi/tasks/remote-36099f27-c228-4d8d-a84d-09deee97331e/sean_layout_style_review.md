# 脸部布局与生成风格复核

Owner: Sean。2026-10-03，PC only。

用户确认 side 为侧面。实现追加在二期同一任务、generation 2 中。

## 页面与运行配置

- 视图目录：three、four、face-front-back-side。
- 风格目录：original、cinematic、concept、photoreal、anime、three-dimensional、watercolor、ink。
- 新布局为单张中性头肩特写＋正／背／侧全身；1536×1024、25 步、默认 seed 6200605，采样图沿用 V3 Simple 的本地 int8/标准 VAE。
- 原三／四视图模板未改，原风格快照未改。运行快照继续保存生效提示词和风格配置，旧记录按原设置恢复。

## PC 检查

`npm run build` 成功，输出 `index-DjsD22LB.js`。仅重载本应用 4188，重载前其 active runs 为空。

1440×1000 浏览器手动操作：选 face-front-back-side、anime，保存输入，刷新页面后恢复；载入旧 run `3547aa4f-9e72-4c7c-9694-3b74e2a733d5` 后显示 four/original。页面显示已载入历史布局、风格、参数及主形象版本，兼容错误为空。其 `/input` 实际返回 compatible=true。document scrollWidth 未超过 innerWidth，console 0 errors/warnings。

SQLite 返回保存值：layout=face-front-back-side、styleId=anime、appearanceId=4e1b9ef4-326f-40cb-be07-4b974f4a8129，size=1536x1024、seed=6200605、steps=25。既有主形象及确认视图保留。

PC 截图 `sean_face_style_pc.png` 留本机。浏览器已关闭，应用服务继续运行。

## 限制

本轮未提交任何生成、未新增/运行单元测试。新增布局与各风格的出图质量尚未验证；此前原版表情栏“喜”表情不严格的限制仍有效。
