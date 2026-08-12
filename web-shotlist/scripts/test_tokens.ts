import { tokenizePrompt, extractPictureRefs } from '@shotlist/shared'

const sample = `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] The scene opens as <Subject 1> walks along the beach. At 00:02.500, the camera cuts to [Shot 2] as the camera pushes in with small amplitude at slow speed.
overall_soundscape: ambient: gentle waves and sea wind; fx: cloth rustling
non_diegetic_music: N/A`

for (const t of tokenizePrompt(sample)) {
  if (t.kind === 'text') continue
  console.log(t.kind.padEnd(9), JSON.stringify(t.text.slice(0, 55)))
}
console.log('pics:', extractPictureRefs(sample))
