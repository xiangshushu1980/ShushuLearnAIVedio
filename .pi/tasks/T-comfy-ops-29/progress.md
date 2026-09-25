# T-comfy-ops-29 进度

## 2026-09-03 入库：社区方案筛选

### 当前结论

- **Extender 2.0**：三个方向中最值得立即本地验证。已具备 FL2VA、多段 Motion Context、动态图片 Guide、视频/音频参考、项目保存恢复和逐段颜色校正；但功能迭代很快，长链身份稳定性仍未被社区充分独立验证。适合作为实验编排层，不直接视为生产稳定方案。
- **H3 Director / Director Guide**：适合作为时间线、分镜和输入语义层。Director 支持轨道、shot、逐段 prompt、预览和 retake；Guide 以 Plan v2 显式区分 identity、keyframe、motion、voice、soundtrack，并自动路由媒体。两者能降低手工接线和 prompt 错配，但多个示例仍标记 WIP，不能把编排成功等同于生成连续性成功。
- **GuideMaster / 动态 Guide**：最适合做 MC 累计变形的对照实验。中间帧锚点理论上可周期性重置身份，但独立社区实测少；锚点过强可能造成姿态/口型跳变，过弱则不能抑制漂移。暂不替换 MC。

### 与当前数字人问题的关系

建议把“纯 MC 继承”改成周期性重锚的实验结构：MC 负责局部运动，主播图负责身份，视频参考负责动作/镜头/口型，NativeAudioLock 负责外部粤语母带。先比较纯 MC、MC+身份图、MC+身份图+上一段视频参考，重点检查第 3/4 段而非只看第二段。

### 最小验证矩阵

同一主播首帧、同一粤语母带、4 段×5 秒：

1. 纯 MC；
2. MC + 每段主播身份图；
3. MC + 身份图 + 上一段视频/音频参考；
4. 在第 2/3 段插入动态 Guide，检查身份稳定性与口型是否跳变。

记录：脸部身份、发型/服装、背景色、口型、音频对齐、有效帧损失、显存、RAM、单段耗时。

### 证据锚

- Extender README：动态 FL2VA Guide、视频/音频参考、24fps 修正、项目恢复和逐段色彩编辑：https://github.com/tritant/ComfyUI_MiniMax_H3_Extender
- Director README/CHANGELOG：时间线、shot、retake、参考模式；Director Chain 曾因不可操作撤回，部分长视频模板仍属 WIP：https://github.com/seesee75-commits/ComfyUI-MiniMaxH3-Director
- Guide README：Plan v2、显式媒体角色、确定性标签/校验/路由；多个业务示例仍为 WIP：https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide
- H3-World：需要约 135GB 基础权重和 DiffSynth 定制补丁，属于动作控制世界模型，不是数字人长视频稳定方案：https://github.com/Danzer1xxxxChan/H3-World

## 待办

- [ ] 本地先验证 Extender 2.0，不与现有热文件并行改动。
- [ ] 之后引入 Director/Guide 做同素材编排成本对比。
- [ ] 最后做动态 Guide 与纯 MC 的第 3/4 段对照。
