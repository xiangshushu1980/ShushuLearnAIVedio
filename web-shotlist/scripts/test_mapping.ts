import { parseRefMapping } from '@shotlist/shared'
import fs from 'node:fs'

const dir = '/home/sean/projects/comfy-ops/web-shotlist/data/projects/alya_海边黄昏_e2e'
const prompt = fs.existsSync(dir + '/prompt_ref2va.txt') ? fs.readFileSync(dir + '/prompt_ref2va.txt', 'utf-8') : ''

const m = parseRefMapping(prompt, ['alya_v1'])
console.log('映射:', JSON.stringify(m))
console.log('含 reference image 行:', /<Picture \d+> is the reference image for <Subject \d+>/i.test(prompt))
