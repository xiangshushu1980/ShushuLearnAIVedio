#!/usr/bin/env python3
"""DeepSeek 提示词生成（路线 1 验证：DeepSeek vs IR 文本对比）

规则注入 = docs/17_h3_prompt_writing_rules.md（生成器合成规则手册，单一写者）。
引擎 = deepseek-v4-flash（试错）/ deepseek-v4-pro（精写），reasoning 开 MAX。
用法：
  python3 scripts/deepseek_prompt_gen.py --scene onsen --text "..." --duration 10 --ratio 16:9 --model deepseek-v4-flash
Key：~/.config/mem0_deepseek_key 或环境变量 DEEPSEEK_API_KEY
"""
import argparse
import json
import os
from pathlib import Path

import requests

API_URL = "https://api.deepseek.com/chat/completions"
RULES_FILE = Path(__file__).resolve().parent.parent / "docs" / "17_h3_prompt_writing_rules.md"

SYSTEM_TEMPLATE = """你是 MiniMax H3 视频模型的提示词合成器（T2VA 模式）。严格按以下规则手册输出：
===== 规则手册开始 =====
{rules}
===== 规则手册结束 =====

铁律：只输出三核心段（integrated_multimodal_description / overall_soundscape / non_diegetic_music），
无任何前言、解释、markdown fence。全部英文。"""


def get_key() -> str:
    env = os.environ.get("DEEPSEEK_API_KEY")
    if env:
        return env
    f = Path.home() / ".config" / "mem0_deepseek_key"
    if f.exists():
        return f.read_text().strip()
    raise SystemExit("缺少 DeepSeek key：~/.config/mem0_deepseek_key 或 DEEPSEEK_API_KEY")


def gen(key: str, model: str, scene_text: str, duration: int, ratio: str, mode: str = "t2va", first_frame_desc: str = "") -> str:
    rules = RULES_FILE.read_text()
    sys_prompt = SYSTEM_TEMPLATE.format(rules=rules)
    user_lines = [
        f"场景（中文意图，保持原意）：{scene_text}",
        f"参数：duration={duration}s, ratio={ratio}, mode={mode}。",
    ]
    if mode == "i2va" and first_frame_desc:
        user_lines.append(f"首帧图像内容描述（参考图不可见，以下是对首帧的准确描述）：{first_frame_desc}")
        user_lines.append("需输出 instruction line + 三核心段（i2va 模式，instruction line 逐字套用规则手册模板）。")
    else:
        user_lines.append("请按规则手册输出增强后的英文三核心段提示词。")
    user_prompt = "\n".join(user_lines)
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "reasoning": {"effort": "high"},  # 思考参数开 MAX（用户决策）
        "temperature": 0.7,
        "max_tokens": 16000,  # reasoning tokens 计入 completion，需给思考+正文留足空间
    }
    r = requests.post(API_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=300)
    if r.status_code != 200:
        raise SystemExit(f"[DeepSeek] HTTP {r.status_code}: {r.text[:500]}")
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, help="场景名（落盘文件名用）")
    ap.add_argument("--text", required=True, help="中文场景描述")
    ap.add_argument("--duration", type=int, default=10)
    ap.add_argument("--ratio", default="16:9")
    ap.add_argument("--model", default="deepseek-v4-flash", choices=["deepseek-v4-flash", "deepseek-v4-pro"])
    ap.add_argument("--mode", default="t2va", choices=["t2va", "i2va"])
    ap.add_argument("--first-frame-desc", default="", help="i2va 模式：首帧图像内容描述")
    ap.add_argument("--output", help="落盘路径（默认 experiments/prompt_compare/{scene}_{model}.txt）")
    args = ap.parse_args()

    out = args.output or f"experiments/prompt_compare/{args.scene}_{args.model}.txt"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    prompt = gen(get_key(), args.model, args.text, args.duration, args.ratio, args.mode, args.first_frame_desc)
    Path(out).write_text(prompt)
    print(f"[ok] {out} ({len(prompt)} chars)")


if __name__ == "__main__":
    main()
