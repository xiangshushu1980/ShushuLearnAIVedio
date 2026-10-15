"""Owner: Sean. Freeze concept briefs before generating or inspecting candidates."""
import json, pathlib, shutil
R=pathlib.Path(__file__).resolve().parent
old=R.parent/'sean_qwen_turbo_chart_aesthetics_20261015'
p=json.loads((old/'plan.json').read_text())
p={k:p[k] for k in ['owner','sampling','canvas']}
p.update(task_id='remote-2e8d6440-d620-4537-9567-4c5efbc1d882',pe='off',debug_seeds=[871,1873],confirmation_seeds=[91001+i*1021 for i in range(20)],transfer_seeds=[121001+i*1031 for i in range(20)],datasets={'area':{'categories':['甲','乙','丙','丁'],'values':[20,70,40,90],'unit':'公顷'},'area_holdout':{'categories':['甲','乙','丙','丁'],'values':[73,31,76,28],'unit':'公顷'},'time':{'events':['启程','营地','观测','返航'],'hours':[0,2,7,10],'domain':[0,12],'unit':'小时'},'time_holdout':{'events':['启程','营地','观测','返航'],'hours':[0,5,6,11],'domain':[0,12],'unit':'小时'},'flow':{'source':100,'branches':{'湿地':20,'森林':50,'农田':30},'unit':'万吨/年'}})
base='设计一张精致、有叙事趣味的中文信息图，横向1536×1024，清楚的信息层级；数字、单位与尺度融入场景设计。不是传统柱形图换材质。只呈现给定数据，不虚构数据。二维正交俯视，无透视厚度，没有遮挡数值边界。'
p['prompts']={
'islands':base+'主题“生态修复群岛”。四座分离的不规则岛屿轮廓，实体二维占地面积编码修复面积：甲20公顷、乙70公顷、丙40公顷、丁90公顷。岛名、数字与公顷单位放在各自港口铭牌，面积图例是一块标有“10公顷”的标准方形测绘地块。海洋测绘、岛内生态纹理、精致航海图式排版；所有岛以同一面积比例，不通过高度/体积编码。各岛都完整显示，轮廓深色清楚，无边缘装饰遮挡。',
'route':base+'主题“十二小时科考航线”。一条自左向右连续蜿蜒的探险路线，水平位置严格编码自启程以来时间0至12小时；垂直起伏仅为构图。四个路标：启程0小时、营地2小时、观测7小时、返航10小时。下方一条融入场景的航海计时尺标0、2、4、6、8、10、12小时，事件节点与计时尺水平对齐。大型小时数字作为路标的一部分，沿途精致地貌、科考小插画、暖白纸张与海蓝/珊瑚配色；不要把所有事件等距排列，不要按路径长度读时间。',
'ribbons':base+'主题“一滴水的年度去向”。100万吨/年的单条水平河流自左流向右侧分成湿地20、森林50、农田30万吨/年三条二维蜿蜒水带。垂直截面宽度唯一编码流量，上游总宽等于三支流宽度之和。数字单位融入河口浮标与目的地地名；设一个标有“10万吨/年”的宽度标尺。纸质地图的丰富视觉语言，流带边界清晰、平面俯视、分流后不再合流，三目的地嵌入精致生态场景。'}
(R/'plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
s=(old/'runner.py').read_text().replace('Material reconstruction runner. Adapted from ../sean_qwen_turbo_chart_control_20261015/run.py.','Concept-first runner; adapted from chart aesthetics runner.').replace('sean_chart_aesthetics','sean_concept_first')
(R/'runner.py').write_text(s)
(R/'README.md').write_text('# 概念图先行闭环\n\nOwner: Sean。原始实验，原图不修复。任务 '+p['task_id']+'。\n\n数据、brief、采样与独立seed先冻结在 plan.json；概念阶段每方向2张，之后按叙事、读数机制、可校准性选型，不按偶然几何正确性挑图。\n\n参考节点：TextEncodeQwenImage21；参考同时进入视觉编码与reference_latents，第一图确定输出空latent尺寸；无独立几何保护通道。A=概念图；B=结构图在image_1、概念图在image_2；C=仅结构图。PE关闭。每图保存workflow、prompt、history、GPU样本、耗时与输出hash。\n')
