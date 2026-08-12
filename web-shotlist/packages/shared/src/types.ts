/** 共享类型定义（docs/22 数据模型：剧本/拍摄本/实体/提示词） */

// ===== 剧本 script.yaml（YAML 参数头 + 正文）=====
export interface ScriptHead {
  title: string
  style?: string
  ratio?: string
  scene?: string
  duration?: number
  sound?: string
  role_cards?: string[]
  chain?: Chain
  audio_refs?: Record<string, string>
  no_bgm?: boolean
  /** 兼容参数头直接写 bgm: N/A 的旧剧本 */
  bgm?: string
  shot_style?: string
  /** 预留分支扩展点（V2：决策点标记 → 路径展开，拍摄本保持线性） */
  branch?: unknown
}

export interface Script {
  head: ScriptHead
  body: string
  /** 原始文本（YAML 参数头 + 正文） */
  raw: string
}

// ===== 拍摄本 shotlist.yaml（工具 A 输出，web 只读展示）=====
export type Chain = 'first_static' | 'firstlast_bridge' | 'independent'

export const FRAMINGS = ['特写', '近景', '中景', '中全景', '全景', '大远景'] as const
export type Framing = (typeof FRAMINGS)[number]

export const CAMERA_TYPES = [
  'zoom_in', 'zoom_out', 'push_in', 'pull_out', 'pan_l', 'pan_r',
  'truck_l', 'truck_r', 'tilt_up', 'tilt_down', 'pedestal_up', 'pedestal_down',
  'arc_shot', 'tracking', 'static', 'shake_slight', 'shake_strong', 'pov', 'roll_cw', 'roll_ccw',
] as const
export type CameraType = (typeof CAMERA_TYPES)[number]

export type Amplitude = 'small' | 'medium' | 'large'
export type Speed = 'slow' | 'normal' | 'fast'

export interface DialogueLine {
  speaker: string
  text: string
}

export interface ShotSound {
  ambient?: string
  fx?: string
  /** 'N/A' = 导演特意决策无配乐（bgm 三件套触发 no_music 模式） */
  bgm: string
}

export interface Shot {
  id: number
  duration_s: number
  framing: Framing
  camera: {
    type: CameraType
    amplitude?: Amplitude
    speed?: Speed
  }
  subject: string
  action: string
  dialogue?: DialogueLine[]
  sound: ShotSound
  continuity: string
}

export interface Shotlist {
  title: string
  style?: string
  ratio?: string
  scene: string
  duration_total: number
  chain: Chain
  role_cards?: string[]
  audio_refs?: Record<string, string>
  shots: Shot[]
}

// ===== 实体（世界观设定单元，docs/22 实体系统）=====
export const ENTITY_TYPES = ['角色', '场景', '物件', '技能', '组织', '地点'] as const
export type EntityType = (typeof ENTITY_TYPES)[number]

/** 重要程度：核心（实线边框）/ 次要（虚线边框） */
export type EntityImportance = 'core' | 'secondary'

export interface Entity {
  id: string
  name: string
  type: EntityType
  importance: EntityImportance
  /** 详细设定（markdown） */
  description: string
}

// ===== 提示词（工具 B 输出）=====
export type PromptMode = 'i2va' | 'ref2va'

// ===== 渲染输入源（docs/22 侧栏清单，解析自拍摄本 audio_refs / 提示词引用）=====
export interface InputRefImage {
  kind: 'image'
  /** <Picture N> 编号 */
  n: number
  /** 文件相对路径或 URL */
  src: string
  /** 用途标注，如 "Subject 1 Alya 角色卡 canon" */
  label: string
  /** 关联实体 id（如有） */
  entityId?: string
}

export interface InputRefAudio {
  kind: 'audio'
  /** <Audio N> 编号 */
  n: number
  src: string
  label: string
  entityId?: string
}

export type InputRef = InputRefImage | InputRefAudio

// ===== 项目（docs/22 项目 = 目录）=====
export interface ProjectMeta {
  id: string
  name: string
  createdAt: string
  /** 引用的实体注册表（V1 基础版） */
  entities?: string[]
  /** 入回收站时间（在回收站时存在） */
  trashedAt?: string
}

export interface TrashItem {
  id: string
  name: string
  trashedAt: string
}

export interface Project {
  meta: ProjectMeta
  script?: Script
  shotlist?: Shotlist
  /** 拍摄本原始 YAML 文本（工具 B 直接消费） */
  shotlistRaw?: string
  /** 提示词原始文本 */
  prompt?: string
  promptMode?: PromptMode
  inputs: InputRef[]
}
