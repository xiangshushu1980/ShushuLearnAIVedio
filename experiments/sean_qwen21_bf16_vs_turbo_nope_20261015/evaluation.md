# 视觉评估：Qwen Image 2.1 BF16 vs Turbo INT8（无 PE）

Owner: Sean · Task: `remote-97ccaaac-e730-4c57-875c-c86954ca0518` · 2026-10-15

## 评分约定

Codex 对 12 个案例 × 2 个 seed 的 48 张图做非盲目视。每个案例分数是两张 seed 图的综合判断，范围 1–5：文字可读/忠实度、数据与视觉标记映射、版式/构图。文字分数同时考虑缺字、错字、重复值和额外小字；映射分数关注类别和值是否正确绑定、坐标/面积/方向是否真实表达数据；布局分数看层级、留白和视觉秩序。中文专项只对六个中文案例打分。**没有运行 OCR，因此这里不是逐字符自动统计，也不是独立评审。**

## 总览

| 配置 | 目标文字可读/忠实度 | 数据到图形映射 | 布局/构图 | 中文专项（6 案） |
|---|---:|---:|---:|---:|
| Qwen Image 2.1 BF16，40 步 | 3.3/5 | 2.8/5 | 3.5/5 | 3.2/5 |
| Qwen Image 2.1 Turbo INT8 ConvRot，8 步 | 3.7/5 | 3.2/5 | 4.0/5 | 3.8/5 |

在这组 12 个图表案例中，Turbo 没有出现明显的整体画质崩塌；本次人工评分里，它的文字可读性、图形映射和版式都略高于 BF16。主要差距不是标题美术，而是坐标轴、小字和复杂结构的可靠性：两个 checkpoint 都会输出伪刻度、重复标签、数值错配或不按指定类型画图。Turbo 在通勤双指标、小倍图、区间图、流向图和散点图上的表现相对更稳；BF16 在睡眠点图、部分瀑布图/哑铃图上保留了更有辨识度的结构。两 seed 的方向不完全一致，不能把分差当成普遍排名。

## 每案观察及原图

分数列顺序为“文字 / 映射 / 布局”。seed 链接直接打开归档 PNG；对应输入 prompt、API workflow、运行 JSON、模型/图片 SHA 与逐秒资源样本列在同名运行 JSON 及 `runs/manifest.json`。

| 案例 | BF16（42 · 1337） | Turbo（42 · 1337） | BF16 分 | Turbo 分 | 目视观察 |
|---|---|---|---:|---:|---|
| 电力接入折线 | [42](images/qwen21_bf16/c09_electricity_access_en__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c09_electricity_access_en__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c09_electricity_access_en__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c09_electricity_access_en__qwen21_turbo_int8__seed1337.png) | 3/2/4 | 3/3/4 | 两配置大体显示 83.5→91.6 的上升，但纵轴刻度失真；两张 seed 1337 图把 2015 写成 8015。Turbo 的点和值更完整。 |
| 通勤双指标条形 | [42](images/qwen21_bf16/c10_city_transport_zh__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c10_city_transport_zh__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c10_city_transport_zh__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c10_city_transport_zh__qwen21_turbo_int8__seed1337.png) | 2/2/3 | 3/3/4 | Turbo 两张都保留三类占比和分钟数，seed 42 有重复/错绑分钟标记；BF16 也有重复占比、缺失/错放分钟值。 |
| 学段出勤热力图 | [42](images/qwen21_bf16/c11_school_attendance_en__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c11_school_attendance_en__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c11_school_attendance_en__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c11_school_attendance_en__qwen21_turbo_int8__seed1337.png) | 2/2/3 | 3/3/4 | 两边都未稳定还原 4×3 网格；行列标签重复、位置错位，数值不能逐格可靠核对。Turbo 色阶与网格更清楚。 |
| 食物损耗瀑布图 | [42](images/qwen21_bf16/c12_food_waste_zh__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c12_food_waste_zh__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c12_food_waste_zh__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c12_food_waste_zh__qwen21_turbo_int8__seed1337.png) | 4/4/4 | 4/3/4 | BF16 seed 42 的阶梯瀑布结构较接近要求；Turbo 两张标签和值较清楚，但把损耗画成从共同起点伸出的独立条形，未正确表达累计递减。 |
| 睡眠时长点图 | [42](images/qwen21_bf16/c13_sleep_distribution_en__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c13_sleep_distribution_en__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c13_sleep_distribution_en__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c13_sleep_distribution_en__qwen21_turbo_int8__seed1337.png) | 4/3/3 | 4/2/3 | BF16 至少一张能按 5.5–9.0 小时排开点位；Turbo 两张点都集中在同一竖线附近，未把观测值映射到横轴。 |
| 年龄人口金字塔 | [42](images/qwen21_bf16/c14_population_pyramid_zh__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c14_population_pyramid_zh__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c14_population_pyramid_zh__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c14_population_pyramid_zh__qwen21_turbo_int8__seed1337.png) | 3/3/4 | 3/3/4 | 双侧金字塔视觉完整，但部分年龄段被重复/改写，组别顺序和男女数值绑定不够稳定。 |
| 家庭用水哑铃图 | [42](images/qwen21_bf16/c15_household_water_zh__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c15_household_water_zh__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c15_household_water_zh__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c15_household_water_zh__qwen21_turbo_int8__seed1337.png) | 4/4/4 | 4/3/4 | BF16 两图的四组前后值较齐；Turbo seed 42 把部分前后端点重复，seed 1337 更接近正确配对。两边横轴刻度都有乱码/重复。 |
| 社区太阳能预算树图 | [42](images/qwen21_bf16/c16_community_solar_en__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c16_community_solar_en__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c16_community_solar_en__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c16_community_solar_en__qwen21_turbo_int8__seed1337.png) | 4/4/4 | 4/3/4 | seed 42 两模型都较清楚地表达 45/25/20/10；seed 1337 两边均出现重复类别、额外金额或面积与标签不一致。 |
| 城乡互联网小倍图 | [42](images/qwen21_bf16/c17_internet_gap_zh__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c17_internet_gap_zh__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c17_internet_gap_zh__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c17_internet_gap_zh__qwen21_turbo_int8__seed1337.png) | 2/2/3 | 4/4/4 | Turbo 两图均清晰区分四个地区和城市/乡村数据；BF16 分面布局重复/错位较多。两模型纵轴刻度仍有错误。 |
| 实验组区间图 | [42](images/qwen21_bf16/c18_lab_results_en__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c18_lab_results_en__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c18_lab_results_en__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c18_lab_results_en__qwen21_turbo_int8__seed1337.png) | 4/3/3 | 4/4/4 | Turbo 两图大体保留四个估计值及区间；BF16 seed 1337 有重复点/区间文字。两者都生成多余纵轴刻度，Turbo 布局更整齐。 |
| 闲置物品流向图 | [42](images/qwen21_bf16/c19_reuse_network_zh__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c19_reuse_network_zh__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c19_reuse_network_zh__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c19_reuse_network_zh__qwen21_turbo_int8__seed1337.png) | 4/3/4 | 5/4/5 | Turbo 两张都把 80 分为 36/28/16，目标文字清楚、图形阅读路径强；BF16 seed 42 多出一个 18 件分支/标记。 |
| 设备价格与续航散点 | [42](images/qwen21_bf16/c20_product_tradeoff_en__qwen21_bf16__seed42.png) · [1337](images/qwen21_bf16/c20_product_tradeoff_en__qwen21_bf16__seed1337.png) | [42](images/qwen21_turbo_int8/c20_product_tradeoff_en__qwen21_turbo_int8__seed42.png) · [1337](images/qwen21_turbo_int8/c20_product_tradeoff_en__qwen21_turbo_int8__seed1337.png) | 3/2/3 | 3/3/4 | Turbo 的点数和类别标签更可读，但仍有坐标刻度/金额标签错误；BF16 seed 42 产生大量多余点，未通过五设备散点映射。 |

