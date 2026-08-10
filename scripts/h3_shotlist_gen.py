#!/usr/bin/env python3
"""工具 A：剧本 + 参数头 → 导演拍摄本（stage1，断点审阅）

分层管线控制点 1（docs/16 方案 A）：
  剧本(YAML 参数头+正文) --[DeepSeek]--> 拍摄本 YAML（镜头/景别/运动/时长/角色卡/声音/连续性）

设计约束（2026-08-08/09 用户决策 + 补测结论）：
- 拍摄本 = 导演控制面（中文，供人审阅修改）；工具 B 负责英文化合成三核心段/六段式
- 跨段策略（docs/19）：禁帧链硬桥；first_static=静态首帧锚 / firstlast_bridge=静态双锚转场 / independent=独立段
- 引擎：deepseek-v4-flash（试错）/ pro（精写），reasoning high
- 纯文本模型看不到图：i2v 首帧靠文本描述注入（role_cards 提供外观锚定）

用法：
  python3 scripts/h3_shotlist_gen.py --script experiments/shotlist/scripts/alya_beach.yaml --model deepseek-v4-flash
Key：~/.config/mem0_deepseek_key 或环境变量 DEEPSEEK_API_KEY
输出：experiments/shotlist/<title>_shotlist.yaml（校验通过后落盘）
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
import yaml

API_URL = "https://api.deepseek.com/chat/completions"
BASE = Path(__file__).resolve().parent.parent
RULES_FILE = BASE / "docs" / "17_h3_prompt_writing_rules.md"
ROLE_CARD_DIR = BASE / "experiments" / "shotlist" / "rolecards"
OUT_DIR = BASE / "experiments" / "shotlist"

CAMERA_TYPES = {"zoom_in", "zoom_out", "push_in", "pull_out", "pan_l", "pan_r",
                "truck_l", "truck_r", "tilt_up", "tilt_down", "pedestal_up", "pedestal_down",
                "arc_shot", "tracking", "static", "shake_slight", "shake_strong", "pov", "roll_cw", "roll_ccw"}

SYSTEM_TPL = """你是视频导演拍摄本规划器（工具 A 阶段）。输入=剧本+参数头，输出=结构化拍摄本 YAML。

你的职责边界：只做镜头规划（切分/景别/运动/时长/声音分层/连续性），
不做最终提示词合成（那是工具 B 的工作）。拍摄本用中文，供导演（用户）审阅修改。

===== 拍摄本 Schema（严格遵循，字段名不可改）=====
title: 场景标题
style: 风格（来自参数头）
ratio: 画幅
duration_total: 总时长秒
role_cards: [角色卡 id 列表]
chain: first_static | firstlast_bridge | independent（来自参数头）
shots:
  - id: 1                    # 从 1 递增
    duration_s: 3.5          # 秒，可小数
    framing: 特写|近景|中景|中全景|全景|大远景（选一个）
    camera:
      type: 运动类型（见规则 5 枚举）
      amplitude: small|medium|large
      speed: slow|normal|fast
    subject: alya_v1         # 角色卡 id（role_cards 中引用）；无角色用 scene/object
    action: 本镜主导动作（中文，一镜一动作）
    sound:
      ambient: 环境音（如：海浪+海风）
      fx: 物理动作声（如：布料飘动声；无则省略）
      bgm: 配乐情绪与配器（只写"配乐"，不写 diegetic 音乐进镜头内容）
    continuity: 本镜锚定与跨镜延续（身份锚点/状态延续/屏幕方向；首镜注明锚定策略）
===== Schema 结束 =====

