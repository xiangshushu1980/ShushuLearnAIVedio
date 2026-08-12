/** 音色种子生成（Qwen3-TTS 独立推理，独立 venv 避免污染 ComfyUI 环境）
 * 三种模式（对齐实体声音描述）：
 *  - custom: 预设音色（speaker）+ 可选风格指令
 *  - design: 文字描述设计声音（VoiceDesign，最贴合"声音描述→音色"）
 *  - clone: 参考音频克隆（需上传 wav + 文本）
 * 显存自适应：GPU 空闲 >6GB 用 CUDA，否则 CPU。
 */
import { execFile, execFileSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { importAsset } from './assets.ts'
import { REPO_ROOT } from './config.ts'

const VENV_PY = process.env.QWEN_TTS_PY ?? path.join(process.env.HOME ?? '/home/sean', 'miniconda3', 'envs', 'qwen-tts', 'bin', 'python')
const SCRIPT = path.join(REPO_ROOT, 'scripts', 'qwen_tts_gen.py')

export type VoiceGenKind = 'custom' | 'design' | 'clone'

export interface VoiceGenInput {
  kind: VoiceGenKind
  text: string
  speaker?: string
  instruct?: string
  /** clone 用：参考音频本地路径 */
  refPath?: string
  refText?: string
  seed?: number
}

export function ttsReady(): boolean {
  return fs.existsSync(SCRIPT) && fs.existsSync(VENV_PY)
}

/** 生成音色种子 wav（同步阻塞执行；由任务队列 runner 调用） */
export function generateVoice(entityId: string, input: VoiceGenInput): { file: string; durSec: number } {
  if (!fs.existsSync(SCRIPT)) throw new Error(`缺少推理脚本: ${SCRIPT}`)
  if (!fs.existsSync(VENV_PY)) throw new Error(`缺少 Qwen3-TTS venv: ${VENV_PY}（需创建 ~/miniconda3/envs/qwen-tts）`)
  const outDir = fs.mkdtempSync('/tmp/qtts_out_')
  const outFile = path.join(outDir, 'voice.wav')
  const args = ['--kind', input.kind, '--text', input.text, '--out', outFile, '--seed', String(input.seed ?? 42)]
  if (input.kind === 'custom') {
    args.push('--speaker', input.speaker ?? 'ryan')
    if (input.instruct) args.push('--instruct', input.instruct)
  } else if (input.kind === 'design') {
    args.push('--instruct', input.instruct ?? '')
  } else if (input.kind === 'clone') {
    if (!input.refPath || !fs.existsSync(input.refPath)) throw new Error('克隆模式需要参考音频文件')
    args.push('--ref', input.refPath)
    if (input.refText) args.push('--ref-text', input.refText)
  }
  const stdout = execFileSync(VENV_PY, [SCRIPT, ...args], { timeout: 600_000, maxBuffer: 8 * 1024 * 1024, encoding: 'utf-8' })
  if (!fs.existsSync(outFile)) throw new Error(`生成失败（无输出文件）: ${stdout.slice(-500)}`)
  const asset = importAsset(entityId, 'voice', outFile)
  // 清理临时目录
  try {
    fs.rmSync(outDir, { recursive: true, force: true })
  } catch {
    /* ignore */
  }
  const durMatch = /dur=([\d.]+)s/.exec(stdout)
  return { file: asset.file, durSec: durMatch ? Number(durMatch[1]) : 0 }
}
