# Qwen-Image-2.1 双人头身比例控制

> Owner: Sean

## 目的

上一轮用裸肩头部身份参考后，脸和制服基本稳定，但全身图的头身比例仍偏大。此实验保留两张身份参考、同一制服参考和短提示词，比较：

1. 在提示词中直接指定每人 8 头身；
2. 额外加入一张双人中性比例/站姿参考图，沿用其 8 头身结构。

两种条件都要求双手可见、空手，不加武器或配饰。每种条件使用相同两个 seed。

## 提示词

直接文字条件：

`Use <image1> as the left identity and <image2> as the right identity. Both wear the uniform from <image3>. Exactly two full-body adult women, front view, side by side. Each is eight heads tall; each head is one eighth of body height. Hands visible. Plain studio.`

比例图条件：

`Follow <image1> only for the two-person pose and adult body proportions. Use <image2> as the left identity, <image3> as the right identity; both wear the uniform from <image4>. Exactly two full-body women side by side. Preserve the guide's 8-head-tall proportions, equal figure height and visible hands. Plain studio.`

QC 记录两人头身比、身高一致性、双人构图、制服一致性和手部。目标比例 8 头身是本轮测试假设，不是用户已定的最终美术标准。

## 结果

2026-10-02 完成两个 seed 的配对比较，见 [QC.md](QC.md) 和 [对照拼图](outputs/duo_proportion_comparison.png)。纯文字指定八头身后，两张都保持完整双人构图，但头部相对偏大、人物更紧凑。加入灰色比例图后，两张都呈现较小头部和更修长的腿身，视觉上更接近八头身目标。四张均保留两张不同身份、同款制服和可见双手。

当前推荐下一流程先把双人比例图作为 pose/body guide，再叠加身份图和制服图。此结果来自两组配对 seed 的目视检查，未进行像素级人体测量；如果用户希望更修长，需另定比例目标（如 8.5 头身）再验证。实验状态：`review`。
