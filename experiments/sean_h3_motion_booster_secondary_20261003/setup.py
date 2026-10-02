#!/usr/bin/env python3
"""Owner: Sean. Build matched secondary-motion Ref2VA workflows."""
import copy
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
OLD = ROOT.parent / 'sean_h3_motion_booster_ref2va_20261002'
INPUT = pathlib.Path('/home/sean/projects/ComfyUI/input')
SOURCE = pathlib.Path('/home/sean/.codex/generated_images/01a0fd3f-7e1b-72f1-87ee-7b0d78e3e5b5/exec-fd25cc39-8a7c-4b48-a7df-d0c176add581.png')
if (ROOT / 'manifest.json').exists():
    raise SystemExit('Existing experiment manifest; resume run_cases.py rather than resetting this experiment.')

COMMON = '''subject_definitions:
<Subject 1> is the adult forest spirit defined by <Picture 1>, including the long silver hair, attached brown root tendrils, crimson shoulder ribbons, clothing, and identity.
<Subject 2> is the stone terrace and surrounding landscape defined by <Picture 1>, providing environment layout and lighting.

summary:
[reference generation] Generate an eight-second continuous full-body shot of <Subject 1> on <Subject 2>. ACTION_SUMMARY Use the image as the authority for appearance and environment rather than an exact opening frame.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - Preserve identity, costume, and the attachment points and separate materials of the hair, root tendrils, and ribbons.
<Subject 2> (appears in [Shot 1]): fully_preserved - Preserve the terrace layout, landscape, and lighting throughout the shot.

detailed_description:
Detailed fantasy character rendering matching the reference image, with readable material motion under soft overcast daylight. The source image guides appearance and landscape rather than requiring a frozen first-frame copy.
DETAIL

overall_soundscape:
SOUND

non_diegetic_music:
N/A
'''

WIND = '''[Shot 1] dynv2. A static wide full-body shot places <Subject 1> near the center of <Subject 2>, with both feet and every free material tip visible. The stone floor anchors the character, and the surrounding terrace and distant landscape extend continuously to both edges of the wide frame. Leave generous empty space on either side so that windblown strands remain inside the image. The camera maintains a static shot with unchanged lens, amplitude, and speed throughout all eight seconds. There are no cuts, zooms, or changes of viewpoint. Keep the background geographically fixed so that material movement can be judged against stable stone edges.
The single dominant action is a sustained wind gust blowing from screen left toward screen right while <Subject 1> remains standing. From the beginning through the first second, a gentle airflow lifts the free ribbon ends and loosely separates the outer hair strands. The feet stay firmly planted, the torso stays upright, and the arms hang comfortably clear of the body. The face remains neutral and the character does not perform a separate gesture or step. At approximately one second, the wind increases smoothly and reaches a strong, sustained level by two seconds. This change should be visible in the attached materials, rather than represented by camera movement or a change of location.
From two to six seconds, the long hair streams toward screen right in several distinct flowing groups. Fine hair tips respond readily, while the heavier sections form broad delayed waves. The free root tendrils bend to the same side in slower, smaller arcs, retaining their branching shapes and original attachment points. They behave as flexible woody strands with more resistance than the hair, rather than becoming smooth cloth. The two ribbons rise into large looping curves and flutter at their free ends, with brief traveling ripples passing from the shoulders toward the tips. Keep all three materials visually distinguishable and let their different stiffness produce different responses to the same airflow. Preserve the character's face, hands, costume, and limb arrangement throughout this sustained gust.
From six seconds to the eight-second end, the wind gradually weakens. The ribbon ends drop and flutter with smaller oscillations, the hair swings back toward its resting position, and the root tendrils settle more slowly with a short residual bend. These settling motions remain connected to the anchored body. Leaves in the distant trees can sway subtly without obscuring the silhouette. A continuous wind rush grows and fades with the gust, with light silk flutter and hair rustle nearby. The character remains silent and in the same standing location through the final frame.'''

