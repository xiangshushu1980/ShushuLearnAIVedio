/**
 * 实体设定图生成（ANIMA t2i，移植 scripts/anima_scene_batch.py 逻辑）
 * 模板 = workflows/anima_alya_169_t2i.json；prompt 用实体外观描述；图落 ComfyUI/output/shotlist-art/
 */
import fs from 'node:fs'
import path from 'node:path'
import { importAsset, listAssets } from './assets.ts'
import { REPO_ROOT } from './config.ts'

const COMFY_API = process.env.COMFYUI_API ?? 'http://127.0.0.1:8188'
const COMFY_HOME = path.resolve(REPO_ROOT, '..', 'ComfyUI')
const OUTPUT_DIR = path.join(COMFY_HOME, 'output', 'shotlist-art')
const TPL = path.join(REPO_ROOT, '..', 'workflows', 'anima_alya_169_t2i.json')
const ART_PREFIX = 'shotlist-art'

export interface ArtResult {
  ok: boolean
  images: string[]
  promptId?: string
}

/** ComfyUI 是否在线 */
export async function comfyAlive(): Promise<boolean> {
  try {
    const r = await fetch(`${COMFY_API}/system_stats`, { signal: AbortSignal.timeout(3000) })
    return r.ok
  } catch {
    return false
  }
}

/** 生成实体设定图（prompt 缺省 = 实体外观 + 通用站姿） */
export async function generateArt(entityId: string, prompt?: string, seed?: number): Promise<ArtResult> {  if (!fs.existsSync(TPL)) throw new Error(`缺少 ANIMA 模板: ${TPL}`)
  const wf = JSON.parse(fs.readFileSync(TPL, 'utf-8')) as Record<string, { inputs: Record<string, unknown> }>
  const text =
    prompt?.trim() ||
    'masterpiece, best quality, score_9, score_8, score_7, official art, 1girl, solo, clean lineart, detailed eyes, soft shading,\n' +
      'a character standing at the center of the frame, eye-level frontal view, looking directly at the camera, straight-on composition, no high angle, warm dusk light, soft blurred background, gentle golden hour ambience'
  wf['5']!.inputs.text = text
  const s = seed ?? Math.floor(Math.random() * 1_000_000)
  wf['8']!.inputs.seed = s
  // 通用角色设定图：移除角色 LoRA（LoraLoaderModelOnly），KSampler 直连 UNETLoader
  delete wf['4']
  wf['8']!.inputs.model = ['1', 0]
  wf['10']!.inputs.filename_prefix = `${ART_PREFIX}/${entityId}_${Date.now()}`
  const r = await fetch(`${COMFY_API}/prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: wf, client_id: 'shotlist-art' }),
    signal: AbortSignal.timeout(15_000),
  })
  if (!r.ok) throw new Error(`ComfyUI 提交失败 HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`)
  const { prompt_id } = (await r.json()) as { prompt_id: string }
  return { ok: true, images: [], promptId: prompt_id }
}

/** 轮询等待生成完成，把图移入实体资产目录，返回文件名列表 */
export async function waitArtDone(entityId: string, promptId: string, timeoutMs = 300_000): Promise<string[]> {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const r = await fetch(`${COMFY_API}/history/${promptId}`, { signal: AbortSignal.timeout(10_000) })
    const h = (await r.json()) as Record<string, { status?: { completed?: boolean; status_str?: string }; outputs?: Record<string, { images?: Array<{ filename: string; subfolder: string; type: string }> }> }>
    const entry = h[promptId]
    if (entry) {
      const st = entry.status ?? {}
      if (st.completed) {
        const imgs: string[] = []
        for (const out of Object.values(entry.outputs ?? {})) {
          for (const img of out.images ?? []) {
            const from = path.join(OUTPUT_DIR, img.filename)
            if (fs.existsSync(from)) {
              importAsset(entityId, 'art', from)
              imgs.push(path.basename(from))
            }
          }
        }
        return imgs
      }
      if (st.status_str === 'error') throw new Error('ComfyUI 生成失败')
    }
    await new Promise((res) => setTimeout(res, 3000))
  }
  throw new Error(`生成超时 ${timeoutMs / 1000}s`)
}

/** 该实体的设定图列表（读资产目录 data/entities/assets/<id>/） */
export function listEntityArt(entityId: string): string[] {
  return listAssets(entityId)
    .filter((a) => a.kind === 'art')
    .map((a) => a.file)
}

/** 读图文件（前端 <img> 用；改读资产目录） */
export function readArtFile(filename: string): { buf: Buffer; mime: string } | null {
  void filename
  return null
}
