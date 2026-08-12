/** server 侧路径常量与 key 读取（node-only，不进 shared 包） */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

/** web-shotlist 仓库根（src/config.ts → 上三级） */
export const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..')

/** 默认项目数据目录（docs/22：项目=目录；对应 experiments/shotlist 结构） */
export const DEFAULT_DATA_DIR = path.join(REPO_ROOT, '..', 'experiments', 'shotlist')

/** web 工具自己的数据根（data/ gitignored；V2 对接 experiments/shotlist 导入） */
export const DATA_ROOT = path.join(REPO_ROOT, 'data')

/** 实体注册表目录（V1 基础版：data/entities；V2 对接 experiments/entities） */
export const ENTITIES_DIR = path.join(DATA_ROOT, 'entities')

/** 角色卡目录（工具 A/B 注入外观锚定用） */
export const ROLE_CARD_DIR = path.join(DEFAULT_DATA_DIR, 'rolecards')

/** docs/17 规则手册（工具 A/B 系统提示注入） */
export const RULES_FILE = path.join(REPO_ROOT, '..', 'docs', '17_h3_prompt_writing_rules.md')

/** IR 逆向 few-shot 样本库 */
export const IR_REVERSE_DIR = path.join(DEFAULT_DATA_DIR, 'ir_reverse')

/** 官方 IR 输出样本（i2va 模式 few-shot） */
export const IR_SAMPLE = path.join(REPO_ROOT, '..', 'experiments', 'ir_samples', 'i2v_alya_beach.txt')

/** ref2va 官方参考指南 */
export const REF2VA_GUIDE = path.join(REPO_ROOT, '..', '.pi', 'skills', 'h3-prompt-writing', 'references', 'ref-en.txt')

/** DeepSeek key 读取（不进 git） */
export function getDeepSeekKey(): string {
  const env = process.env.DEEPSEEK_API_KEY
  if (env) return env
  const f = path.join(process.env.HOME ?? '/home/sean', '.config', 'mem0_deepseek_key')
  if (fs.existsSync(f)) return fs.readFileSync(f, 'utf-8').trim()
  throw new Error('缺少 DeepSeek key：~/.config/mem0_deepseek_key 或 DEEPSEEK_API_KEY')
}