===== 镜头规划规则（来自 docs/17，必须遵守）=====
1. 时长→镜头数预算：4-6s→1-2 镜；7-10s→2-3 镜；11-15s→3-5 镜；每镜至少 1.5-2s
2. 切 vs 移：仅距离/角度变化 → 用镜头运动不切；切必须引入新信息（新主体/空间/状态/视角/时间）
3. 一镜一动作（硬约束）：一个镜头只有一个主导动作
4. 连续性：每镜重复身份锚点（换措辞但一致）；状态变化跨镜延续；保持屏幕方向
5. 运动语法 type 枚举：{camera_types}
6. 声音三层：ambient=环境底噪、fx=物理动作声、bgm=背景配乐（情绪+配器）；音乐两分法：
   角色能听到的音乐写进 action（diegetic），背景配乐只写 bgm
7. 跨段策略（chain 参数，写入首镜 continuity）：
   first_static → 首镜注明"首帧=角色静态图锚定（角色卡+参考图）"
   firstlast_bridge → 注明"首尾帧静态双锚（首帧=角色图，尾帧=转场目标图）"
   independent → 注明"独立段生成，一致性靠 prompt 文本锚定"
8. 镜头策略（shot_style 参数，决定镜头拆解方式）：
   分镜剪辑(默认) → 3-5 镜（预算内），景别递进（远景→中景→特写或逆），每镜一主导动作，叙事节奏感
   长镜头流 → 1-2 镜（预算内），镜内多事件连续推进，机位随事件缓慢变化（如 tracking/arc 贯穿），
             适合氛围/纪实/演出场景；镜头内信息密度高：一个镜头完成 站位+环境+动作变化+情绪转变
9. 镜头内信息密度（参考 IR 基准）：单镜内容要饱满——身份锚点+环境+动作+光线氛围在镜内一次交代，
   不要用松散的一句话打发一个镜头
10. 音乐场景驱动判断：若场景本身含表演/演出/现场音乐（舞台/演唱会/收音机/街头艺人），
   bgm 可写"无（演出音乐即 diegetic）"，不必硬塞背景配乐
