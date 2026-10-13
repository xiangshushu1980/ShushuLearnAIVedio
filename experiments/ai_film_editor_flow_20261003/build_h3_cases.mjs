// Owner: Sean — produce a reproducible H3 runner input from the reviewed prompts.
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const prompt = async name => (await readFile(path.join(root, 'prompts', name), 'utf8')).trim();
const shared = {
  unet: 'minimax_h3_ref2va_pruned_int8_convrot.safetensors',
  pdd: 'minimax_h3_ref2va_pdd_acc_8step_comfyui.safetensors',
  pdd_nfe: 8,
  steps: 8,
  width: 1024,
  height: 576,
  sage_attention: true,
  refs: ['sean_ai_film_main_appearance.png', 'sean_ai_film_three_view.png'],
};
const cases = [
  {
    ...shared,
    name: 'S01_setup_candidate_A',
    seed: 2026100311,
    length: 96,
    prompt: await prompt('S01_guardroom_setup_ref2va.txt'),
    prefix: 'video/sean_ai_film_flow_20261003/S01_setup_candidate_A',
  },
  {
    ...shared,
    name: 'S02_greeting_candidate_A',
    seed: 2026100321,
    length: 148,
    audio: 'sean_ai_film_voice.wav',
    prompt: await prompt('S02_greeting_ref2va.txt'),
    prefix: 'video/sean_ai_film_flow_20261003/S02_greeting_candidate_A',
  },
  {
    ...shared,
    name: 'S02_greeting_retry_B',
    seed: 2026100322,
    length: 148,
    audio: 'sean_ai_film_voice.wav',
    prompt: await prompt('S02_greeting_ref2va.txt'),
    prefix: 'video/sean_ai_film_flow_20261003/S02_greeting_candidate_B',
  },
];
await writeFile(path.join(root, 'h3_cases.json'), `${JSON.stringify(cases, null, 2)}\n`);
console.log(`Wrote ${cases.length} serial H3 cases to ${path.relative(process.cwd(), path.join(root, 'h3_cases.json'))}`);
