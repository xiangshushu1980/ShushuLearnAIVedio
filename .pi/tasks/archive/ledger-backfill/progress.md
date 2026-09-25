# 任务进度：ledger-backfill（结论谱系首轮回填）

> 私有进度。回填已收尾调查任务的实测定论到 .pi/ledger/。

## 任务
- 目标：把已收尾的 comfyUI 调查任务中实测得出的「定论」（参数值/加速比/可行性/选型）回填进结论谱系（.pi/ledger/），后续新调查持续追加
- 当前状态：✅ 完成（2026-08-16）
- 我负责的文件区：.pi/ledger/（README 索引 + 4 个主题文件）、本 progress

## 回填范围（12 条已收尾任务线）
- h3-patch-test（补测批 D：MC/sage 音频/fp8 矩阵）
- h3-turbo-pilot + h3-today-testing（Turbo LoRA 代际定案、flags/Sage v2/Sol Engine/fal/纯音频参考）
- comfyui-032-verify（T-20260812-07：#15486/#15446、风格词主导 V7、15s 长档）
- prompt-audio（BGM 触发矩阵、demucs 定案；T-20260812-06 收尾）
- seedance-h3-verify（34 条 7 经验适用性）
- h3-ref2v-pilot（Ref2VA Turbo 4 步、FaceRefine 参数铁律）
- h3-new-findings-test（T-20260815-07：Sol-Attn/Hybrid/turnaround/六块文字/ref_image_size）
- cond-cache-node + cond-roundtrip（T-20260816-01/02：加载时间修正、两阶段流水线）
- vllm-h3-stream-analysis（Cache-DiT 🟡待验证）
- h3-prompt-agent（IR API 选型、BGM 触发调查）
- speech-video（H3 能力边界选型）

## 产物
- .pi/ledger/h3-speed.md（C-01~C-10）
- .pi/ledger/h3-audio.md（C-11~C-14）
- .pi/ledger/h3-prompt.md（C-15~C-19）
- .pi/ledger/h3-models.md（C-20~C-27）
- .pi/ledger/README.md（〇节全量索引 + 八节文件组织现状）

## 过程要点
- 编号统一用登记日 C-20260816-NN，真实日期记在时间线里（与 README 示例一致）
- 未收尾/未定论不误入：mc-test（MC 验收中）、h3-face-fix（挂起）、refimage-system/vimax-dissect（设计非实测定论）未回填
- 冲突处理：Sol-Attn 结论反转（1.07x→快 8%→最终弃用）记完整时间线；TE 80s→11s 修正按覆盖链记录
- 2 条 🟡待验证（Hybrid 写实域、Cache-DiT）明确标注待实测

## 下一步
- 后续调查任务收尾时按 README 收尾四步第①步分流：定论 → 谱系 + docs 现行值；经验 → mem0
- 注意：本线仅回填，未动 docs/params.md（现行值已由各任务线维护）
