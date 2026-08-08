#!/bin/bash
# DeepSeek 多场景批量生成（路线 1 验收扩充：8 场景，与 IR 样本库一一对应）
# 用法: bash scripts/deepseek_prompt_batch.sh [model]
set -e
cd "$(dirname "$0")/.."
MODEL=${1:-deepseek-v4-flash}
GEN="python3 scripts/deepseek_prompt_gen.py --model $MODEL"

run() { # name duration mode text [first_frame_desc]
  local name=$1 dur=$2 mode=$3 text=$4 desc=$5
  echo "=== $name ($mode) ==="
  if [ "$mode" = i2va ]; then
    $GEN --scene "$name" --duration "$dur" --mode i2va --first-frame-desc "$desc" --text "$text"
  else
    $GEN --scene "$name" --duration "$dur" --text "$text"
  fi
}

# ---- t2v 场景（与 IR t2v 样本同输入）----
run cyberpunk_rainy 5 t2va "赛博朋克风格，雨夜霓虹都市街道，霓虹灯牌倒映在湿润路面，一名穿着透明雨衣的女子撑伞缓步走过，全息广告在楼宇间闪烁，镜头缓慢跟拍，氛围冷峻迷离"
run doc_streetfood 5 t2va "纪录片纪实风格，深夜街头小吃摊，厨师熟练颠锅翻炒，火焰从锅中腾起，热油滋滋作响，蒸汽升腾，食客围坐等候，微距特写镜头捕捉食材翻动细节，暖色路灯照明"
run dream_cloudsea 5 t2va "梦幻风格，云海之上日出时刻，延时摄影，层层云海翻滚流动，金色阳光穿透云隙洒下，远处山峦若隐若现，镜头缓慢平移，氛围宁静壮阔"
run retro_cafe 5 t2va "复古胶片风格，老式咖啡馆内，留声机播放爵士乐，穿旗袍的年轻女子坐在窗边翻看旧书，暖黄色灯光，墙上有旧海报，镜头缓慢推近，画面带轻微胶片颗粒感"

# ---- i2v 场景（首帧描述从 IR 输出反推）----
run alya_beach 5 i2va "保持图中少女形象，少女站在海边沙滩，海风吹拂她的长发和裙摆，海浪轻轻拍打脚踝，她望向远方微笑，镜头缓慢环绕，阳光明媚，日系清新氛围" \
  "2D 动漫风格少女：银白色长发、左侧红色丝带、蓝色大眼睛、白色金边外套、深蓝内搭红色领结、黑色百褶裙（裙摆白色条纹）、白色过膝袜（袜口金带）、黑鞋；背景是夜晚灯光街道"
run alya_stage 5 i2va "保持图中少女形象，少女站在演唱会舞台上，聚光灯从头顶打下，台下观众挥舞荧光棒，她向观众挥手，镜头缓缓推进，绚丽灯光氛围" \
  "2D 动漫风格少女：银白色长发（带粉色反光、呆毛）、苍白皮肤、大而明亮的蓝眼睛，站在蓝色调的路面上"
run forest_fairy 5 i2va "保持图中森林环境，迷雾笼罩的原始森林，光线从树冠洒落形成丁达尔光束，精灵般的少女在林间轻盈穿行，裙摆拂过蕨类植物，镜头跟随移动" \
  "真人电影感：迷雾原始森林，苔藓覆盖的巨树、蕨类与阔叶植被、蜿蜒碎石小路，丁达尔光束"
run dessert 5 i2va "保持图中甜点，甜点放在大理石台面上，奶油缓缓流动，巧克力酱从顶部淋下，微距镜头缓缓推进，暖色背景光，美食广告质感" \
  "真人电影感微距：玻璃展示柜中的多款甜点——左侧圆形白盘上的草莓奶油蛋糕（厚海绵层、白奶油玫瑰裱花），白色大理石台面，明亮暖光"

echo "=== 批次完成 ==="
ls experiments/prompt_compare/
