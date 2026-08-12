import { serializeScript, parseScript, scriptTemplate } from '@shotlist/shared'

// 1) 模板预填
const tpl = scriptTemplate('测试项目')
const { script } = parseScript(tpl)
console.log('模板解析:', script?.head.title, script?.head.duration, script?.head.chain)

// 2) 表单修改 → 重写（保留未知字段 + 注释行外的内容）
const raw = `---
title: 旧标题
style: 日系清新
ratio: 16:9
scene: beach
duration: 8
custom_field: keep_me
# 手写备注
---
正文第一行`
const next = serializeScript(raw, { ...script!.head, title: '新标题', duration: 10, scene: 'stage' })
console.log('--- 重写后 ---')
console.log(next)
console.log('--- 重写后解析 ---')
const { script: s2, errs } = parseScript(next)
console.log('errs:', errs, '| title:', s2?.head.title, '| duration:', s2?.head.duration, '| scene:', s2?.head.scene, '| custom:', s2?.head.branch === undefined && JSON.stringify(s2?.head).includes('keep_me'))
