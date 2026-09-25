# Git 历史交接导出

更新时间：2026-09-04

本文件由当前仓库导出，覆盖 `--all` 可见引用下的全部提交。

- 当前分支：`main`
- 当前 HEAD：`a945972d5bf7dec1d29a5907f23c878071458da4`
- 可见提交数：`270`
- 导出命令：`git log --all --date=iso-strict --pretty=... --stat`

## 当前引用

```text
a945972d5bf7dec1d29a5907f23c878071458da4 refs/heads/main
80e96c33b58bd419eb9490bb7e7efee5a1c5539e refs/remotes/origin/main
```

## 当前工作区状态

```text
## main...origin/main [ahead 255]
 M .pi/ledger/README.md
 M .pi/ledger/h3-speed.md
 M .pi/skills/comfyui/references/nodes.md
 D .pi/tasks/comfy-ops-antirez/progress.md
 D .pi/tasks/comfy-ops-awesome/progress.md
 D .pi/tasks/easycache-test/progress.md
 D .pi/tasks/h3-new-findings-test/progress.md
 D .pi/tasks/img-qc-api-test/progress.md
 M .pi/tasks/mc-test/progress.md
 D .pi/tasks/refimage-system/progress.md
 M .pi/tasks/story-e2e-v1/progress.md
 D .pi/tasks/vimax-dissect/progress.md
 D .pi/tasks/vimax-dissect/stage2_consistency.md
 M docs/INDEX.md
 D output/compare/attn3way_dance.png
 D output/compare/attn3way_wave.png
 D output/compare/easycache_dance.png
 D output/compare/easycache_wave.png
 D output/compare/text_ctrl3_matrix.png
 D output/compare/text_ctrl4_matrix.png
 M scripts/h3_audio_sep.py
 M scripts/h3_batch_runner.py
 M scripts/h3_mc_runner.py
?? .pi/ledger/va-ocr.md
?? .pi/settings.json
?? .pi/tasks/T-20260812-03/
?? .pi/tasks/T-20260814-01/
?? .pi/tasks/T-20260814-02/
?? .pi/tasks/T-20260815-07/
?? .pi/tasks/T-20260816-07/
?? .pi/tasks/T-comf-01/
?? .pi/tasks/T-comfy-ops-04/
?? .pi/tasks/T-comfy-ops-09/
?? .pi/tasks/T-comfy-ops-27/
?? .pi/tasks/T-comfy-ops-28/
?? .pi/tasks/T-comfy-ops-29/
?? .pi/tasks/T-comfy-ops-31/
?? .pi/tasks/T-duix-avatar-01/
?? .pi/tasks/h3-face-fix/
?? .pi/tasks/h3-ref2v-pilot/
?? .playwright-mcp/
?? assets/
?? "docs/27_DUIX_Avatar_\346\225\260\345\255\227\344\272\272\350\257\204\344\274\260.md"
?? "docs/28_\346\225\260\345\255\227\344\272\272\345\234\250\347\272\277\346\226\271\346\241\210_\345\257\271\346\257\224\344\270\216\344\273\267\344\275\215.md"
?? docs/dev/
?? docs/h3-digital-human-research/
?? docs/project/
?? experiments/h3_digital_human/
?? experiments/h3_ref2v/
?? experiments/mc_test/mc_sfx2_cases.json
?? experiments/mc_test/mc_sfx2_cases.json.results.json
?? experiments/mc_test/mc_sfx_cases.json
?? experiments/mc_test/mc_sfx_cases.json.results.json
?? experiments/mc_test/prompts/
?? output/audio/
?? scripts/ace_t2i_probe.py
?? scripts/h3_download.py
?? scripts/h3_facerefine_batch.py
?? scripts/h3_fl_motion_context_runner.py
?? scripts/h3_join_overlap_shift.py
?? scripts/h3_mc_recover.py
?? scripts/h3_ref2v_runner.py
?? scripts/run_music3.py
?? scripts/style_probe.py
?? scripts/vlm_batch.py
?? vendor/gathered-scenes-zine-skill/
?? workflows/krea_h3_anchor_host.json
?? workflows/krea_h3_anchor_host_16x9.json
?? workflows/krea_text_ctrl5_firstframe.json
?? workflows/longcat_avatar15_at2v_test.json
?? workflows/solattn_baseline.json
?? workflows/solattn_test.json
?? workflows/turnaround_test.json
```

## 全部提交记录

## a945972d5bf7dec1d29a5907f23c878071458da4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-28T03:09:10-04:00
- Subject: [spectrum-ab] T-comfy-ops-11 Spectrum v0.2.20 A/B 定论：仅 std 20步档推荐（1.55x采样/1.22x端到端/画质反升）；docs09批E+docs10家族对比+ledger C-20260828-01


 .pi/ledger/README.md                               |   4 +
 .pi/ledger/h3-speed.md                             |   7 +
 .pi/tasks/T-comfy-ops-11/progress.md               |  44 +++++
 docs/09_h3_test_plan.md                            |  33 ++++
 docs/10_h3_batch_optimization.md                   |  14 +-
 .../spectrum_ab/ab_f4_20260814.results.json        |  59 +++++++
 .../spectrum_ab/ab_f8_20260814.results.json        |  65 ++++++++
 .../spectrum_ab/ab_s8_20260814.results.json        | 128 +++++++++++++++
 .../spectrum_ab/ab_t20_20260814.results.json       |  32 ++++
 experiments/spectrum_ab/frames/f4_dance_cmp.png    | Bin 0 -> 1282251 bytes
 experiments/spectrum_ab/frames/f8_dance_cmp.png    | Bin 0 -> 2254363 bytes
 experiments/spectrum_ab/frames/s8_dance_cmp.png    | Bin 0 -> 3623022 bytes
 experiments/spectrum_ab/frames/s8_wave_cmp.png     | Bin 0 -> 3111067 bytes
 experiments/spectrum_ab/frames/t20_dance_cmp.png   | Bin 0 -> 3544127 bytes
 scripts/h3_spectrum_ab_runner.py                   | 182 +++++++++++++++++++++
 15 files changed, 567 insertions(+), 1 deletion(-)

## 6e56da9d447714d4dfccb1ba57f565ef8bd8b7ab
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-25T14:00:47-04:00
- Subject: [结论] C-20260825-02 v4-600EMA 无法跨用 ref2va pruned（LoRA 键名不匹配）


 .pi/ledger/h3-models.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## b17563b67f563afd8d736b42472592177c2fb6b5
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-25T13:19:48-04:00
- Subject: [结论] C-20260825-01 新增 H3 TE 精度选型定论（维持 NVFP4）；顺带落盘 C-20260816-20 Hybrid 状态注


 .pi/ledger/h3-models.md | 11 ++++++++++-
 1 file changed, 10 insertions(+), 1 deletion(-)

## 6e4b2e9fa5ede3350c3d3e9829b6915099949d81
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-22T01:49:04-04:00
- Subject: [结论] C-20260822-01 协作三时点分层定论（建任务体检/自由对话轻检/锚点注入）


 .pi/ledger/collab-governance.md | 23 +++++++++++++++++++++++
 1 file changed, 23 insertions(+)

## 7eab237c9c04eb9d08b61fd7639576626aacc11b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-22T00:28:13-04:00
- Subject: [T-comfy-ops-20] progress: 认知架构 v3 四件套落地完成（两条纪律+refs试点3条+验证）


 .pi/tasks/T-comfy-ops-20/progress.md | 42 ++++++++++++++++++++++++++++++++++++
 1 file changed, 42 insertions(+)

## 94fc015e330732c2812812971d285685d498962f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-22T00:27:07-04:00
- Subject: [T-comfy-ops-20] 项目 AGENTS：内容落盘补强制点（收尾五步①定论落 ledger / retain 打标转 ledger）


 AGENTS.md | 1 +
 1 file changed, 1 insertion(+)

## 7dcd03ba3b2cebf912b2920ce25bc334376bd298
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-21T11:46:35-04:00
- Subject: Music3 音质探索收尾：音质规律/台词修复定论(docs/26) + 超分母带分离工具 + 30+首各国风格测试输入


 .../minimax_music3_api_template.json               |  53 +++
 .../minimax_music3_official_readme.md              | 235 ++++++++++++++
 .../multimodalart_prompting_guide.html             | 356 +++++++++++++++++++++
 .../T-comfy-ops-16/music3_control_baseline.md      | 135 ++++++++
 .pi/tasks/T-comfy-ops-16/progress.md               | 129 ++++++++
 .../T-comfy-ops-16/prompting_guide_index.html      | 356 +++++++++++++++++++++
 .pi/tasks/T-comfy-ops-16/tests/TA_duet.json        |   4 +
 .pi/tasks/T-comfy-ops-16/tests/TB_child.json       |   4 +
 .pi/tasks/T-comfy-ops-16/tests/TC_suona.json       |   4 +
 .pi/tasks/T-comfy-ops-16/tests/V4_v1_120s.json     |   4 +
 .pi/tasks/T-comfy-ops-16/tests/V5_3min.json        |   4 +
 .pi/tasks/T-comfy-ops-16/tests/V5_3min_lyrics.txt  |  90 ++++++
 .../T-comfy-ops-16/tests/emotion/E1_peace.json     |   4 +
 .../T-comfy-ops-16/tests/emotion/E2_despair.json   |   4 +
 .../T-comfy-ops-16/tests/emotion/E3_lonely.json    |   4 +
 .pi/tasks/T-comfy-ops-16/tests/emotion/E4_joy.json |   4 +
 .pi/tasks/T-comfy-ops-16/wow_input.json            |   4 +
 .../T-comfy-ops-16/wow_newbie_caption_lyrics.md    |  26 ++
 docs/26_music3_audio_quality.md                    |  43 +++
 docs/INDEX.md                                      |   3 +-
 scripts/acoustic_folk_input.json                   |   4 +
 scripts/african_drums_input.json                   |   4 +
 scripts/arabic_oud_fix_input.json                  |   4 +
 scripts/arabic_oud_input.json                      |   4 +
 scripts/batch_music.sh                             |  44 +++
 scripts/bossa_nova_input.json                      |   4 +
 scripts/celtic_irish_fix_input.json                |   4 +
 scripts/celtic_irish_input.json                    |   4 +
 scripts/flamenco_input.json                        |   4 +
 scripts/german_harpsichord_fix_input.json          |   4 +
 scripts/german_harpsichord_input.json              |   4 +
 scripts/greek_bouzouki_input.json                  |   4 +
 scripts/hawaiian_ukulele_input.json                |   4 +
 scripts/indian_sitar_input.json                    |   4 +
 scripts/italian_mandolin_input.json                |   4 +
 scripts/japanese_koto_fix_input.json               |   4 +
 scripts/japanese_koto_input.json                   |   4 +
 scripts/jazz_trio_fix_input.json                   |   4 +
 scripts/jazz_trio_input.json                       |   4 +
 scripts/mariachi_input.json                        |   4 +
 scripts/master_music.py                            |  53 +++
 scripts/pure_orchestral_input.json                 |   4 +
 scripts/pureorch_fix_input.json                    |   4 +
 scripts/remix_music_stems.py                       |  71 ++++
 scripts/russian_balalaika_input.json               |   4 +
 scripts/scandinavian_folk_fix_input.json           |   4 +
 scripts/scandinavian_folk_input.json               |   4 +
 scripts/scottish_bagpipe_fix_input.json            |   4 +
 scripts/scottish_bagpipe_input.json                |   4 +
 scripts/string_quartet_fix_input.json              |   4 +
 scripts/string_quartet_input.json                  |   4 +
 scripts/test_instruments_input.json                |   4 +
 scripts/turkish_ney_fix_input.json                 |   4 +
 scripts/turkish_ney_input.json                     |   4 +
 scripts/upscale_music3.py                          |  64 ++++
 scripts/vietnamese_danbai_fix_input.json           |   4 +
 scripts/vietnamese_danbai_input.json               |   4 +
 scripts/weak_instr_fix_input.json                  |   4 +
 scripts/weak_instr_input.json                      |   4 +
 59 files changed, 1837 insertions(+), 1 deletion(-)

## 985e3ee3672605a9062a4b0b26ded677ff042333
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T11:36:06-04:00
- Subject: [agents] 项目 AGENTS 瘦身：只留项目专属，通用纪律全部指向用户级+全局 skill


 AGENTS.md | 27 +++++++--------------------
 1 file changed, 7 insertions(+), 20 deletions(-)

## a83201c15f578c574152cd2e7fbb2e199333405c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:59:57-04:00
- Subject: [agents] 项目 AGENTS 同步新系统：STATE 移出 mem0 → hive-state/state.json，收尾四步


 AGENTS.md | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)

## 7dd541c975899a50650f3fccfc31cea0f6c7c14b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:57:18-04:00
- Subject: story-e2e-v1: 任务启动（T-comfy-ops-15 新故事端到端第一轮）


 .pi/tasks/story-e2e-v1/progress.md | 38 ++++++++++++++++++++++++++++++++++++++
 1 file changed, 38 insertions(+)

## d4a5fdbaeb25ac69de1f8e96b53a21a428c0d0a3
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:40:38-04:00
- Subject: [comfy-ops-promptor] progress: P1 视频实测结果


 .pi/tasks/comfy-ops-promptor/progress.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## 5dc368ae5bad10fbf6f3a3f2995d279f9f4b1bfd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:40:33-04:00
- Subject: [comfy-ops-promptor] P1 视频实测：FL2VA 单镜偏好+T8 锚点验证成立（6 条 8步turbo）


 docs/11_h3_case_library.md                         |   7 +-
 docs/17_h3_prompt_writing_rules.md                 |   2 +-
 experiments/promptor_compare/p1_video/README.md    |  28 +++++
 .../p1_video/framediff_report.json                 |  74 ++++++++++++
 .../p1_video/water_anchor_state2_filter_macro.png  | Bin 0 -> 179900 bytes
 .../p1_video/water_anchor_state4_pour_clear.png    | Bin 0 -> 164022 bytes
 scripts/h3_promptor_p1.py                          | 134 +++++++++++++++++++++
 7 files changed, 243 insertions(+), 2 deletions(-)

## 3c1580fe09e5fc6998945c8d9044eefa75a5344f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:21:37-04:00
- Subject: [comfy-ops-allinone] T-comfy-ops-14 三集成节点横向对比：ALLinONE忽略/Extender借鉴不装/Easy推荐安装，结论落mem0


 .pi/tasks/comfy-ops-allinone/progress.md | 33 ++++++++++++++++++++++++++++++++
 1 file changed, 33 insertions(+)

## cf1c63f6fc97dc3fa1e5e2358c96d422ef708a6d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:20:06-04:00
- Subject: [comfy-ops-promptor] progress 更新：P0 回归结果


 .pi/tasks/comfy-ops-promptor/progress.md | 4 ++++
 1 file changed, 4 insertions(+)

## 67bad40dc3d6d8e195b0d102098226a8e59f79a0
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T10:20:00-04:00
- Subject: [comfy-ops-promptor] P0 文本级回归：强化句生效验证 + 偶发格式违规发现（自检重试入 16 号）


 docs/16_prompt_generator_plan.md                   |   1 +
 experiments/promptor_compare/README.md             |  16 +++
 .../regression/results_20260817.json               | 144 +++++++++++++++++++++
 .../regression/t3_ref2va_OLD_retry1.txt            |  24 ++++
 .../regression/t3_ref2va_OLD_retry2.txt            |  21 +++
 5 files changed, 206 insertions(+)

## 9e8dfbb1a76514d5fc785c582791ceeb6bbcd1bf
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T09:58:28-04:00
- Subject: [comfy-ops-promptor] T-comfy-ops-03 两提示词工具对比：吸收进 17/11/16 + 抽样归档


 .pi/tasks/comfy-ops-promptor/progress.md           |   31 +
 docs/11_h3_case_library.md                         |   45 +
 docs/16_prompt_generator_plan.md                   |    9 +
 docs/17_h3_prompt_writing_rules.md                 |   13 +
 .../promptor_compare/1038lab_system_base.txt       |   44 +
 experiments/promptor_compare/README.md             |   51 +
 .../promptor_compare/sample_A_1038lab_i2v.txt      |    9 +
 experiments/promptor_compare/sample_B_T8_i2va.txt  |   10 +
 .../promptor_compare/sample_C_ours_baseen_i2va.txt |    7 +
 experiments/promptor_compare/t8_case_catalog.json  | 6578 ++++++++++++++++++++
 10 files changed, 6797 insertions(+)

## a834fb78392cebf3ac598cb6f6b9a910125d8e63
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T09:58:25-04:00
- Subject: [comfy-ops-antirez] T-comfy-ops-09 h3.c 架构研究：docs/25 学习笔记 + INDEX 登记


 .pi/tasks/comfy-ops-antirez/progress.md |  23 ++++++
 docs/25_h3c_study.md                    | 128 ++++++++++++++++++++++++++++++++
 docs/INDEX.md                           |   3 +-
 3 files changed, 153 insertions(+), 1 deletion(-)

## fcda65fb5c91c3eb40c2823b1d3584cee685bbe6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T09:56:34-04:00
- Subject: [comfy-ops-awesome] 进度文件标记完成


 .pi/tasks/comfy-ops-awesome/progress.md | 11 ++++++-----
 1 file changed, 6 insertions(+), 5 deletions(-)

## b5d2ab0b3269d394a3cde3ebbe7bb677f1a56828
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T09:56:22-04:00
- Subject: [comfy-ops-awesome] 吸收 BeatAPI awesome-minimax-h3-prompts：6 模式+2 冲突惯例落盘 docs/11 社区精选分节（来源标注）


 .pi/tasks/comfy-ops-awesome/progress.md |  60 ++++++++++++++++++
 docs/11_h3_case_library.md              | 105 ++++++++++++++++++++++++++++++++
 2 files changed, 165 insertions(+)

## 0e29b4ecf5c7815d82b3fd943edb952a8311286b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-17T05:28:33-04:00
- Subject: [hivemind-bootstrap] 开场路由化：任务会话/自由对话分流，去掉「声明任务名」绑定（与 multi-agent-collab skill 开场清单同步）


 AGENTS.md | 10 ++++++----
 1 file changed, 6 insertions(+), 4 deletions(-)

## 43cad251346e7cf8935f7b3073807199a509e8fe
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T07:19:36-04:00
- Subject: [easycache-test] T-20260814-01 收尾：EasyCache 分档结论入 params.md（加速策略节+关键参数节），progress 归档 ✅


 .pi/skills/comfyui/references/params.md | 2 ++
 .pi/tasks/easycache-test/progress.md    | 6 +++---
 2 files changed, 5 insertions(+), 3 deletions(-)

## ea9508917483788e0efc4587e856a513f7e4150f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T07:16:33-04:00
- Subject: [comfy-ops-补清理] T-20260816-08 残留 [STATE] 删除收尾（progress）


 .../progress.md"                                   | 32 ++++++++++++++++++++++
 1 file changed, 32 insertions(+)

## 33074910f8939b98a91cbc43b99aca89fe4a5918
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T06:10:02-04:00
- Subject: [easycache-test] T-20260814-01 EasyCache 成片档实测：wave/dance 同 seed 双跑（跳2/8步 采样1.25-1.38x）+ SSIM 0.86 + 对比图，结论待用户目视


 .pi/tasks/easycache-test/progress.md |  55 ++++++++++++
 output/compare/easycache_dance.png   | Bin 0 -> 3620397 bytes
 output/compare/easycache_wave.png    | Bin 0 -> 3338888 bytes
 scripts/h3_easycache_runner.py       | 165 +++++++++++++++++++++++++++++++++++
 4 files changed, 220 insertions(+)

## eced6043621d49d85ec19257c1b7a490c9864f23
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T03:41:51-04:00
- Subject: [img-qc-api-test] 主线收口：progress 状态 ✅（剩余低优先项保留）


 .pi/tasks/img-qc-api-test/progress.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## 8ca8bf5356a0ae973addbed6bf6bf3ae8f96ef3e
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T03:33:39-04:00
- Subject: [img-qc-api-test] 出图质检线上 VL API 选型定论：docs/24 + INDEX + progress


 .pi/tasks/img-qc-api-test/progress.md | 23 +++++++++----
 docs/24_vl_qc_api.md                  | 65 +++++++++++++++++++++++++++++++++++
 docs/INDEX.md                         |  3 +-
 3 files changed, 83 insertions(+), 8 deletions(-)

## e6ce3819a67fb5ed21473900d6f52e3f04b2bcf9
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T03:22:41-04:00
- Subject: img-qc-api-test: 首次联测通过（生图12s + vision_chat qwen3-vl-flash 识别全对 ~0.003元/张）+ 测试脚本


 .pi/tasks/img-qc-api-test/progress.md |  39 +++++++++++++
 scripts/img_qc_test.py                | 100 ++++++++++++++++++++++++++++++++++
 2 files changed, 139 insertions(+)

## 08d01a6f4bb9aced1ce8a6fb6c9ef97a246836cf
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T01:56:04-04:00
- Subject: [结论] 回填 27 条结论谱系：h3-speed(01-10)/h3-audio(11-14)/h3-prompt(15-19)/h3-models(20-27)（12 条收尾任务线定论）


 .pi/ledger/README.md                  |  50 +++++++++++++++--
 .pi/ledger/h3-audio.md                |  45 +++++++++++++++
 .pi/ledger/h3-models.md               |  75 +++++++++++++++++++++++++
 .pi/ledger/h3-prompt.md               |  54 ++++++++++++++++++
 .pi/ledger/h3-speed.md                | 102 ++++++++++++++++++++++++++++++++++
 .pi/tasks/ledger-backfill/progress.md |  38 +++++++++++++
 6 files changed, 358 insertions(+), 6 deletions(-)

## 56bffaa618d6662e564153b4b843a1bcb94cfc00
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T01:43:42-04:00
- Subject: [结论谱系] 规则落地：AGENTS.md 判定树加「定论→docs现行值+ledger演进史」分流；INDEX 加 .pi/ledger 导航


 AGENTS.md     | 3 ++-
 docs/INDEX.md | 4 ++--
 2 files changed, 4 insertions(+), 3 deletions(-)

## a25dc9fc5572daa9d16fe3723059c5142934ce7a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T01:37:21-04:00
- Subject: [结论谱系] 建 .pi/ledger/README.md：结论谱系系统定稿（对标 ADR superseded-by + TKG valid_from，append-only）


 .pi/ledger/README.md | 105 +++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 105 insertions(+)

## c4c4cd05fc05fb7229141e098e491da090df3882
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-16T00:18:42-04:00
- Subject: [宿主编排] ViMax阶段2拆解+设定图体系设计：stage2_consistency.md 落 .pi/tasks（过程产物）、设定图体系设计归位 docs/23（INDEX 收录）、下游登记 T-20260812-05


 .pi/tasks/refimage-system/progress.md         |  30 ++++
 .pi/tasks/vimax-dissect/progress.md           |  17 +-
 .pi/tasks/vimax-dissect/stage2_consistency.md | 161 +++++++++++++++++
 docs/23_refimage_system.md                    | 249 ++++++++++++++++++++++++++
 docs/INDEX.md                                 |   3 +-
 5 files changed, 456 insertions(+), 4 deletions(-)

## 14df98ed6cce73d7aa04e02da7dd680a4f50aa8a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T13:23:01-04:00
- Subject: [docs-audit-0816] docs 过时信息修正（80s TE 开销→11s 冷/两阶段已落地/Bernini 缺失注/停止命令）


 .pi/tasks/docs-audit-0816/progress.md | 22 ++++++++++++++++++++++
 docs/01_environment.md                |  2 +-
 docs/06_extras_install.md             |  3 ++-
 docs/10_h3_batch_optimization.md      |  8 +++-----
 docs/INDEX.md                         |  4 ++--
 5 files changed, 30 insertions(+), 9 deletions(-)

