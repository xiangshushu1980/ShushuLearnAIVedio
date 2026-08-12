#!/usr/bin/env python3
"""工具 B stage2：导演拍摄本 → H3 提示词（三核心段快车道 / 六段式 Ref2VA 慢车道）

分层管线控制点 2（docs/16）：拍摄本（工具 A 输出，中文控制面）→ 英文 H3 提示词。
消费拍摄本 YAML（experiments/shotlist/*_shotlist.yaml），角色卡注入外观锚定。
模式：
  --mode i2va   快车道：instruction line + integrated_multimodal_description
                + overall_soundscape + non_diegetic_music（官方 IR i2v 样本为 few-shot）
  --mode ref2va 慢车道：六段式 subject_definitions / summary / retention_analysis
                / detailed_description / overall_soundscape / non_diegetic_music
                （官方 ref-en 指南 + ref2va 样本改写版为 few-shot）

设计约束：
- 拍摄本中文 action → 英文：忠实翻译 + 按 docs/17 规则扩写（运动语法/声音三层/连续性锚点）
- 跨段策略来自拍摄本 chain 字段（first_static/firstlast_bridge/independent）
- 纯文本模型看不到参考图：角色卡提供外观锚定；<Picture N> 引用由拍摄本 subject 生成
- 校验：复用 prompt_validator.py（确定性规则）；六段式额外检查六段齐全

用法：
  python3 scripts/h3_prompt_stage2.py --shotlist experiments/shotlist/Alya的海边黄昏_shotlist.yaml --mode i2va --model deepseek-v4-flash
输出：experiments/shotlist/prompts/<title>_<mode>.txt（校验通过后落盘）
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import requests
import yaml

API_URL = "https://api.deepseek.com/chat/completions"
BASE = Path(__file__).resolve().parent.parent
RULES_FILE = BASE / "docs" / "17_h3_prompt_writing_rules.md"
ROLE_CARD_DIR = BASE / "experiments" / "shotlist" / "rolecards"
OUT_DIR = BASE / "experiments" / "shotlist" / "prompts"
VALIDATOR = BASE / "scripts" / "prompt_validator.py"
IR_SAMPLE = BASE / "experiments" / "ir_samples" / "i2v_alya_beach.txt"
REF2VA_GUIDE = BASE.parent / "ComfyUI" / ".." / "comfy-ops" / ".pi" / "skills" / "h3-prompt-writing" / "references" / "ref-en.txt"
SIX_FIELDS = ["subject_definitions", "summary", "retention_analysis",
              "detailed_description", "overall_soundscape", "non_diegetic_music"]

I2VA_TPL = """你是 MiniMax H3 提示词合成器（工具 B 阶段）。输入=导演拍摄本 YAML（已确认），输出=英文 H3 提示词。

职责边界：把拍摄本忠实地转成官方格式提示词——不自己加戏（不加未在拍摄本中的主体/镜头），
但允许按规则扩写（运动幅度速度、声音细节、光线氛围）。

===== 输出模式（i2va 快车道，三核心段）=====
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
The opening frame shows exactly the content of <Picture 1> (the reference image, scene: {scene}); keep it unchanged, do not redraw or alter the opening frame.

integrated_multimodal_description: [Shot 1] ...（按拍摄本镜头展开，每镜 `[Shot N]` + 时间戳）
overall_soundscape: ...（只含 diegetic：环境音+动作声+非语言人声）
non_diegetic_music: N/A
===== 模式结束 =====

音乐策略（用户决策 2026-08-10）：默认不生成 BGM——短片内 BGM 无法连续（实测），
后期独立配乐（本地 MusicGen/ACE-Step 管线）。除非用户显式要求，否则 non_diegetic_music 一律写 N/A。
diegetic 声音（环境音/音效/演出音乐）保留在画面与 soundscape 描述中。

===== 合成规则（docs/17 关键节）=====
1. 每镜：[Shot 1] 不带时间戳；第 N 镜（N>1）写作 `[Shot N] At MM:SS.mmm, the camera cuts to ...`
   时间严格递增且总长=拍摄本 duration_total