11. 输出必须为合法 YAML 纯文本：无前言、无解释、无 markdown fence（``` 禁止）
===== 规则结束 =====

{role_cards_block}
{fewshot_block}
"""


def get_key() -> str:
    env = os.environ.get("DEEPSEEK_API_KEY")
    if env:
        return env
    f = Path.home() / ".config" / "mem0_deepseek_key"
    if f.exists():
        return f.read_text().strip()
    raise SystemExit("缺少 DeepSeek key：~/.config/mem0_deepseek_key 或 DEEPSEEK_API_KEY")


def load_script(path: Path) -> dict:
    """剧本 = YAML 参数头 + 正文"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"剧本格式错误（需 --- 参数头 --- 正文）: {path}")
    head = yaml.safe_load(m.group(1))
    if "ratio" in head:
        head["ratio"] = str(head["ratio"])
    body = m.group(2).strip()
    head["_body"] = body
    return head


def load_role_cards(ids: list) -> str:
    if not ids:
        return "（无角色卡）"
    blocks = []
    for rid in ids:
        f = ROLE_CARD_DIR / f"{rid}.md"
        if f.exists():
            blocks.append(f"===== 角色卡 {rid} =====\n{f.read_text(encoding='utf-8')}")
        else:
            blocks.append(f"（角色卡 {rid} 未找到，忽略）")
    return "\n".join(blocks)


IR_REVERSE_DIR = BASE / "experiments" / "shotlist" / "ir_reverse"


def load_fewshot(names: list) -> str:
    """从 IR 逆向样本库加载代表样本作为 few-shot（风格锚点，不复制内容）"""
    if not names:
        return ""
    blocks = []
    for n in names:
        # 支持 样本名 或 文件名
        cand = IR_REVERSE_DIR / (n if n.endswith("_ir_shotlist.yaml") else f"{n}_ir_shotlist.yaml")
        if cand.exists():
            blocks.append(f"===== IR 参考样本（模仿其镜头内信息密度/景别选择/声音写法，不要复制具体内容）=====\n{cand.read_text(encoding='utf-8')}")
        else:
            print(f"⚠️ few-shot 样本 {n} 不存在，跳过", flush=True)
    return "\n\n".join(blocks)


def gen_shotlist(key: str, model: str, script: dict, effort: str = "high", max_tokens: int = 12000, shot_style: str = "分镜剪辑", fewshot_names: list = None) -> str:
    rules = RULES_FILE.read_text(encoding="utf-8")
    # 只注入镜头规划相关节（二、三节），避免无关内容干扰
    sec2 = re.search(r"## 二、镜头规划.*?(?=## )", rules, re.S)
    role_block = load_role_cards(script.get("role_cards", []))
    sys_prompt = SYSTEM_TPL.format(camera_types=", ".join(sorted(CAMERA_TYPES)),
                                   role_cards_block=role_block,
                                   fewshot_block=load_fewshot(fewshot_names or []))
    user_lines = [
        f"===== 剧本 =====\n{script['_body']}",
        f"===== 参数 =====\n"
        f"style: {script.get('style','')}\nratio: {script.get('ratio','16:9')}\n"
        f"duration_total: {script.get('duration','8')}s\nsound: {script.get('sound','')}\n"
        f"role_cards: {script.get('role_cards',[])}"
        f"\nchain: {script.get('chain','independent')}\nshot_style: {shot_style}",
        "请输出拍摄本 YAML（严格按 Schema）。",
    ]
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": "\n".join(user_lines)},
        ],
        "reasoning": {"effort": effort},
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    r = requests.post(API_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=300)
    if r.status_code != 200:
        raise SystemExit(f"[DeepSeek] HTTP {r.status_code}: {r.text[:500]}")
    return r.json()["choices"][0]["message"]["content"].strip()


def strip_fence(text: str) -> str:
    text = re.sub(r"^```(?:yaml|yml)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def validate(data: dict, duration_total: float) -> list:
    """返回错误列表（空 = 通过）"""
    errs = []
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        return ["shots 缺失或为空"]
    ids = [s.get("id") for s in shots]
    if ids != list(range(1, len(shots) + 1)):
        errs.append(f"shot id 必须从 1 连续递增: {ids}")
    total = sum(float(s.get("duration_s", 0)) for s in shots)
    if abs(total - duration_total) > 1.0:
        errs.append(f"镜头时长和 {total}s 与 duration_total {duration_total}s 不符")
    # 镜头预算
    n = len(shots)
    if duration_total <= 6 and n > 2:
        errs.append(f"镜头预算超限: {duration_total}s 最多 2 镜（实际 {n}）")
    elif duration_total <= 10 and n > 3:
        errs.append(f"镜头预算超限: {duration_total}s 最多 3 镜（实际 {n}）")
    elif duration_total > 10 and n > 5:
        errs.append(f"镜头预算超限: {duration_total}s 最多 5 镜（实际 {n}）")
    for s in shots:
        for k in ("framing", "camera", "action", "sound", "continuity"):
            if k not in s:
                errs.append(f"shot {s.get('id','?')} 缺字段 {k}")
        cam = s.get("camera", {})
        if cam.get("type") not in CAMERA_TYPES:
            errs.append(f"shot {s.get('id','?')} camera.type 非法: {cam.get('type')}（枚举见脚本）")
        if not s.get("duration_s") or float(s.get("duration_s", 0)) < 1.5:
            errs.append(f"shot {s.get('id','?')} 时长 <1.5s: {s.get('duration_s')}")
        for k in ("ambient", "bgm"):
            if k not in s.get("sound", {}):
                errs.append(f"shot {s.get('id','?')} sound 缺 {k}")
    return errs


