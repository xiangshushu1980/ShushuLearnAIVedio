# 通用节点入口

本文件只放跨任务的节点概念和路由；具体模型节点、参数和本地实测见旧版完整档案 [nodes.md](../nodes.md)，按需读取对应小节。

## 基础图像链

```text
模型加载 → 文本编码 → 空 latent → 采样 → VAE 解码 → SaveImage
```

常见节点：`UNETLoader`、`CLIPLoader`、`CLIPTextEncode`、`EmptyLatentImage`、`KSampler`、`VAEDecode`、`SaveImage`。

## 基础视频链

```text
模型/文本/参考输入 → 视频条件节点 → 采样 → VAE 解码 → CreateVideo/SaveVideo
```

H3、Wan 和 Ref2VA 的节点不能只看名称套用，必须读取对应视频分册和工作流档案。

## 查找规则

- 需要输入输出类型：读旧版 `nodes.md` 对应节点。
- 需要实际参数：读 `image/` 或 `video/` 对应参数分册。
- 第一次使用新节点：按 [learning.md §3.5](../learning.md) 走源码、官方用法、最小验证、沉淀四步。
