/**
 * 实体资源系统：data/entities/assets/<entityId>/（设定图/音色/通用文件）
 * 与实体卡关联保存，可上传/查看/删除；渲染前门禁按三态检查
 */
import fs from 'node:fs'
import path from 'node:path'
import { entitiesDir } from './entities.ts'

export type AssetKind = 'art' | 'voice' | 'file'

export interface Asset {
  kind: AssetKind
  file: string
  size: number
  createdAt: number
}

export function assetsDir(entityId: string): string {
  const dir = path.join(entitiesDir(), 'assets', entityId)
  fs.mkdirSync(dir, { recursive: true })
  return dir
}

function assetMeta(dir: string, kind: AssetKind, file: string): Asset {
  const stat = fs.statSync(path.join(dir, file))
  return { kind, file, size: stat.size, createdAt: stat.mtimeMs }
}

// 防穿越：仅允许 assets/<entityId>/ 下的文件
function assetsDirSafe(entityId: string): string {
  return assetsDir(path.basename(entityId))
}

const KIND_PREFIX: Record<AssetKind, string> = { art: 'art_', voice: 'voice_', file: 'file_' }

/** 保存资源文件（kind 前缀 + 时间戳去重） */
export function saveAsset(entityId: string, kind: AssetKind, originalName: string, buf: Buffer): Asset {
  const dir = assetsDirSafe(entityId)
  const ext = path.extname(originalName).toLowerCase() || (kind === 'voice' ? '.wav' : kind === 'art' ? '.png' : '')
  const file = `${KIND_PREFIX[kind]}${Date.now()}${ext}`
  fs.writeFileSync(path.join(dir, file), buf)
  return assetMeta(dir, kind, file)
}

/** 从外部目录移入资源（设定图生成后使用） */
export function importAsset(entityId: string, kind: AssetKind, fromPath: string): Asset {
  const dir = assetsDirSafe(entityId)
  const file = `${KIND_PREFIX[kind]}${Date.now()}${path.extname(fromPath).toLowerCase() || '.png'}`
  fs.copyFileSync(fromPath, path.join(dir, file))
  return assetMeta(dir, kind, file)
}

export function listAssets(entityId: string): Asset[] {
  const dir = assetsDirSafe(entityId)
  if (!fs.existsSync(dir)) return []
  return fs
    .readdirSync(dir)
    .filter((f) => fs.statSync(path.join(dir, f)).isFile())
    .map((f) => {
      const kind: AssetKind = f.startsWith('art_') ? 'art' : f.startsWith('voice_') ? 'voice' : 'file'
      const stat = fs.statSync(path.join(dir, f))
      return { kind, file: f, size: stat.size, createdAt: stat.mtimeMs }
    })
    .sort((a, b) => b.createdAt - a.createdAt)
}

export function countAssets(entityId: string, kind: AssetKind): number {
  return listAssets(entityId).filter((a) => a.kind === kind).length
}

export function deleteAsset(entityId: string, file: string): void {
  const dir = assetsDirSafe(entityId)
  const f = path.join(dir, path.basename(file)) // 防穿越
  if (!fs.existsSync(f)) throw new Error(`资源不存在: ${file}`)
  fs.rmSync(f)
}

export function readAsset(entityId: string, file: string): { buf: Buffer; mime: string } | null {
  const dir = assetsDirSafe(entityId)
  const f = path.join(dir, path.basename(file))
  if (!fs.existsSync(f)) return null
  const ext = path.extname(f).toLowerCase()
  const mime =
    ext === '.wav' ? 'audio/wav' : ext === '.mp3' ? 'audio/mpeg' : ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : ext === '.webp' ? 'image/webp' : ext === '.png' ? 'image/png' : 'application/octet-stream'
  return { buf: fs.readFileSync(f), mime }
}
