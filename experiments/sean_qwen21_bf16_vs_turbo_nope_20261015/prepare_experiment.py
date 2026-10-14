#!/usr/bin/env python3
"""Owner: Sean. Prepare the no-PE Qwen 2.1 BF16/Turbo comparison."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/home/sean/projects/comfy-ops/experiments/infograph_krea2_qwen21_v3_20261014/data_matrix_v2/casebook.json')
TASK = 'remote-97ccaaac-e730-4c57-875c-c86954ca0518'
SEEDS = [42, 1337]
WIDTH, HEIGHT = 1536, 1024
SIGMAS = '1.0, 0.978453, 0.954180, 0.926626, 0.895080, 0.845148, 0.704534, 0.414568, 0.0'

STYLE_EN = {
    'c10_city_transport_zh': 'restrained city newspaper graphic, warm ivory paper, dark green and vermilion, a few fine line icons, no photorealistic illustration',
    'c12_food_waste_zh': 'warm hand-drawn editorial chart on cream paper, tomato red and leaf green, spare linework and prominent quantities',
    'c14_population_pyramid_zh': 'modern public data report, mist blue and coral orange, clean grid, very small simplified human silhouettes as accents',
    'c15_household_water_zh': 'minimal environmental public information design, white ground, deep teal and bright cyan, large readable values and only a few water-drop icons',
    'c17_internet_gap_zh': 'newspaper data column, warm gray ground, black typography, lake blue and brick red, moderate chart density',
    'c19_reuse_network_zh': 'recycled-paper collage poster, indigo and orange, a clear reading path and carefully aligned flow arrows',
}
CHART_EN = {
    'c10_city_transport_zh': 'a horizontal grouped bar chart with three transport rows and two clearly separated measures per row: mode share and average commute time',
    'c12_food_waste_zh': 'a waterfall chart: begin at 100 kg, subtract purchasing loss, storage loss, and meal-preparation loss in sequence, and end at 50 kg; each connector shows the cumulative decrease',
    'c14_population_pyramid_zh': 'a population pyramid with male bars on the left and female bars on the right, sharing one central baseline across five age groups; bar lengths must match the counts',
    'c15_household_water_zh': 'a dumbbell chart with one thin horizontal connector per household and before/after endpoints on a shared zero-based 0–300 L scale',
    'c17_internet_gap_zh': 'four small-multiple paired bar charts for East, South, West, and North; every panel shares the same zero-based 0–100% vertical scale, with urban and rural bars paired',
    'c19_reuse_network_zh': 'a directed flow diagram from 80 idle items into three destinations; branch widths must be proportional to their quantities and all arrows flow outward from the source',
}
KEY_EN = {
    'c10_city_transport_zh': 'Keep share and minutes in separate visual tracks; pair each mode with both of its own values. Metro has the greatest share and cycling the shortest commute.',
    'c12_food_waste_zh': 'The arithmetic must balance. Loss bars descend to the final 50 kg; the largest single loss is meal preparation.',
    'c14_population_pyramid_zh': 'Order age groups from youngest at the top to oldest at the bottom. Mirror bar lengths around the center without swapping counts. The 30–44 group is largest; women outnumber men among people aged 60 and above.',
    'c15_household_water_zh': 'Pair each household’s before and after values correctly. All four households save between 30 and 60 liters per day. Do not exaggerate the differences.',
    'c17_internet_gap_zh': 'Keep the urban and rural values attached to the correct region. The West has the widest gap at 32 percentage points.',
    'c19_reuse_network_zh': 'The three destination quantities must sum to 80. Donation is the largest branch.',
}

def flat_texts(case):
    vals = [case['title'], case['subtitle']]
    for row in case['rows']:
        vals.extend(row)
    return list(dict.fromkeys(str(x) for x in vals))

def make_prompt(case):
    chart = CHART_EN.get(case['id'], case['chart'])
    style = STYLE_EN.get(case['id'], case['style'])
    key = KEY_EN.get(case['id'], case['key'])
    row_lines = [' | '.join(map(str, row)) for row in case['rows']]
    inventory = '\n'.join(f'• {s}' for s in flat_texts(case))
    return (
        f"Create one finished landscape 3:2 editorial infographic as an article illustration. "
        f"Use a quiet, clean composition in this art direction: {style}. "
        f"At the top, give the exact title \"{case['title']}\" clear visual priority; place the exact subtitle "
        f"\"{case['subtitle']}\" directly beneath it. Let the chart occupy most of the remaining canvas: {chart}. "
        f"The rows below are the ground truth. Keep each value attached to its exact category and preserve order, units, "
        f"signs, and scale relationships:\n" + '\n'.join(row_lines) + '\n' +
        f"Design intent: {key} Make the main visual carry the comparison, with labels close to their marks, "
        f"consistent alignment, generous spacing, legible type, and restrained decoration. Use small icons only when they "
        f"clarify the subject; the data chart remains the focal point. Do not turn the composition into a table of text.\n"
        f"Exact visible text inventory (copy the strings exactly, including script, punctuation, spaces, and symbols):\n"
        f"{inventory}\n"
        f"Show only strings from this inventory. Do not invent captions, axis numbers, legends, claims, labels, letters, "
        f"logos, or watermarks. No extra text."
    )

def base_graph(prompt, seed, prefix):
    return {
        '1': {'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_bf16.safetensors','weight_dtype':'default'}},
        '2': {'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_bf16.safetensors','type':'qwen_image'}},
        '3': {'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
        '4': {'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},
        '5': {'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':''}},
        '6': {'class_type':'EmptySD3LatentImage','inputs':{'width':WIDTH,'height':HEIGHT,'batch_size':1}},
        '7': {'class_type':'KSampler','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'latent_image':['6',0],'seed':seed,'steps':40,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
        '8': {'class_type':'VAEDecode','inputs':{'samples':['7',0],'vae':['3',0]}},
        '9': {'class_type':'SaveImage','inputs':{'images':['8',0],'filename_prefix':prefix}},
    }

def turbo_graph(prompt, seed, prefix):
    return {
        '1': {'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_turbo_int8_convrot.safetensors','weight_dtype':'default'}},
        '2': {'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_bf16.safetensors','type':'qwen_image'}},
        '3': {'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
        '4': {'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},
        '5': {'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':''}},
        '6': {'class_type':'EmptySD3LatentImage','inputs':{'width':WIDTH,'height':HEIGHT,'batch_size':1}},
        '7': {'class_type':'ManualSigmas','inputs':{'sigmas':SIGMAS}},
        '8': {'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},
        '9': {'class_type':'SamplerCustom','inputs':{'model':['1',0],'add_noise':True,'noise_seed':seed,'cfg':1.0,'positive':['4',0],'negative':['5',0],'sampler':['8',0],'sigmas':['7',0],'latent_image':['6',0]}},
        '10': {'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['3',0]}},
        '11': {'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':prefix}},
    }

def main():
    source=json.loads(SOURCE.read_text())
    (ROOT/'source_casebook.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
    for name in ('prompts','workflows','images','runs'):
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    prompts={}
    jobs=[]
    for case in source['cases']:
        prompt=make_prompt(case)
        prompts[case['id']]=prompt
        (ROOT/'prompts'/f"{case['id']}.txt").write_text(prompt+'\n')
        for model in ('qwen21_bf16','qwen21_turbo_int8'):
            for seed in SEEDS:
                job=f"{case['id']}__{model}__seed{seed}"
                graph=base_graph(prompt,seed,f'sean_qwen21_compare_20261015/{job}') if model=='qwen21_bf16' else turbo_graph(prompt,seed,f'sean_qwen21_compare_20261015/{job}')
                (ROOT/'workflows'/f'{job}.json').write_text(json.dumps({'prompt':graph},ensure_ascii=False,indent=2)+'\n')
                jobs.append({'job':job,'case_id':case['id'],'model':model,'seed':seed,'prompt':prompt})
    manifest={'owner':'Sean','task_id':TASK,'experiment':'Qwen Image 2.1 BF16 vs Turbo INT8 ConvRot, direct prompt, no PE','status':'prepared','created_at':None,'source_casebook':str(SOURCE),'models':{'qwen21_bf16':{'weights':'qwen_image_2.1_bf16.safetensors','text_encoder':'qwen3vl_8b_bf16.safetensors','vae':'qwen_image_2.1_vae_bf16.safetensors','steps':40,'cfg':1.0,'sampler':'euler','scheduler':'simple'},'qwen21_turbo_int8':{'weights':'qwen_image_2.1_turbo_int8_convrot.safetensors','text_encoder':'qwen3vl_8b_bf16.safetensors','vae':'qwen_image_2.1_vae_bf16.safetensors','steps':8,'sigma_schedule':SIGMAS,'cfg':1.0,'sampler':'euler'}},'prompting':'Hand-authored in English using the Qwen official observer-style prompt guidance and infographic skill structure; no PE node or LLM rewriting at runtime. Exact same prompt is used for both checkpoints. Text labels retain the casebook language.','resolution':[WIDTH,HEIGHT],'seeds':SEEDS,'cases':[{'id':c['id'],'language':c['lang'],'title':c['title'],'ground_truth':c['rows'],'target_text':flat_texts(c),'data_source':c.get('data_source'),'source_url':c.get('source_url')} for c in source['cases']],'planned_images':len(jobs),'successes':0,'failures':0,'jobs':jobs}
    (ROOT/'runs'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f"Prepared {len(source['cases'])} cases, {len(prompts)} direct prompts, {len(jobs)} workflows")

if __name__=='__main__': main()