2. 镜头运动语法 = type + amplitude + speed 自然句（如 "the camera pushes in with small amplitude at slow speed"）
3. 一镜一动作；身份锚点每镜重复（换措辞但一致）；状态跨镜延续；保持屏幕方向
4. 声音三层进 overall_soundscape：环境音+物理动作声+非语言人声；
   对话/台词按“对话语法”合成（见下），verbatim 原文不翻译

===== 对话语法（docs/17 三节，有 dialogue 字段时强制，否则忽略）=====
- 发声者稳定 ID `(S1)`、`(S2)`…按出现顺序分配，跨镜复用；不发声角色无 ID；群声 `(S1,S2)`
- 识别短语（角色卡外观/语气/动作）+ ID 在 `<d>` 外；`<d>` 内只有语言标签+原词：
  `<d>[Chinese] 台词原文。</d>`（中文台词语言标签用 Chinese，英文用 English；verbatim 不译不改）
- 画外音旁白：精确短语 "says in an off-screen voiceover" + 立即声明镜内角色嘴唇闭合
  "while her lips remain completely closed"（拍摄本 speaker=off_screen 时用）
- 台词时间锚点：台词所在镜头的时间戳必须精确（[Shot N] At MM:SS.mmm），
  模型会按时间把话安到镜内说话者嘴上；无锚点会错位/重叠
- 说话者与镜头主体绑定：谁在镜内谁说话（拍摄本已保证，合成时保持）
5. 音乐策略：默认不生成 BGM——non_diegetic_music 写 N/A（后期配乐）；角色能听到的音乐（演出/收音机）写进画面（diegetic）
6. 跨段策略（拍摄本 chain 字段）：
   first_static → 首句保留 instruction line（首帧静态图锚定）
   firstlast_bridge → 结尾注明尾帧锚定画面
   independent → 无特殊处理
7. 场景一致性防重绘（2026-08-10 实测硬约束）：
   - instruction line 已注明首帧画面=<Picture 1> 参考图内容（scene: {scene}），不得重绘/改动首帧
   - integrated_multimodal_description 首镜描述必须与拍摄本 scene 一致（环境/光线/色调），
     不得写与参考图冲突的场景——冲突时模型会重绘首帧（SSIM 归零）；一致时 0.99
8. 输出纯文本：无前言、无解释、无 markdown fence

===== 官方 IR 输出示例（逐字模仿结构）=====
{ir_sample}
===== 示例结束 =====
"""

REF2VA_TPL = """你是 MiniMax H3 提示词合成器（工具 B 阶段）。输入=导演拍摄本 YAML（已确认），输出=英文 Ref2VA 六段式提示词。

职责边界：把拍摄本忠实地转成官方格式提示词——不自己加戏（不加未在拍摄本中的主体/镜头），
但允许按规则扩写（运动幅度速度、声音细节、光线氛围）。

===== 输出模式（ref2va 慢车道，六段式）=====
subject_definitions:
<Subject 1> is ...（来自拍摄本 subject 引用的角色卡外观，逐字采用）
<Picture 1> is the reference image for <Subject 1>.（若有参考图）

summary:
[...] The target video ...（任务类型前缀：[reference generation]）

retention_analysis:
<Subject 1> (appears in [Shot N]): fully_preserved - ...
（视觉: fully_preserved / partially_preserved / attribute_transfer / weak_reference）

detailed_description:
The target video is in the style from the shooting plan (use its style field).
[Shot 1] ...（按拍摄本镜头展开，label 首现处插入引用，350-500 词）

overall_soundscape:
...（环境音+物理动作声+非语言人声，1-4 句）

non_diegetic_music: N/A
===== 模式结束 =====

音乐策略（用户决策 2026-08-10）：默认不生成 BGM（短片 BGM 无法连续，后期独立配乐）；
non_diegetic_music 一律写 N/A，除非显式要求。diegetic 声音保留。

