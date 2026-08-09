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
import subprocess
import sys
from pathlib import Path

import requests

API_URL = "https://api.deepseek.com/chat/completions"
RULES_FILE = Path(__file__).resolve().parent.parent / "docs" / "17_h3_prompt_writing_rules.md"
VALIDATOR = Path(__file__).resolve().parent / "prompt_validator.py"

SYSTEM_TEMPLATE = """你是 MiniMax H3 视频模型的提示词合成器（T2VA 模式）。严格按以下规则手册输出：
===== 规则手册开始 =====
{rules}
===== 规则手册结束 =====

铁律：只输出三核心段（integrated_multimodal_description / overall_soundscape / non_diegetic_music），
无任何前言、解释、markdown fence。全部英文。

===== 格式示例（逐字模仿其结构，尤其是时间戳语法；这是官方 IR 输出）=====
{example}
===== 示例结束 =====

时间戳铁律（示例中可见）：[Shot 1] 永不带时间戳；第 N 镜（N>1）写作 `[Shot N] At MM:SS.mmm, the camera cuts to ...`，时间严格递增且在时长内。"""

EXAMPLE_FILE = Path(__file__).resolve().parent.parent / "experiments" / "ir_samples" / "official_t2va_10s.txt"


def get_key() -> str:
    env = os.environ.get("DEEPSEEK_API_KEY")
    if env:
        return env
    f = Path.home() / ".config" / "mem0_deepseek_key"
    if f.exists():
        return f.read_text().strip()
    raise SystemExit("缺少 DeepSeek key：~/.config/mem0_deepseek_key 或 DEEPSEEK_API_KEY")


def gen(key: str, model: str, scene_text: str, duration: int, ratio: str, mode: str = "t2va", first_frame_desc: str = "", effort: str = "high", max_tokens: int = 24000) -> str:
    rules = RULES_FILE.read_text()
    if mode == "i2va":
        # i2v 示例用含切点时间戳的 IR 实测样本（官方 i2va 示例无切点）
        example_file = Path(str(EXAMPLE_FILE).replace("official_t2va_10s", "i2v_alya_beach"))
    else:
        example_file = EXAMPLE_FILE
    example = example_file.read_text() if example_file.exists() else ""
    sys_prompt = SYSTEM_TEMPLATE.format(rules=rules, example=example)
    user_lines = [
        f"场景（中文意图，保持原意）：{scene_text}",
        f"参数：duration={duration}s, ratio={ratio}, mode={mode}。",
        "每个镜头切点必须带 [Shot N] 标签（如 `[Shot 2] At 00:02.500, the camera cuts to`），严禁裸切点。",
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
        "reasoning": {"effort": effort},  # 思考程度（用户授权可调；high=MAX 精写）
        "temperature": 0.7,
        "max_tokens": max_tokens,  # reasoning tokens 计入 completion，给足防正文截断
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
    ap.add_argument("--effort", default="high", choices=["high", "medium", "low"], help="reasoning 程度（用户授权可随时调；high=MAX 精写，low=快速）")
    ap.add_argument("--first-frame-desc", default="", help="i2va 模式：首帧图像内容描述")
    ap.add_argument("--output", help="落盘路径（默认 experiments/prompt_compare/{scene}_{model}.txt）")
    ap.add_argument("--output-dir", help="输出目录（与 --output 互斥，文件名 = {scene}_{model}.txt）")
    ap.add_argument("--retry", type=int, default=3, help="生成后本地校验不过时自动重试次数（默认 3）")
    ap.add_argument("--max-tokens", type=int, default=24000, help="completion 上限（含 reasoning；默认 24000 给足）")
    args = ap.parse_args()

    out = args.output
    if not out:
        base = args.output_dir or "experiments/prompt_compare"
        out = f"{base}/{args.scene}_{args.model}.txt"
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, args.retry + 1):
        prompt = gen(get_key(), args.model, args.text, args.duration, args.ratio, args.mode, args.first_frame_desc, args.effort, args.max_tokens)
        Path(out).write_text(prompt)
        r = subprocess.run(
            [sys.executable, str(VALIDATOR), out, "--mode", args.mode, "--duration", str(args.duration), "--allow-warn"],
            capture_output=True, text=True)
        if r.returncode == 0:
            print(f"[ok] {out} ({len(prompt)} chars, 校验通过 attempt={attempt})")
            return
        if attempt < args.retry:
            print(f"[retry] 校验不过（attempt={attempt}），重新生成...")
        else:
            print(f"[warn] {out} ({len(prompt)} chars, 达重试上限 {args.retry}，校验未过，文件已保留)")


if __name__ == "__main__":
    main()
