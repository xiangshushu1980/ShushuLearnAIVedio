# 结论谱系 — 视频分析（OCR 压缩 / fund-video-analysis）

> 本文件索引见 ledger README 〇节；规则/模板见 README。

### C-20260827-01 | OCR 文字流压缩范式与 _condense_ocr 参数定论
- 状态：✅现行（valid_from 2026-08-27）
- 现行值：**视频 OCR 逐帧事件压缩采用「文本相似度(编辑距离≥0.75) + 空间 IoU(≥0.35，box 缺失降级 pos-only) + 时间连续(间隙≤1.5s)」三要素联合判重，配合置信度过滤(≥0.55)、纯数字 ticker 降噪、覆盖占比≥50% 判常驻（上限 8 行，超出视为密集静态文字卡整体降级）、token 限量（0.65 字符/行估算，估算/真实=1.03-1.30）**。对齐学术界 VTS/VTT 范式（STVText4 Temporal Clustering）+ EVE 编辑距离匹配（arxiv 2503.04058）。实测 16 样本压缩比 2.9-6.8×（均值 ~4.3×），全部 ≤1400 真实 token。
- 时间线：
  - 2026-08-27 提出：T-comfy-ops-24 研究+实现（来源任务 T-comfy-ops-24，父 T-comfy-ops-23）
  - 2026-08-27 修正：Codex gpt-5.6-terra 评审后微调——单帧事件补 frame_sec=0.5 覆盖（去 [0-0s]）、IoU 并集改最近框轨迹关联、窗口行同文去重、脏数据逐事件容错、移除 MAX_SPANS 死常量、极小预算跳过注入（验证：估算/真实 min=1.03 mean=1.12，无 [0-0s]）
- 证据锚：fund-video-analysis/docs/ocr_condense.md（研究结论+算法+验证数据）/ ocr_condense.py（实现）/ schema_contract.md（box 字段）/ 真实 tokenizer 校验（Qwen3-Omni tokenizer 16 样本 min=1.03 mean=1.13）

### C-20260827-02 | P1 OCR 合并逻辑失效（数据实证）
- 状态：✅现行（valid_from 2026-08-27）
- 现行值：**P1 run_ocr 的相邻流文本合并实际不工作（16 条视频 merged≈0）**——每帧多行文字在排序流中交错，相同文本跨帧不连续相邻；时间跨度语义由 _condense_ocr 的时间聚合接管，P1 合并保留为向后兼容（近似恒等）。
- 时间线：
  - 2026-08-27 提出：T-comfy-ops-24 摸底（来源任务 T-comfy-ops-24）
- 证据锚：fund-video-analysis/p1_cpu.py run_ocr / data/results/*/p1.json（全部 dur=0 事件）
