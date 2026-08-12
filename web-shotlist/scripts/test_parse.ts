import { parseShotlistYaml } from '@shotlist/shared'
import fs from 'node:fs'
const text = fs.readFileSync('/home/sean/projects/comfy-ops/experiments/shotlist/Alya 的海边黄昏_shotlist.yaml', 'utf-8')
const { data, errs } = parseShotlistYaml(text)
console.log('errs:', errs)
console.log('shots:', data?.shots?.length)
