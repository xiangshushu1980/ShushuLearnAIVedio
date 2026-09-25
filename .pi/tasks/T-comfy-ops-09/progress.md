# 任务进度：comfy-ops-antirez

## 任务
- 目标：研究 antirez/h3.c（纯 C 原生 MiniMax-H3 推理引擎，Metal 后端）架构：切片顺序/块实现/Metal 内存策略 → 提炼可借鉴模式 → 结论落 docs 学习笔记
- 当前状态：🟡 进行中
- 我负责的文件区：docs/25_h3c_study.md（新文件）、.pi/tasks/comfy-ops-antirez/progress.md

## 进度日志（append-only，每条带日期）
### 2026-08-17
- 开场对账：TODO T-comfy-ops-09 已认领，建 [STATE] + progress
- clone 源码（/tmp/h3c-study，后续研究参考）→ 通读 README（811 行全读）
- 架构分析：h3.h/h3_gpu.h/h3_host.h/h3_dit.c(h3_gpu.m/h3_shaders.metal 结构、run_block 块流水、allocate_activations 别名、SSD 双缓冲、Qwen prefetch、测试对拍机制
- git 历史实证垂直切片顺序：22 个里程碑 commit 拉全（S1 元数据→S2 toy parity→S3 checkpoint 布局→S4 prompt→S5 T2V→S6 T2A→S7 首尾帧→S8 Ref2VA→性能层）
- **产出 docs/25_h3c_study.md**（8 节：概况/架构/切片顺序/块实现/内存策略/优化方法论/本项目启示/参考）+ INDEX.md 登记
- 收尾：retain 经验 + [STATE] 删除 + TODO 完成

## 下一步
1.（已完成）文档落盘；后续如做自研推理/服务化可回查 25 文档 7.2 节

## 关键链接
- 源码：https://github.com/antirez/h3.c（本地镜像 /tmp/h3c-study）
- 学习笔记：docs/25_h3c_study.md
- 相关文档：docs/02_models.md、docs/09_h3_test_plan.md（H3 背景）
