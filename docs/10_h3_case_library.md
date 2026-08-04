# 10 H3 提示词案例库（持续生成，2026-08-04 起）

> 依据：A 提示词强度测试结论（镜头语言最强、动作中等、约束部分有效、双图融合可用）+ B 参考强度测试。参考图来自底图库 `input/ref_lib/`。全部 ref2va int8 20步（除非注明），review 目录可目测。

## 批 1（写实人物 × 镜头/动作/约束/声音升级，bikini_beach 参考）
| 案例 | 变体 | 耗时 | 目录 |
|------|------|------|------|
| C01 | 拉远大幅慢速 + 强风 + 海鸥 + 海浪声 | 152s | video/h3_cases/C01 |
| C02 | 环绕镜头 + 转身看海 | 147s | video/h3_cases/C02 |
| C03 | 奔跑 + 跟踪镜头 + 溅水 + 脚步声 | 147s | video/h3_cases/C03 |
| C04 | 坐下 + 推近 + 保脸/服装约束 + 音乐 | 142s | video/h3_cases/C04 |
| C05 | 静态 + 轻微抖动 + 紧张氛围 | 146s | video/h3_cases/C05 |
| C06 | **双图**（bikini+森林）+ 触树 + 森林鸟声 | 155s | video/h3_cases/C06 |

## 批 2（写实双图融合 + 文化特色）
| 案例 | 变体 | 耗时 | 目录 |
|------|------|------|------|
| C07 | 双图 bikini+霓虹夜景 + 雨声 | 153s | video/h3_cases/C07 |
| C08 | 双图 hanfu+灯笼街 + 鞭炮声 | 153s | video/h3_cases/C08 |
| C09 | qipao 单图 + 老上海复古 + 爵士乐 | 145s | video/h3_cases/C09 |
| C10 | bikini+水墨意境融合（partially）| 153s | video/h3_cases/C10 |
| C11 | tibetan + 经幡 + 强风 | 152s | video/h3_cases/C11 |
| C12 | fisherman **10s** + 船体晃动 + 海鸥声 | 待填 | video/h3_cases/C12 |