===== 合成规则（docs/17 六段式要点）=====
1. 角色卡是 <Subject N> 不是 <Picture N>（<Picture N> 仅当图本身是帧锚点）
2. label 只能引用已定义；视频/音频独立编号
3. retention_analysis 每 label 一行；音频用 fully_copy / partially_copy / reference / weak_reference
4. detailed_description：风格开场 → [Shot N] 时间线（[Shot 1] 无时间戳，N>1 写 At MM:SS.mmm）
5. 每镜一动作；身份锚点每镜重复；状态跨镜延续；保持屏幕方向
6. 声音三层进 overall_soundscape（diegetic）；non_diegetic_music 默认 N/A（后期配乐）
7. 场景一致性防重绘（拍摄本 scene 字段，2026-08-10 实测）：
   - detailed_description 首镜场景元素必须与拍摄本 scene 一致（环境/光线/色调），
     不得与参考图场景冲突（冲突时模型会重绘首帧，SSIM 归零；一致时 0.99）
8. 音频参考（拍摄本 audio_refs 字段，有则强制）：
   - subject_definitions 写 "<Audio N> is the voice-timbre reference for <Subject N> (Sx)."
     （N 按 audio_refs 顺序从 1 起；Sx 用该角色在对话语法中的稳定 ID）
   - summary 任务类型前缀追加 + audio reference（如 [reference generation + audio reference]）
   - retention_analysis 每音频一行："<Audio N> (voice-timbre for <Subject N> (Sx)): reference - ..."
   - detailed_description 中该角色首次发声处写明 "using the voice timbre referenced from <Audio N>"
   - 音色参考不复制台词：台词仍由 <d> 文本生成（<Audio N> 只锁音色/语气/语速）

===== 对话语法（docs/17 三节，有 dialogue 字段时强制，否则忽略）=====
- 发声者稳定 ID `(S1)`、`(S2)`…按出现顺序分配，跨镜复用；不发声角色无 ID；群声 `(S1,S2)`
- 识别短语（角色卡外观/语气/动作）+ ID 在 `<d>` 外；`<d>` 内只有语言标签+原词：
  `<d>[Chinese] 台词原文。</d>`（中文用 Chinese，英文用 English；verbatim 不译不改）
- 说话主体写法：`<Subject N> (S1)`（subject 与说话者一致时）；画外音旁白用
  "says in an off-screen voiceover" + 立即声明镜内角色嘴唇闭合 "while her lips remain completely closed"
- 台词时间锚点：台词所在镜头时间戳必须精确，防止模型把话安到镜内其他人嘴上
- 谁在镜内谁说话（拍摄本已保证）；台词只在 detailed_description 内写，
  overall_soundscape 不重复对话内容
7. 输出纯文本：无前言、无解释、无 markdown fence