## 速度与资源

| 指标 | BF16 | Turbo INT8 |
|---|---:|---:|
| 成功图片 | 24/24 | 24/24 |
| 全批平均生成耗时 | 31.79 s/张 | 4.09 s/张 |
| 首张（含切换/首次加载开销） | 79.71 s | 9.75 s |
| 去除首张后的均值 | 29.71 s/张 | 3.84 s/张 |
| 去除首张后的中位数 | 29.97 s/张 | 4.22 s/张 |
| 峰值显存 | 23,118 MB | 23,134 MB |
| 峰值 ComfyUI RSS | 32,314 MB | 31,716 MB |
| 峰值 GPU 温度 | 81°C | 75°C |

稳定态均值下 Turbo 约快 **7.7×**；包含两边首张初始化的整批平均约快 **7.8×**。本地 GPU 仍受相同 8B 编码器/VAE 驻留和 offload 影响，因此峰值显存近似相同；Turbo 的优势主要是少量 denoising steps 带来的时间缩短。

## 结论边界

- **数据不是生成时随机出来的。** 每案的类别和值在 `source_casebook.json` 中预先固定；合成数据是人工构造的测试值，不是随机抽样或真实统计。两个 checkpoint 对同一案例使用相同 prompt 和数据，seed 42/1337 用来观察图像生成的波动。
- **两边的图表都未达到可靠的数据表达。** Turbo 的布局和标签可读性在本批样本略好，但仍存在坐标错误、值与标签错配、重复/遗漏以及图表类型偏离；BF16 也出现同类问题。目视上更整齐不能证明图形编码正确，不能把这些图片当作准确的数据图表。
- 这是实用配置对比：BF16 base 40 步 vs Turbo INT8 ConvRot 固定 8 步。结果同时包含蒸馏、步数/采样 schedule 和量化的影响，**不能解释为只测了 BF16 与 INT8 的精度差**。
- 两边共用逐案相同的手写 prompt、1536×1024、seed 42/1337、BF16 Qwen3-VL 8B encoder、BF16 VAE。没有 PE、LoRA、图后叠字或编辑。
- 12 个图表案例均使用整理好的已知数据；其中六个案例保留中文标签。该测试不验证模型从原始数据自行分析和选择图表的能力。
- 输出图的轴/小字仍是主要短板。虽然 Turbo 在本批评分上略占优势，所有分数均来自单一评审、每案两个 seeds；不用于宣称普遍质量排名。