MOVE = '''[Shot 1] dynv2. A static wide full-body shot frames <Subject 1> near the center of <Subject 2>, with the complete head, hands, feet, and all flexible material tips visible. The terrace floor is level and its stone joints provide fixed spatial markers. Keep the landscape extending naturally across the entire wide frame, with ample space around the character for the sweeping material arcs. The camera holds one static shot for the complete eight seconds, with unchanged lens and viewpoint. There are no cuts, camera tracking, zooms, or slow-motion segments. Ambient airflow is weak, so that the secondary movement is driven primarily by the character's body.
From the opening to the final frame, <Subject 1> performs one continuous exercise: large alternating whole-body pivot turns around the standing position. Begin facing the camera, rotate the hips and shoulders briskly toward screen left, then reverse toward screen right, and repeat the same left-right pattern at a steady ordinary-speed cadence. Each half-turn reaches a clear three-quarter profile rather than spinning through a complete revolution. The feet pivot and make short repositioning contacts on the stones, while the knees soften slightly at each direction reversal. The torso leads each turn, and the comfortably bent arms counterbalance without covering the face. The center of the body remains close to its initial position and the feet maintain believable contact with the ground. Show multiple complete reversal cycles during the eight seconds, using approximately two seconds for each full left-right cycle.
At every reversal, the attached materials briefly continue traveling in the previous direction before following the new direction of the shoulders and hips. Long hair sweeps through wide trailing arcs and breaks into several distinct strand groups. The ribbon ends fly outward in broad curved loops, with a visible delay between the shoulder turn and the changing direction of the free tips. The attached root tendrils trace narrower, slower arcs because they are heavier and stiffer. Preserve their woody branching shapes and attachment points, and show a brief elastic recovery after each reversal rather than making them rigid or weightless. Hair, root strands, and silk remain separate throughout the movement. Their trails should clearly follow the same turning body instead of independently orbiting it.
Keep the reference-defined face and costume recognizable as the head turns with the shoulders, without adding another character, prop, or action. Preserve correct limb arrangement and the broad full-body silhouette even when strands overlap briefly. The background remains stable while each successive turn continues at consistent tempo through the ending. Short boot scuffs and contacts correspond to the pivots, with silk flutter and material rustle occurring just after each reversal. The character does not speak; the final frame remains within the ongoing alternating exercise.'''

for label, detail, action, sound in [
    ('wind', WIND, 'A left-to-right wind gust drives the secondary materials while the character stays planted.', 'Outdoor air and a wind rush that grows and fades, with nearby silk flutter and material rustle. No spoken dialogue.'),
    ('move', MOVE, 'Large alternating pivot turns drive secondary follow-through with very little ambient wind.', 'Quiet outdoor air, rhythmic boot contacts and scuffs on stone, and silk flutter and material rustle following each turn. No spoken dialogue.'),
]:
    words = len(detail.split()) + 30
    assert 350 <= words <= 500, (label, words)
    (ROOT / f'prompt_{label}.txt').write_text(COMMON.replace('DETAIL', detail).replace('ACTION_SUMMARY', action).replace('SOUND', sound))

shutil.copy2(SOURCE, ROOT / 'reference.png')
input_name = 'sean_h3_secondary_reference_20261003.png'
shutil.copy2(SOURCE, INPUT / input_name)
(ROOT / 'workflows').mkdir(exist_ok=True)
old = json.loads((OLD / 'manifest.json').read_text())
base = json.loads((OLD / 'workflows/baseline.json').read_text())
cases = []
for label in ['wind', 'move']:
    for suffix, strength in [('base', 0), ('motion', 0.7)]:
        name = f'{label}_{suffix}'
        w = copy.deepcopy(base)
        w['5']['inputs']['image'] = input_name
        w['6']['inputs'].update(prompt=(ROOT / f'prompt_{label}.txt').read_text(), length=192)
        w['10']['inputs']['noise_seed'] = 2026100302
        if strength:
            w['20'] = {'class_type':'LoraLoaderModelOnly', 'inputs':{'model':['1',0], 'lora_name':old['model_file'], 'strength_model':strength}}
            for node in ['8','9']:
                w[node]['inputs']['model'] = ['20',0]
        w['15']['inputs']['filename_prefix'] = f'{ROOT.name}/{name}'
        w['15']['_meta']['title'] = f'[Sean] H3 secondary motion {name}'
        (ROOT / f'workflows/{name}.json').write_text(json.dumps(w, ensure_ascii=False, indent=2) + '\n')
        cases.append({'id':name, 'group':label, 'motion_lora_strength':strength, 'workflow':f'workflows/{name}.json', 'status':'pending'})
params = copy.deepcopy(old['parameters'])
params.update(frames=192, expected_duration_seconds=8.0, seed=2026100302)
manifest = {'owner':'Sean', 'experiment':'H3 Motion Booster V0.2 secondary hair/root/ribbon motion', 'status':'ready',
    'model_version_id':3246346, 'model_file':old['model_file'], 'expected_sha256':old['expected_sha256'], 'model_download':old['model_download'],
    'trigger':'dynv2', 'parameters':params, 'reference':{'experiment_file':'reference.png','comfy_input':input_name,
    'source':'built-in imagegen', 'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
    'comparison_rule':'Within each wind/move pair, identical reference, prompt including dynv2, seed, duration, sampler and steps; only add Motion Booster at strength 0.7. Single seed exploratory comparison, no physics benchmark.',
    'cases':cases,'results':[]}
(ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
runner = (OLD / 'run_cases.py').read_text().replace('"motion_07", "motion_08", "motion_07_no_ref_latent", "motion_07_fullwidth_prompt", "motion_07_landscape_ref"', '"wind_base", "wind_motion", "move_base", "move_motion"')
runner = runner.replace('case["id"] == "baseline" or ', '').replace('sean_h3_motion_booster_ref2va_20261002', ROOT.name).replace('sean-motion-booster', 'sean-secondary-motion')
(ROOT / 'run_cases.py').write_text(runner)
print(json.dumps({'owner':'Sean','cases':[x['id'] for x in cases],'frames':192,'seconds':8.0}))
