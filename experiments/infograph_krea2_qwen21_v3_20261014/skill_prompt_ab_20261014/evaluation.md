# [Sean] 目视评估：Qwen prompt / skill 方法 A/B

评审：2026-10-14；方法：非盲、人工目视；无 OCR 或程序化像素坐标审计。共有 4 个案例 × 2 个 prompt 臂 × 2 seeds = 16 张。该评审用于定位下一轮 prompt 修改，不表示统计显著或普遍排名。

## 逐案结果

| 案例 | Baseline · seed 42 / 1337 | Skill-guided · seed 42 / 1337 | 结论 |
|---|---|---|---|
| Electricity trend | [42 PNG](images/case01_electricity_trend__baseline__seed42.png) · [1337 PNG](images/case01_electricity_trend__baseline__seed1337.png) | [42 PNG](images/case01_electricity_trend__skill_guided__seed42.png) · [1337 PNG](images/case01_electricity_trend__skill_guided__seed1337.png) | 四张都把四个标签和值写对，趋势线也向上；但 0–100% 轴上的点从约 10–15% 画到 70–85%，与 83.5%→91.6% 的实际位置不符，斜率被严重夸大。两种 prompt 都未通过数值到坐标的忠实度。Skill-guided 有更鲜明的乡居/照明视觉，但没修复坐标映射。 |
| Food waste flow | [42 PNG](images/case02_food_waste_flow__baseline__seed42.png) · [1337 PNG](images/case02_food_waste_flow__baseline__seed1337.png) | [42 PNG](images/case02_food_waste_flow__skill_guided__seed42.png) · [1337 PNG](images/case02_food_waste_flow__skill_guided__seed1337.png) | 四张都保留 100、−12、−18、−20、50 kg，算术守恒；阶段图示可辨。Skill-guided 的食物流长图更突出图形、比 baseline 的网格卡片更有叙事感，尤其 seed 1337；seed 42 有更多装饰和重复结论，精简文字的收益不稳定。 |
| City commute | [42 PNG](images/case03_city_commute__baseline__seed42.png) · [1337 PNG](images/case03_city_commute__baseline__seed1337.png) | [42 PNG](images/case03_city_commute__skill_guided__seed42.png) · [1337 PNG](images/case03_city_commute__skill_guided__seed1337.png) | Baseline 两张都正确显示 46%/28 min、31%/42 min、23%/19 min。Skill-guided seed 42 也显示完整数据，交通工具大图很醒目；seed 1337 漏掉 28/42/19 min，并把 “min” 放在百分比旁边，导致量纲错配。Skill-guided 视觉更丰富，但成对数据绑定稳定性下降。 |
| Solar budget | [42 PNG](images/case04_solar_budget__baseline__seed42.png) · [1337 PNG](images/case04_solar_budget__baseline__seed1337.png) | [42 PNG](images/case04_solar_budget__skill_guided__seed42.png) · [1337 PNG](images/case04_solar_budget__skill_guided__seed1337.png) | 所有图片的四个类别和值均可辨。Skill-guided seed 42 把 45/25/20/10 的四项预算画成近似等大的四块，明显错误；seed 1337 相对更接近比例，但面积关系仍不精确。Baseline seed 1337 的分区更接近预期比例；seed 42 也有面积偏差。数字文本正确不等于面积编码正确。 |

## 汇总结论

- **Skill-guided 的可见图形更突出，但没稳定提高数据忠实度。**食物流和通勤图的插画/主视觉明显变大；同时 skill-guided 城市通勤 seed 1337 漏掉一整组分钟数，太阳能预算 seed 42 把不同金额画成近似等面积，电力折线四张均严重错轴。当前小样本里 baseline 的关键关系稍稳，skill-guided 的视觉丰富度更高。
- **文字比“长 prompt”更值得直接限额。**PE 把输入扩成约 418–814 词的英文场景说明；长描述用于控制画面，并不等于图内文案多。skill-guided 有时去掉结论栏，有时仍添加/重复结论，也有时误删必需数据。现有两臂都把 takeaway 作为可渲染引号文字提供，下一版应把它声明为设计意图而非画内文案，并单独列出封闭的可见文字清单。
- **需要把图形关系写成可检验约束。**折线例应明确每个点的坐标相对 0–100% 轴，并说明四个点都位于 80–100% 区间；预算图应说明面积占比并禁止等面积分区；双指标比较应要求每个类别必须同时有 share 与 minutes 两个数值，再用清单式 QA 检查输出。
- 本批全为英文，没有中文专项结论。4 个案例、2 个 seed、小样本人工非盲评；坐标与面积判定是人工目测，尚无自动像素审计。

## 下一步 prompt 修订

继续直接由 Qwen 生成图片，LoRA 暂不加入。使用 skill 的 takeaway/topology 规划，但 takeaway 只作内部设计 brief，不进入最终 prompt 的可见文字 allowlist。每例把必需渲染字符串列成封闭集合，并逐项验证：

1. 可见文本只允许 title、subtitle、短 category labels 和 ground-truth values；不渲染 takeaway 句、额外图例、重复数据表或装饰性文字。
2. 图表需要明确的几何约束：值到坐标/长度/面积的映射，刻度范围和零点，类别顺序与单位配对。
3. 生成后逐项核对可见字符串和映射；缺数、错位、错轴或面积失真都算失败，即使插画和版式更漂亮。