## e99b2c7fe0d09d2919109b44dbab7dff87a3ab6a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T13:10:14-04:00
- Subject: [cond-cache-node] docs/10 修正：TE 加载 ~80s→~11s/DiT ~15s（swap 污染说明）


 docs/10_h3_batch_optimization.md | 16 +++++++++-------
 1 file changed, 9 insertions(+), 7 deletions(-)

## 29e9c295ee390c0c918526c0bb3e1031e72870a8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T13:06:13-04:00
- Subject: [cond-cache-node] 第二步批处理脚本：N=3 省 ~37s（vs 单任务）


 .pi/tasks/cond-cache-node/progress.md |  12 ++-
 scripts/h3_two_stage_batch.py         | 181 ++++++++++++++++++++++++++++++++++
 2 files changed, 189 insertions(+), 4 deletions(-)

## 7d51c46e376f4e952cfa0546f77d529b34f4f875
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:59:56-04:00
- Subject: [cond-cache-node] 单任务耗时构成定准：sage 节点采样 1.65x，两阶段省 ~22s/任务


 .pi/tasks/cond-cache-node/progress.md |   4 ++
 scripts/h3_sage_breakdown.py          | 119 ++++++++++++++++++++++++++++++++++
 2 files changed, 123 insertions(+)

## 8ad191715d733d1a5ec8ef9e3d13a5caac52d7ef
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:48:51-04:00
- Subject: [cond-cache-node] T2 受控复测：112s/171s 为 swap 污染，真实 TE 冷 ~11s/DiT 冷 ~15s


 .pi/tasks/cond-cache-node/progress.md |  10 ++-
 scripts/h3_load_cost_probe.py         | 113 ++++++++++++++++++++++++++++++++++
 2 files changed, 121 insertions(+), 2 deletions(-)

## 482504bcb81a9a65fe388f49ac7a56fb3fc34f67
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:36:12-04:00
- Subject: [h3-new-findings-test] 六块文字补测：中文×时长×位置 4 组矩阵


 .pi/tasks/h3-new-findings-test/progress.md |  13 +++
 output/compare/text_ctrl4_matrix.png       | Bin 0 -> 3387816 bytes
 workflows/textctrl4_cn_3s.json             | 182 +++++++++++++++++++++++++++++
 workflows/textctrl4_cn_5s.json             | 182 +++++++++++++++++++++++++++++
 workflows/textctrl4_cn_5s_center.json      | 182 +++++++++++++++++++++++++++++
 workflows/textctrl4_en_5s_low3.json        | 182 +++++++++++++++++++++++++++++
 6 files changed, 741 insertions(+)

## bcd7a25cd1c402006104d347ae79b78aae004043
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:30:01-04:00
- Subject: [cond-cache-node] 自定义节点 Save/LoadMiniMaxH3Cond + API 验证免 TE 重载


 .pi/tasks/cond-cache-node/progress.md              |  40 +++++
 .pi/tasks/cond-roundtrip/progress.md               |   6 +-
 .../ComfyUI-MiniMax-H3-CondCache/README.md         |  40 +++++
 .../ComfyUI-MiniMax-H3-CondCache/__init__.py       |  32 ++++
 .../ComfyUI-MiniMax-H3-CondCache/cond_cache.py     | 148 ++++++++++++++++
 scripts/h3_condcache_verify.py                     | 193 +++++++++++++++++++++
 6 files changed, 457 insertions(+), 2 deletions(-)

## 17b8fb9edba2c75f80f6aaf59120ec899f6461ee
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:20:09-04:00
- Subject: [h3-new-findings-test] 六块文字收口（块5必要+块6提升+位置弱）落 params.md；本线完成 T-20260815-07 ✅


 .pi/skills/comfyui/references/params.md    |  1 +
 .pi/tasks/h3-new-findings-test/progress.md | 12 +++++-------
 2 files changed, 6 insertions(+), 7 deletions(-)

## 917f7be2b6053a989049673a37f58a3ea3f50f66
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:15:32-04:00
- Subject: vllm-h3-stream-analysis: 收尾——固化链路查证 + 声音纪律桥接 gap 落盘


 .pi/tasks/vllm-h3-stream-analysis/progress.md | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

## 27b720ed3c950ee3ba3a4577f5c8250ef09f840b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:13:23-04:00
- Subject: [h3-new-findings-test] 六块文字再测：换场景四组矩阵（A基准/B块5/C块6/D完整）+ 对比图


 .pi/tasks/h3-new-findings-test/progress.md |  17 ++-
 output/compare/text_ctrl3_matrix.png       | Bin 0 -> 3082198 bytes
 workflows/krea_text_ctrl3_firstframe.json  |  91 +++++++++++++++
 workflows/textctrl3_A_base.json            | 182 +++++++++++++++++++++++++++++
 workflows/textctrl3_B_block5.json          | 182 +++++++++++++++++++++++++++++
 workflows/textctrl3_C_block6.json          | 182 +++++++++++++++++++++++++++++
 workflows/textctrl3_D_full.json            | 182 +++++++++++++++++++++++++++++
 7 files changed, 834 insertions(+), 2 deletions(-)

## 2ab784056e7eb03723fb750fe02b6b0ed0b69e5b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T12:10:01-04:00
- Subject: [cond-roundtrip] H3 两阶段流水线前置验证：cond 往返+采样链路逐位一致 PASS，加载时间实测（TE 冷112s/热24s, DiT 冷171s/热34s）


 .pi/tasks/cond-roundtrip/progress.md |  41 +++++++
 scripts/h3_cond_roundtrip.py         | 143 ++++++++++++++++++++++++
 scripts/h3_load_time_sampling.py     | 206 +++++++++++++++++++++++++++++++++++
 3 files changed, 390 insertions(+)

## 3a6f3e6204d712386976ac0385a31dec4b317faa
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T11:55:09-04:00
- Subject: vllm-h3-stream-analysis: Cache-DiT 调研结果 + 音画耦合分层结论落盘


 .pi/tasks/vllm-h3-stream-analysis/progress.md | 27 +++++++++++++++++++++++++++
 1 file changed, 27 insertions(+)

## 2839d471fd3b7071128c6c70f7bf4a32f562162b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T11:44:29-04:00
- Subject: [h3-new-findings-test] 三方加速对比收口：精确计时（sage/sol持平~1.5-2x，Sol弃用）+ 加速策略落 params.md


 .pi/skills/comfyui/references/params.md    | 23 ++++++++++++++++++++++-
 .pi/tasks/h3-new-findings-test/progress.md | 22 +++++++++++++++-------
 2 files changed, 37 insertions(+), 8 deletions(-)

## 4291aa883b8ebe65ca9446eb1cd45f5ac6554e5d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-15T11:27:45-04:00
- Subject: [h3-new-findings-test] 三方加速对比跑批完成（纯/Sage/Sol×wave/dance）+ Hybrid 调研结论 + b20 放弃 + T-20260815-09 拆分


 .pi/tasks/h3-new-findings-test/progress.md |  93 ++++++++++++++
 output/compare/attn3way_dance.png          | Bin 0 -> 3669437 bytes
 output/compare/attn3way_wave.png           | Bin 0 -> 3288862 bytes
 workflows/attn3way_dance_plain.json        | 172 +++++++++++++++++++++++++
 workflows/attn3way_dance_sage.json         | 183 +++++++++++++++++++++++++++
 workflows/attn3way_dance_sol.json          | 193 +++++++++++++++++++++++++++++
 workflows/attn3way_wave_plain.json         | 172 +++++++++++++++++++++++++
 workflows/attn3way_wave_sage.json          | 183 +++++++++++++++++++++++++++
 workflows/attn3way_wave_sol.json           | 193 +++++++++++++++++++++++++++++
 9 files changed, 1189 insertions(+)

## 16119390da48bafc60bc6d4aa0bd9215b4f7f761
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T06:22:00-04:00
- Subject: [vimax-dissect] 阶段1 产出（codex）：ViMax 模块地图 8 模块 + 对标点 8 条


 .pi/tasks/vimax-dissect/progress.md | 26 ++++++++++++++++++++++++++
 1 file changed, 26 insertions(+)

## fc4b9076feb787d851e0e4813d51efcb4f10c380
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T06:19:15-04:00
- Subject: [vimax-dissect] 任务线认领：进度文件初始化


 .pi/tasks/vimax-dissect/progress.md | 23 +++++++++++++++++++++++
 1 file changed, 23 insertions(+)

## 5d1d710ae8be5760a5b5c07d0bc4a30eb071c809
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T03:09:53-04:00
- Subject: [collab] 开场清单第3步移除：recall [STATE]+TODO 对账已全局化，项目只留专属步骤


 AGENTS.md | 7 ++++---
 1 file changed, 4 insertions(+), 3 deletions(-)

## d6197169be191e4af5971bc8db5c5bfbf9800168
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T02:49:01-04:00
- Subject: [web-shotlist-tool] 方案A落地：API schema单源（shared/apiSchema.ts）+ server消费shared + 前端z.input类型推导 + 类型漏洞修复（shotStyle枚举/A0Dialog缺参）


 .pi/tasks/web-shotlist-tool/progress.md            |  22 ++--
 web-shotlist/apps/server/src/routes/draft.ts       |   9 +-
 web-shotlist/apps/server/src/routes/entities.ts    |  60 +++--------
 web-shotlist/apps/server/src/routes/projects.ts    |  65 +++--------
 web-shotlist/apps/web/src/App.tsx                  |   2 +-
 .../web/src/components/shotlist/ShotListView.tsx   |   6 +-
 web-shotlist/apps/web/src/lib/api.ts               |  37 ++++---
 web-shotlist/packages/shared/src/apiSchema.ts      | 120 +++++++++++++++++++++
 web-shotlist/packages/shared/src/index.ts          |   1 +
 9 files changed, 192 insertions(+), 130 deletions(-)

## c8d4a811ff9a56f14f1c3ad3d8d7d69c242c36e3
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T02:46:49-04:00
- Subject: [mc-test] 会话收尾：状态更新+交接点（第二批完成待验收，队列已释放，目录已迁 .pi/tasks/）


 .pi/tasks/mc-test/progress.md | 10 +++++++++-
 1 file changed, 9 insertions(+), 1 deletion(-)

## 1d31688569950a8470a5aac1e0b51582168315c2
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T02:41:33-04:00
- Subject: [collab] .pi/agents 旧路径放迁移路标（.txt 避开 pi agent 扫描），防进行中旧会话重建目录


 ".pi/agents/\350\277\201\347\247\273\350\257\264\346\230\216.txt" | 7 +++++++
 1 file changed, 7 insertions(+)

## fad25ffbac046cad683ce88efa2729c8923b2adb
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T02:38:10-04:00
- Subject: [collab] 协作纪律压缩为 multi-agent-collab skill 引用；进度目录 .pi/agents→.pi/tasks（避开 pi agent 配置目录）


 .pi/{agents => tasks}/PROGRESS_TEMPLATE.md         |  0
 .pi/{agents => tasks}/bgm-pos-control/progress.md  |  2 +-
 .../comfyui-032-verify/progress.md                 |  2 +-
 .pi/{agents => tasks}/context-opt/progress.md      |  0
 .pi/{agents => tasks}/docs-opt/progress.md         |  2 +-
 .pi/{agents => tasks}/h3-params/progress.md        |  0
 .pi/{agents => tasks}/h3-patch-test/progress.md    |  0
 .pi/{agents => tasks}/h3-prompt-agent/progress.md  |  0
 .pi/{agents => tasks}/h3-today-testing/progress.md |  2 +-
 .pi/{agents => tasks}/h3-turbo-pilot/progress.md   |  0
 .pi/{agents => tasks}/mc-test/progress.md          |  2 +-
 .pi/{agents => tasks}/prompt-audio/progress.md     |  0
 .../seedance-h3-verify/progress.md                 |  2 +-
 .pi/{agents => tasks}/speech-video/progress.md     |  2 +-
 .../web-shotlist-tool/progress.md                  |  2 +-
 AGENTS.md                                          | 29 +++-------------------
 docs/12_speech_to_video_pipeline.md                |  6 ++---
 docs/22_shotlist_web_tool.md                       |  2 +-
 18 files changed, 16 insertions(+), 37 deletions(-)

## c9e378722c850a29cbbce0399071b1f086409dc8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T02:25:56-04:00
- Subject: [companion-drone] 归档：进度目录删除（git 历史保留，[STATE]+经验已落 mem0）


 .pi/agents/companion-drone/progress.md | 28 ----------------------------
 1 file changed, 28 deletions(-)

## 183efe2ff72d0a23864c1d0594ce14907c47cbff
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-13T02:25:56-04:00
- Subject: [companion-drone] 任务完成：KREA 陪伴式预警无人机概念图 3 变体 + 进度归档标记


 .pi/agents/companion-drone/progress.md | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)

## fa0513afcd1703e39b8e79aec5c8235e6a72439d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T23:49:32-04:00
- Subject: [web-shotlist-tool] 修复：实体新建 e=null trim 崩溃（React 整树冻结→按钮全部失效）+ 侧滑面板 pointer-events 透传主界面可交互 + ErrorBoundary 兜底 + 保存/删除错误提示


 web-shotlist/apps/web/src/App.tsx                  | 37 ++++++++++++++++++++--
 .../web/src/components/entity/EntityDialogs.tsx    | 33 ++++++++++++-------
 2 files changed, 55 insertions(+), 15 deletions(-)

## 75eea187a143db585bb7fa9252837e9173541f1b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T16:03:51-04:00
- Subject: [web-shotlist-tool] 进度更新：实体系统升级+Qwen3-TTS 接入完成


 .pi/agents/web-shotlist-tool/progress.md | 7 +++++++
 1 file changed, 7 insertions(+)

## cdcce83c1a31a07fed06d3bc291822ccbf1364a3
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T14:25:43-04:00
- Subject: [web-shotlist-tool] Qwen3-TTS 音色生成接入：独立 venv 推理脚本+voice 任务 runner+前端三模式 UI（custom/design/clone）


 web-shotlist/apps/server/src/index.ts              |   8 ++
 web-shotlist/apps/server/src/routes/entities.ts    |  24 +++++
 web-shotlist/apps/server/src/voice.ts              |  62 +++++++++++++
 .../web/src/components/entity/EntityDialogs.tsx    |  66 +++++++++++++-
 web-shotlist/apps/web/src/lib/api.ts               |   4 +
 web-shotlist/scripts/qwen_tts_gen.py               | 101 +++++++++++++++++++++
 6 files changed, 262 insertions(+), 3 deletions(-)

## 89b81ebee718699e92f69babaf9c866939f5a46d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T13:13:26-04:00
- Subject: [mc-test] 第二批：同场景连续动作测试（相同段1 对比 baseline vs chain），待用户目视验收


 .pi/agents/mc-test/progress.md                     | 10 ++++
 experiments/mc_test/mc_same_cases.json             | 63 ++++++++++++++++++++++
 .../mc_test/mc_same_cases.json.results.json        | 23 ++++++++
 3 files changed, 96 insertions(+)

## 9562f1099e9f1f0fb5d29355bc090dad49aecb84
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T13:07:26-04:00
- Subject: [web-shotlist-tool] 实体系统升级：侧滑面板+星级+变体+关系编辑+全局风格（用户决策 2026-08-14）


 web-shotlist/apps/server/src/art.ts                |  19 +-
 web-shotlist/apps/server/src/entities.ts           |  31 +-
 web-shotlist/apps/server/src/index.ts              |   4 +-
 web-shotlist/apps/server/src/routes/entities.ts    |  31 +-
 web-shotlist/apps/server/src/style.ts              |  33 ++
 web-shotlist/apps/web/src/App.tsx                  |   7 +-
 .../apps/web/src/components/ProjectDialogs.tsx     |  51 ++-
 .../web/src/components/entity/EntityDialogs.tsx    | 356 ++++++++++++++++++---
 .../web/src/components/sidebar/EntityPanel.tsx     |   2 +-
 web-shotlist/apps/web/src/lib/api.ts               |   7 +-
 web-shotlist/packages/shared/src/types.ts          |  19 +-
 11 files changed, 487 insertions(+), 73 deletions(-)

## 0fd43412c3ff10eb10a17768399be66f9c863afe
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:49:09-04:00
- Subject: [mc-test] MC 跨段连续性首批跑批：两段链式 vs 静态锚（corr 0.739 vs 0.277），待用户验收


 .pi/agents/mc-test/progress.md                 |  13 ++
 experiments/mc_test/mc_cases.json              |  45 +++++
 experiments/mc_test/mc_cases.json.results.json |  16 ++
 scripts/h3_mc_runner.py                        | 234 +++++++++++++++++++++++++
 4 files changed, 308 insertions(+)

## cee868bf80c604ff9b1c1e683c3ee0cc5fb6aa8f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:43:05-04:00
- Subject: [web-shotlist-tool] 体验收尾：顶栏任务指示+项目重命名+导入导出+设定图按实体类型优化


 web-shotlist/apps/server/src/art.ts                |  27 +++--
 web-shotlist/apps/server/src/index.ts              |   4 +-
 web-shotlist/apps/server/src/routes/entities.ts    |   2 +-
 web-shotlist/apps/server/src/routes/projects.ts    |  48 ++++++++-
 web-shotlist/apps/server/src/store.ts              |  48 ++++++++-
 web-shotlist/apps/web/src/App.tsx                  |  71 ++++++++++++-
 .../apps/web/src/components/ProjectDialogs.tsx     | 116 +++++++++++++++++++++
 web-shotlist/apps/web/src/lib/api.ts               |   3 +
 web-shotlist/packages/shared/src/types.ts          |  13 +++
 9 files changed, 318 insertions(+), 14 deletions(-)

## 532b5679225dcabb078a4ed4673ea05088b779d2
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:35:38-04:00
- Subject: [web-shotlist-tool] 恢复上下文：mem0 整理（STATE 更新/去重 12 条/建 mc-test STATE）+ 进度更新


 .pi/agents/mc-test/progress.md           | 7 ++++++-
 .pi/agents/web-shotlist-tool/progress.md | 4 ++++
 2 files changed, 10 insertions(+), 1 deletion(-)

## 621917b1d4edee253a90c27c6aeccfb12637fb37
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:31:12-04:00
- Subject: [web-shotlist-tool] 阶段收尾落盘（主线告一段落）


 .pi/agents/web-shotlist-tool/progress.md | 22 ++++++++++++++--------
 1 file changed, 14 insertions(+), 8 deletions(-)

## 498bee626a92f13b1a5a21ab66a711005cd60ad4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:30:52-04:00
- Subject: [web-shotlist-tool] progress 更新（输入源联动完成）


 .pi/agents/web-shotlist-tool/progress.md | 16 +++++++++++-----
 1 file changed, 11 insertions(+), 5 deletions(-)

## 32043adafb28bd86b50764228ad93d33a69ed02d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:30:42-04:00
- Subject: [web-shotlist-tool] 输入源真实化+提示词联动（docs/22 第4步）

- parseRefMapping：<Picture N> ↔ <Subject N> ↔ 实体（role_cards 顺序）映射解析（兼容 LLM 句式变体 reference image / reference still image）
- InputsSidebar 参考图墙真实化：每张参考图显示实体设定图缩略图（无图占位+引导），标注 Picture N · Subject N · 实体名
- 联动：hover 提示词 ref chip → 对应参考图卡片高亮（ring）；点击卡片 → 提示词对应引用闪烁 1.5s
- PromptHighlight 支持 onRefHover/activeRef（外部高亮）
- 实测映射：Alya 项目 prompt → Picture1↔Subject1↔alya_v1

 .../web/src/components/prompt/PromptHighlight.tsx  | 34 +++++++-
 .../apps/web/src/components/prompt/PromptPage.tsx  | 14 +++-
 .../web/src/components/sidebar/InputsSidebar.tsx   | 95 ++++++++++++++++++----
 .../packages/shared/src/promptTokenizer.ts         | 27 ++++++
 web-shotlist/scripts/test_mapping.ts               |  9 ++
 5 files changed, 155 insertions(+), 24 deletions(-)

## 7097000ad3921a8b8eebda8e0073c31b2feeffce
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:25:28-04:00
- Subject: [comfyui-032-verify] 收尾：V5/V6 验收通过、V7 风格发现、对比图按新约定存 ComfyUI output


 .pi/agents/comfyui-032-verify/progress.md | 8 ++++++--
 1 file changed, 6 insertions(+), 2 deletions(-)

## 496e49c58432ed6996c8e105f61db9c571c58a1a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:23:39-04:00
- Subject: [web-shotlist-tool] progress 更新（队列/资源/门禁/迁移完成）


 .pi/agents/web-shotlist-tool/progress.md | 25 +++++++++++++++++--------
 1 file changed, 17 insertions(+), 8 deletions(-)

## a0dc81e4cc0fa11a1959deda711de1d8c94a06bd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T12:23:27-04:00
- Subject: [web-shotlist-tool] 任务队列接线+实体资源系统+渲染门禁+角色卡迁移

- 单实例任务队列（tasks.ts）：extract/art 走任务式（提交立即返回 taskId，2s 轮询，冲突 409）；前端 useTaskPoll
- 实体资源系统：data/entities/assets/<id>/（art/voice/file）；上传（multipart）/试听/删除/静态服务；设定图生成后移入资产目录；三态徽章（文字✓/画面✓/声音✓）列表可观测
- 渲染门禁：generate-prompt 前检查引用实体（剧本参数头+拍摄本+audio_refs 三来源，防 LLM 丢 role_cards）——文字不合格=422 硬阻塞（无 fallback），画面/声音缺失=警告
- 角色卡迁移：experiments/shotlist/rolecards → 实体库一键导入（外观节→appearance，行为/场景→description）；老项目不再被无 fallback 阻断
- 实体单体重刷 API（LLM 精修单个实体卡）
- 踩坑：edit 转义层数导致正则损坏（\s→\s）；catch 块访问 try 块 const 静默解析到全局 window.name(void)
- Motion Context 任务线孵化（.pi/agents/mc-test/）：节点已 clone（未重启，等 seedance 线释放），测试计划已写

 .pi/agents/mc-test/progress.md                     |  30 +++++
 web-shotlist/apps/server/src/art.ts                |  38 +++---
 web-shotlist/apps/server/src/assets.ts             |  86 +++++++++++++
 web-shotlist/apps/server/src/entities.ts           |  59 ++++++++-
 web-shotlist/apps/server/src/gate.ts               |  66 ++++++++++
 web-shotlist/apps/server/src/index.ts              |  22 ++++
 web-shotlist/apps/server/src/routes/entities.ts    | 132 +++++++++++++++----
 web-shotlist/apps/server/src/routes/projects.ts    |  12 +-
 web-shotlist/apps/web/src/App.tsx                  |   4 +-
 .../web/src/components/entity/EntityDialogs.tsx    | 141 +++++++++++++++++----
 .../web/src/components/entity/ExtractDialog.tsx    | 120 ++++++++++++------
 .../web/src/components/sidebar/EntityPanel.tsx     |  46 ++++++-
 web-shotlist/apps/web/src/lib/api.ts               |  20 ++-
 web-shotlist/apps/web/src/lib/useTaskPoll.ts       |  50 ++++++++
 14 files changed, 705 insertions(+), 121 deletions(-)

## 4b289d126ff03480ecd8a3c7a8a43adb37cd75f5
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T11:06:25-04:00
- Subject: [web-shotlist-tool] progress 更新（自动策略+实体注入+ref2va）


 .pi/agents/web-shotlist-tool/progress.md | 17 ++++++++++++++---
 1 file changed, 14 insertions(+), 3 deletions(-)

## 33f0d78bc5709876d00abf9ec13a2867b0cf80fb
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T11:06:15-04:00
- Subject: [web-shotlist-tool] chain/shot_style 自动推断 + 实体库角色卡注入 + 默认 ref2va

