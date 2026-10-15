# 概念图先行闭环

Owner: Sean。原始实验，原图不修复。任务 remote-2e8d6440-d620-4537-9567-4c5efbc1d882。

数据、brief、采样与独立seed先冻结在 plan.json；概念阶段每方向2张，之后按叙事、读数机制、可校准性选型，不按偶然几何正确性挑图。

参考节点：TextEncodeQwenImage21；参考同时进入视觉编码与reference_latents，第一图确定输出空latent尺寸；无独立几何保护通道。A=概念图；B=结构图在image_1、概念图在image_2；C=仅结构图。PE关闭。每图保存workflow、prompt、history、GPU样本、耗时与输出hash。
