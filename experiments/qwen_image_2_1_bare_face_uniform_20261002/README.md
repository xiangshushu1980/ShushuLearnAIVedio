# Qwen-Image-2.1：裸肩身份参考与统一制服

> Owner: Sean

## 问题

测试原全身角色图裁出的脸部参考是否携带服装信息，进而干扰共同制服；并测试把脸图整理成头部+肩部、裸露颈肩的中性身份参考后，能否改善双人制服图。主提示词刻意压短。当前不加入武器和配饰。

## 对照

- A：两张原始脸部 crop（包含少量原服装/肩甲）+ 同一制服参考图。
- B：从相同脸部 crop 经 Qwen 编辑得到的中性头肩肖像（裸露颈肩、无衣物）+ 同一制服参考图。
- 两条件使用相同短提示词、两个相同 seed。要求两人全身、制服相同、双手可见且空手。

## 短提示词

`Use <image1> as the left woman's identity and <image2> as the right woman's identity. Both wear the same uniform from <image3>. Exactly two adult women, full-body, front-facing. Arms slightly away; hands visible and empty. Plain studio background. No objects.`

此实验先判断人物数、两张脸是否仍有区别、头身比例和制服迁移、是否画出手。每条件仅两个 seed，结果是早期方向信号。

## 当前结论

对照支持这个假设：旧 crop 带着肩甲/衣领等服装信息，双人结果会沿用各自原服装；从同一 crop 编辑出的裸颈肩身份图则在两个 seed 中都保留了两张脸，并让两人穿同款制服，双手清楚可见。当前建议先用这种中性头肩 ref 和短提示词稳定双人、比例、制服、手部，再逐项加入物品。逐图判定见 [QC.md](QC.md)。