- 用户决策 2026-08-12：默认全部 ref2va（靠实体连接保证一致性）；fl2va 除非解决一致性不引入；衔接暂不考虑
- chain/shot_style 参数头改自动默认：表单加'自动（推荐）'；工具 A 不写时提示 LLM 自动推断（chain 按段位置：第一段 first_static/多段中间 firstlast_bridge/散段 independent；shot_style 按剧本内容自决）——实测 auto 出 first_static+2镜
- 拍摄本页生成后微调：跨段策略下拉（生成后可切换保存，提示词合成生效）+ 镜头策略下拉（重新生成时应用）
- 工具 A/B 角色卡注入改为实体库优先（data/entities/ 外观/声音/介绍），缺失 fallback rolecards 目录——实体连接一致性落地
- PromptPage 默认 ref2va（未生成时高亮 ref2va 按钮）
- ref2va 速度实测答复：提示词生成 87s vs i2va 62s；渲染 150-165s/段 vs fl2va 67s（慢 2.5 倍但一致性收益大）

 web-shotlist/apps/server/package.json              |  1 +
 web-shotlist/apps/server/src/entities.ts           | 24 +++++-
 web-shotlist/apps/server/src/tasks.ts              | 87 ++++++++++++++++++++++
 web-shotlist/apps/server/src/tools/promptStage2.ts | 16 +---
 web-shotlist/apps/server/src/tools/shotlistGen.ts  | 27 +++----
 web-shotlist/apps/web/src/App.tsx                  |  8 +-
 .../apps/web/src/components/prompt/PromptPage.tsx  |  6 +-
 .../web/src/components/script/ScriptHeadForm.tsx   | 17 ++++-
 .../web/src/components/shotlist/ShotListView.tsx   | 40 +++++++++-
 web-shotlist/pnpm-lock.yaml                        | 29 ++++++++
 10 files changed, 215 insertions(+), 40 deletions(-)

## 3f52daf8765b93ad7ddcd84b81a80fe97147a045
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T09:43:22-04:00
- Subject: [seedance-h3-verify] Seedance 7条提示词经验 H3 验证完成（34条AB对比：T2/T7成立、T1部分、T3/T4/T5不成立、T6相反=强调）


 .pi/agents/seedance-h3-verify/progress.md          |  67 ++++++++++++
 experiments/seedance_verify/analysis.json          |  82 +++++++++++++++
 experiments/seedance_verify/cases.json             |  55 ++++++++++
 .../seedance_verify/cases.json.results.json        | 114 +++++++++++++++++++++
 experiments/seedance_verify/cases2.json            |  38 +++++++
 .../seedance_verify/cases2.json.results.json       |  72 +++++++++++++
 experiments/seedance_verify/cases3.json            |  32 ++++++
 .../seedance_verify/cases3.json.results.json       |  58 +++++++++++
 experiments/seedance_verify/compare_T1_long.png    | Bin 0 -> 3640175 bytes
 experiments/seedance_verify/compare_T1_short.png   | Bin 0 -> 3019099 bytes
 experiments/seedance_verify/compare_T1_xlong.png   | Bin 0 -> 3743276 bytes
 experiments/seedance_verify/compare_T2_bad.png     | Bin 0 -> 3050844 bytes
 experiments/seedance_verify/compare_T2_good.png    | Bin 0 -> 3006258 bytes
 experiments/seedance_verify/compare_T3_bad.png     | Bin 0 -> 3434288 bytes
 experiments/seedance_verify/compare_T3_good.png    | Bin 0 -> 3523318 bytes
 experiments/seedance_verify/compare_T3r_a.png      | Bin 0 -> 3000683 bytes
 experiments/seedance_verify/compare_T3r_b.png      | Bin 0 -> 3221344 bytes
 experiments/seedance_verify/compare_T3r_c.png      | Bin 0 -> 3136841 bytes
 experiments/seedance_verify/compare_T4_ctl.png     | Bin 0 -> 3529559 bytes
 experiments/seedance_verify/compare_T4_neg.png     | Bin 0 -> 3417124 bytes
 experiments/seedance_verify/compare_T4_pos.png     | Bin 0 -> 3446793 bytes
 experiments/seedance_verify/compare_T4r_ctl.png    | Bin 0 -> 2937832 bytes
 experiments/seedance_verify/compare_T4r_neg.png    | Bin 0 -> 2945776 bytes
 experiments/seedance_verify/compare_T4r_pos.png    | Bin 0 -> 2934205 bytes
 experiments/seedance_verify/compare_T5_fast.png    | Bin 0 -> 2751822 bytes
 experiments/seedance_verify/compare_T5_phys.png    | Bin 0 -> 2906986 bytes
 experiments/seedance_verify/compare_T5r2_base.png  | Bin 0 -> 3069666 bytes
 experiments/seedance_verify/compare_T5r2_fast.png  | Bin 0 -> 3173081 bytes
 experiments/seedance_verify/compare_T5r_fast.png   | Bin 0 -> 3462036 bytes
 experiments/seedance_verify/compare_T5r_phys.png   | Bin 0 -> 3673815 bytes
 experiments/seedance_verify/compare_T6_bad.png     | Bin 0 -> 4080057 bytes
 experiments/seedance_verify/compare_T6_good.png    | Bin 0 -> 3708638 bytes
 .../seedance_verify/compare_T6r2_detail.png        | Bin 0 -> 3956541 bytes
 experiments/seedance_verify/compare_T6r2_mid.png   | Bin 0 -> 3584252 bytes
 experiments/seedance_verify/compare_T6r2_none.png  | Bin 0 -> 3575514 bytes
 experiments/seedance_verify/compare_T6r_a.png      | Bin 0 -> 3912557 bytes
 experiments/seedance_verify/compare_T6r_b.png      | Bin 0 -> 3685302 bytes
 experiments/seedance_verify/compare_T6r_c.png      | Bin 0 -> 3638060 bytes
 experiments/seedance_verify/compare_T7_bad.png     | Bin 0 -> 3711981 bytes
 experiments/seedance_verify/compare_T7_good.png    | Bin 0 -> 3513419 bytes
 experiments/seedance_verify/compare_T7r_bad.png    | Bin 0 -> 2802013 bytes
 experiments/seedance_verify/compare_T7r_good.png   | Bin 0 -> 2830601 bytes
 experiments/seedance_verify/curve_T1_long.png      | Bin 0 -> 21352 bytes
 experiments/seedance_verify/curve_T1_short.png     | Bin 0 -> 20245 bytes
 experiments/seedance_verify/curve_T1_xlong.png     | Bin 0 -> 28182 bytes
 experiments/seedance_verify/curve_T2_bad.png       | Bin 0 -> 18897 bytes
 experiments/seedance_verify/curve_T2_good.png      | Bin 0 -> 23036 bytes
 experiments/seedance_verify/curve_T3_bad.png       | Bin 0 -> 20276 bytes
 experiments/seedance_verify/curve_T3_good.png      | Bin 0 -> 21554 bytes
 experiments/seedance_verify/curve_T3r_a.png        | Bin 0 -> 22044 bytes
 experiments/seedance_verify/curve_T3r_b.png        | Bin 0 -> 18932 bytes
 experiments/seedance_verify/curve_T3r_c.png        | Bin 0 -> 19910 bytes
 experiments/seedance_verify/curve_T4_ctl.png       | Bin 0 -> 19009 bytes
 experiments/seedance_verify/curve_T4_neg.png       | Bin 0 -> 19936 bytes
 experiments/seedance_verify/curve_T4_pos.png       | Bin 0 -> 22409 bytes
 experiments/seedance_verify/curve_T4r_ctl.png      | Bin 0 -> 28653 bytes
 experiments/seedance_verify/curve_T4r_neg.png      | Bin 0 -> 27780 bytes
 experiments/seedance_verify/curve_T4r_pos.png      | Bin 0 -> 27475 bytes
 experiments/seedance_verify/curve_T5_fast.png      | Bin 0 -> 17153 bytes
 experiments/seedance_verify/curve_T5_phys.png      | Bin 0 -> 20481 bytes
 experiments/seedance_verify/curve_T5r2_base.png    | Bin 0 -> 25964 bytes
 experiments/seedance_verify/curve_T5r2_fast.png    | Bin 0 -> 25290 bytes
 experiments/seedance_verify/curve_T5r_fast.png     | Bin 0 -> 23175 bytes
 experiments/seedance_verify/curve_T5r_phys.png     | Bin 0 -> 38280 bytes
 experiments/seedance_verify/curve_T6_bad.png       | Bin 0 -> 36219 bytes
 experiments/seedance_verify/curve_T6_good.png      | Bin 0 -> 29177 bytes
 experiments/seedance_verify/curve_T6r2_detail.png  | Bin 0 -> 33850 bytes
 experiments/seedance_verify/curve_T6r2_mid.png     | Bin 0 -> 34170 bytes
 experiments/seedance_verify/curve_T6r2_none.png    | Bin 0 -> 32957 bytes
 experiments/seedance_verify/curve_T6r_a.png        | Bin 0 -> 30986 bytes
 experiments/seedance_verify/curve_T6r_b.png        | Bin 0 -> 29796 bytes
 experiments/seedance_verify/curve_T6r_c.png        | Bin 0 -> 28498 bytes
 experiments/seedance_verify/curve_T7_bad.png       | Bin 0 -> 21697 bytes
 experiments/seedance_verify/curve_T7_good.png      | Bin 0 -> 22606 bytes
 experiments/seedance_verify/curve_T7r_bad.png      | Bin 0 -> 28468 bytes
 experiments/seedance_verify/curve_T7r_good.png     | Bin 0 -> 33981 bytes
 experiments/seedance_verify/overview_all.png       | Bin 0 -> 54484517 bytes
 experiments/seedance_verify/run.log                |  34 ++++++
 experiments/seedance_verify/run2.log               |  22 ++++
 experiments/seedance_verify/run3.log               |  18 ++++
 scripts/h3_seedance_analyze.py                     |  95 +++++++++++++++++
 81 files changed, 687 insertions(+)

## 358b8a2657600a157fd1df7089c9fff065085e5b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T09:05:07-04:00
- Subject: [web-shotlist-tool] progress 更新（三页重构+设定图）


 .pi/agents/web-shotlist-tool/progress.md | 19 ++++++++++++++-----
 1 file changed, 14 insertions(+), 5 deletions(-)

## 17bf6958cdfdeec0a29306e52e2ed65766efbb1b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T09:04:56-04:00
- Subject: [web-shotlist-tool] 三大步骤页重构 + 设定图生成

- 信息架构：0/1/2 三个大选项卡（顶栏 Tab 主入口）：①剧本（剧本+实体+设定图）②拍摄本（镜头+关联实体）③H3 提示词（调试检查+输入源+视频预览占位 V2）
- 页 0：剧本编辑（参数表单+正文+AI 创作弹层）+ 实体库（AI 抽取/新建/详情含设定图）
- 页 1：时间轴+两列卡片流；[Shot N] 跨页跳转高亮；镜头主体点击 → 实体库关联/替换（保存回 shotlist）
- 页 2：提示词标色+校验+复制；[Shot N] chip → 跳拍摄本镜头；ref chip → 实体选择器；输入源侧栏；视频生成预览占位（V2）
- 设定图生成：实体详情内 ANIMA t2i（通用角色无 LoRA，移除模板角色 LoRA 节点）；ComfyUI 在线检测/提交/轮询/图片静态服务；实测 106s 出图
- 实体弹层全局化（EntityDialogHost + EntityPickerDialog），三页共用
- 删除旧布局组件（SidebarPanel/ShotList/OutputPanel/A0View）

 web-shotlist/apps/server/src/art.ts                |  99 +++++++++++
 web-shotlist/apps/server/src/routes/entities.ts    |  32 ++++
 web-shotlist/apps/web/src/App.tsx                  | 142 ++++++++-------
 .../apps/web/src/components/a0/A0Dialog.tsx        |  90 ++++++++++
 web-shotlist/apps/web/src/components/a0/A0View.tsx | 118 ------------
 .../web/src/components/entity/EntityDialogs.tsx    | 169 ++++++++++++++++++
 .../web/src/components/entity/ExtractDialog.tsx    |  67 +++++++
 .../apps/web/src/components/prompt/OutputPanel.tsx |  74 --------
 .../web/src/components/prompt/PromptHighlight.tsx  |  22 ++-
 .../apps/web/src/components/prompt/PromptPage.tsx  | 120 +++++++++++++
 .../apps/web/src/components/script/ScriptPanel.tsx |  12 +-
 .../apps/web/src/components/shotlist/ShotCard.tsx  |   8 +-
 .../apps/web/src/components/shotlist/ShotList.tsx  |  38 ----
 .../web/src/components/shotlist/ShotListView.tsx   | 117 ++++++++++++
 .../web/src/components/sidebar/EntityPanel.tsx     | 197 ++-------------------
 .../{SidebarPanel.tsx => InputsSidebar.tsx}        |  60 ++-----
 web-shotlist/apps/web/src/lib/api.ts               |   4 +
 web-shotlist/apps/web/src/lib/store.ts             |  25 ++-
 web-shotlist/packages/shared/src/index.ts          |   1 +
 19 files changed, 859 insertions(+), 536 deletions(-)

## 96752fae583bba981a9aab5b170bc48fdb36b0aa
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T08:43:34-04:00
- Subject: [web-shotlist-tool] progress 更新（用户反馈修复）


 .pi/agents/web-shotlist-tool/progress.md | 15 ++++++++++++---
 1 file changed, 12 insertions(+), 3 deletions(-)

## 6c3775e79b86842c141ed599b77ac060efd8c913
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T08:43:25-04:00
- Subject: [web-shotlist-tool] 修复 A0 剧本导入不可见 + 实体抽取流程

- 根因：A0 模板输出 '--- ' 带尾空格 → parseScript 不匹配 → 应用后剧本空白
- 修：模板去除首尾 '--- ' 空格；parseScript/serializeScript 正则容忍 '--- '（LLM/手写兼容）
- A0 模板正文约束：禁 markdown 符号/时间码，按镜头段落写
- 实体抽取：修 state 共用 bug（无剧本时两个 textarea 同绑一个 state）；无剧本时明确引导粘贴；世界观标注建议填写；成功后显示生成的实体名单
- 删除 AI 抽取测试遗留实体（Alya/Yuki/天台）——实体库初始为空，只能从剧本+世界观获得
- 顶栏按钮 ✍ 改文字'创作'（✍ 渲染异常）；A0 页布局 min-w-0 防挤压
- V2 预留：外部实体导入/多设定适配（source 字段已存）

 web-shotlist/apps/server/src/tools/draftGen.ts     |  7 ++--
 web-shotlist/apps/web/src/App.tsx                  |  2 +-
 web-shotlist/apps/web/src/components/a0/A0View.tsx |  8 ++---
 .../web/src/components/sidebar/EntityPanel.tsx     | 39 ++++++++++++++--------
 web-shotlist/packages/shared/src/scriptSchema.ts   |  4 +--
 5 files changed, 36 insertions(+), 24 deletions(-)

## 42345a0ceb31ce6a68904b267e511996c5dd1ec2
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T08:31:16-04:00
- Subject: [web-shotlist-tool] progress 更新（+新建/实体卡/A0 完成）


 .pi/agents/web-shotlist-tool/progress.md | 16 ++++++++++++----
 1 file changed, 12 insertions(+), 4 deletions(-)

## bd8ef4744bd4430acb54ddfa8b6131b22fc1e657
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T08:31:04-04:00
- Subject: [web-shotlist-tool] +新建对话框/AI实体卡/工具A0创作页

- 新建简化为 + 按钮（顶栏不占空间）：对话框输入名字；空名默认未命名剧本；重名自动加数字
- 实体卡系统 V1：外观+声音+介绍 结构化卡（data/entities/<id>.md frontmatter）；CRUD API + AI 抽取（世界观+剧本→实体卡，实测 31s 出 Alya/Yuki/天台）；侧栏 Tab（输入源/实体）+ 详情/编辑/删除弹层
- 工具 A0 创作页（顶栏主入口 ✍）：输入点子 → 长度档（短8s/中12s/长20s）+ 世界观开关 → 世界观手册+剧本 YAML → 应用到新项目
- 修复：shot_style 参数头被工具 A 忽略（改读 head 值）；A0 模板约束 duration 数字/shot_style 枚举
- scene 预设=首帧图库真实子目录（beach/forest/night/night_street/portrait/stage/multi）+ 惯例补充

 web-shotlist/apps/server/src/entities.ts           | 124 ++++++++++++
 web-shotlist/apps/server/src/index.ts              |   2 +
 web-shotlist/apps/server/src/routes/draft.ts       |  24 +++
 web-shotlist/apps/server/src/routes/entities.ts    |  77 +++++++-
 web-shotlist/apps/server/src/store.ts              |  30 ++-
 web-shotlist/apps/server/src/tools/draftGen.ts     |  82 ++++++++
 .../apps/server/src/tools/entityExtract.ts         |  76 ++++++++
 web-shotlist/apps/server/src/tools/shotlistGen.ts  |   2 +-
 web-shotlist/apps/web/src/App.tsx                  |  68 ++++---
 .../apps/web/src/components/NewProjectDialog.tsx   |  51 +++++
 web-shotlist/apps/web/src/components/a0/A0View.tsx | 118 ++++++++++++
 .../web/src/components/sidebar/EntityPanel.tsx     | 212 +++++++++++++++++++++
 .../web/src/components/sidebar/SidebarPanel.tsx    |  29 ++-
 web-shotlist/apps/web/src/lib/api.ts               |  11 +-
 web-shotlist/packages/shared/src/types.ts          |  21 +-
 15 files changed, 870 insertions(+), 57 deletions(-)

## 013aaf0b45807c972d643293a0b588ce499533cf
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T08:07:29-04:00
- Subject: [web-shotlist-tool] progress 更新（参数头表单/自动保存/回收站完成）


 .pi/agents/web-shotlist-tool/progress.md | 19 +++++++++++++++----
 1 file changed, 15 insertions(+), 4 deletions(-)

## 82353d313bdf29607c8a3c1bd58fa548801ee884
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T08:07:19-04:00
- Subject: [web-shotlist-tool] 参数头模板化表单+自动保存+回收站

- 参数头表单（ScriptHeadForm）：title/style/ratio/scene/duration 快捷档/chain/shot_style/sound/no_bgm/role_cards 多选（扫描 rolecards）/audio_refs 键值对
- 双向绑定：表单修改→重写参数头（yaml merge 保留未知字段如 branch）；文本修改→防抖 500ms 解析回填；解析错误红条不覆盖文本
- 自动保存：剧本改动 2s 防抖 PUT + 保存状态指示（已保存/保存中/未保存）；生成前强制落盘（修复旧剧本生成 bug）
- 新建项目预填剧本模板（scriptTemplate）
- 回收站（次要入口）：顶栏右侧 项目操作▾(删除→确认→回收站) + 🕘回收站(角标数)；恢复/永久删除(确认)
- scene 预设=首帧图库真实子目录（beach/forest/night/...）+ 惯例补充
- 布局：左列 280→340px、右列 240→260px；输出区 260px
- 修复：Fastify 空 body 400（req 无 body 不带 Content-Type）；YAML 空值 null 宽容（zod preprocess）；audio_refs 输入中不触发序列化

 web-shotlist/apps/server/src/routes/projects.ts    |  36 +++-
 web-shotlist/apps/server/src/store.ts              |  73 ++++++-
 web-shotlist/apps/web/src/App.tsx                  | 126 +++++++++++-
 .../web/src/components/script/ScriptHeadForm.tsx   | 221 +++++++++++++++++++++
 .../apps/web/src/components/script/ScriptPanel.tsx |  82 ++++++--
 .../apps/web/src/components/trash/TrashPanel.tsx   |  80 ++++++++
 web-shotlist/apps/web/src/components/ui/dialog.tsx |  76 +++++++
 web-shotlist/apps/web/src/lib/api.ts               |  11 +-
 web-shotlist/apps/web/src/lib/store.ts             |   7 +
 web-shotlist/packages/shared/src/constants.ts      |  38 ++++
 web-shotlist/packages/shared/src/scriptSchema.ts   |  52 ++++-
 web-shotlist/packages/shared/src/types.ts          |   8 +
 web-shotlist/scripts/test_trash.ts                 |  24 +++
 13 files changed, 793 insertions(+), 41 deletions(-)

## d770ee8cc64c6de1925887a80d29f661cfae0190
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T07:27:03-04:00
- Subject: [web-shotlist-tool] 脚手架+工具A/B TS重写+三段式骨架+标色组件

- monorepo：pnpm workspace（shared/server/web）+ Node22 + Vite7 + React19 + Fastify5 + Tailwind v4 + shadcn 风格 + zod4
- 工具 A/B 重写：模板忠实搬运 + zod 校验（拍摄本 schema/提示词确定性规则/六段式）
- API：projects CRUD + generate-shotlist/prompt + inputs + entities；项目=目录格式
- 前端：三段式（剧本/拍摄本卡片流+时间轴/侧栏输入源）+ 输出区标色（ref chip/时间戳/台词/motion/声音三层/N/A）
- e2e 实测：Alya 剧本 → 3镜拍摄本 → ref2va 六段式 + i2va 三核心段全部通过
- 相关：docs/22 开发计划第 1-3 步完成；data/ gitignored

 .pi/agents/web-shotlist-tool/progress.md           |   25 +-
 web-shotlist/.gitignore                            |    6 +
 web-shotlist/.node-version                         |    1 +
 web-shotlist/apps/server/package.json              |   23 +
 web-shotlist/apps/server/src/config.ts             |   40 +
 web-shotlist/apps/server/src/index.ts              |   28 +
 web-shotlist/apps/server/src/llm.ts                |   53 +
 web-shotlist/apps/server/src/routes/entities.ts    |   15 +
 web-shotlist/apps/server/src/routes/projects.ts    |  116 ++
 web-shotlist/apps/server/src/store.ts              |  167 ++
 web-shotlist/apps/server/src/tools/promptStage2.ts |   95 +
 web-shotlist/apps/server/src/tools/shotlistGen.ts  |  133 ++
 web-shotlist/apps/server/src/tools/templates.ts    |  222 +++
 web-shotlist/apps/server/tsconfig.json             |   15 +
 web-shotlist/apps/web/index.html                   |   12 +
 web-shotlist/apps/web/package.json                 |   32 +
 web-shotlist/apps/web/src/App.tsx                  |  138 ++
 .../apps/web/src/components/prompt/OutputPanel.tsx |   74 +
 .../web/src/components/prompt/PromptHighlight.tsx  |   67 +
 .../apps/web/src/components/script/ScriptPanel.tsx |   59 +
 .../apps/web/src/components/shotlist/ShotCard.tsx  |   85 +
 .../apps/web/src/components/shotlist/ShotList.tsx  |   38 +
 .../web/src/components/shotlist/TimelineBar.tsx    |   46 +
 .../web/src/components/sidebar/SidebarPanel.tsx    |   99 +
 web-shotlist/apps/web/src/components/ui/badge.tsx  |   27 +
 web-shotlist/apps/web/src/components/ui/button.tsx |   46 +
 web-shotlist/apps/web/src/components/ui/card.tsx   |   22 +
 web-shotlist/apps/web/src/index.css                |   30 +
 web-shotlist/apps/web/src/lib/api.ts               |   28 +
 web-shotlist/apps/web/src/lib/store.ts             |   24 +
 web-shotlist/apps/web/src/lib/utils.ts             |    6 +
 web-shotlist/apps/web/src/main.tsx                 |   17 +
 web-shotlist/apps/web/tsconfig.json                |   22 +
 web-shotlist/apps/web/vite.config.ts               |   20 +
 web-shotlist/components.json                       |   20 +
 web-shotlist/package.json                          |   17 +
 web-shotlist/packages/shared/package.json          |   21 +
 web-shotlist/packages/shared/src/colors.ts         |   52 +
 web-shotlist/packages/shared/src/constants.ts      |   10 +
 web-shotlist/packages/shared/src/index.ts          |    7 +
 web-shotlist/packages/shared/src/promptSchema.ts   |  116 ++
 .../packages/shared/src/promptTokenizer.ts         |   79 +
 web-shotlist/packages/shared/src/scriptSchema.ts   |   45 +
 web-shotlist/packages/shared/src/shotlistSchema.ts |  133 ++
 web-shotlist/packages/shared/src/types.ts          |  147 ++
 web-shotlist/packages/shared/tsconfig.json         |   15 +
 web-shotlist/pnpm-lock.yaml                        | 2020 ++++++++++++++++++++
 web-shotlist/pnpm-workspace.yaml                   |    9 +
 web-shotlist/scripts/test_parse.ts                 |    6 +
 web-shotlist/scripts/test_tokens.ts                |   13 +
 50 files changed, 4535 insertions(+), 6 deletions(-)

