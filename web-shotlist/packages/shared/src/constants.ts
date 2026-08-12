/** 纯常量（无 node 依赖，前端可安全引用） */

/** 项目文件命名约定（docs/22 五节） */
export const PROJECT_FILES = {
  script: 'script.yaml',
  shotlist: 'shotlist.yaml',
  prompt: (mode: 'i2va' | 'ref2va') => `prompt_${mode}.txt`,
  inputs: 'inputs.json',
  meta: 'meta.json',
} as const
