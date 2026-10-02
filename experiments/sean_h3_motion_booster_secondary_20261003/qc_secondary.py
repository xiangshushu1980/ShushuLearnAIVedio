#!/usr/bin/env python3
"""Owner: Sean. Decode video integrity and build frame-aligned comparison artifacts."""
import hashlib
import copy
import json
import pathlib
import re
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    records = []
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    assert hashlib.sha256((ROOT / 'reference.png').read_bytes()).hexdigest() == manifest['reference']['sha256']
    normalized = {}
    for case in manifest['cases']:
        w = copy.deepcopy(json.loads((ROOT / case['workflow']).read_text()))
        w.pop('20', None)
        for node in ['8','9']:
            w[node]['inputs']['model'] = ['1',0]
        w['15']['inputs']['filename_prefix'] = 'comparison'
        w['15'].pop('_meta', None)
        if case['group'] in normalized:
            assert w == normalized[case['group']], 'Unexpected paired workflow confound'
        else:
            normalized[case['group']] = w
    for case in manifest['cases']:
        path = ROOT / case['output']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == case['sha256']
        capture = cv2.VideoCapture(str(path))
        count = 0
        bands = []
        dark_bands = []
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            count += 1
            assert frame.shape == (448,768,3), frame.shape
            white = (frame.min(axis=2) > 245).mean(axis=0) > .98
            left = right = 0
            while left < 768 and white[left]:
                left += 1
            while right < 768 and white[767-right]:
                right += 1
            bands.append((left, right))
            dark = (frame.max(axis=2) < 10).mean(axis=0) > .98
            left = right = 0
            while left < 768 and dark[left]:
                left += 1
            while right < 768 and dark[767-right]:
                right += 1
            dark_bands.append((left, right))
        fps = capture.get(cv2.CAP_PROP_FPS)
        capture.release()
        assert count == 192 and fps == 24, (case['id'],count,fps)
        subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'], check=True)
        audio = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-f','f32le','-ac','1','-ar','48000','-'])
        samples = np.frombuffer(audio, dtype='<f4')
        logs = (ROOT / f"{case['id']}_runtime.log").read_text()
        progress = re.findall(r'20/20\s*\[([^\]]+)\]', logs)
        records.append({'case':case['id'], 'frames':count,'fps':fps,'video_seconds':count/fps,'size':[768,448],
            'max_white_side_band_px':np.max(bands,axis=0).tolist(),
            'black_side_band_range_px':[np.min(dark_bands,axis=0).tolist(),np.max(dark_bands,axis=0).tolist()],
            'median_black_side_band_px':np.median(dark_bands,axis=0).tolist(),
            'nonband_content_width_range_px':[int(np.min(768-np.array(bands).sum(axis=1)-np.array(dark_bands).sum(axis=1))),int(np.max(768-np.array(bands).sum(axis=1)-np.array(dark_bands).sum(axis=1)))],
            'audio_seconds':len(samples)/48000,
            'decoded_audio_peak':float(np.abs(samples).max()), 'near_full_scale_fraction':float((np.abs(samples)>=.999).mean()),
            'sampling_progress':progress[-1] if progress else None, 'decode':'ffmpeg full decode passed',
            'unmatched_lora_warnings':case['lora_unmatched_log_count']})
    report = {'owner':'Sean','method':'All frames decoded; white side columns require >98% pixels in all channels >245; black requires >98% pixels in all channels <10. Band removal width is a frame-content proxy, not a semantic quality score. Sampling timing from final 20/20 progress, separate from whole-job loading/encoding time. Audio peak measured after decoding AAC, not a listening evaluation.', 'results':records}
    (ROOT / 'integrity.json').write_text(json.dumps(report,indent=2)+'\n')
    groups = [('wind',['wind_base','wind_motion']),('move',['move_base','move_motion'])]
    if any(c['id']=='move_motion10' and c['status']=='success' for c in manifest['cases']):
        groups.append(('move_strength',['move_base','move_motion','move_motion10']))
    strengths = {c['id']:c['motion_lora_strength'] for c in manifest['cases']}
    for group,names in groups:
        times = [.25,1.75,3.25,4.75,6.25,7.75]
        canvas = Image.new('RGB',(1536,len(names)*2*258),'#202020')
        draw = ImageDraw.Draw(canvas)
        for i,name in enumerate(names):
            capture = cv2.VideoCapture(str(ROOT / f'{name}.mp4'))
            for j,t in enumerate(times):
                x,y = (j%3)*512, (i*2+j//3)*258
                capture.set(cv2.CAP_PROP_POS_MSEC,t*1000)
                ok,frame = capture.read()
                assert ok,(name,t)
                draw.text((x+8,y+5),f'{name} | {t:.2f}s',font=font,fill='white')
                picture = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((384,224))
                canvas.paste(picture,(x+64,y+32))
            capture.release()
        canvas.save(ROOT / f'{group}_contact.png')
        labels = []
        inputs = []
        filters = []
        for i,name in enumerate(names):
            inputs += ['-i', str(ROOT / f'{name}.mp4')]
            label = f'a{i}'
            labels.append(f'[{label}]')
            filters.append(f"[{i}:v]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='LoRA {strengths[name]:g}':x=15:y=15:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.7[{label}]")
        filters.append(''.join(labels)+f'hstack=inputs={len(names)}[v]')
        subprocess.run(['ffmpeg','-v','error','-y']+inputs+['-filter_complex',';'.join(filters),'-map','[v]','-an','-c:v','libx264','-crf','18',str(ROOT / f'{group}_comparison.mp4')], check=True)
    artifacts = {'integrity':'integrity.json'}
    for group,_ in groups:
        artifacts[group+'_comparison'] = group+'_comparison.mp4'
        artifacts[group+'_contact'] = group+'_contact.png'
    manifest.update(status='awaiting_visual_review', artifacts=artifacts)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
