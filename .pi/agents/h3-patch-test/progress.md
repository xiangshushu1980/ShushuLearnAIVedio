# 任务进度：h3-patch-test（H3 补测批）

## 任务
- 目标：补齐 H3 优化策略的数据缺口（快速档端到端 / fp8 矩阵 / sage 音频对照）
- 当前状态：✅ 完成（2026-08-05）
- 我负责的文件区：docs/09_h3_test_plan.md（补测批 D 节）、.pi/skills/comfyui/references/params.md（管线表）

## 进度日志（append-only，每条带日期）
### 2026-08-05
- 补测批 P（13 条全跑完，产物 video/h3_patch/）：P1-P7 + V1/V2 + W1-W4
- 核心结论：
  1. 快速抽卡档实测 75s/条（fp8+sage+14步 @768×448 5s 驻留）；**MC 在 14 步无实用价值**（默认只跳 1/14，激进参数跳 4/14 但净收益仅 ~3s）→ 快速档去 MC
  2. sage 对音频零影响（0.2 LU 不可辨）→ "声音变弱"100% 归因 MC
  3. fp8 干净矩阵：5s=195s / 10s=405s / 15s=615s（vs int8 165/295/503）；15s 差异疑内存压力（fp8 驻留 17.1GB+TE 15.7GB 顶满 WSL 47GB）
- 踩坑记录：重启脚本 pgrep 误杀 bash 自身（ComfyUI 没死→后续数据污染）、忘 venv、重启过渡期提交被 runner 误判完成 → 已 retain mem0
- 文档：docs/09 追加"补测批 D"；params.md 管线表更新（快速档去 MC、MC 定位改 20 步档）

## 下一步
- 用户已预告：优化测试流程（内存压力 / 重启脚本 / TE 优化）→ 接新任务线

## 关键链接
- 测试数据：docs/09_h3_test_plan.md（补测批 D）
- 批量优化既有分析：docs/10_h3_batch_optimization.md（TE 80s 加载 / 两阶段流水线）
- 脚本：/tmp/patch_runner.py（补测 runner，串行提交+轮询耗时）、/tmp/patch_cases*.json
