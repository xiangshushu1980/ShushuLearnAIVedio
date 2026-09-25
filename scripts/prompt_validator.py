#!/usr/bin/env python3
"""H3 提示词规则校验器（生成器规则校验层，docs/16 设计组件）

确定性规则检查（IR 输出实测基准 + docs/17 规则手册）：
  1. 基础模式检查三核心段；Ref2VA 检查六段式
  2. 字段冒号存在
  3. [Shot 1] 不带时间戳
  4. 第 N 镜（N>1）切点式时间戳 `At MM:SS.mmm`，递增且在时长内
  5. 镜头数符合预算（4-6s→1-2 镜；7-10s→2-3 镜；11-15s→3-5 镜）
  6. 无前言/解释/fence（首行即字段）
  7. 无第三方 IP/名人名（粗查）
用法：python3 scripts/prompt_validator.py <file>...  （--json 输出）
退出码：0=通过 1=有警告 2=有硬伤
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIELDS = ["integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]
REF_FIELDS = [
    "subject_definitions",
    "summary",
    "retention_analysis",
    "detailed_description",
    "overall_soundscape",
    "non_diegetic_music",
]
IP_PATTERN = re.compile(r"\b(Warcraft|Marvel|Star Wars|Pok[eé]mon|Disney|Nintendo|Batman|Superman)\b", re.I)


def check(text: str, duration: int = None, mode: str = None) -> dict:
    issues, warns = [], []
    t = text.strip()

    if mode == "auto" or mode is None:
        if t.startswith("subject_definitions:"):
            mode = "ref2va"
        elif t.startswith("For the target video"):
            mode = "i2va"
        elif t.startswith("How the reference pictures align"):
            mode = "fl2va" if "Picture 2" in t.splitlines()[0] else "l2va"
        else:
            mode = "t2va"

    # 1. 字段齐全 + 冒号
    expected_fields = REF_FIELDS if mode == "ref2va" else FIELDS
    for f in expected_fields:
        if f not in t:
            issues.append(f"缺字段: {f}")
        elif not re.search(rf"{f}\s*:", t):
            issues.append(f"字段缺冒号: {f}")

    # 2. 镜头数与 Shot1 时间戳
    shots = re.findall(r"\[Shot (\d+)\]", t)
    if not shots:
        issues.append("无 [Shot N] 镜头标记")
    else:
        n = len(set(shots))
        if duration:
            if duration <= 6 and n > 2:
                warns.append(f"镜头预算超: {duration}s 出 {n} 镜（应 1-2）")
            elif 7 <= duration <= 10 and (n < 2 or n > 3):
                warns.append(f"镜头预算偏离: {duration}s 出 {n} 镜（应 2-3）")
            elif duration >= 11 and (n < 3 or n > 5):
                warns.append(f"镜头预算偏离: {duration}s 出 {n} 镜（应 3-5）")
        # Shot 1 带时间戳？（只在 [Shot 1] 段内检查，排除 instruction line 与后续镜头）
        m1 = re.search(r"\[Shot 1\]([^\[]*?)(?:\[Shot 2\]|\Z)", t, re.S)
        if m1 and re.search(r"At\s*0*:\d", m1.group(1)):
            # IR 实测：i2v 输出为 [Shot 1] 段内嵌切点（无 [Shot 2] 标签），t2v 才有标签
            if mode in {"i2va", "fl2va", "l2va"}:
                warns.append("Shot 1 段内嵌切点（i2v 与 IR 实测同构，软要求）")
            else:
                issues.append("Shot 1 段落内出现时间戳（t2v 应带 [Shot N] 标签切点）")
        # 切点式时间戳（须带 [Shot N] 标签）
        cut_ts = re.findall(r"\[Shot (\d+)\](?:[^\[]*?)At (00:\d{2}\.\d{3})", t)
        times = [float(x.split(":")[1]) for x in [c[1] for c in cut_ts]]
        # 裸切点 = 切点总数 - 带 [Shot N] 标签数
        all_cuts = re.findall(r"At 00:\d{2}\.\d{3}, the camera (?:cuts|transitions|changes)", t)
        tagged_cuts = re.findall(r"\[Shot \d+\](?:[^\[]*?)At 00:\d{2}\.\d{3}, the camera (?:cuts|transitions|changes)", t)
        bare = len(all_cuts) - len(tagged_cuts)
        if bare > 0:
            warns.append(f"裸切点缺 [Shot N] 标签: {bare} 处（i2v 软要求，t2v 建议修）")
        if len(set(shots)) > 1 and not cut_ts and not bare:
            warns.append("多镜但无切点式时间戳（At MM:SS.mmm）")
        if times != sorted(times):
            issues.append(f"时间戳非递增: {times}")
        if duration and times and max(times) >= duration:
            issues.append(f"时间戳超时长: {times} >= {duration}s")
        # 时段式（错误格式）
        if re.search(r"(?:[Ff]rom|[Tt]o) 00:", t):
            warns.append("使用时段式时间（From..to），应为切点式")

    # 3. 无前言
    first_line = t.splitlines()[0]
    valid_first_line = {
        "ref2va": r"^subject_definitions\s*:",
        "i2va": r"^For the target video",
        "fl2va": r"^How the reference pictures align",
        "l2va": r"^How the reference pictures align",
        "t2va": r"^integrated_multimodal_description\s*:",
    }[mode]
    if not re.match(valid_first_line, first_line):
        warns.append(f"首行非字段开头（有前言?）: {first_line[:60]!r}")

    # 4. 无 fence / IP
    if "```" in t:
        issues.append("包含 markdown fence")
    for m in IP_PATTERN.finditer(t):
        issues.append(f"含第三方 IP 名: {m.group(1)}")

    # 5. 声音层非空
    for f in ["overall_soundscape", "non_diegetic_music"]:
        m = re.search(rf"{f}\s*:\s*(.+)", t, re.S)
        if not m or not m.group(1).strip():
            issues.append(f"{f} 为空")
        elif m.group(1).strip() == "N/A" and f == "overall_soundscape":
            issues.append("overall_soundscape 不允许 N/A")

    level = "pass" if not issues and not warns else ("warn" if warns and not issues else "fail")
    return {"issues": issues, "warns": warns, "level": level, "shots": len(set(shots))}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--duration", type=int, help="已知目标时长（秒）；不传则不检查镜头预算/超时")
    ap.add_argument(
        "--mode",
        default="auto",
        choices=["t2va", "i2va", "fl2va", "l2va", "ref2va", "auto"],
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-warn", action="store_true", help="warn 级也视为通过（exit 0），仅 fail 阻断")
    args = ap.parse_args()

    all_pass = True
    results = {}
    for f in args.files:
        t = Path(f).read_text()
        r = check(t, duration=args.duration, mode=args.mode)
        results[f] = r
        if r["level"] != "pass":
            all_pass = False
        if not args.json:
            print(f"{'✅' if r['level']=='pass' else '⚠️' if r['level']=='warn' else '❌'} {f} (镜数={r['shots']})")
            for w in r["warns"]:
                print(f"    ⚠ {w}")
            for i in r["issues"]:
                print(f"    ❌ {i}")
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    if any(r["level"] == "fail" for r in results.values()):
        sys.exit(2)
    if any(r["level"] == "warn" for r in results.values()) and not args.allow_warn:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