===== 官方参考指南（ref-en.txt）=====
{ref_guide}
===== 指南结束 =====
"""


def get_key() -> str:
    env = os_environ_key()
    if env:
        return env
    f = Path.home() / ".config" / "mem0_deepseek_key"
    if f.exists():
        return f.read_text().strip()
    raise SystemExit("缺少 DeepSeek key：~/.config/mem0_deepseek_key 或 DEEPSEEK_API_KEY")


def os_environ_key() -> str:
    import os
    return os.environ.get("DEEPSEEK_API_KEY", "")


def load_role_cards(ids: list) -> str:
    if not ids:
        return ""
    blocks = []
    for rid in ids:
        f = ROLE_CARD_DIR / f"{rid}.md"
        if f.exists():
            blocks.append(f.read_text(encoding="utf-8"))
    return "\n\n".join(blocks)


def gen(key: str, model: str, mode: str, shotlist_yaml: str, effort: str, max_tokens: int) -> str:
    sl = yaml.safe_load(shotlist_yaml)
    role_cards = load_role_cards(sl.get("role_cards", []))
    if mode == "i2va":
        ir_sample = IR_SAMPLE.read_text(encoding="utf-8") if IR_SAMPLE.exists() else ""
        scene = str(sl.get("scene", "")) or "as described in the shooting plan"
        sys_prompt = I2VA_TPL.format(ir_sample=ir_sample, scene=scene)
    else:
        ref_guide = ""
        for cand in (Path(".pi/skills/h3-prompt-writing/references/ref-en.txt"),
                     Path("/home/sean/projects/comfy-ops/.pi/skills/h3-prompt-writing/references/ref-en.txt")):
            if cand.exists():
                ref_guide = cand.read_text(encoding="utf-8")
                break
        sys_prompt = REF2VA_TPL.format(ref_guide=ref_guide)
    user_lines = [
        f"===== 拍摄本（导演已确认）=====\n{shotlist_yaml}",
        f"===== 角色卡（subject_definitions 外观锚定用）=====\n{role_cards}" if role_cards else "===== 角色卡 =====（无）",
        "请输出 H3 提示词（纯文本，严格按模式）。",
    ]
    audio_refs = sl.get("audio_refs", {})
    if audio_refs:
        lines = [f"{rid} -> {path}" for rid, path in audio_refs.items()]
        user_lines.insert(1, f"===== 音频参考（音色种子，按顺序编 <Audio N>）=====\n" + "\n".join(lines))
    scene = str(sl.get("scene", "")) or "as described in the shooting plan"
    body = {
        "model": model,
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": "\n".join(user_lines)}],
        "reasoning": {"effort": effort},
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    r = requests.post(API_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=600)
    if r.status_code != 200:
        raise SystemExit(f"[DeepSeek] HTTP {r.status_code}: {r.text[:500]}")
    ch = r.json()["choices"][0]["message"]
    content = (ch.get("content") or "").strip()
    if not content:
        raise SystemExit(f"[DeepSeek] 正文为空（reasoning 吃满 {max_tokens} tokens，请调大 --max-tokens 或降 --effort）")
    return content


def strip_fence(text: str) -> str:
    text = re.sub(r"^```(?:txt|text)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def six_field_check(text: str) -> list:
    errs = []
    for f in SIX_FIELDS:
        if f not in text:
            errs.append(f"缺六段式字段: {f}")
        elif not re.search(rf"{f}\s*:", text):
            errs.append(f"字段缺冒号: {f}")
    if "<Subject" not in text and "<Picture" not in text:
        errs.append("六段式缺 <Subject N>/<Picture N> label")
    return errs


def validate(mode: str, text: str, duration: int) -> list:
    errs = []
    if mode == "i2va":
        tmp = Path("/tmp/h3_stage2_check.txt")
        tmp.write_text(text, encoding="utf-8")
        r = subprocess.run([sys.executable, str(VALIDATOR), "--mode", "i2va", "--duration", str(int(duration)), "--json", str(tmp)],
                           capture_output=True)
        try:
            v = json.loads(r.stdout)
            res = list(v.values())[0]
            if res.get("level") == "fail":
                errs = res.get("issues", [])[:5]
        except Exception:
            errs = ["校验器调用失败: " + r.stderr.decode()[:200]]
    else:
        errs = six_field_check(text)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shotlist", required=True, help="拍摄本 YAML（工具 A 输出）")
    ap.add_argument("--mode", required=True, choices=["i2va", "ref2va"])
    ap.add_argument("--model", default="deepseek-v4-flash", choices=["deepseek-v4-flash", "deepseek-v4-pro"])
    ap.add_argument("--effort", default="high", choices=["high", "medium", "low"])
    ap.add_argument("--max-tokens", type=int, default=24000, help="reasoning 会吃大量 token，默认给足")
    ap.add_argument("--retry", type=int, default=3)
    ap.add_argument("--output")
    args = ap.parse_args()

    sl_path = Path(args.shotlist)
    sl_yaml = sl_path.read_text(encoding="utf-8")
    sl = yaml.safe_load(sl_yaml)
    title = sl.get("title") or sl_path.stem
    duration = float(sl.get("duration_total", 8))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    last_err = "未执行"
    for attempt in range(1, args.retry + 2):
        print(f"[{title}] 合成 {args.mode} 提示词 (try {attempt}) ...", flush=True)
        raw = gen(get_key(), args.model, args.mode, sl_yaml, args.effort, args.max_tokens)
        raw = strip_fence(raw)
        errs = validate(args.mode, raw, duration)
        if not errs:
            out = Path(args.output) if args.output else OUT_DIR / f"{title}_{args.mode}.txt"
            out.write_text(raw, encoding="utf-8")
            print(f"✅ 校验通过，落盘: {out}")
            return
        last_err = "；".join(errs)
        print(f"   ⚠️ 校验失败: {last_err[:200]}", flush=True)
    print(f"❌ {args.retry + 1} 次尝试后仍失败: {last_err}")


if __name__ == "__main__":
    main()
