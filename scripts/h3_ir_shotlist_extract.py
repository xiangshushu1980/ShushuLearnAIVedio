#!/usr/bin/env python3
"""IR 输出 → 隐含拍摄本逆向解析（2026-08-10 h3-prompt-agent）

目的：把官方 IR 的增强提示词逆向成与工具 A 同构的拍摄本 YAML，
用于「工具 A 分镜师 vs IR 隐含分镜」逐维度对比 + 构建专业样本库。

输入：IR 输出 txt（experiments/ir_samples/*.txt）
输出：experiments/shotlist/ir_reverse/<name>_ir_shotlist.yaml

提取维度（与工具 A schema 对齐）：
- 镜头数/切点时间戳（[Shot N] At MM:SS.mmm）
- 每镜：framing/camera(type+amplitude+speed)/action（英文原样保留+中文摘要）
- sound 三层：从 overall_soundscape 拆分 ambient/fx；non_diegetic_music → bgm
- 连续性锚点（每镜身份锚定/状态延续关键词）
- chain 推断：instruction line 含 "fully referenced" → first_static
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests
import yaml

API_URL = "https://api.deepseek.com/chat/completions"
BASE = Path(__file__).resolve().parent.parent
IR_DIR = BASE / "experiments" / "ir_samples"
OUT_DIR = BASE / "experiments" / "shotlist" / "ir_reverse"

EXTRACT_TPL = """你是镜头结构分析师。给定 MiniMax H3 官方 IR 的提示词输出，逆向提取其镜头规划为 YAML。

===== 输出 Schema（与分镜师工具同构，字段名不可改）=====
title: 场景名（自拟，简短）
style: 从 detailed_description/描述推断（如：日系清新/赛博朋克/纪实）
duration_total: 从最后切点+尾镜时长推断（秒，整数）
chain: first_static | firstlast_bridge | independent | unknown（从 instruction line 推断：
  "fully referenced" 且只有 <Picture 1> → first_static；有多个 picture 对齐不同时间 → firstlast_bridge；无 → unknown）
shots:
  - id: 1
    duration_s: 3.5
    framing: 特写|近景|中景|中全景|全景|大远景（从英文镜头描述推断）
    camera:
      type: push_in|pull_out|pan_l|pan_r|truck_l|truck_r|tilt_up|tilt_down|arc_shot|tracking|static|pov|其他（从动词推断）
      amplitude: small|medium|large|（未提及省略）
      speed: slow|normal|fast|（未提及省略）
    subject: 主体（角色/物体/场景，中文）
    action: 本镜主导动作（中文摘要，忠实原文不发挥）
    sound:
      ambient: 环境音（中文，从 overall_soundscape 拆）
      fx: 物理动作声（无则省略）
      bgm: 配乐（从 non_diegetic_music 概括，中文）
    continuity: 本镜身份锚点/状态延续/屏幕方向（中文，无则写 无）
===== Schema 结束 =====

规则：
1. [Shot N] 是切分依据：每镜从 [Shot N] 到下一个 [Shot N] 的时间区间
2. 时间戳："[Shot N] At MM:SS.mmm" 切点；[Shot 1] 无时间戳，其时长 = 下一镜切点
3. 最后一镜时长 = duration_total - 最后切点
4. 一镜一动作：若一段内多动作，取主导动作；明显的连续小动作合并
5. 输出纯 YAML，无前言无 fence

===== IR 输出 =====
{ir_text}
"""


def get_key() -> str:
    import os
    env = os.environ.get("DEEPSEEK_API_KEY")
    if env:
        return env
    f = Path.home() / ".config" / "mem0_deepseek_key"
    if f.exists():
        return f.read_text().strip()
    raise SystemExit("缺少 DeepSeek key")


def extract(key: str, ir_text: str, model: str) -> str:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是镜头结构分析器，只输出 YAML。"},
            {"role": "user", "content": EXTRACT_TPL.format(ir_text=ir_text)},
        ],
        "reasoning": {"effort": "medium"},
        "temperature": 0.2,
        "max_tokens": 16000,
    }
    r = requests.post(API_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=600)
    if r.status_code != 200:
        raise SystemExit(f"[DeepSeek] HTTP {r.status_code}: {r.text[:300]}")
    ch = r.json()["choices"][0]["message"]
    content = (ch.get("content") or "").strip()
    if not content:
        raise SystemExit("正文为空（reasoning 吃满 token，调大 max_tokens）")
    content = re.sub(r"^```(?:yaml)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    return content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="IR 样本 txt（或目录）")
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    files = []
    for f in args.files:
        p = Path(f)
        if p.is_dir():
            files += sorted(p.glob("*.txt"))
        else:
            files.append(p)

    key = get_key()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        ir_text = f.read_text(encoding="utf-8")
        print(f"[{f.stem}] 逆向中 ({len(ir_text)} 字符) ...", flush=True)
        raw = extract(key, ir_text, args.model)
        try:
            yaml.safe_load(raw)  # 语法校验
        except Exception as e:
            print(f"   ❌ YAML 解析失败: {e}")
            print(raw[:300])
            continue
        out = OUT_DIR / f"{f.stem}_ir_shotlist.yaml"
        out.write_text(raw, encoding="utf-8")
        n = raw.count("- id:")
        print(f"   ✅ {n} 镜 -> {out}", flush=True)


if __name__ == "__main__":
    main()
