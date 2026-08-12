/**
 * 标色方案（docs/22 第三节 + 实体系统颜色）
 * 用户确认 2026-08-12：实体类型定色 + 重要程度加边框
 */

// ===== 实体类型色 =====
export const ENTITY_TYPE_COLORS: Record<string, { bg: string; text: string; border: string; chip: string }> = {
  角色: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-400', chip: 'bg-blue-100 text-blue-800' },
  场景: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-400', chip: 'bg-emerald-100 text-emerald-800' },
  物件: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-400', chip: 'bg-orange-100 text-orange-800' },
  技能: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-400', chip: 'bg-purple-100 text-purple-800' },
  组织: { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-400', chip: 'bg-cyan-100 text-cyan-800' },
  地点: { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-400', chip: 'bg-teal-100 text-teal-800' },
}

export const ENTITY_IMPORTANCE_BORDER: Record<'core' | 'secondary', string> = {
  core: 'border-2 border-solid',
  secondary: 'border border-dashed',
}

/** 重要度标签文案 */
export const IMPORTANCE_LABEL: Record<'core' | 'secondary', string> = {
  core: '核心',
  secondary: '次要',
}

// ===== 提示词元素标色（docs/22 表）=====
/** 参考标签 <Subject N>/<Picture N>/<Video N>/<Audio N> 徽章色（S1 蓝/S2 粉…循环） */
export const REF_BADGE_COLORS = [
  'bg-blue-600 text-white',
  'bg-pink-600 text-white',
  'bg-emerald-600 text-white',
  'bg-amber-600 text-white',
  'bg-purple-600 text-white',
  'bg-cyan-600 text-white',
]

/** 声音三层色（环境=绿 / fx=橙 / bgm=紫） */
export const SOUND_LAYER_COLORS: Record<'ambient' | 'fx' | 'bgm', string> = {
  ambient: 'text-emerald-700 bg-emerald-50 border-emerald-300',
  fx: 'text-orange-700 bg-orange-50 border-orange-300',
  bgm: 'text-purple-700 bg-purple-50 border-purple-300',
}

/** 镜头运动语法 token 集（docs/17 运动语法枚举，标斜体 + 🎥） */
export const CAMERA_MOTION_TOKENS = [
  'zoom_in', 'zoom_out', 'push_in', 'pull_out', 'pan_l', 'pan_r',
  'truck_l', 'truck_r', 'tilt_up', 'tilt_down', 'pedestal_up', 'pedestal_down',
  'arc_shot', 'tracking', 'static', 'shake_slight', 'shake_strong', 'pov', 'roll_cw', 'roll_ccw',
  'push in', 'push-in', 'zoom in', 'zoom out', 'pan left', 'pan right',
  'tilt up', 'tilt down', 'tracking shot', 'arc shot', 'static shot',
]