## 0538e5554958ef9ee0415dd21646f42962ba5765
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T07:10:45-04:00
- Subject: [comfyui-032-verify] 渲染风格词主导实锤：V7 Anime style 混合风（真实光照+卡通渲染）记录入 params.md


 .pi/skills/comfyui/references/params.md | 2 ++
 1 file changed, 2 insertions(+)

## fd169d2c6afe3cb0e940ded6fb31d4a294ba6311
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T07:05:32-04:00
- Subject: [web-shotlist-tool] 设计文档 docs/22 定稿：全 TS 单栈三段式看板 + 实体系统 + 标色方案 + 项目格式 + 扩展路线


 .pi/agents/web-shotlist-tool/progress.md |   5 +
 docs/22_shotlist_web_tool.md             | 178 +++++++++++++++++++++++++++++++
 docs/INDEX.md                            |   3 +-
 3 files changed, 185 insertions(+), 1 deletion(-)

## 3b0b8327131497e2632b03a5af15171bdbf82b29
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T07:04:26-04:00
- Subject: [comfyui-032-verify] 15s 长档正式开放：三 seed 验收通过（230-275s），入三档表；用户决策 2026-08-12 放宽 ≤10s 限制


 .pi/skills/comfyui/references/params.md | 1 +
 1 file changed, 1 insertion(+)

## fbd1ed641b6bd8b6dca22be1a37b9f727f7749f5
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T06:12:23-04:00
- Subject: [comfyui-032-verify] T-20260812-07 完成：#15486 生效（15s int8 503→245s/-51%），成片档 15s=275s 新能力，params.md 补充 0.32.0 数据


 .pi/agents/comfyui-032-verify/progress.md | 41 +++++++++++++++++++++++++++++++
 .pi/skills/comfyui/references/params.md   |  9 +++++++
 2 files changed, 50 insertions(+)

## 88606ff6625c531ea95754b98074d7bc6b6f37a8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T05:15:34-04:00
- Subject: [comfyui-update] Bernini 缺失状态落定：用户决策暂不找回，需要时再下（指引保留 docs/02）


 .pi/skills/comfyui/SKILL.md | 2 +-
 docs/02_models.md           | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)

## 845c0cd6bfb97aa853ce415314a240bb065538d8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T04:54:10-04:00
- Subject: [web-shotlist-tool] 全域调研：导演台工具三类（ComfyUI 时间线编辑器/Web 应用/协议层），无现成替代，UI 范式可借鉴，核心自研


 .pi/agents/web-shotlist-tool/progress.md | 15 +++++++++++++++
 1 file changed, 15 insertions(+)

## 7209875db848782f1528717c7c77db0e82b3711d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T04:49:51-04:00
- Subject: [comfyui-update] 模型清单盘点重写 docs/02（磁盘实况权威）+ SKILL 模型栈/工作流同步（Wan 栈清理、H3 主力、Bernini 缺失标注）


 .pi/skills/comfyui/SKILL.md |  34 +++++-----
 docs/02_models.md           | 149 +++++++++++++++++++++++---------------------
 2 files changed, 96 insertions(+), 87 deletions(-)

## 356613940f793cf10bf75c0f15d986b2e19c1b49
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T04:39:26-04:00
- Subject: [web-shotlist-tool] 新任务线：网页拍摄本工具设计讨论启动


 .pi/agents/web-shotlist-tool/progress.md | 22 ++++++++++++++++++++++
 1 file changed, 22 insertions(+)

## f58e1f256975646e0b748f4c9c5fa98bceb1079f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T04:28:48-04:00
- Subject: [h3-prompt-agent] 成片试跑 3 段完成 + 音乐策略修订（跟随拍摄本/no_bgm 三件套）+ T-01 站位对照 + 用户反馈定位（镜头主体绑定/环境音变轻）+ 网页工具任务登记


 .pi/agents/h3-prompt-agent/progress.md             | 13 ++++
 experiments/shotlist/film_cases.json               | 68 +++++++++++++++++++
 experiments/shotlist/film_cases.json.results.json  | 23 +++++++
 ...347\232\204\351\201\223\345\210\253_ref2va.txt" | 26 ++++++++
 ...347\232\204\347\272\246\345\256\232_ref2va.txt" | 26 ++++++++
 ...345\246\271\347\272\246\345\256\232_ref2va.txt" | 26 ++++++++
 experiments/shotlist/scripts/agreement_night.yaml  | 16 +++++
 experiments/shotlist/t01_cases.json                | 26 ++++++++
 experiments/shotlist/t01_cases.json.results.json   |  9 +++
 ...\302\267\345\244\251\345\217\260_shotlist.yaml" | 61 +++++++++++++++++
 ...\302\267\345\275\222\351\200\224_shotlist.yaml" | 57 ++++++++++++++++
 ...\302\267\346\265\267\350\276\271_shotlist.yaml" | 58 ++++++++++++++++
 scripts/h3_concat.py                               | 77 ++++++++++++++++++++++
 scripts/h3_prompt_stage2.py                        | 29 +++++---
 scripts/h3_shotlist_gen.py                         |  9 ++-
 15 files changed, 514 insertions(+), 10 deletions(-)

## 061599a7c95aa31972eff0f1f843f27e3839dd22
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:51:41-04:00
- Subject: [bgm-pos-control] T-20260812-02 完成：正向控制实测定论（P1/P4 触发、P2 diegetic 可区分、P3 时间cue半可控），docs/17 音乐策略节落地


 .pi/agents/bgm-pos-control/progress.md | 52 ++++++++++++++++++++++++++++++++++
 docs/17_h3_prompt_writing_rules.md     |  2 ++
 2 files changed, 54 insertions(+)

## 9bf0db58ad2a300533e5dd9bc9b5698d1bf30100
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:42:02-04:00
- Subject: [h3-prompt-agent] 社区评价调研（Motion Context 正面但上限明确）+ 技能沉淀盘点 + 交互策略建议


 .pi/agents/h3-prompt-agent/progress.md | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)

## 784dc742b6e12ef1c9fc248437634c7a1a1b47fa
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:34:47-04:00
- Subject: [h3-prompt-agent] 调研：H3 Director/Motion Context 跨段连续性正解 + 官方 skill 镜像同步 compatibility 字段 + 今日 H3 提示词新动态落盘


 .pi/agents/h3-prompt-agent/progress.md                | 17 +++++++++++++++++
 .pi/skills/3d-animation-short-generator/SKILL.md      |  1 +
 .pi/skills/brand-promo-video-generator/SKILL.md       |  1 +
 .pi/skills/co-op-game-intro-generator/SKILL.md        |  1 +
 .pi/skills/h3-prompt-writing/SKILL.md                 |  1 +
 .pi/skills/handdrawn-live-video-generator/SKILL.md    |  1 +
 .pi/skills/minimalist-product-ad-generator/SKILL.md   |  1 +
 .pi/skills/mv-subtitle-skill-confirmed/SKILL.md       |  1 +
 .pi/skills/paper-collage-explainer-generator/SKILL.md |  1 +
 .pi/skills/papercraft-stop-motion-explainer/SKILL.md  |  1 +
 vendor/minimax-h3                                     |  2 +-
 11 files changed, 27 insertions(+), 1 deletion(-)

## 4314fd5499499104b7358d65ccfd2d6a2ece6a03
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:26:46-04:00
- Subject: [h3-prompt-agent] 会话收尾：下一步指引落盘（成片试跑/T-03设定图体系/机制沉淀）


 .pi/agents/h3-prompt-agent/progress.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## 8a5b39cc959ed35731b4cf086c9fce68477a287c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:25:41-04:00
- Subject: [h3-prompt-agent] v3 用户验收通过：多角色多场景一致性闭环（canon基准图+角色卡对齐+同图跨段+同音色种子）


 .pi/agents/h3-prompt-agent/progress.md | 6 ++++++
 1 file changed, 6 insertions(+)

## d07b5ded6b6fa858df2656219023e012e6adb341
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:24:34-04:00
- Subject: [h3-prompt-agent] 清理 output/：图片统一归档 ComfyUI/output/compare（用户指示：图片视频放 ComfyUI output，音频暂留项目内）；agreement_beach 站位对齐段1


 experiments/shotlist/scripts/agreement_beach.yaml |   2 +-
 output/compare/h3v1_round1_768.png                | Bin 10962031 -> 0 bytes
 output/compare/h3v1_round2_1024.png               | Bin 14945896 -> 0 bytes
 3 files changed, 1 insertion(+), 1 deletion(-)

## 8284f1eafdc1979042df2c06c1f1bb44fe9f1cb6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:21:59-04:00
- Subject: [h3-prompt-agent] v3 重跑：Yuki 角色卡对齐参考图（白色水手服），提示词与设定图一致后跨段服装应稳定


 .pi/agents/h3-prompt-agent/progress.md    | 7 +++++++
 experiments/shotlist/rolecards/yuki_v1.md | 2 +-
 2 files changed, 8 insertions(+), 1 deletion(-)

## 00cc5297ce6bbd5e2b4dd5fd7711f204c9eae093
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:18:59-04:00
- Subject: [h3-turbo-pilot] 收口：试点被 h3-today-testing T1 覆盖定案，runner WIP 两分支入库（clipproj 弃用留史/native 已验证），[STATE] 补建✅


 .pi/agents/h3-turbo-pilot/progress.md | 12 +++++++++++-
 scripts/h3_turbo_runner.py            | 24 ++++++++++++++++++------
 2 files changed, 29 insertions(+), 7 deletions(-)

## bcfc426b145b607d777889d5bca9f232b4cce198
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:15:37-04:00
- Subject: [docs] INDEX 更新：review/ 已归档至 output_archive/（2026-08-12 清理）


 docs/INDEX.md | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)

## 4d9ee4dd42312cbeac8c38652e7425997be6da96
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T03:11:18-04:00
- Subject: [h3-prompt-agent] 变体机制决策落盘：设定图 source of truth + 禁文本微调（社区证据+用户拍板）


 .pi/agents/h3-prompt-agent/progress.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## 2514d913f24c40cf0679adbded1cadca733eaa2c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T02:59:57-04:00
- Subject: [h3-today-testing] 收尾修正：产物位置核实（视频完好于 ~/projects/ComfyUI/output/video/h3v1/，对比图已恢复）


 .pi/agents/h3-today-testing/progress.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## 0c0d213fdb93e862e753ad9a7a1e7be392e7a665
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T02:59:46-04:00
- Subject: [h3-prompt-agent] anima_scene_batch 支持 i2i 改色模式（--i2i/--denoise）+ Yuki 深色制服描述强化


 scripts/anima_scene_batch.py | 43 ++++++++++++++++++++++++++++++++++++-------
 1 file changed, 36 insertions(+), 7 deletions(-)

## aee00cdefc083ff85ff1c7bb308b39c18c6f8976
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T02:37:08-04:00
- Subject: [h3-today-testing] 收尾：T1-T6 全部完成+用户定案，output 误删记录（对比图已恢复），[STATE] 补建✅


 .pi/agents/h3-today-testing/progress.md | 17 ++++++++++-------
 1 file changed, 10 insertions(+), 7 deletions(-)

## 549dc4534237bda9b978438a60038261d05282d6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T02:21:50-04:00
- Subject: [prompt-audio] demucs 6s 去 BGM 定案：复杂条目全验证 + 生产脚本封装


 .pi/agents/prompt-audio/progress.md | 19 ++++++----
 scripts/h3_demucs.py                | 76 +++++++++++++++++++++++++++++++++++++
 2 files changed, 88 insertions(+), 7 deletions(-)

## a62c03c00bdc1fe71198da11cec825615c0f42fa
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T02:09:26-04:00
- Subject: [h3-prompt-agent] 多角色多场景一致性测试：工具A audio_refs透传，天台/海边2段双人对话出片，切点执行完美待用户验收


 .pi/agents/h3-prompt-agent/progress.md              | 10 ++++++++++
 experiments/shotlist/scripts/agreement_beach.yaml   | 16 ++++++++++++++++
 experiments/shotlist/scripts/agreement_rooftop.yaml | 16 ++++++++++++++++
 scripts/h3_shotlist_gen.py                          |  8 +++++++-
 4 files changed, 49 insertions(+), 1 deletion(-)

## a984a92e8bed477cd56214c8608168584f029edc
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T00:48:07-04:00
- Subject: [h3-prompt-agent] 删除防重绘句（实测零增益：一致时模型本会锚定、冲突时无效），scene 字段保留操作层选图用


 docs/21_pipeline_acceptance.md |  4 ++--
 scripts/h3_prompt_stage2.py    | 16 +++-------------
 2 files changed, 5 insertions(+), 15 deletions(-)

## eb4259979753935c1a3aaf668be937414be6db18
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-12T00:42:09-04:00
- Subject: [h3-prompt-agent] T5 防重绘规则视频端验证：一致组SSIM 0.865 vs 冲突组0.020，instruction line软约束无效、操作层纪律为硬防线；docs21 行动项落地


 .pi/agents/h3-prompt-agent/progress.md       | 10 ++++++++++
 docs/21_pipeline_acceptance.md               |  9 +++++----
 experiments/shotlist/scripts/alya_stage.yaml |  1 +
 3 files changed, 16 insertions(+), 4 deletions(-)

## 3c973f264fcfe1f9b75c2f112870b59fea7dbd3c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T23:49:07-04:00
- Subject: [h3-prompt-agent] T5 收尾：拍摄本 scene 字段+工具B防重绘规则+169图库按场景归档+Yuki场景版3张


 .pi/agents/h3-prompt-agent/progress.md       |  17 ++++
 experiments/shotlist/rolecards/alya_v1.md    |   4 +-
 experiments/shotlist/rolecards/yuki_v1.md    |   6 +-
 experiments/shotlist/scripts/alya_beach.yaml |   1 +
 scripts/anima_scene_batch.py                 | 113 +++++++++++++++++++++++++++
 scripts/h3_prompt_stage2.py                  |  16 +++-
 scripts/h3_shotlist_gen.py                   |  11 ++-
 7 files changed, 160 insertions(+), 8 deletions(-)

## ad9e12ff9b3662723e9d78e733101cbc6b1bda95
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T23:18:54-04:00
- Subject: [h3-prompt-agent] 音色实验收尾：d8 A/B 确认弱参考、edge-tts 合成男声种子、d9 异口同声双音色用户验收✅（d8b/d9 被外部清理，d9 重跑复现）


 .pi/agents/h3-prompt-agent/progress.md             |  7 ++++
 ...345\217\243\345\220\214\345\243\260_ref2va.txt" | 24 +++++++++++++
 ...347\232\204\345\260\221\345\245\263_ref2va.txt" | 21 +++++++++++
 ...\217\243\345\220\214\345\243\260_shotlist.yaml" | 42 ++++++++++++++++++++++
 ...\232\204\345\260\221\345\245\263_shotlist.yaml" | 24 +++++++++++++
 5 files changed, 118 insertions(+)

## 143187cf39cf2a5a56876f01d9a8a2252e245910
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T22:35:14-04:00
- Subject: [h3-today-testing] 用户目视定案：成片档维持 v4-600EMA 8步，v1.0 仅作风备选


 .pi/agents/h3-today-testing/progress.md | 1 +
 1 file changed, 1 insertion(+)

## e2222fdc176186bc3ab5c183e9616326fcfef495
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T14:19:40-04:00
- Subject: [h3-today-testing] T1-T6 今日动态测试：v1.0 LoRA 评测/Ref2VA 纯音频验证/flags 实测退回/Sol/fal 调研


 .pi/agents/h3-today-testing/progress.md |  35 +++++++
 output/compare/h3v1_round1_768.png      | Bin 0 -> 10962031 bytes
 output/compare/h3v1_round2_1024.png     | Bin 0 -> 14945896 bytes
 scripts/h3_v1_test_runner.py            | 116 +++++++++++++++++++++
 workflows/h3v1_r2_audio_only.json       | 176 ++++++++++++++++++++++++++++++++
 5 files changed, 327 insertions(+)

## 2665164bd1011b154b6a23a4cef4c4840f5fed57
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T12:32:15-04:00
- Subject: [h3-prompt-agent] 音色种子：调研+制作+d7 实验（性能影响≈0）；d4/d5/d6 群像批；runner/stage2 支持 audio_refs；魔兽配音 sample 3条备用


 .pi/agents/h3-prompt-agent/progress.md             | 24 +++++++++
 ...347\232\204\345\257\271\350\257\235_ref2va.txt" | 22 ++++++++
 ...347\232\204\351\227\256\347\255\224_ref2va.txt" | 27 ++++++++++
 ...347\232\204\346\212\242\350\257\235_ref2va.txt" | 22 ++++++++
 experiments/shotlist/scripts/duo_crowd_bg.yaml     | 26 +++++++++
 experiments/shotlist/scripts/duo_interrupt.yaml    | 24 +++++++++
 .../shotlist/scripts/trio_group_answer.yaml        | 23 ++++++++
 ...\232\204\345\257\271\350\257\235_shotlist.yaml" | 58 ++++++++++++++++++++
 ...\232\204\351\227\256\347\255\224_shotlist.yaml" | 63 ++++++++++++++++++++++
 ...\232\204\346\212\242\350\257\235_shotlist.yaml" | 62 +++++++++++++++++++++
 scripts/h3_gap_runner.py                           |  8 +++
 scripts/h3_prompt_stage2.py                        | 11 ++++
 12 files changed, 370 insertions(+)

## 21f53454129b80318738c73402c23122d0a6bd9a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T11:51:53-04:00
- Subject: [prompt-audio] BGM 验证收束：单镜头免疫规则 + AudioSep 分离工具封装


 .pi/agents/prompt-audio/progress.md | 52 ++++++++++++++++++++++++++++++++++
 scripts/h3_audio_sep.py             | 56 +++++++++++++++++++++++++++++++++++++
 2 files changed, 108 insertions(+)

## ae98d0b0617e9f9225fda12ab2129384edab0de0
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T10:50:55-04:00
- Subject: [h3-prompt-agent] 对话批 d3：群像压力测试（3人+人群口号+同时说话+抢话，5.2s 2镜），141s 切点 2.54 精确，音频略低待用户判定


 ...347\232\204\345\221\220\345\226\212_ref2va.txt" | 27 ++++++++++++++
 experiments/shotlist/scripts/multi_race.yaml       | 20 +++++++++++
 ...\232\204\345\221\220\345\226\212_shotlist.yaml" | 41 ++++++++++++++++++++++
 3 files changed, 88 insertions(+)

## 52425a804969a51ef605b7e08db822129e12f985
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T10:28:12-04:00
- Subject: [h3-prompt-agent] 对话批 d2：双人同框三镜+对画外第三人（Alya 右/Yuki 左位置锚定进 retention），188s 切点 2.96/5.21 音频正常


 .pi/agents/h3-prompt-agent/progress.md             |  7 +++
 ...347\232\204\347\255\211\345\276\205_ref2va.txt" | 21 ++++++++
 experiments/shotlist/scripts/alya_yuki_trio.yaml   | 18 +++++++
 ...\232\204\347\255\211\345\276\205_shotlist.yaml" | 57 ++++++++++++++++++++++
 4 files changed, 103 insertions(+)

## 40edf55dae42f02babb79d6fc22042063e28ba1d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T10:16:01-04:00
- Subject: [h3-prompt-agent] 对话落地：工具A/B 升级 dialogue 字段+对话语法（S1/S2+<d>+VO 闭嘴+时间锚点），d1 双角色对话 Ref2VA 验证批（切点 2.54/5.04 精确、音频正常）；否定句回滚；yuki_v1 角色卡+对话剧本；旧验收体系删除补提交


 .pi/agents/h3-prompt-agent/progress.md             |  10 ++
 .../README_\351\252\214\346\224\266.md"            | 145 ---------------------
 experiments/prompt_compare/compare.html            |  83 ------------
 ...3\347\232\204\350\207\264\346\204\217_i2va.txt" |   7 +
 ...0\345\244\234\351\262\270\345\275\261_i2va.txt" |   7 +
 ...6\345\217\221\345\260\221\345\245\263_i2va.txt" |  11 ++
 ...345\217\221\345\260\221\345\245\263_ref2va.txt" |  22 ++++
 ...345\233\255\345\244\251\345\217\260_ref2va.txt" |  22 ++++
 experiments/shotlist/rolecards/yuki_v1.md          |  30 +++++
 .../shotlist/scripts/alya_yuki_dialogue.yaml       |  20 +++
 ...\244\234\351\234\223\350\231\271_shotlist.yaml" |  61 +++++----
 ...\246\271\345\257\271\350\257\235_shotlist.yaml" |  59 +++++++++
 scripts/h3_ab_turbo_submit.py                      |  85 ++++++++++++
 scripts/h3_prompt_stage2.py                        |  25 +++-
 scripts/h3_shotlist_gen.py                         |  16 ++-
 15 files changed, 341 insertions(+), 262 deletions(-)

## 4bbb8049c9d81ca164d3273cdbe1aa416b65ca90
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T04:13:23-04:00
- Subject: [docs-opt] docs 体系整理：13→12/04→06/20→21 合并、09 瘦身、INDEX 重写+维护规则、docs_check.sh、sources_手册删除


 .pi/agents/docs-opt/progress.md     |  31 ++++++++++
 docs/02_models.md                   |  28 ++-------
 docs/04_bernini_int8_findings.md    | 113 ------------------------------------
 docs/06_extras_install.md           |  27 ++++++++-
 docs/07_video_material.md           |   2 +
 docs/09_h3_test_plan.md             |  68 +++++-----------------
 docs/10_h3_batch_optimization.md    |   2 +-
 docs/11_h3_case_library.md          |   7 +--
 docs/12_speech_to_video_pipeline.md |  73 ++++++++++++++++++++++-
 docs/13_bgm_music_production.md     |  78 -------------------------
 docs/16_prompt_generator_plan.md    |   4 +-
 docs/17_h3_prompt_writing_rules.md  |   2 +-
 docs/18_ir_sample_teardown.md       |   2 +-
 docs/19_h3_dual_track_gap_test.md   |  22 ++-----
 docs/20_storyboard_vs_ir.md         |  58 ------------------
 docs/21_pipeline_acceptance.md      |  36 +++++++++++-
 docs/INDEX.md                       |  44 +++++++++-----
 scripts/docs_check.sh               |  55 ++++++++++++++++++
 18 files changed, 281 insertions(+), 371 deletions(-)

## a83492a3fcc58c80a4a4226c3d9b9633e45fc790
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-11T04:07:36-04:00
- Subject: [h3-prompt-agent] BGM 调查收官：触发=i2v+长prompt+8s 三因素可复现，快车道 8s 必带音乐


 .pi/agents/h3-prompt-agent/progress.md | 9 +++++++++
 1 file changed, 9 insertions(+)

