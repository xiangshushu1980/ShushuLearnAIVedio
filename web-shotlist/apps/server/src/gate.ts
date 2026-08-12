/**
 * 实体合格检查（渲染门禁，用户决策 2026-08-12）
 * H3 提示词进入渲染前必须检查所有引用实体合格：文字（外观/声音/介绍）、画面（设定图）、声音（音色种子）
 * 文字不合格 = 硬阻塞（无 fallback）；画面/声音缺失 = 警告（可后补）
 */
import { countAssets, listAssets } from './assets.ts'
import { readEntity } from './entities.ts'

export interface EntityCheck {
  id: string
  name: string
  text: { ok: boolean; missing: string[] }
  art: { ok: boolean; count: number }
  voice: { ok: boolean; count: number }
}

export function checkEntity(id: string): EntityCheck {
  const e = readEntity(id)
  if (!e) {
    return {
      id,
      name: id,
      text: { ok: false, missing: ['实体不存在（无 fallback，请先抽取）'] },
      art: { ok: false, count: 0 },
      voice: { ok: false, count: 0 },
    }
  }
  const missing: string[] = []
  if (!e.appearance?.trim()) missing.push('外观（可作画级描述，必须）')
  if (!e.description?.trim()) missing.push('介绍')
  const artCount = countAssets(id, 'art')
  const voiceCount = countAssets(id, 'voice')
  return {
    id,
    name: e.name,
    text: { ok: missing.length === 0, missing },
    art: { ok: artCount > 0, count: artCount },
    voice: { ok: voiceCount > 0, count: voiceCount },
  }
}

export interface GateResult {
  allTextOk: boolean
  blocks: string[] // 硬阻塞原因
  warns: string[] // 警告
  checks: EntityCheck[]
}

/** 检查一组引用实体（拍摄本 role_cards / audio_refs 的实体） */
export function gateEntities(ids: string[]): GateResult {
  const unique = [...new Set(ids.filter(Boolean))]
  const checks = unique.map(checkEntity)
  const blocks: string[] = []
  const warns: string[] = []
  for (const c of checks) {
    if (!c.text.ok) {
      blocks.push(`实体「${c.name}」文字不合格：${c.text.missing.join('、')}`)
    }
    if (!c.art.ok) warns.push(`实体「${c.name}」无设定图（画面，可在实体详情生成）`)
    if (!c.voice.ok) warns.push(`实体「${c.name}」无音色种子（声音，可在实体详情上传）`)
  }
  return { allTextOk: blocks.length === 0, blocks, warns, checks }
}

/** 资源列表（实体详情面板用） */
export { listAssets }
