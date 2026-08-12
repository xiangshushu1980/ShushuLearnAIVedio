/** 纯常量（无 node 依赖，前端可安全引用） */

/** 项目文件命名约定（docs/22 五节） */
export const PROJECT_FILES = {
  script: 'script.yaml',
  shotlist: 'shotlist.yaml',
  prompt: (mode: 'i2va' | 'ref2va') => `prompt_${mode}.txt`,
  inputs: 'inputs.json',
  meta: 'meta.json',
} as const

/** 新建项目预填剧本模板（参数头 + 正文占位） */
export function scriptTemplate(title: string): string {
  return `---
title: ${title}
style: 日系清新
ratio: 16:9
scene: beach
duration: 8
sound: 
role_cards: []
chain: independent
shot_style: 分镜剪辑
---
（正文：在此写剧本——场景/动作/台词。一镜一动作，画面具体。生成拍摄本前可先填角色卡。）`
}

/** scene 预设（首帧图库 input/start/169/ 真实子目录 2026-08-12 + docs/17 惯例 id；V2 从磁盘扫描） */
export const SCENE_PRESETS = [
  'beach', 'forest', 'night', 'night_street', 'portrait', 'stage', 'multi',
  'classroom', 'city', 'street', 'rooftop', 'room', 'park', 'snow',
]

/** ratio 选项 */
export const RATIO_OPTIONS = ['16:9', '9:16', '1:1', '4:3', '21:9'] as const

/** 时长快捷档（对应 docs/17 镜头预算：4-6s→1-2 镜；7-10s→2-3 镜；11-15s→3-5 镜） */
export const DURATION_PRESETS = [4, 6, 8, 10, 12, 15]

/** chain 选项说明 */
export const CHAIN_OPTIONS: Array<{ value: string; label: string; hint: string }> = [
  { value: 'first_static', label: 'first_static', hint: '首帧=角色静态图锚定' },
  { value: 'firstlast_bridge', label: 'firstlast_bridge', hint: '首尾帧静态双锚转场' },
  { value: 'independent', label: 'independent', hint: '独立段，一致性靠文本锚定' },
]

/** shot_style 选项 */
export const SHOT_STYLE_OPTIONS = ['分镜剪辑', '长镜头流'] as const