REVIEW_TPL = """你是资深分镜导演，审阅以下拍摄本。只找问题，不改写。
检查维度：\n1. 镜头预算与节奏（时长分配是否合理，是否有过长/过短的镜头）\n2. 一镜一动作（有没有镜头塞了两个主导动作）\n3. 切 vs 移（切是否引入了新信息；纯距离/角度变化是否误用了切）\n4. 连续性（身份锚点是否每镜重复、状态是否跨镜延续、屏幕方向是否保持）\n5. 声音分层（ambient/fx/bgm 是否每镜合理，是否与画面内容匹配）\n6. 跨段策略与 chain 参数是否一致\n\n输出格式：\n- 问题清单（无问题则写“无”），每条：镜号 | 问题 | 建议\n- 最后一行给出总评：通过 / 建议修改（理由一句话）\n\n===== 拍摄本 =====\n{shotlist}\n"""


def review_shotlist(key: str, model: str, shotlist_path: Path, effort: str = "high") -> str:
    shotlist = shotlist_path.read_text(encoding="utf-8")
    body = {
        "model": model,
        "messages": [{"role": "system", "content": "你是审阅助手，只输出结构化审阅结果。"},
                      {"role": "user", "content": REVIEW_TPL.format(shotlist=shotlist)}],
        "reasoning": {"effort": effort},
        "temperature": 0.3,
        "max_tokens": 16000,  # reasoning 会吃大量 token（实测 4000 不够，思考吃满则正文为空）
    }
    r = requests.post(API_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=300)
    if r.status_code != 200:
        raise SystemExit(f"[DeepSeek] HTTP {r.status_code}: {r.text[:500]}")
    return r.json()["choices"][0]["message"]["content"].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="剧本文件（YAML 参数头+正文）")
    ap.add_argument("--model", default="deepseek-v4-flash", choices=["deepseek-v4-flash", "deepseek-v4-pro"])
    ap.add_argument("--effort", default="high", choices=["high", "medium", "low"])
    ap.add_argument("--max-tokens", type=int, default=12000)
    ap.add_argument("--retry", type=int, default=3, help="校验不过自动重试次数")
    ap.add_argument("--output", help="落盘路径（默认 experiments/shotlist/<title>_shotlist.yaml）")
    ap.add_argument("--review", action="store_true", help="生成后调用 DeepSeek 导演视角自审（只报问题不改写）")
    ap.add_argument("--shot-style", default="分镜剪辑", choices=["分镜剪辑", "长镜头流"], help="镜头拆解策略（默认分镜剪辑）")
    ap.add_argument("--fewshot", default="", help="IR 逆向样本 few-shot，逗号分隔样本名（如 i2v_alya_beach,t2v_doc_streetfood）")
    args = ap.parse_args()

    script = load_script(Path(args.script))
    title = script.get("title") or Path(args.script).stem
    duration = float(script.get("duration", 8))

    last_err = "未执行"
    fewshot_names = [s.strip() for s in args.fewshot.split(",") if s.strip()] if args.fewshot else None
    for attempt in range(1, args.retry + 2):
        print(f"[{title}] 生成拍摄本 (try {attempt}) ...", flush=True)
        raw = gen_shotlist(get_key(), args.model, script, args.effort, args.max_tokens, args.shot_style, fewshot_names)
        raw = strip_fence(raw)
        try:
            data = yaml.safe_load(raw)
            errs = validate(data, duration)
        except Exception as e:
            errs = [f"YAML 解析失败: {e}"]
        if not errs:
            out = Path(args.output) if args.output else OUT_DIR / f"{title}_shotlist.yaml"
            out.write_text(raw, encoding="utf-8")
            n = len(data["shots"])
            print(f"✅ 拍摄本通过校验（{n} 镜），落盘: {out}")
            print("=" * 60)
            print(raw)
            if args.review:
                print("=" * 60)
                print("📋 导演自审（--review）:")
                print(review_shotlist(get_key(), args.model, out, args.effort))
            return
        last_err = "；".join(errs)
        print(f"   ⚠️ 校验失败: {last_err[:200]}", flush=True)
    print(f"❌ {args.retry + 1} 次尝试后仍失败，最后错误: {last_err}")
    print("调试: 重跑加 --retry 0 查看原始输出")


if __name__ == "__main__":
    main()