## 15cb5e93991bb15b07796914609bd700b67d6478
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T21:50:41-04:00
- Subject: [h3-prompt-agent] H3 新消息调研 + 社区范文扩充（BeatAPI 精选 8 条）


 .pi/agents/h3-prompt-agent/progress.md             | 11 +++++++
 experiments/community_samples/README.md            | 22 +++++++++++++
 ...o-performance-with-on-screen-titles-931081.json | 34 +++++++++++++++++++
 ...cinematic-dialogue-set-piece-scenes-875568.json | 38 ++++++++++++++++++++++
 ...ideo-make-the-character-from-video1-107776.json | 33 +++++++++++++++++++
 ...1-for-the-character-image-2-for-the-619967.json | 34 +++++++++++++++++++
 .../image-1-starting-frame-474111.json             | 31 ++++++++++++++++++
 ...ly-good-at-this-kind-of-k-pop-lyric-987242.json | 32 ++++++++++++++++++
 .../jazz-noir-anime-title-sequence-652641.json     | 33 +++++++++++++++++++
 .../lilia-astra-title-sequence.json                | 33 +++++++++++++++++++
 10 files changed, 301 insertions(+)

## 1ee915ae20d7b837bc167ca428d47dd22aec6b81
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T21:22:03-04:00
- Subject: [h3-prompt-agent] BGM 调查收束：矩阵完整（t2v 全无音乐/i2v 嫌疑），P2 待试听判定


 .pi/agents/h3-prompt-agent/progress.md | 23 +++++++++++++++++++++++
 1 file changed, 23 insertions(+)

## 434593d5ee19b4ae7a1f91c198d0426018fec67b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T11:53:22-04:00
- Subject: [h3-nobgm-test] 环境音场景无BGM测试工作流（海边海浪+海鸥）


 workflows/minimax_h3_t2v_api_nobgm_sfx_test.json | 162 +++++++++++++++++++++++
 1 file changed, 162 insertions(+)

## b5fe7632c64e47321c1f8c5eda5194f7d722e672
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T11:47:52-04:00
- Subject: [h3-prompt-agent] 音乐控制逐步对比：静音=场景无内容非N/A功效，音乐先验恒定（修正 nobgm 结论）


 .pi/agents/h3-prompt-agent/progress.md | 6 ++++++
 1 file changed, 6 insertions(+)

## 6569c29cbddc919a6504378a726ebc0416ffe529
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T11:34:05-04:00
- Subject: [h3-turbo-pilot] P1.4 ClipProj 判失败：音频 gate 不过 + 效果简化；成片档维持 32B TE 125s


 .pi/agents/h3-turbo-pilot/progress.md | 7 +++++++
 1 file changed, 7 insertions(+)

## 1905ded0ff868b8d685f85596830a54c264851f4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T11:23:14-04:00
- Subject: [h3-nobgm-test] 最简 H3 T2V 测试工作流（non_diegetic_music: N/A）


 workflows/minimax_h3_t2v_api_nobgm_test.json | 161 +++++++++++++++++++++++++++
 1 file changed, 161 insertions(+)

## bad944d07f38978de47a65fa0e3e89b6b9f6ad58
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T11:05:29-04:00
- Subject: [h3-prompt-agent] docs/17 音乐策略实测结论补录


 docs/17_h3_prompt_writing_rules.md | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

## ac1d28f9867559778914d87544957c784a5d20ac
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T11:05:21-04:00
- Subject: [h3-prompt-agent] 音乐控制调查结论：prompt 级去音乐 4 写法全无效（H3 音乐先验与 prompt 解耦），后期分离待定


 .pi/agents/h3-prompt-agent/progress.md | 7 +++++++
 1 file changed, 7 insertions(+)

## 97a3ecb1358b71cdea77953ca9fce1d5f31d70bf
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T10:40:10-04:00
- Subject: [h3-prompt-agent] 工具链vs IR 公平对比（首帧锚定 0.989 vs -0.127，IR加戏实证）+ 无BGM版验证 + 对比集整理


 .pi/agents/h3-prompt-agent/progress.md |  5 +++++
 docs/21_pipeline_acceptance.md         | 25 +++++++++++++++++++++++++
 2 files changed, 30 insertions(+)

## e9ae0328146586ca6b901985c270c21c4c065d5d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T10:34:50-04:00
- Subject: [h3-turbo-pilot] P1.4 ClipProj 首测：0.31.0 + TE 4B 投影 = 1024 成片 60s（快 2.1x）；pilot_archive 被用户清理


 .pi/agents/h3-turbo-pilot/progress.md | 9 +++++++++
 1 file changed, 9 insertions(+)

## 295fa7c23b510bbfde2c0383bc21bc7d4cf79dbd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T10:33:43-04:00
- Subject: [h3-prompt-agent] 音乐策略定版：默认无 BGM（短片不连续实测）+ 社区验证（Sogni diegetic-only）+ 后期配乐对接 docs/13


 .pi/agents/h3-prompt-agent/progress.md |  7 +++++++
 docs/17_h3_prompt_writing_rules.md     |  3 ++-
 scripts/h3_prompt_stage2.py            | 18 ++++++++++++------
 3 files changed, 21 insertions(+), 7 deletions(-)

## 0e7a60ff2d474d31b6eda30a01b698729bd045cc
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T10:21:19-04:00
- Subject: [h3-prompt-agent] 新管线验收：F批切点100%+音频正常；核心发现=首帧锚定依赖场景匹配（F3/F3b 对照闭环）


 .pi/agents/h3-prompt-agent/progress.md | 12 ++++++++++
 docs/21_pipeline_acceptance.md         | 44 ++++++++++++++++++++++++++++++++++
 2 files changed, 56 insertions(+)

## f688b589097d1ed47f4db88c5757ec82521b424e
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T09:50:20-04:00
- Subject: [h3-turbo-pilot] 第七轮扩大调研：原生 AV 采样确认、ClipProj TE 瘦身 POC（试点候选）、t8star ref2va patch 无效、8/10 生态扎堆


 .pi/agents/h3-turbo-pilot/progress.md | 9 +++++++++
 1 file changed, 9 insertions(+)

## afcbf202e48aa171d9471835e78f7a64d360ebba
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T09:24:24-04:00
- Subject: [h3-prompt-agent] IR 逆向 13 条全量 + 工具A 升级（few-shot/shot_style/音乐场景判断）+ 验证达 IR 级


 .pi/agents/h3-prompt-agent/progress.md             |  12 ++
 docs/17_h3_prompt_writing_rules.md                 |   1 +
 docs/20_storyboard_vs_ir.md                        |  58 +++++++++
 ...\276\271\351\273\204\346\230\217_shotlist.yaml" |  52 ++++----
 ...\217\260\344\271\213\345\244\234_shotlist.yaml" |  50 ++------
 .../ir_reverse/ab_A_onsen_10s_ir_shotlist.yaml     |  19 +++
 .../ir_reverse/ab_B_wow_fight_10s_ir_shotlist.yaml |  19 +++
 .../ir_reverse/i2v_alya_beach_ir_shotlist.yaml     |  31 +++++
 .../ir_reverse/i2v_alya_stage_ir_shotlist.yaml     |  17 +++
 .../ir_reverse/i2v_dessert_ir_shotlist.yaml        |  19 +++
 .../ir_reverse/i2v_forest_fairy_ir_shotlist.yaml   |  19 +++
 .../ir_reverse/official_i2va_8s_ir_shotlist.yaml   |  17 +++
 .../ir_reverse/official_ref2va_5s_ir_shotlist.yaml |  17 +++
 .../ir_reverse/official_t2va_10s_ir_shotlist.yaml  |  33 +++++
 .../t2v_cyberpunk_rainy_ir_shotlist.yaml           |  18 +++
 .../ir_reverse/t2v_doc_streetfood_ir_shotlist.yaml |  27 ++++
 .../ir_reverse/t2v_dream_cloudsea_ir_shotlist.yaml |  17 +++
 .../ir_reverse/t2v_retro_cafe_ir_shotlist.yaml     |  18 +++
 ...7\345\210\266\345\256\236\351\252\214_i2va.txt" |   7 ++
 ...\225\277\346\216\247\345\210\266_shotlist.yaml" |  49 ++++++++
 scripts/h3_ir_shotlist_extract.py                  | 136 +++++++++++++++++++++
 scripts/h3_shotlist_gen.py                         |  42 ++++++-
 22 files changed, 609 insertions(+), 69 deletions(-)

## 5b5c44ffa0a01109e3a71d82b8eb554633d86d70
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T06:37:09-04:00
- Subject: [h3-turbo-pilot] ref2va 优化现状专项：无 turbo、量化齐全、Kijai ref lora 实验性发现


 .pi/agents/h3-turbo-pilot/progress.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## 0c88868b2165942c4d084ac7f51cd8375501c59b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T06:32:59-04:00
- Subject: [h3-prompt-agent] 角色图库重建：anima 编码器补回 + Alya×3/Yuki LoRA + 4 张 16:9 首帧


 .pi/agents/h3-prompt-agent/progress.md | 12 ++++++++++++
 docs/02_models.md                      |  7 +++++--
 2 files changed, 17 insertions(+), 2 deletions(-)

## cfc134060d6f61589534f9f64b7e81d3258ae608
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T06:13:34-04:00
- Subject: [h3-turbo-pilot] 成片档定案 int8@1024=125s（用户目视 gate 通过）；管线三档定稿 params.md


 .pi/agents/h3-turbo-pilot/progress.md   |  7 +++++++
 .pi/skills/comfyui/references/params.md | 12 ++++++++----
 2 files changed, 15 insertions(+), 4 deletions(-)

## 3de35b7d63a11c935aa70fd967bf115c7227b44c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T05:54:19-04:00
- Subject: [h3-prompt-agent] 反推第一轮：切点执行率 100% + 控制有效性验证（时长跟随）+ 首帧底图规范


 .pi/agents/h3-prompt-agent/progress.md | 13 +++++++++++++
 1 file changed, 13 insertions(+)

## 6e6c352cf5765fe38b32dd65d4b8900f3ae358b4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T05:53:56-04:00
- Subject: [h3-prompt-agent] 首帧底图规范：16:9 强制（变形传导实测 0.47 vs 0.99）+ 适配库规则


 docs/19_h3_dual_track_gap_test.md | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)

## f7d18ce81e3311c53827964c41a0a243eb33495e
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T05:11:57-04:00
- Subject: [h3-prompt-agent] 工具B stage2（拍摄本→三核心段/六段式）+ 全链路闭环试跑（首帧锚定 0.992=IR 基准）+ 工具A --review 自审


 .pi/agents/h3-prompt-agent/progress.md             |  14 ++
 ...\276\271\351\273\204\346\230\217_shotlist.yaml" |  90 ++++----
 ...7\347\232\204\346\265\267\350\276\271_i2va.txt" |   7 +
 ...347\232\204\346\265\267\350\276\271_ref2va.txt" |  22 ++
 scripts/h3_prompt_stage2.py                        | 253 +++++++++++++++++++++
 scripts/h3_shotlist_gen.py                         |  25 ++
 6 files changed, 366 insertions(+), 45 deletions(-)

## dde2195d97f647f4e1438ea6df495ac6a506b1cd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T04:18:57-04:00
- Subject: [h3-turbo-pilot] 8/10 调研补充：官方 int8 首选（cu130 已具备）、nvfp4 TE 官方确认 4090 可用、AMA 稀疏注意力近期发布


 .pi/agents/h3-turbo-pilot/progress.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## ec6b0774dd8b52c78c75239536b4059624242dd6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T04:15:08-04:00
- Subject: [h3-turbo-pilot] 8/10 第六轮调研：unsloth GGUF 发布、w4a8/int8 VAE（0.31.0）、nvfp4 TE 本地证伪；int8 DiT 下载完成


 .pi/agents/h3-turbo-pilot/progress.md | 11 +++++++++++
 1 file changed, 11 insertions(+)

## 157f03753e3402a5ead1201df481450fe80fa3c6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T04:15:06-04:00
- Subject: [h3-prompt-agent] 工具A stage1：剧本→导演拍摄本（3场景验证全过）+ 角色卡 alya_v1


 .pi/agents/h3-prompt-agent/progress.md             |  12 ++
 ...\276\271\351\273\204\346\230\217_shotlist.yaml" |  49 +++++
 ...\217\260\344\271\213\345\244\234_shotlist.yaml" |  48 +++++
 experiments/shotlist/rolecards/alya_v1.md          |  29 +++
 experiments/shotlist/scripts/alya_beach.yaml       |  12 ++
 experiments/shotlist/scripts/alya_stage.yaml       |  12 ++
 experiments/shotlist/scripts/cyberpunk_rain.yaml   |  12 ++
 ...\244\234\351\234\223\350\231\271_shotlist.yaml" |  49 +++++
 scripts/h3_shotlist_gen.py                         | 234 +++++++++++++++++++++
 9 files changed, 457 insertions(+)

## 1d5b57ce2c445677efb3023c9afd195aa35b1bac
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-10T04:11:46-04:00
- Subject: [h3-prompt-agent] vendor 同步上游 05d91ff（skill 无实质更新，仅 compatibility 注释+目录改名）


 vendor/minimax-h3 | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## 20c59a530557050d2d1f9d6ce5ca691e9672967e
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T12:14:45-04:00
- Subject: [h3-prompt-agent] 双轨盲区补测 18 case 完成（快车道 i2v turbo 定档/慢车道 ref2va 多图/帧链硬桥判死刑）+ docs/19


 .pi/agents/h3-prompt-agent/progress.md |  14 ++
 docs/19_h3_dual_track_gap_test.md      |  67 +++++++++
 scripts/h3_gap_analyze.py              | 129 +++++++++++++++++
 scripts/h3_gap_runner.py               | 246 +++++++++++++++++++++++++++++++++
 4 files changed, 456 insertions(+)

## 5d4d6719d62bd967ef760b6b2fb2e9e91e253b66
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T11:05:48-04:00
- Subject: [h3-prompt-agent] 会话收尾：设计定稿（工具A/B架构+H3模式边界+生产双轨）落盘


 .pi/agents/h3-prompt-agent/progress.md | 18 +++++++++++++-----
 1 file changed, 13 insertions(+), 5 deletions(-)

## 7813c460056aea18f5db5fcbb7a4ea58bfad2803
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T11:05:09-04:00
- Subject: [h3-prompt-agent] 三层提示词对照表（原始剧本/IR/DS-Pro）


 ...217\220\347\244\272\350\257\215\345\257\271\347\205\247.md" | 10 ++++++++++
 1 file changed, 10 insertions(+)

## f9a6f2bc94d01b06a11e795e12754aa1e6f938a9
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T10:59:02-04:00
- Subject: [h3-turbo-pilot] 定档收尾：快速 v4-8@768=67s + 极速 v4-4@768=45s；成片档挂起等 int8


 .pi/agents/h3-turbo-pilot/progress.md | 7 +++++++
 1 file changed, 7 insertions(+)

## a91230bfeafbd9afff636da802dd109fdac1acab
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T10:51:38-04:00
- Subject: [h3-turbo-pilot] 复杂动作 4/6/8 对比 + 社区步数建议查证（8 步甜点共识）


 .pi/agents/h3-turbo-pilot/progress.md | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

