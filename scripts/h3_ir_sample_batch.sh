#!/bin/bash
# IR 样本库批量收集（docs/16 清单 #1）：多风格 t2v + 真实素材 i2v
# 用法: bash scripts/h3_ir_sample_batch.sh [start|t2v|i2v]
# 输出: experiments/ir_samples/<name>.txt（含 source 元数据头）
set -e
cd "$(dirname "$0")/.."
OUT=experiments/ir_samples
START=${1:-all}
mkdir -p "$OUT"
KEY="--duration 5"

run_t2v() { # name text
  local name=$1 text=$2
  echo "=== [t2v] $name ==="
  python3 scripts/h3_ir_rewrite.py --text "$text" --duration 5 --ratio 16:9 \
    --output "$OUT/$name.txt"
  echo "[ok] $OUT/$name.txt"
}

run_i2v() { # name text image
  local name=$1 text=$2 img=$3
  echo "=== [i2v] $name ==="
  python3 scripts/h3_ir_rewrite.py --text "$text" --duration 5 \
    --image "first_frame=$img" --output "$OUT/$name.txt"
  echo "[ok] $OUT/$name.txt"
}

if [ "$START" = all ] || [ "$START" = t2v ]; then
  run_t2v "t2v_cyberpunk_rainy" "赛博朋克风格，雨夜霓虹都市街道，霓虹灯牌倒映在湿润路面，一名穿着透明雨衣的女子撑伞缓步走过，全息广告在楼宇间闪烁，镜头缓慢跟拍，氛围冷峻迷离"
  run_t2v "t2v_doc_streetfood" "纪录片纪实风格，深夜街头小吃摊，厨师熟练颠锅翻炒，火焰从锅中腾起，热油滋滋作响，蒸汽升腾，食客围坐等候，微距特写镜头捕捉食材翻动细节，暖色路灯照明"
  run_t2v "t2v_dream_cloudsea" "梦幻风格，云海之上日出时刻，延时摄影，层层云海翻滚流动，金色阳光穿透云隙洒下，远处山峦若隐若现，镜头缓慢平移，氛围宁静壮阔"
  run_t2v "t2v_retro_cafe" "复古胶片风格，老式咖啡馆内，留声机播放爵士乐，穿旗袍的年轻女子坐在窗边翻看旧书，暖黄色灯光，墙上有旧海报，镜头缓慢推近，画面带轻微胶片颗粒感"
fi

if [ "$START" = all ] || [ "$START" = i2v ]; then
  run_i2v "i2v_alya_beach" "保持图中少女形象，少女站在海边沙滩，海风吹拂她的长发和裙摆，海浪轻轻拍打脚踝，她望向远方微笑，镜头缓慢环绕，阳光明媚，日系清新氛围" \
    /home/sean/projects/ComfyUI/input/start/alya_169.png
  run_i2v "i2v_alya_stage" "保持图中少女形象，少女站在演唱会舞台上，聚光灯从头顶打下，台下观众挥舞荧光棒，她向观众挥手，镜头缓缓推进，绚丽灯光氛围" \
    /home/sean/projects/ComfyUI/input/start/alya_768.png
  run_i2v "i2v_forest_fairy" "保持图中森林环境，迷雾笼罩的原始森林，光线从树冠洒落形成丁达尔光束，精灵般的少女在林间轻盈穿行，裙摆拂过蕨类植物，镜头跟随移动" \
    /home/sean/projects/ComfyUI/input/start/forest_1024.png
  run_i2v "i2v_dessert" "保持图中甜点，甜点放在大理石台面上，奶油缓缓流动，巧克力酱从顶部淋下，微距镜头缓缓推进，暖色背景光，美食广告质感" \
    /home/sean/projects/ComfyUI/input/start/dessert_1024.png
fi
echo "=== 批次完成 ==="
ls -la "$OUT"
