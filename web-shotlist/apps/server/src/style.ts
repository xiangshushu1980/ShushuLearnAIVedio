/** 全局风格设定（data/style.json；用户决策 2026-08-14：只影响设定图生成） */
import fs from 'node:fs'
import path from 'node:path'
import { DATA_ROOT } from './config.ts'

export interface StyleConfig {
  /** 风格描述（英文 prompt 词，注入设定图生成；空 = 默认写实动画风） */
  prompt: string
  updatedAt?: string
}

const STYLE_FILE = path.join(DATA_ROOT, 'style.json')

export function readStyle(): StyleConfig {
  try {
    return JSON.parse(fs.readFileSync(STYLE_FILE, 'utf-8')) as StyleConfig
  } catch {
    return { prompt: '' }
  }
}

export function writeStyle(prompt: string): StyleConfig {
  fs.mkdirSync(path.dirname(STYLE_FILE), { recursive: true })
  const cfg: StyleConfig = { prompt, updatedAt: new Date().toISOString() }
  fs.writeFileSync(STYLE_FILE, JSON.stringify(cfg, null, 2), 'utf-8')
  return cfg
}

/** 注入用：全局风格词（空则返回空串，不改变默认基线） */
export function styleSuffix(): string {
  const s = readStyle().prompt.trim()
  return s ? `, ${s}` : ''
}