## e45e397a889a91f40a7de51724113555b0bda960
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T09:39:07-04:00
- Subject: [security] 移除实验媒体资产出跟踪（experiments/speech-video/assets），gitignore 补 *.safetensors/*.m4a


 .gitignore                                           |   5 +++++
 .../speech-video/assets/ace/ace_seg1_intro.wav       | Bin 1058478 -> 0 bytes
 .../assets/ace/ace_seg2_constructive.wav             | Bin 4798158 -> 0 bytes
 .../speech-video/assets/ace/ace_seg3_xexam_a.wav     | Bin 4318350 -> 0 bytes
 .../speech-video/assets/ace/ace_seg4_xexam_b.wav     | Bin 4318350 -> 0 bytes
 .../speech-video/assets/ace/ace_seg5_xexam_c.wav     | Bin 3563358 -> 0 bytes
 .../speech-video/assets/ace/ace_seg6_summary.wav     | Bin 5447310 -> 0 bytes
 .../speech-video/assets/ace/v2_seg1_intro.wav        | Bin 1058478 -> 0 bytes
 .../speech-video/assets/ace/v2_seg2_constructive.wav | Bin 5609598 -> 0 bytes
 .../speech-video/assets/ace/v2_seg3_xexam_long.wav   | Bin 10584078 -> 0 bytes
 .../speech-video/assets/ace/v2_seg4_xexam_tail.wav   | Bin 2857758 -> 0 bytes
 .../speech-video/assets/ace/v2_seg5_summary.wav      | Bin 3401070 -> 0 bytes
 experiments/speech-video/assets/anim_F1.mp4          | Bin 282544 -> 0 bytes
 experiments/speech-video/assets/anim_F1_v2.mp4       | Bin 177880 -> 0 bytes
 experiments/speech-video/assets/anim_F5.mp4          | Bin 142658 -> 0 bytes
 experiments/speech-video/assets/anima_sample.png     | Bin 778570 -> 0 bytes
 experiments/speech-video/assets/bgm_bed.wav          | Bin 23161398 -> 0 bytes
 experiments/speech-video/assets/bgm_full.wav         | Bin 23519490 -> 0 bytes
 experiments/speech-video/assets/bgm_full_ace.wav     | Bin 23519490 -> 0 bytes
 experiments/speech-video/assets/bgm_full_ace_v2.wav  | Bin 23519490 -> 0 bytes
 experiments/speech-video/assets/bgm_seg1.wav         | Bin 1916204 -> 0 bytes
 experiments/speech-video/assets/bgm_seg2.wav         | Bin 1916204 -> 0 bytes
 experiments/speech-video/assets/bgm_seg3.wav         | Bin 1596204 -> 0 bytes
 .../speech-video/assets/debate_final_acebgm.mp4      | Bin 10201140 -> 0 bytes
 .../speech-video/assets/debate_final_acebgm_v2.mp4   | Bin 10197564 -> 0 bytes
 .../speech-video/assets/debate_final_animated.mp4    | Bin 10234369 -> 0 bytes
 .../speech-video/assets/debate_final_sound.mp4       | Bin 5312379 -> 0 bytes
 experiments/speech-video/assets/final_audio.wav      | Bin 23519490 -> 0 bytes
 experiments/speech-video/assets/final_audio_ace.wav  | Bin 23520078 -> 0 bytes
 .../speech-video/assets/final_audio_ace_v2.wav       | Bin 23520078 -> 0 bytes
 experiments/speech-video/assets/krea_sample.png      | Bin 552735 -> 0 bytes
 experiments/speech-video/assets/narr_denoised.wav    | Bin 23520078 -> 0 bytes
 experiments/speech-video/assets/sfx_applause.wav     | Bin 176478 -> 0 bytes
 experiments/speech-video/assets/sfx_ding.wav         | Bin 44178 -> 0 bytes
 experiments/speech-video/assets/sfx_full.wav         | Bin 22755678 -> 0 bytes
 experiments/speech-video/assets/sfx_gavel.wav        | Bin 35358 -> 0 bytes
 experiments/speech-video/assets/sfx_whoosh.wav       | Bin 39768 -> 0 bytes
 37 files changed, 5 insertions(+)

## 99b3ecdaf59435a2f545707faf8ec02d4664e99c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T09:17:24-04:00
- Subject: [h3-prompt-agent] 视频验收 12 条完成（6场景×DS-Pro/IR）+ 对比页 + 音频检查（onsen DS 近静音发现）


 .pi/agents/h3-prompt-agent/progress.md  | 15 ++++--
 experiments/prompt_compare/compare.html | 83 +++++++++++++++++++++++++++++++++
 scripts/h3_prompt_video_ab.py           |  4 +-
 3 files changed, 96 insertions(+), 6 deletions(-)

## a49341f95f43c3e3e5d75f05ba33b3a12ed3cb7c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T08:48:14-04:00
- Subject: [h3-prompt-agent] Pro 10/10 合规通过 + 校验器 i2v 规则对齐 IR 实测 + 重试逻辑修复 + 视频验收批脚本


 .../pro/alya_beach_deepseek-v4-pro.txt             |   7 ++
 .../pro/alya_stage_deepseek-v4-pro.txt             |   7 ++
 .../pro/cyberpunk_rainy_deepseek-v4-pro.txt        |   3 +
 .../prompt_compare/pro/dessert_deepseek-v4-pro.txt |   7 ++
 .../pro/doc_streetfood_deepseek-v4-pro.txt         |   3 +
 .../pro/dream_cloudsea_deepseek-v4-pro.txt         |   3 +
 .../pro/forest_fairy_deepseek-v4-pro.txt           |   7 ++
 .../prompt_compare/pro/onsen_deepseek-v4-pro.txt   |   3 +
 .../pro/retro_cafe_deepseek-v4-pro.txt             |   3 +
 .../pro/wow_fight_deepseek-v4-pro.txt              |   3 +
 scripts/deepseek_prompt_gen.py                     |  19 ++--
 scripts/h3_prompt_video_ab.py                      | 119 +++++++++++++++++++++
 scripts/prompt_validator.py                        |  12 ++-
 13 files changed, 183 insertions(+), 13 deletions(-)

## 778c600a20a04630c5314ba74a0ac63a575b535c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T08:41:17-04:00
- Subject: [h3-turbo-pilot] 快速档定档 v4-8 + 960×544 分辨率档测试任务


 .pi/agents/h3-turbo-pilot/progress.md | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

## 5e00e7df136bcd4e5a258375559f9dfb4a44a21a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T08:33:36-04:00
- Subject: [h3-turbo-pilot] 产物迁移：项目 video/ 删除 → ComfyUI output/pilot_archive/（36 文件）；产物规范改为一律 output/


 .pi/agents/h3-turbo-pilot/progress.md  |   2 ++
 video/1024x576_10s_base_14.mp4         | Bin 3036993 -> 0 bytes
 video/1024x576_10s_hand_base_14.mp4    | Bin 1014432 -> 0 bytes
 video/1024x576_10s_hand_tlx2v_10.mp4   | Bin 2159327 -> 0 bytes
 video/1024x576_10s_hand_tv4_6s1.mp4    | Bin 1363485 -> 0 bytes
 video/1024x576_10s_hand_tv4_6s2.mp4    | Bin 4554622 -> 0 bytes
 video/1024x576_10s_hand_tv4_8s1.mp4    | Bin 1428136 -> 0 bytes
 video/1024x576_10s_t850_06.mp4         | Bin 3915918 -> 0 bytes
 video/1024x576_10s_tlx2v_075.mp4       | Bin 1647344 -> 0 bytes
 video/1024x576_10s_tlx2v_10.mp4        | Bin 1987458 -> 0 bytes
 video/1024x576_10s_tv4_06.mp4          | Bin 1430921 -> 0 bytes
 video/1024x576_10s_tv4_08.mp4          | Bin 1507607 -> 0 bytes
 video/768x448_08s_base_14.mp4          | Bin 2487729 -> 0 bytes
 video/768x448_08s_t500_06.mp4          | Bin 3025020 -> 0 bytes
 video/768x448_08s_t850_04.mp4          | Bin 3666987 -> 0 bytes
 video/768x448_08s_t850_06.mp4          | Bin 3025024 -> 0 bytes
 video/768x448_08s_wave_base_14.mp4     | Bin 640220 -> 0 bytes
 video/768x448_08s_wave_tv4_06.mp4      | Bin 804419 -> 0 bytes
 video/768x448_08s_wave_tv4_08.mp4      | Bin 832371 -> 0 bytes
 video/768x448_08s_wave_tv4_10.mp4      | Bin 847757 -> 0 bytes
 video/768x448_08s_wave_tv4_14.mp4      | Bin 916551 -> 0 bytes
 video/768x448_10s_base_14.mp4          | Bin 2122714 -> 0 bytes
 video/768x448_10s_t500_06.mp4          | Bin 2898753 -> 0 bytes
 video/768x448_10s_t850_04.mp4          | Bin 3638677 -> 0 bytes
 video/768x448_10s_t850_06.mp4          | Bin 2898757 -> 0 bytes
 video/960x544_10s_base_16.mp4          | Bin 1592107 -> 0 bytes
 video/README.md                        |  22 ----------------------
 video/cmp_hand_1024x576_5way_mid.png   | Bin 1384366 -> 0 bytes
 video/cmp_real_1024x576_10s_mid.png    | Bin 1382787 -> 0 bytes
 video/cmp_real_1024x576_5way_mid.png   | Bin 1394963 -> 0 bytes
 video/cmp_real_768x448_10s_mid.png     | Bin 705972 -> 0 bytes
 video/cmp_real_960vs1024_mid.png       | Bin 1940408 -> 0 bytes
 video/cmp_wave_768x448_8s_3way_mid.png | Bin 813081 -> 0 bytes
 video/cmp_wave_768x448_8s_5way_mid.png | Bin 766535 -> 0 bytes
 video/cmp_wow_768x448_08s_end.png      | Bin 821737 -> 0 bytes
 video/cmp_wow_768x448_08s_mid.png      | Bin 822349 -> 0 bytes
 video/lx2v_vs_base_mid.png             | Bin 1200059 -> 0 bytes
 37 files changed, 2 insertions(+), 22 deletions(-)

## a87da5abcf77cd36203dbd8b74c4cd5cab0beb73
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T08:05:16-04:00
- Subject: [h3-turbo-pilot] 快速档定档 v4-8@768（67s）+ 10/14 步收益曲线结论


 .pi/agents/h3-turbo-pilot/progress.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## 4e1477b6dce742fadb2c283298c8b8145d1aff7f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T07:57:25-04:00
- Subject: [h3-prompt-agent] 合规修复：few-shot 注入 + 规则校验器 + 自动重试，10/10 场景通过合规校验


 .../README_\351\252\214\346\224\266.md"            |  15 +++
 .../fewshot/alya_beach_deepseek-v4-flash.txt       |   7 ++
 .../fewshot/alya_stage_deepseek-v4-flash.txt       |   9 ++
 .../fewshot/cyberpunk_rainy_deepseek-v4-flash.txt  |   3 +
 .../fewshot/dessert_deepseek-v4-flash.txt          |   7 ++
 .../fewshot/doc_streetfood_deepseek-v4-flash.txt   |   3 +
 .../fewshot/dream_cloudsea_deepseek-v4-flash.txt   |   3 +
 .../fewshot/forest_fairy_deepseek-v4-flash.txt     |   7 ++
 .../fewshot/onsen_deepseek-v4-flash.txt            |   3 +
 .../fewshot/retro_cafe_deepseek-v4-flash.txt       |   3 +
 .../fewshot/wow_fight_deepseek-v4-flash.txt        |   3 +
 scripts/deepseek_prompt_batch.sh                   |   3 +-
 scripts/deepseek_prompt_gen.py                     |  51 +++++++--
 scripts/prompt_validator.py                        | 127 +++++++++++++++++++++
 14 files changed, 235 insertions(+), 9 deletions(-)

## a6b77ff57578fdc3a471c4dde4beea65f8e58c52
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T07:55:02-04:00
- Subject: [h3-turbo-pilot] 768 步数收益曲线补测：v4-10/v4-14 + 五格对比图


 video/768x448_08s_wave_tv4_10.mp4      | Bin 0 -> 847757 bytes
 video/768x448_08s_wave_tv4_14.mp4      | Bin 0 -> 916551 bytes
 video/cmp_wave_768x448_8s_5way_mid.png | Bin 0 -> 766535 bytes
 3 files changed, 0 insertions(+), 0 deletions(-)

## e3e9a19334a472ea49d333ccc88175e88307821f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T07:39:16-04:00
- Subject: [h3-turbo-pilot] P0 重做批：挥手场景（手可见+非主体）768×448 8s 三档 + 计划更新（P3 移交提示词线）


 .pi/agents/h3-turbo-pilot/progress.md    |  21 +++++++++++++++++++++
 video/768x448_08s_handbg_base_14.mp4     | Bin 660625 -> 0 bytes
 video/768x448_08s_handbg_tv4_06.mp4      | Bin 935897 -> 0 bytes
 video/768x448_08s_handbg_tv4_08.mp4      | Bin 979422 -> 0 bytes
 video/768x448_08s_wave_base_14.mp4       | Bin 0 -> 640220 bytes
 video/768x448_08s_wave_tv4_06.mp4        | Bin 0 -> 804419 bytes
 video/768x448_08s_wave_tv4_08.mp4        | Bin 0 -> 832371 bytes
 video/cmp_handbg_768x448_8s_3way_mid.png | Bin 797491 -> 0 bytes
 video/cmp_wave_768x448_8s_3way_mid.png   | Bin 0 -> 813081 bytes
 9 files changed, 21 insertions(+)

## 2a0e6be2b413a933f6c913270fda397717290968
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-09T00:20:11-04:00
- Subject: [h3-turbo-pilot] 五轮社区调研落盘：larryvrh v5 实验权重 + lightx2v Prompt-Rewriter + SeedScout 补漏


 .pi/agents/h3-params/progress.md | 26 ++++++++++++++++++++++++++
 1 file changed, 26 insertions(+)

## 70de65031283667594f5f64780e9c3e5668fdb91
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T04:36:36-04:00
- Subject: [h3-prompt-agent] 路线1验证：DeepSeek flash 10场景对比生成（vs IR 样本库）+ 验收材料


 experiments/ir_samples/ab_A_onsen_10s.txt          |   3 +
 experiments/ir_samples/ab_B_wow_fight_10s.txt      |   3 +
 .../README_\351\252\214\346\224\266.md"            | 130 +++++++++++++++++++++
 .../alya_beach_deepseek-v4-flash.txt               |  14 +++
 .../alya_stage_deepseek-v4-flash.txt               |  12 ++
 .../cyberpunk_rainy_deepseek-v4-flash.txt          |   8 ++
 .../prompt_compare/dessert_deepseek-v4-flash.txt   |  14 +++
 .../doc_streetfood_deepseek-v4-flash.txt           |  12 ++
 .../dream_cloudsea_deepseek-v4-flash.txt           |  13 +++
 .../forest_fairy_deepseek-v4-flash.txt             |  14 +++
 .../prompt_compare/onsen_deepseek-v4-flash.txt     |  20 ++++
 .../retro_cafe_deepseek-v4-flash.txt               |   8 ++
 .../prompt_compare/wow_fight_deepseek-v4-flash.txt |  17 +++
 scripts/deepseek_prompt_batch.sh                   |  36 ++++++
 scripts/deepseek_prompt_gen.py                     |  89 ++++++++++++++
 15 files changed, 393 insertions(+)

## ccf8bcf4fed6ad93b7ccd41d564ce3798b80cf6c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T04:14:31-04:00
- Subject: [h3-turbo-pilot] 手非主体验证批 768×448 8s：base/v4-6/v4-8 三档


 video/768x448_08s_handbg_base_14.mp4     | Bin 0 -> 660625 bytes
 video/768x448_08s_handbg_tv4_06.mp4      | Bin 0 -> 935897 bytes
 video/768x448_08s_handbg_tv4_08.mp4      | Bin 0 -> 979422 bytes
 video/cmp_handbg_768x448_8s_3way_mid.png | Bin 0 -> 797491 bytes
 4 files changed, 0 insertions(+), 0 deletions(-)

## b748624b4c50887427e35f6988493a958e7683ec
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T04:00:16-04:00
- Subject: [h3-turbo-pilot] 手部验证批：5 档（base/lx2v/v4-6s1/v4-6s2/v4-8s1）+ 五格对比图


 video/1024x576_10s_hand_base_14.mp4  | Bin 0 -> 1014432 bytes
 video/1024x576_10s_hand_tlx2v_10.mp4 | Bin 0 -> 2159327 bytes
 video/1024x576_10s_hand_tv4_6s1.mp4  | Bin 0 -> 1363485 bytes
 video/1024x576_10s_hand_tv4_6s2.mp4  | Bin 0 -> 4554622 bytes
 video/1024x576_10s_hand_tv4_8s1.mp4  | Bin 0 -> 1428136 bytes
 video/1024x576_10s_tv4_06.mp4        | Bin 0 -> 1430921 bytes
 video/1024x576_10s_tv4_08.mp4        | Bin 0 -> 1507607 bytes
 video/cmp_hand_1024x576_5way_mid.png | Bin 0 -> 1384366 bytes
 video/cmp_real_1024x576_5way_mid.png | Bin 0 -> 1394963 bytes
 9 files changed, 0 insertions(+), 0 deletions(-)

## 3d1a4b65a54115f05f62ddce7e5fe6a09a263203
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T03:55:52-04:00
- Subject: [h3-prompt-agent] 生成器前期准备：IR 样本库 13 条 + benjiyaya 拆解 + docs/17/18 + IR 脚本嵌套格式修复


 .pi/agents/h3-prompt-agent/progress.md         |  16 +++-
 docs/16_prompt_generator_plan.md               |  16 ++--
 docs/17_h3_prompt_writing_rules.md             | 101 ++++++++++++++++++++++
 docs/18_ir_sample_teardown.md                  | 112 +++++++++++++++++++++++++
 experiments/ir_samples/i2v_alya_beach.txt      |   7 ++
 experiments/ir_samples/i2v_alya_stage.txt      |   6 ++
 experiments/ir_samples/i2v_dessert.txt         |   7 ++
 experiments/ir_samples/i2v_forest_fairy.txt    |   9 ++
 experiments/ir_samples/official_i2va_8s.txt    |   7 ++
 experiments/ir_samples/official_ref2va_5s.txt  |  24 ++++++
 experiments/ir_samples/official_t2va_10s.txt   |   3 +
 experiments/ir_samples/t2v_cyberpunk_rainy.txt |   3 +
 experiments/ir_samples/t2v_doc_streetfood.txt  |   3 +
 experiments/ir_samples/t2v_dream_cloudsea.txt  |   3 +
 experiments/ir_samples/t2v_retro_cafe.txt      |   3 +
 scripts/h3_ir_rewrite.py                       |  15 ++--
 scripts/h3_ir_sample_batch.sh                  |  46 ++++++++++
 17 files changed, 363 insertions(+), 18 deletions(-)

## ce53521f5fc75dbbb0f60d1b17d08b17334b4ec7
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T03:30:58-04:00
- Subject: [h3-prompt-agent] docs/16 补 DeepSeek 配置：key 两处 + reasoning MAX


 docs/16_prompt_generator_plan.md | 3 +++
 1 file changed, 3 insertions(+)

## a85c683f77240aaa8a4db1c84a47c9c7c92b5f5a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T03:27:47-04:00
- Subject: [h3-turbo-pilot] 四轮增量调研落盘 + lx2v/v4 试点产物归档（1024x576_10s_tlx2v_*）


 .pi/agents/h3-params/progress.md |  20 ++++++++++++++++++++
 video/1024x576_10s_tlx2v_075.mp4 | Bin 0 -> 1647344 bytes
 video/1024x576_10s_tlx2v_10.mp4  | Bin 0 -> 1987458 bytes
 video/lx2v_vs_base_mid.png       | Bin 0 -> 1200059 bytes
 4 files changed, 20 insertions(+)

## 38c3aa02dcb7d9bd68167f9b5f55cada06a718f2
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T03:11:21-04:00
- Subject: [h3-prompt-agent] 提示词生成器前期准备落盘：docs/16 计划 + 收集清单 + 设计结论


 .pi/agents/h3-prompt-agent/progress.md |  8 ++++
 docs/16_prompt_generator_plan.md       | 71 ++++++++++++++++++++++++++++++++++
 2 files changed, 79 insertions(+)

## 356abf456bb69d59b1878553d2259cbff1e761b0
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T01:52:08-04:00
- Subject: [h3-turbo-pilot] 社区三轮调研落盘：lightx2v v0.1 官方4步LoRA + larryvrh v4-600 EMA（重启试点计划）


 .pi/agents/h3-params/progress.md      | 30 ++++++++++++++++++++++++++++++
 .pi/agents/h3-turbo-pilot/progress.md | 22 ++++++++++++++++++----
 2 files changed, 48 insertions(+), 4 deletions(-)

## f99ce3c619d6f14e4850154449b621dc1551af9d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T01:44:28-04:00
- Subject: [h3-turbo-pilot] video 全平铺：文件名=分辨率_时长_优化_步数（排序即对比顺序）+ 对比图 cmp_ 前缀


 .../base14.mp4 => 1024x576_10s_base_14.mp4}        | Bin
 .../850_6.mp4 => 1024x576_10s_t850_06.mp4}         | Bin
 .../base14.mp4 => 768x448_08s_base_14.mp4}         | Bin
 .../500_6.mp4 => 768x448_08s_t500_06.mp4}          | Bin
 .../850_4.mp4 => 768x448_08s_t850_04.mp4}          | Bin
 .../850_6.mp4 => 768x448_08s_t850_06.mp4}          | Bin
 .../base14.mp4 => 768x448_10s_base_14.mp4}         | Bin
 .../500_6.mp4 => 768x448_10s_t500_06.mp4}          | Bin
 .../850_4.mp4 => 768x448_10s_t850_04.mp4}          | Bin
 .../850_6.mp4 => 768x448_10s_t850_06.mp4}          | Bin
 .../base16.mp4 => 960x544_10s_base_16.mp4}         | Bin
 video/README.md                                    |  33 ++++++++++-----------
 ...d_compare.png => cmp_real_1024x576_10s_mid.png} | Bin
 ...id_compare.png => cmp_real_768x448_10s_mid.png} | Bin
 ...r960_vs_1024.png => cmp_real_960vs1024_mid.png} | Bin
 ...end_compare.png => cmp_wow_768x448_08s_end.png} | Bin
 ...mid_compare.png => cmp_wow_768x448_08s_mid.png} | Bin
 17 files changed, 15 insertions(+), 18 deletions(-)

## cabd365215e671e4b74d747f5d39794ddbb24c44
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-08T01:44:09-04:00
- Subject: [h3-prompt-agent] 第二轮 turbo 步数矩阵：t4/t6/t8 全对比 + 音频规律 + 耗时标注纪律


 .pi/agents/h3-prompt-agent/progress.md | 13 +++++++++++++
 1 file changed, 13 insertions(+)

## 8da72c5eebd73687a1c578d19ab683dfdf12c7e4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T16:27:25-04:00
- Subject: [h3-turbo-pilot] video 目录重组：编号分组+规范化命名（01-04 实验批次/05_compare 对比图/README 规范）


 video/01_wow_anime_8s/500_6.mp4           | Bin 0 -> 3025020 bytes
 video/01_wow_anime_8s/850_4.mp4           | Bin 0 -> 3666987 bytes
 video/01_wow_anime_8s/850_6.mp4           | Bin 0 -> 3025024 bytes
 video/01_wow_anime_8s/base14.mp4          | Bin 0 -> 2487729 bytes
 video/02_real_10s_768/500_6.mp4           | Bin 0 -> 2898753 bytes
 video/02_real_10s_768/850_4.mp4           | Bin 0 -> 3638677 bytes
 video/02_real_10s_768/850_6.mp4           | Bin 0 -> 2898757 bytes
 video/02_real_10s_768/base14.mp4          | Bin 0 -> 2122714 bytes
 video/03_real_10s_1024/850_6.mp4          | Bin 0 -> 3915918 bytes
 video/03_real_10s_1024/base14.mp4         | Bin 0 -> 3036993 bytes
 video/04_real_10s_960/base16.mp4          | Bin 0 -> 1592107 bytes
 video/05_compare/r960_vs_1024.png         | Bin 0 -> 1940408 bytes
 video/05_compare/real1024_mid_compare.png | Bin 0 -> 1382787 bytes
 video/05_compare/real_mid_compare.png     | Bin 0 -> 705972 bytes
 video/05_compare/wow_end_compare.png      | Bin 0 -> 821737 bytes
 video/05_compare/wow_mid_compare.png      | Bin 0 -> 822349 bytes
 video/README.md                           |  25 +++++++++++++++++++++++++
 17 files changed, 25 insertions(+)

## 53df8e2adc8a47591f23c7a76c9dec21025bb31c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T15:29:30-04:00
- Subject: [h3-prompt-agent] A/B 测试提交脚本（4条：A温泉/B魔兽 × raw/IR，同seed 10s 1024×576）


 scripts/h3_ab_submit.py | 41 +++++++++++++++++++++++++++++++++++++++++
 1 file changed, 41 insertions(+)

## 3b84c4d3ced3cb5773fe2c2c9c69f333289425cd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T15:24:13-04:00
- Subject: [h3-prompt-agent] 冒烟测试通过：IR 全链路 OK，25 元≈200+ 次调用


 .pi/agents/h3-prompt-agent/progress.md | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)

## 96787d027e0ac3ab80b6f9f98af70b0866f26f07
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T15:21:30-04:00
- Subject: [h3-prompt-agent] IR API 接入：脚本+docs/08 落地（待充值冒烟测试）


 .pi/agents/h3-prompt-agent/progress.md |  14 ++-
 docs/08_h3_prompt_agent.md             |  23 ++++-
 scripts/h3_ir_rewrite.py               | 174 +++++++++++++++++++++++++++++++++
 3 files changed, 205 insertions(+), 6 deletions(-)

## a6435d208546abf105e1bc2ad473a1b772653990
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T15:07:10-04:00
- Subject: [h3-prompt-agent] 安装官方 MiniMax-H3 9 skill + vendor sparse 克隆（跟踪 commit 8d8824e）


 .pi/agents/h3-prompt-agent/progress.md             |  31 ++
 .../3d-animation-short-generator/SKILL.cn.md       | 615 +++++++++++++++++++++
 .pi/skills/3d-animation-short-generator/SKILL.md   | 248 +++++++++
 .pi/skills/3d-animation-short-generator/meta.yaml  |  19 +
 .../references/fallback-policy.md                  |  52 ++
 .../references/model-selection.md                  |  49 ++
 .../references/qc-checklist.md                     |  99 ++++
 .../references/shot-table-spec.md                  |  75 +++
 .../references/storyboard-guidelines.md            | 185 +++++++
 .pi/skills/brand-promo-video-generator/SKILL.cn.md | 178 ++++++
 .pi/skills/brand-promo-video-generator/SKILL.md    | 188 +++++++
 .pi/skills/brand-promo-video-generator/meta.yaml   |  19 +
 .pi/skills/co-op-game-intro-generator/SKILL.cn.md  |  44 ++
 .pi/skills/co-op-game-intro-generator/SKILL.md     |  53 ++
 .pi/skills/co-op-game-intro-generator/meta.yaml    |  15 +
 .../references/h3-confirmation-image-template.md   | 388 +++++++++++++
 .../references/h3-video-prompt-template.md         | 133 +++++
 .pi/skills/h3-prompt-writing/SKILL.md              |  34 ++
 .pi/skills/h3-prompt-writing/agents/openai.yaml    |   4 +
 .../h3-prompt-writing/references/base-en.txt       | 222 ++++++++
 .pi/skills/h3-prompt-writing/references/ref-en.txt | 341 ++++++++++++
 .../handdrawn-live-video-generator/SKILL.cn.md     |  86 +++
 .pi/skills/handdrawn-live-video-generator/SKILL.md |  86 +++
 .../handdrawn-live-video-generator/meta.yaml       |  17 +
 .../minimalist-product-ad-generator/SKILL.cn.md    | 397 +++++++++++++
 .../minimalist-product-ad-generator/SKILL.md       | 397 +++++++++++++
 .../minimalist-product-ad-generator/meta.yaml      |  19 +
 .pi/skills/mv-subtitle-skill-confirmed/SKILL.cn.md | 213 +++++++
 .pi/skills/mv-subtitle-skill-confirmed/SKILL.md    | 204 +++++++
 .pi/skills/mv-subtitle-skill-confirmed/meta.yaml   |  19 +
 .../paper-collage-explainer-generator/SKILL.cn.md  | 271 +++++++++
 .../paper-collage-explainer-generator/SKILL.md     | 272 +++++++++
 .../paper-collage-explainer-generator/meta.yaml    |  19 +
 .../papercraft-stop-motion-explainer/SKILL.cn.md   | 470 ++++++++++++++++
 .../papercraft-stop-motion-explainer/SKILL.md      | 470 ++++++++++++++++
 .../papercraft-stop-motion-explainer/meta.yaml     |  19 +
 vendor/minimax-h3                                  |   1 +
 37 files changed, 5952 insertions(+)

## ac6974fa0f6311c801f246b8ebb85a01e98e7705
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T14:52:00-04:00
- Subject: [h3-turbo-pilot] 二批：动漫风WoW 8s四档对比（base185s vs 850-4=50s），音频通过，产物video/h3_wow


 .pi/agents/h3-turbo-pilot/progress.md | 6 ++++++
 1 file changed, 6 insertions(+)

## f3ad8ea059dfa41fc0e73e78fa5beb6b256f29e7
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T14:07:27-04:00
- Subject: [h3-turbo-pilot] 批跑完成：速度矩阵+音频gate通过（4/6步50s vs 基线97s），待用户画质确认


 .pi/agents/h3-turbo-pilot/progress.md | 19 +++++++++++--------
 1 file changed, 11 insertions(+), 8 deletions(-)

## 2918c6e9d36b113a421a5084bcf449ee9ab07573
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T13:59:12-04:00
- Subject: [h3-turbo-pilot] 任务线启动：独立turbo runner+progress；环境就绪（ComfyUI 344b439/kitchen 0.2.27/Larryvrh节点/2×pruned lora）


 .pi/agents/h3-turbo-pilot/progress.md |  38 ++++++++++++
 scripts/h3_turbo_runner.py            | 113 ++++++++++++++++++++++++++++++++++
 2 files changed, 151 insertions(+)

## da878dc5c2e0b6e84abb081347aab275799bdf2c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T13:16:28-04:00
- Subject: [h3-params] 社区反应深挖：B站怀疑派+Reddit权威参数（larryvrh/Kijai PR已合/Spectrum/Ostris）+最佳选择结论


 .pi/agents/h3-params/progress.md | 21 +++++++++++++++++++++
 1 file changed, 21 insertions(+)

## 79bcbbc725ed9dc356c50bcd8b3ae7013f2dbd31
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-07T11:31:27-04:00
- Subject: [h3-params] 社区进展快照：08-07 lightX2V 4步加速LoRA发布+Kijai参数+三重加速组合拳实测


 .pi/agents/h3-params/progress.md | 21 +++++++++++++++++++++
 1 file changed, 21 insertions(+)

## e5457b775cea06bb993a6ad1ce328e05d616a6ae
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-06T11:10:10-04:00
- Subject: [h3-params] 首轮讨论沉淀：放大路线调研结论+架构决策+H3社区BV清单


 .pi/agents/h3-params/progress.md | 50 ++++++++++++++++++++++++++++++++++++++++
 1 file changed, 50 insertions(+)

## 6d28d11bf51a09ea51b0b53e043608c80af2f964
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-06T08:06:01-04:00
- Subject: [speech-video] BGM V2：简单风重生成+60s长段减接缝+混音三改（音量0.4/sidechain加强/中频让位）


 .pi/agents/speech-video/progress.md                  |  16 ++++++++++------
 .../speech-video/assets/ace/v2_seg1_intro.wav        | Bin 0 -> 1058478 bytes
 .../speech-video/assets/ace/v2_seg2_constructive.wav | Bin 0 -> 5609598 bytes
 .../speech-video/assets/ace/v2_seg3_xexam_long.wav   | Bin 0 -> 10584078 bytes
 .../speech-video/assets/ace/v2_seg4_xexam_tail.wav   | Bin 0 -> 2857758 bytes
 .../speech-video/assets/ace/v2_seg5_summary.wav      | Bin 0 -> 3401070 bytes
 experiments/speech-video/assets/bgm_full_ace_v2.wav  | Bin 0 -> 23519490 bytes
 .../speech-video/assets/debate_final_acebgm_v2.mp4   | Bin 0 -> 10197564 bytes
 .../speech-video/assets/final_audio_ace_v2.wav       | Bin 0 -> 23520078 bytes
 9 files changed, 10 insertions(+), 6 deletions(-)

## 11ced55f43bd059e1ccdbef9373be75fa7838dbe
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-06T05:10:12-04:00
- Subject: [speech-video] ACE-Step 版 BGM 素材落库（6段wav+bgm_full+final_audio+对比版mp4）


 .../speech-video/assets/ace/ace_seg1_intro.wav       | Bin 0 -> 1058478 bytes
 .../assets/ace/ace_seg2_constructive.wav             | Bin 0 -> 4798158 bytes
 .../speech-video/assets/ace/ace_seg3_xexam_a.wav     | Bin 0 -> 4318350 bytes
 .../speech-video/assets/ace/ace_seg4_xexam_b.wav     | Bin 0 -> 4318350 bytes
 .../speech-video/assets/ace/ace_seg5_xexam_c.wav     | Bin 0 -> 3563358 bytes
 .../speech-video/assets/ace/ace_seg6_summary.wav     | Bin 0 -> 5447310 bytes
 experiments/speech-video/assets/bgm_full_ace.wav     | Bin 0 -> 23519490 bytes
 .../speech-video/assets/debate_final_acebgm.mp4      | Bin 0 -> 10201140 bytes
 experiments/speech-video/assets/final_audio_ace.wav  | Bin 0 -> 23520078 bytes
 9 files changed, 0 insertions(+), 0 deletions(-)

## 1cd6a0f7274dc1dfce6edf9b0204ee7949cb49fe
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-06T05:10:06-04:00
- Subject: [speech-video] ACE-Step 版 BGM 完成：6段生成+拼接混音，对比版 debate_final_acebgm.mp4（旧版保留）


 .pi/agents/speech-video/progress.md | 9 +++++++++
 1 file changed, 9 insertions(+)

## b23eeb988c08348d5dcbd554e4b971df193943ee
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-06T04:48:46-04:00
- Subject: [speech-video] progress 更新：ACE-Step 模型就绪 + BGM 重做 runbook


 .pi/agents/speech-video/progress.md | 20 +++++++++++++++++++-
 1 file changed, 19 insertions(+), 1 deletion(-)

## a6c2b58fec72fb423a69e7265916c313719bde22
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-06T03:59:06-04:00
- Subject: [speech-video] 首个试验项目：音频+文字→视频 全流程交付（管线+BGM文档、skill治理框架、experiments/speech-video 归档）


 .pi/agents/speech-video/progress.md                |  36 +++++
 AGENTS.md                                          |   6 +
 docs/12_speech_to_video_pipeline.md                | 101 +++++++++++++
 docs/13_bgm_music_production.md                    |  78 ++++++++++
 docs/14_skill_governance.md                        |  82 +++++++++++
 docs/INDEX.md                                      |   3 +
 experiments/speech-video/README.md                 |  46 ++++++
 experiments/speech-video/assets/anim_F1.mp4        | Bin 0 -> 282544 bytes
 experiments/speech-video/assets/anim_F1_v2.mp4     | Bin 0 -> 177880 bytes
 experiments/speech-video/assets/anim_F5.mp4        | Bin 0 -> 142658 bytes
 experiments/speech-video/assets/anima_sample.png   | Bin 0 -> 778570 bytes
 experiments/speech-video/assets/bgm_bed.wav        | Bin 0 -> 23161398 bytes
 experiments/speech-video/assets/bgm_full.wav       | Bin 0 -> 23519490 bytes
 experiments/speech-video/assets/bgm_seg1.wav       | Bin 0 -> 1916204 bytes
 experiments/speech-video/assets/bgm_seg2.wav       | Bin 0 -> 1916204 bytes
 experiments/speech-video/assets/bgm_seg3.wav       | Bin 0 -> 1596204 bytes
 .../speech-video/assets/debate_final_animated.mp4  | Bin 0 -> 10234369 bytes
 .../speech-video/assets/debate_final_sound.mp4     | Bin 0 -> 5312379 bytes
 experiments/speech-video/assets/final_audio.wav    | Bin 0 -> 23519490 bytes
 experiments/speech-video/assets/krea_sample.png    | Bin 0 -> 552735 bytes
 experiments/speech-video/assets/narr_denoised.wav  | Bin 0 -> 23520078 bytes
 experiments/speech-video/assets/sfx_applause.wav   | Bin 0 -> 176478 bytes
 experiments/speech-video/assets/sfx_ding.wav       | Bin 0 -> 44178 bytes
 experiments/speech-video/assets/sfx_full.wav       | Bin 0 -> 22755678 bytes
 experiments/speech-video/assets/sfx_gavel.wav      | Bin 0 -> 35358 bytes
 experiments/speech-video/assets/sfx_whoosh.wav     | Bin 0 -> 39768 bytes
 experiments/speech-video/data/animation_plan.md    |  30 ++++
 experiments/speech-video/data/motion_map.json      |  24 ++++
 experiments/speech-video/data/ovl/badge2.txt       |   1 +
 experiments/speech-video/data/ovl/badge3.txt       |   1 +
 experiments/speech-video/data/ovl/badge7.txt       |   1 +
 experiments/speech-video/data/ovl/badgeA.txt       |   1 +
 experiments/speech-video/data/ovl/badgeS.txt       |   1 +
 experiments/speech-video/data/ovl/badgeX.txt       |   1 +
 experiments/speech-video/data/ovl/closing.txt      |   2 +
 experiments/speech-video/data/ovl/topic.txt        |   4 +
 experiments/speech-video/data/ovl/topic_label.txt  |   1 +
 experiments/speech-video/data/scenes_v3.json       | 134 ++++++++++++++++++
 experiments/speech-video/data/storyboard.md        |  35 +++++
 experiments/speech-video/data/subtitles.srt        | 120 ++++++++++++++++
 experiments/speech-video/data/subtitles_hms.srt    | 120 ++++++++++++++++
 experiments/speech-video/data/transcript.json      | 157 +++++++++++++++++++++
 experiments/speech-video/scripts/animate_batch.py  |  44 ++++++
 experiments/speech-video/scripts/animate_frame.py  |  62 ++++++++
 experiments/speech-video/scripts/assemble_video.py |  84 +++++++++++
 experiments/speech-video/scripts/gen_bgm.py        |  30 ++++
 experiments/speech-video/scripts/gen_scenes.py     |  73 ++++++++++
 workflows/sample_anima_debate.json                 | 101 +++++++++++++
 workflows/sample_krea_debate.json                  | 101 +++++++++++++
 49 files changed, 1480 insertions(+)

## 636d6a875e794a28c9fd2d723adbc3060507e378
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T03:55:44-04:00
- Subject: [context-opt] progress 收尾：待 /reload 验证 excludeTools


 .pi/agents/context-opt/progress.md | 6 ++++++
 1 file changed, 6 insertions(+)

## f9cd1c542d9c30e9bc0b7a38477bf36aa49d2ac6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T03:54:41-04:00
- Subject: [context-opt] 上下文优化：AGENTS 压缩（3277→2861B）+ comfyui skill 描述精简 + progress


 .pi/agents/context-opt/progress.md |  7 +++++++
 .pi/skills/comfyui/SKILL.md        |  2 +-
 AGENTS.md                          | 40 +++++++++++++++++++-------------------
 3 files changed, 28 insertions(+), 21 deletions(-)

## a39e923854148e18d74eb0532447d737b47d1d1b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T03:52:56-04:00
- Subject: [h3-patch-test] 收尾：restart_comfyui.sh（安全重启+nosage参数化）+ h3_batch_runner.py（提交确认加固）；WSL 56GB 配置待生效


 .pi/agents/h3-patch-test/progress.md |   7 ++
 scripts/h3_batch_runner.py           | 136 +++++++++++++++++++++++++++++++++++
 scripts/restart_comfyui.sh           |  94 ++++++++++++++++++++++++
 3 files changed, 237 insertions(+)

## 556f188620144eed05c2e3fd8b52319ec61654ce
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T03:23:47-04:00
- Subject: [h3-patch-test] 补测批 D 完成：快速档去 MC（75s/条实测）、sage 音频零影响、fp8 矩阵；docs/09 + params 更新


 .pi/agents/h3-patch-test/progress.md    | 24 ++++++++++++++++++++++++
 .pi/skills/comfyui/references/params.md |  4 ++--
 docs/09_h3_test_plan.md                 | 33 +++++++++++++++++++++++++++++++++
 3 files changed, 59 insertions(+), 2 deletions(-)

## 40328ea50539127a39313f6c57b07e2ef92d9256
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T03:16:18-04:00
- Subject: [多agent协议] [STATE] 格式补充：全局待办编号化 T1/T2 + 用户决策标记


 AGENTS.md | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

## 87ea6b49033153fb974fefe881574777faff6c4b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T03:02:25-04:00
- Subject: [多agent协议] 落地：AGENTS 协作纪律+[STATE]+progress 模板，05 归档迁 mem0


 .pi/agents/PROGRESS_TEMPLATE.md | 23 ++++++++++++++
 AGENTS.md                       | 39 +++++++++++++++++-------
 docs/05_TEMPLATE.md             | 41 -------------------------
 docs/05_session_handoff.md      | 66 -----------------------------------------
 docs/INDEX.md                   |  2 +-
 5 files changed, 53 insertions(+), 118 deletions(-)

## 387fe2697259dd27d577ae6a1a60233acc8cba10
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T02:02:00-04:00
- Subject: docs: 整理归档——bernini 快照移入 docs/04，case_library 改 11 解编号冲突，INDEX 补全 07-11 导航并更新速览


 docs/02_models.md                                  |  2 +-
 .../04_bernini_int8_findings.md                    |  6 ++--
 ...10_h3_case_library.md => 11_h3_case_library.md} |  0
 docs/INDEX.md                                      | 34 +++++++++++++---------
 4 files changed, 24 insertions(+), 18 deletions(-)

## 6704334022289c52354527baa4456b2ef17b78a7
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T02:00:41-04:00
- Subject: H3 fl2va 批量优化讨论落盘：新增 docs/10，重写 05 handoff（压缩归档）


 docs/05_session_handoff.md       | 97 +++++++++++++++++-----------------------
 docs/10_h3_batch_optimization.md | 83 ++++++++++++++++++++++++++++++++++
 2 files changed, 124 insertions(+), 56 deletions(-)

## dac445fff47b3e9c96d12664733c1e529d850a9e
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-05T01:54:31-04:00
- Subject: docs: 瘦身 session_handoff（10.7KB→3.5KB），已完结测试报告压成指针指向 docs/08、docs/09


 docs/05_session_handoff.md | 180 ++++++++++++++-------------------------------
 1 file changed, 57 insertions(+), 123 deletions(-)

## 930326168bb9736200ae966d17b91bfd6d4d4886
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T23:38:56-04:00
- Subject: handoff: 新增顺手级待办——H3 速度旧条目记忆整理（id 00d44594 补含加载条件）


 docs/05_session_handoff.md | 1 +
 1 file changed, 1 insertion(+)

## 1f4fb3bd599355469f78435ccc595cb72483c133
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T22:44:31-04:00
- Subject: 方法论整合：提示词/参考图/数值参数三维度归位 params.md + docs/10 总览


 .pi/skills/comfyui/references/params.md | 8 ++++++++
 docs/10_h3_case_library.md              | 4 ++++
 2 files changed, 12 insertions(+)

## 9b700d4a349f0b5494a95e1625346b98a3384f25
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T22:30:36-04:00
- Subject: skill: params.md 新增参考图准备规范（通用+Ref2VA 专项），调研结论落盘 mem0


 .pi/skills/comfyui/references/params.md | 10 ++++++++++
 1 file changed, 10 insertions(+)

## b3fa74bd097b98a696bd7b91252a57162f1f67cd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T14:54:56-04:00
- Subject: 批6完成（E06）


 docs/10_h3_case_library.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## c7fc18747bc45569b7f8df9b763fd7a412468c16
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T14:49:13-04:00
- Subject: 批6：真人崩点梯度 + 动画9s


 docs/10_h3_case_library.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## 4a5c5995855a5f3dd9f148d2d34b1181a3254a8b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T14:09:08-04:00
- Subject: 批5：8s指令遵循（动画vs真人）


 docs/10_h3_case_library.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## a0c444576edafe79385902435f0233044564a7e0
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T12:34:30-04:00
- Subject: 批4完成 + 阶段总结（24案例全部落盘）


 docs/10_h3_case_library.md | 14 ++++++++++++++
 1 file changed, 14 insertions(+)

## 6edef8cc804525b2b2c1fd4579823e9c18220c73
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T11:53:26-04:00
- Subject: 批3案例 + 批2补全（共18案例）


 docs/10_h3_case_library.md | 8 +++++++-
 1 file changed, 7 insertions(+), 1 deletion(-)

## 14df67c0257ef196f4bad9a4b4a3fe2d41993c17
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T11:28:45-04:00
- Subject: 批2案例（6条：双图融合+文化特色）


 docs/10_h3_case_library.md | 6 ++++++
 1 file changed, 6 insertions(+)

## e1c06b31935579178e26c660a200f98c7362e28c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T10:54:38-04:00
- Subject: 案例库建立 + 批1（6案例）


 docs/10_h3_case_library.md | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)

## 6c514470776ee38bfaddbd02e3475014bf1687a8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T10:39:20-04:00
- Subject: B 参考强度测试完成（6条）


 docs/09_h3_test_plan.md | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)

## 9d7aa8beb1fea03f5197d9bd920591fb5c02e25a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T09:56:51-04:00
- Subject: A 提示词强度测试完成：镜头控制最强(3.5x)、动作中等(1.7x)


 docs/09_h3_test_plan.md | 18 ++++++++++++++++++
 1 file changed, 18 insertions(+)

## 53a326e4bbb5dd5da1f7eca799bc75b35ed6017b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T09:25:10-04:00
- Subject: 底图库扩充：清凉美女+文化特色 43 张 + Highres LoRA


 docs/09_h3_test_plan.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## 299e07397db07b0fe4a8c124248d9485036af509
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T09:12:45-04:00
- Subject: H3 ref 底图库 78 张（写实+插画，含 HD/快速对照）


 docs/09_h3_test_plan.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## b7d7bad4fa35163d95b33d91762835e36300a512
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T08:35:58-04:00
- Subject: 社区调研：强度控制=语言量化 + 导演台 4 流派


 docs/09_h3_test_plan.md | 19 +++++++++++++++++++
 1 file changed, 19 insertions(+)

## 3a2b61d7f234e109dd7f502b2eb9e1c8f41c00cc
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T08:27:12-04:00
- Subject: 会话完结交接：H3 管线定论 + 坑清单 + 待办


 docs/05_session_handoff.md | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)

## 601c120711c92cc6c256611ec1cbc81d7f27af20
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T08:26:15-04:00
- Subject: skill params 分册固化 H3 参数经验


 .pi/skills/comfyui/references/params.md | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)

## 486013d0dd7c5427e4dcd7df10c771a8c294d25c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T08:25:56-04:00
- Subject: 画面确认一致 + 管线固化：抽卡 sage+MC+14步 / 成片 sage+20步


 docs/09_h3_test_plan.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## b8d3b9a2682c86d6345f824d89210bd0810f72dd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T08:18:56-04:00
- Subject: sage/MC 10s 放大测试


 docs/09_h3_test_plan.md | 5 +++++
 1 file changed, 5 insertions(+)

## 06d64d22ce928b037eb78c2459a215841aa61f34
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T07:59:14-04:00
- Subject: sage/MC 四状态画面对比 + review/I_sg_mc


 docs/09_h3_test_plan.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## 5d8d7f29ecfdbe931ecac4cd67eff40231d71647
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T06:55:59-04:00
- Subject: 加速组合最终数据：sage+MC 叠加 225s


 docs/09_h3_test_plan.md | 11 +++++++++++
 1 file changed, 11 insertions(+)

## 84c7effeff8252e4700fb056452ef41b9f2e7119
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T06:42:24-04:00
- Subject: SageAttention 关键发现：10s+ 加速 40-48%，必须开启


 docs/09_h3_test_plan.md | 16 ++++++++++++++++
 1 file changed, 16 insertions(+)

## d2d4b2382c63ce00eac338f0e58b683e530c9ede
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T05:11:42-04:00
- Subject: 讨论定论：fp8 默认 + MC 机制分析


 docs/09_h3_test_plan.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## 7ffa6cdd66df501ce1a878fb200a788ed8575734
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T04:20:57-04:00
- Subject: fp8 多案例完成 + review 更新


 docs/09_h3_test_plan.md | 9 +++++++++
 1 file changed, 9 insertions(+)

## e75f2efce073045287a687769b9c4291f4768484
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T03:57:16-04:00
- Subject: review 对比目录 + MotionCache 音频专项测量


 docs/09_h3_test_plan.md | 10 ++++++++++
 1 file changed, 10 insertions(+)

## b52b098ae1b7b9bebacad37b84fd30694e14c63f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T03:42:49-04:00
- Subject: H3 经验落盘 + 后续测试建议


 docs/09_h3_test_plan.md | 14 ++++++++++++++
 1 file changed, 14 insertions(+)

## c961a86aaefbdafb76feea8665c2d5fb719929b7
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T03:37:31-04:00
- Subject: H3 目测反馈整理


 docs/09_h3_test_plan.md | 9 +++++++++
 1 file changed, 9 insertions(+)

## 21729ddd081b69272e0f07421912e33026b55914
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T02:08:24-04:00
- Subject: H3 社区加速节点调研 + MotionCache 实测


 docs/09_h3_test_plan.md | 8 ++++++++
 1 file changed, 8 insertions(+)

## ad56a64fee5ffb709f339d44b3c2b3ccfc050d16
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T01:41:58-04:00
- Subject: H3 补测收尾：交接更新 + 移除 asset-hashing 参数（内存坑）


 docs/05_session_handoff.md | 5 +++++
 1 file changed, 5 insertions(+)

## cfd38706df8f699ff79c3c874aaec159097f77fc
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T01:41:41-04:00
- Subject: H3 补测批C：首尾帧 + 768x448 矩阵，最终速度矩阵定论


 docs/09_h3_test_plan.md | 21 +++++++++++++++++++++
 1 file changed, 21 insertions(+)

## fc9bdfcee25424a0bfefdca867cf7532a2c70bed
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T01:23:54-04:00
- Subject: H3 补测批B：seed 稳定性 + fp8 多组


 docs/09_h3_test_plan.md | 11 +++++++++++
 1 file changed, 11 insertions(+)

## 42ef5c1d407d2dd6300ecf9805f9fc7fe6d0e45f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-04T01:11:07-04:00
- Subject: H3 补测批A：steps 干净环境


 docs/09_h3_test_plan.md | 10 ++++++++++
 1 file changed, 10 insertions(+)

## 4997e53f2c74d21182455454b2a405ac61806939
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T15:00:17-04:00
- Subject: H3 夜跑报告交接更新


 docs/05_session_handoff.md | 21 +++++++++++++++++++++
 1 file changed, 21 insertions(+)

## 09ff6ee7b494777b5e3ea11e54ca5fcd8e341a57
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T14:59:59-04:00
- Subject: H3 全阶段测试完成：steps/提示词/参考图/量化/干净环境速度


 docs/09_h3_test_plan.md | 35 +++++++++++++++++++++++++++++++++++
 1 file changed, 35 insertions(+)

## c700f7aef3f400f7a1c45215e79efb3fa6ee76f5
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T14:38:03-04:00
- Subject: H3 阶段3 完成：ref2va 参考图响应测试


 docs/09_h3_test_plan.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)

## c1168c2cdc7007b582e41396ae1f7699d7764769
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T14:20:56-04:00
- Subject: H3 测试阶段1/2 完成：steps 扫描 + 提示词响应


 docs/09_h3_test_plan.md | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)

## 403894b80a210e4b775078a47fd5c20453946ac3
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T13:49:54-04:00
- Subject: H3 测试计划 v1 + Ref2VA 视频参考 TE-cpu 方案验证


 docs/09_h3_test_plan.md                      | 65 ++++++++++++++++++++++++++++
 workflows/minimax_h3_ref2va_img_api.json     | 22 ++++++++++
 workflows/minimax_h3_ref2va_img_vid_api.json | 24 ++++++++++
 3 files changed, 111 insertions(+)

## c365ef11c50ae52860ee3825a4e95d99854ccd9f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T11:58:10-04:00
- Subject: H3 提示词增强方案调研文档 + 交接更新


 docs/05_session_handoff.md |  8 ++++++
 docs/08_h3_prompt_agent.md | 66 ++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 74 insertions(+)

## 280ed5300cb684eba3e6941122327ff115a60bcc
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T11:34:27-04:00
- Subject: docs: 交接文档记录 skill 体系更新（nodes.md/新节点流程/来源标注）


 docs/05_session_handoff.md | 6 ++++++
 1 file changed, 6 insertions(+)

## ab87aa7d341b2274500e9c24864dcdd3ca473252
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T11:31:47-04:00
- Subject: skill: 新增 nodes.md 节点速查（官方/社区/本地实测分层）+ 新节点落地流程


 .pi/skills/comfyui/SKILL.md               |   7 +-
 .pi/skills/comfyui/references/learning.md |   9 ++
 .pi/skills/comfyui/references/nodes.md    | 133 ++++++++++++++++++++++++++++++
 .pi/skills/comfyui/references/params.md   |   5 +-
 4 files changed, 149 insertions(+), 5 deletions(-)

## 4534eb6db161823f75efda0f42cdb462ff1b33a8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T11:09:22-04:00
- Subject: docs: 05 会话交接套 activeContext 模板（05_TEMPLATE.md）——新增活跃决策/模式偏好板块，AGENTS 开场流程引用模板


 AGENTS.md                  |  4 ++--
 docs/05_TEMPLATE.md        | 41 +++++++++++++++++++++++++++++++++++++++++
 docs/05_session_handoff.md | 40 ++++++++++++++++++++++++++++++++++------
 3 files changed, 77 insertions(+), 8 deletions(-)

## 9468b61dc08f4e8d4731d0258dba485018c428e9
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T10:56:08-04:00
- Subject: MiniMax H3 落地首测：ComfyUI 升级 0.30 + 模型下载 + I2V/T2V 工作流 + 首测成功（带立体声音频）


 docs/02_models.md                 |   12 +
 docs/05_session_handoff.md        |  102 +--
 workflows/minimax_h3_i2v.json     | 1692 +++++++++++++++++++++++++++++++++++++
 workflows/minimax_h3_i2v_api.json |   22 +
 workflows/minimax_h3_r2v.json     | 1259 +++++++++++++++++++++++++++
 workflows/minimax_h3_t2v.json     | 1543 +++++++++++++++++++++++++++++++++
 workflows/minimax_h3_t2v_api.json |   20 +
 7 files changed, 4585 insertions(+), 65 deletions(-)

## 93e600017f6566a72953af4640b7674c73025173
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T09:51:43-04:00
- Subject: 精简项目 AGENTS.md：决策树下沉至 mem0 skill，保留项目专属约束


 AGENTS.md | 22 +++++++---------------
 1 file changed, 7 insertions(+), 15 deletions(-)

## 6db25a7ec730a14cf57d8430253d9594893255fb
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T02:02:07-04:00
- Subject: bernini int8: 归档调研快照 + 下载经验落盘 + 主力工作流切 int8

- docs/02_models.md: 补 int8 下载源/URL/网络实测/三重校验方法
- docs/INDEX.md: 登记 bernini_int8_findings.md 快照
- 下载经验进 Mem0（comfy-ops 池）
- video_bernini_r_v2v_test.json: fp8 → int8（视频任务甜点：快21%画质无损）
- 完整调研快照保留项目根 bernini_int8_findings.md

 docs/02_models.md                       | 7 +++++++
 docs/INDEX.md                           | 1 +
 workflows/video_bernini_r_v2v_test.json | 4 ++--
 3 files changed, 10 insertions(+), 2 deletions(-)

## 143a6df7cb9a0e1c0c3794d6370cb5fdbc363153
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T01:46:16-04:00
- Subject: AGENTS: 决策树补 AGENTS 层（每次必用规则→用户级）+ 指向完整判定树


 AGENTS.md | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

## 68d5cf173a8b856cb2a67276e83ed7f0e2c8c455
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T01:09:23-04:00
- Subject: AGENTS: 精简 — 网络章节上移用户级，记忆纪律并入决策树

- 删除网络章节（已在用户级全局）
- 删除与用户级重复的"记忆纪律"章节，保留"手册 vs 经验"规则并入决策树
- 分布原则：AGENTS 只留每次会话必用的确定性规则；经验/偏好 → Mem0

 AGENTS.md | 15 +--------------
 1 file changed, 1 insertion(+), 14 deletions(-)

## 9cf7da9c1f54a3030915879ac02e92f0457e03d8
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T01:04:57-04:00
- Subject: refactor(mem0): 删除项目级 mem0 skill，统一用户级（全局单一权威）

- mem0 已全局化，skill 只在 ~/.pi/agent/skills/mem0/（对所有项目可见）
- 消除双份维护 + pi 同名 skill 项目级遮蔽用户级的 skipped 噪音
- docs/01_environment.md 引用改指向用户级

 .pi/skills/mem0/SKILL.md | 86 ------------------------------------------------
 docs/01_environment.md   |  2 +-
 2 files changed, 1 insertion(+), 87 deletions(-)

## de2d04fd1c448c8571514d96f1c7162c75e89df2
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T00:58:51-04:00
- Subject: docs(mem0): 同步已知坑（BM25 缺失运维 + 迁移隐患）


 .pi/skills/mem0/SKILL.md | 1 +
 1 file changed, 1 insertion(+)

## 22b52aaea63e05165fddaba144d60dcc7f3df5cf
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T00:16:17-04:00
- Subject: docs(mem0): 同步已知坑（get_all top_k 漏检）


 .pi/skills/mem0/SKILL.md | 1 +
 1 file changed, 1 insertion(+)

## c308c3ea573de75bf226b5edf963169c3780392a
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-03T00:11:47-04:00
- Subject: docs(mem0): 整理同步 — 项目级 SKILL 同步全局化版 + docs 修正过时引用

- .pi/skills/mem0/SKILL.md 同步为用户级最新版（全局路径）
- docs/01_environment.md: mem0_mcp.py → mem0.sh 跳板
- docs/05_session_handoff.md: 移除旧锁问题，标注已全局化

 .pi/skills/mem0/SKILL.md   | 10 ++++++----
 docs/01_environment.md     |  2 +-
 docs/05_session_handoff.md |  2 +-
 3 files changed, 8 insertions(+), 6 deletions(-)

## 88b1fd307a26650637fb70dd1f499516b5b5b6d2
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T23:24:42-04:00
- Subject: mem0 全局化: 脚本迁至 ~/.pi/agent/mem0/，项目脚本改跳板

- scripts/mem0.sh → 跳板（exec 全局脚本）
- 删除 scripts/mem0_mcp.py / mem0_migrate.py（已全局化）
- 数据已迁至 ~/.local/share/mem0/（.mem0 保留备份）

 scripts/mem0.sh         | 108 +----------------------------
 scripts/mem0_mcp.py     | 177 ------------------------------------------------
 scripts/mem0_migrate.py |  58 ----------------
 3 files changed, 3 insertions(+), 340 deletions(-)

## 4c9c6cfe275d94d6226493e1657164270d17702d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T22:34:31-04:00
- Subject: docs(mem0): 标注 mem0 已提升用户级（全局 mcp + 用户级 skill + 全局规则）


 .pi/skills/mem0/SKILL.md | 6 +++++-
 1 file changed, 5 insertions(+), 1 deletion(-)

## 92cd3a3efc1eced2a04dae8e4744097337d8b1a1
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T13:05:48-04:00
- Subject: feat(mem0): 双池架构 — global 跨项目通用池 + comfy-ops 项目池，recall 默认合并

- mem0_mcp.py: GLOBAL_USER 常量；recall 默认双池检索按分数合并去重（带 pool 标记）
- retain 支持 user_id="global" 显式存通用经验；list 按池查看
- AGENTS.md 决策树：通用/跨界 → global（检索命中式，放宽不易丢）
- 迁移 4 条通用经验到 global（网络环境/云服务偏好/pkill坑/WSL2显存测量）
- SKILL.md 双池架构说明

 .pi/skills/mem0/SKILL.md |  2 ++
 AGENTS.md                |  8 +++++++-
 scripts/mem0_mcp.py      | 52 ++++++++++++++++++++++++++++++++++++++----------
 3 files changed, 50 insertions(+), 12 deletions(-)

## 586ad363bfc62e375cc241be2fa582ac476b3359
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T13:03:53-04:00
- Subject: 08-02 Bernini编辑验证/素材库管线/预览插件/SageAttention探索


 docs/05_session_handoff.md                | 169 ++++++++-----------
 docs/07_video_material.md                 |  55 ++++++
 scripts/prep_bernini.py                   |  78 +++++++++
 scripts/video_gallery.py                  | 119 +++++++++++++
 workflows/anima_alya_169_i2i.json         |  97 +++++++++++
 workflows/anima_alya_169_t2i.json         | 112 +++++++++++++
 workflows/anima_alya_768_t2i.json         |   4 +-
 workflows/bernini_edit_81_base.json       | 242 +++++++++++++++++++++++++++
 workflows/bernini_edit_81_int8.json       | 242 +++++++++++++++++++++++++++
 workflows/wan22_720p_test.json            | 266 ++++++++++++++++++++++++++++++
 workflows/wan22_alya169_720p.json         | 266 ++++++++++++++++++++++++++++++
 workflows/wan22_alya169_832x480.json      | 266 ++++++++++++++++++++++++++++++
 workflows/wan22_nosage241_combo.json      | 215 ++++++++++++++++++++++++
 workflows/wan22_nosage241_combo_hilo.json | 215 ++++++++++++++++++++++++
 workflows/wan22_nosage480_8s_test.json    | 215 ++++++++++++++++++++++++
 workflows/wan22_res_sweep_16fps.json      | 266 ++++++++++++++++++++++++++++++
 workflows/wan22_sage480_test.json         | 215 ++++++++++++++++++++++++
 17 files changed, 2938 insertions(+), 104 deletions(-)

## e5d181bf0aef707ade15e8892b78aa735649308b
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T12:14:57-04:00
- Subject: ops(mem0): PID 文件管理脚本 mem0.sh + 启动离线化

- scripts/mem0.sh {start|stop|restart|status}，PID 文件 .mem0/mem0.pid
- 废弃 pkill -f（会匹配自身命令行误杀）和 start_mem0.sh
- mem0_mcp.py: HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE 提前到 import 前
- 启动不再依赖网络（bge-m3 缓存 4.3G 完整），~35s 就绪
- SKILL.md 运维/已知坑同步

 .pi/skills/mem0/SKILL.md   |   8 +--
 scripts/mem0.sh            | 106 ++++++++++++++++++++++++++++++++++++++
 scripts/mem0_mcp.py        |  10 ++--
 scripts/pexels_download.py | 124 +++++++++++++++++++++++++++++++++++++++++++++
 scripts/start_mem0.sh      |  15 ------
 5 files changed, 242 insertions(+), 21 deletions(-)

## 01f8deef6c0e3e202388788abb9592b730d017a9
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T12:03:46-04:00
- Subject: fix(mem0): memory_update 误传 user_id 导致必失败，已修（库不支持该参数）

- mem0 Memory.update(memory_id, text) 无 user_id 参数（创建后不可变）
- wrapper 曾传 user_id= 导致 unexpected keyword argument
- 保留参数兼容调用方，实际不再传递；SKILL.md 记录坑

 .pi/skills/mem0/SKILL.md | 1 +
 scripts/mem0_mcp.py      | 8 ++++++--
 2 files changed, 7 insertions(+), 2 deletions(-)

## 82a4cd1f665ab798855e1620182eb90b8874b726
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T11:57:08-04:00
- Subject: docs: 修正 Manager 旧版描述（已更新到 2026-07-30，API 可用；conflict 红标为静态噪音）


 docs/06_extras_install.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## 339a5001265691003ffc908a22f31c1ee0655618
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T11:51:25-04:00
- Subject: SKILL: 标注 Wan2.1 已删除（2025-08-02，被 2.2 覆盖），VAE 保留


 .pi/skills/comfyui/SKILL.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## 076b953c30e173dc1d61d80f0f021059ad0d561d
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T08:27:50-04:00
- Subject: mem0: 强制 bge-m3 embedder CPU 推理，释放 2.6GB 显存

- sentence-transformers 默认探测 CUDA 后把 bge-m3 放 GPU（实测 2.6GB）
- embedder config 加 model_kwargs:{"device":"cpu"}
- SKILL.md 纠错 + 记录 WSL2 nvidia-smi N/A 测量坑

 .pi/skills/mem0/SKILL.md | 5 ++++-
 scripts/mem0_mcp.py      | 7 ++++++-
 2 files changed, 10 insertions(+), 2 deletions(-)

## be2c1769875e60618dd0049acd60877c5ce22fb4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T07:23:30-04:00
- Subject: feat: mem0 改 HTTP 常驻模式（streamable-http :8899）——单实例服务所有会话，消除 stdio 多进程撞锁；key 改 ~/.config 文件读取


 .pi/skills/mem0/SKILL.md | 12 +++++++-----
 scripts/mem0_mcp.py      | 23 +++++++++++++++++------
 scripts/start_mem0.sh    | 15 +++++++++++++++
 3 files changed, 39 insertions(+), 11 deletions(-)

## 3e802c52ffaa251d80051573357268d038871418
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T07:14:24-04:00
- Subject: docs: mem0 skill 补 Qdrant 单实例锁坑（多进程冲突处理）


 .pi/skills/mem0/SKILL.md | 1 +
 1 file changed, 1 insertion(+)

## ca725cce5da7a80325f6ce2d4974d9b41faaf2ef
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:55:02-04:00
- Subject: feat: mem0 支持独立 key（MEM0_DEEPSEEK_API_KEY 优先，回退主 key）


 scripts/mem0_mcp.py | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

## ff1a337af689195ff248b14ed4cf88a3a7a854d5
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:53:49-04:00
- Subject: feat: AGENTS.md 新会话开场流程（读 INDEX/05 + memory_recall）——用户只需直接说任务


 AGENTS.md | 7 +++++++
 1 file changed, 7 insertions(+)

## eb010377d144d73a64334863d3b7bec66d77df4f
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:47:05-04:00
- Subject: docs: Bernini 收尾——06 精简为纯手册（7KB→4KB）+ references/workflows.md 补 Bernini 档案


 .pi/skills/comfyui/references/workflows.md |  19 +++
 docs/06_extras_install.md                  | 203 ++++++++++++-----------------
 2 files changed, 101 insertions(+), 121 deletions(-)

## 07c67b4b528afefa40070276e9045ac65121edc7
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:43:31-04:00
- Subject: refactor: 文档结构简化——docs 7→4（合并 01+03、删冗余 04）、02 补新模型、INDEX/mem0 skill 同步


 .pi/skills/mem0/SKILL.md | 13 ++++---
 docs/01_environment.md   | 73 +++++++++++++++++++++++++++++++++++++++
 docs/01_install.md       | 57 -------------------------------
 docs/02_models.md        | 15 +++++++-
 docs/03_api.md           | 89 ------------------------------------------------
 docs/04_workflows.md     | 69 -------------------------------------
 docs/INDEX.md            | 16 ++++-----
 7 files changed, 100 insertions(+), 232 deletions(-)

## 80e96c33b58bd419eb9490bb7e7efee5a1c5539e
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:39:53-04:00
- Subject: Bernini 10s 组合管线 + int8 选型 + 时长铁律 + WSL 48GB（2025-08-02 收尾）

- 10s 组合管线验证：Wan2.2 161帧@16fps(280s) → Bernini v2v(1310s)，清晰度 732→870，用户目视确认连贯
- 时长匹配铁律：源视频时长必须==输出时长（10s→5s 脑补/步伐乱根源）
- cfg/fps 对比：cfg1.0@16fps 清晰度最高(1320)，cfg1.5 压低画质+步伐乱
- int8_convrot 选型：视频快21%画质无损 → 默认；图像单帧留 fp8
- WSL 内存 32→48GB（OOM 两次崩溃后）；ComfyUI 模型缓存机制确认
- 新工作流：wan22_alya_10s_f16 / bernini_v2v_10s_f16 / bernini_int8_cfg10_fps16
- docs/06 + params.md + 05_handoff + SKILL 同步

 .pi/skills/comfyui/SKILL.md             |   4 +-
 .pi/skills/comfyui/references/params.md |  22 +++
 docs/05_session_handoff.md              |  17 ++
 docs/06_extras_install.md               |  14 ++
 workflows/bernini_int8_cfg10_fps16.json | 244 +++++++++++++++++++++++++++++
 workflows/bernini_v2v_10s_f16.json      | 244 +++++++++++++++++++++++++++++
 workflows/wan22_alya_10s_f16.json       | 269 ++++++++++++++++++++++++++++++++
 7 files changed, 813 insertions(+), 1 deletion(-)

## 043f207ee667f3b4047048574f876ef96006dcca
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:10:56-04:00
- Subject: docs: mem0 skill 补多 Agent 使用原则（零协调写/命名空间/权威边界/矛盾处理）


 .pi/skills/mem0/SKILL.md | 19 ++++++++++++++++---
 1 file changed, 16 insertions(+), 3 deletions(-)

## f8fa11709466f1c70955830fa9eac98b8acf1682
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T04:03:39-04:00
- Subject: feat: Mem0 中文提取（custom_instructions）+ BM25 混合检索 + delete 签名修正


 .pi/skills/mem0/SKILL.md | 9 +++++----
 scripts/mem0_mcp.py      | 7 ++++---
 2 files changed, 9 insertions(+), 7 deletions(-)

## 43b6fd864d5d53cd889a234f6db6d7c947bd6bd1
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T03:52:43-04:00
- Subject: docs: 05 待办追加 Mem0 系统状态与后续优化（中文输出/Codex接入/文档瘦身/BM25）


 docs/05_session_handoff.md | 2 ++
 1 file changed, 2 insertions(+)

## aaf6cbad4e3960b99be385d6be78c2d0c3bf7f91
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T03:16:20-04:00
- Subject: feat: Mem0 共享记忆系统落地——MCP server + 19 条经验迁移 + AGENTS.md 决策树 + mem0 skill


 .pi/skills/mem0/SKILL.md                |  54 +++++++
 AGENTS.md                               |  31 ++++
 docs/06_extras_install.md               |   3 +-
 scripts/mem0_mcp.py                     | 120 ++++++++++++++++
 scripts/mem0_migrate.py                 |  58 ++++++++
 workflows/bernini_int8_cfg15_fps16.json | 244 ++++++++++++++++++++++++++++++++
 6 files changed, 508 insertions(+), 2 deletions(-)

## 2dfe5581b0dd27b0675fafb238e425d1c069f2a7
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T03:02:46-04:00
- Subject: chore: 移除误提交的 .mem0 数据库（Mem0 本地存储不入库）


 .gitignore                                  |   1 +
 .mem0/qdrant/.lock                          |   1 -
 .mem0/qdrant/collection/mem0/storage.sqlite | Bin 12288 -> 0 bytes
 .mem0/qdrant/meta.json                      |   1 -
 4 files changed, 1 insertion(+), 2 deletions(-)

## 52ce9b439a49096561d8011d8ce513e5f2c60fef
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T03:02:39-04:00
- Subject: Bernini int8_convrot vs fp8_scaled 实测：视频任务 int8 快21%画质无损

- v2v 81帧: int8 105.1s/清晰度1023 vs fp8 133.1s/999 → int8 甜点，默认换用
- 图像单帧: int8 加载开销主导反而慢18%，画质无损(-0.9%)
- 对比图 output/compare/bernini_fp8_vs_int8.png
- 同步 docs/06 + params.md + bernini_int8_findings.md

 .mem0/qdrant/.lock                          |   1 +
 .mem0/qdrant/collection/mem0/storage.sqlite | Bin 0 -> 12288 bytes
 .mem0/qdrant/meta.json                      |   1 +
 .pi/skills/comfyui/references/params.md     |  12 +++
 bernini_int8_findings.md                    | 113 ++++++++++++++++++++++++++++
 docs/06_extras_install.md                   |   6 +-
 6 files changed, 132 insertions(+), 1 deletion(-)

## e3c7dccc36ea15c4bb03e40d452cb6088c5ed6f4
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T02:42:45-04:00
- Subject: Bernini 深度探索完成：组合管线验证通过（Wan2.2 I2V→Bernini v2v→补帧→超分）

- 核心结论：Bernini 是编辑器非生成器（in-context vs concat 硬锁）
- 最终管线 pipeline_wan22_bernini_golden.json 全链路验证（脸部/动作/风格保持）
- 新增工作流：bernini_static2v_test / bernini_rv2v_face_test / pipeline_wan22_bernini_golden
- docs/06: 任务类型表/机制差异/官方参数/提示词技巧
- 05_handoff: Bernini 探索结论 + 最终管线

 docs/05_session_handoff.md                   |   8 +-
 docs/06_extras_install.md                    |  37 ++++
 install.md                                   |   7 -
 workflows/bernini_rv2v_face_test.json        | 251 +++++++++++++++++++++++++++
 workflows/bernini_static2v_test.json         | 245 ++++++++++++++++++++++++++
 workflows/pipeline_wan22_bernini_golden.json | 244 ++++++++++++++++++++++++++
 6 files changed, 784 insertions(+), 8 deletions(-)

## 04e83e7aa4ed347e64bba45a6147a58ca37f1fd6
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T02:10:08-04:00
- Subject: 记录系统 OOM 崩溃 + comfy-cli 安装更新

- troubleshooting: OOM 崩溃分析（Bernini 40步大任务后 python 内存 30GB → OOM killer → dockerd panic → 重启）+ 防护与 setsid 重启命令
- SKILL: comfy-cli 1.13.0 已装 venv，解锁 MCP 8 个 comfy_cli_* 工具
- 注：static2v 测试任务因崩溃丢失（history 内存态），重启后需重跑

 .pi/skills/comfyui/SKILL.md                      |  3 ++-
 .pi/skills/comfyui/references/troubleshooting.md | 10 ++++++++++
 2 files changed, 12 insertions(+), 1 deletion(-)

## a181c3d54064169bbb01064c4ab2d7479f7a2766
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T00:31:59-04:00
- Subject: Bernini v2v 视频编辑测试成功（Alya 金色时刻重打光，整段一致，动作保留）

- workflows/video_bernini_r_v2v_test.json 固化（LoadVideo→GetVideoComponents→BerniniConditioning→SamplerCustom×2）
- docs/06: 追加 v2v 段落 + 踩坑（LoadVideo 只读 input/、SaveVideo 需 format/codec）
- 05_handoff: Bernini 图像+视频编辑全部 ✅
- 产出: output/video/bernini_v2v_alya_golden_00001_.mp4

 docs/05_session_handoff.md              |   2 +-
 docs/06_extras_install.md               |  12 ++
 workflows/video_bernini_r_v2v_test.json | 242 ++++++++++++++++++++++++++++++++
 3 files changed, 255 insertions(+), 1 deletion(-)

## 896665915a5be235095488e445fcd743cc08a1dd
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T00:29:11-04:00
- Subject: Bernini-R 图像编辑测试成功：官方管线（BerniniConditioning + res_multistep + SplitSigmas 3/3 + LoRA 3.0/1.5）

- workflows/video_bernini_r_test.json 固化为官方管线 API 版
- docs/06: Bernini 状态更新为已测成功 + 管线结构 + 4 个踩坑
- SKILL/05_handoff: 编辑能力标记 ✅，待办加 Bernini 视频编辑
- 产出: output/img_bernini/official_relight_00001_.png（928×1280 重打光，用户满意）

 .pi/skills/comfyui/SKILL.md         |   4 +-
 docs/05_session_handoff.md          |   1 +
 docs/06_extras_install.md           |  23 +++-
 workflows/video_bernini_r_test.json | 234 ++++++++++++++++++++++++++++++++++++
 4 files changed, 255 insertions(+), 7 deletions(-)

## e871f2ed2ecb064505e103b6f4d682cbb5b7288c
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T00:25:24-04:00
- Subject: docs: 网络配置以用户为准——Clash Rule+TUN（GitHub代理/国内直连），遇问题先与用户确认


 docs/06_extras_install.md | 9 +++++----
 1 file changed, 5 insertions(+), 4 deletions(-)

## 488cf2133cb5064e63736dff3119147758947490
- Author: shushu <xiangshushu@hotmail.com>
- Date: 2026-08-02T00:23:42-04:00
- Subject: docs: 修正网络经验——TUN 直连优先，-x 为失败兜底（非必须）；git Username 报错为认证问题


 docs/06_extras_install.md | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

## 942945601230fbf9ad82e5c4943cd588d5c490b3
- Author: shushu <sean@Eric>
- Date: 2026-08-01T14:04:44-04:00
- Subject: docs: 新增 06 图像编辑/超分工具安装记录（RMBG/ClearReality/Bernini 状态）+ SKILL/INDEX 增量


 .pi/skills/comfyui/SKILL.md |  5 +++++
 docs/06_extras_install.md   | 53 +++++++++++++++++++++++++++++++++++++++++++++
 docs/INDEX.md               |  1 +
 3 files changed, 59 insertions(+)

## a8f091625854001fbf2d8bd97c0f51a039981345
- Author: shushu <sean@Eric>
- Date: 2026-08-01T14:02:24-04:00
- Subject: Comfy-ops: Wan2.2 I2V 视频生成工作流 + SKILL 知识库 + 实测文档

- workflows/: ANIMA/KREA 生图 + Wan2.1/2.2 I2V + Bernini-R 编辑模板
- docs/: 安装/模型/API/工作流/会话交接全文档
- .pi/skills/comfyui/: SKILL 主干 + 4 分册（参数/工作流/踩坑/学习）
- 脚本: comfy_client.py / run_workflow.py / 下载与监控脚本
- 实测沉淀: 底图分辨率线性增益、41帧@8fps 5秒标准、多人视频、Wan2.1 vs 2.2

 .gitignore                                       |   15 +
 .pi/skills/comfyui/SKILL.md                      |   59 +
 .pi/skills/comfyui/references/learning.md        |   81 +
 .pi/skills/comfyui/references/params.md          |   64 +
 .pi/skills/comfyui/references/troubleshooting.md |   41 +
 .pi/skills/comfyui/references/workflows.md       |  105 +
 comfy_client.py                                  |  148 +
 docs/01_install.md                               |   57 +
 docs/02_models.md                                |  101 +
 docs/03_api.md                                   |   89 +
 docs/04_workflows.md                             |   69 +
 docs/05_session_handoff.md                       |   87 +
 docs/INDEX.md                                    |   61 +
 download_models.sh                               |   63 +
 install.md                                       |    7 +
 monitor_download.sh                              |   50 +
 run_workflow.py                                  |  134 +
 workflows/anima_alya_768_t2i.json                |   82 +
 workflows/anima_i2v_test.json                    |   19 +
 workflows/anima_t2i_test.json                    |   82 +
 workflows/krea2_t2i_test.json                    |   67 +
 workflows/video_bernini_r_image_editing.json     | 3697 ++++++++++++++++++++
 workflows/video_bernini_r_video_editing.json     | 3919 ++++++++++++++++++++++
 workflows/wan2.1_i2v_480p.json                   |  860 +++++
 workflows/wan2.2_i2v_lightning_test.json         |  266 ++
 workflows/wan2.2_i2v_standard_multiaction.json   |   17 +
 26 files changed, 10240 insertions(+)
