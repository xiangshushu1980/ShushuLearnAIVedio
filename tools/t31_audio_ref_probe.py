#!/usr/bin/env python3
"""Matched one-clip Ref2VA audio-reference probe for T31."""
import json, time, urllib.request

API = "http://127.0.0.1:8188"

def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def get(path):
    with urllib.request.urlopen(urllib.request.Request(API + path), timeout=30) as r:
        return json.load(r)

def main():
    clips = {"version":1,"clips":[{"id":"t31_audio_ref_20_probe","name":"T31 audio ref 20-step probe","prompt":"subject_definitions:\n<Picture 1> defines the exact identity, face, hairstyle, clothing and appearance of <Subject 1>.\n<Audio 1> provides speech timing and expressive rhythm.\n\n<Subject 1> is a photorealistic Mandarin-speaking presenter speaking naturally to camera in the same light-gray studio, with accurate mouth motion, stable identity and restrained gestures.","seed":71090801,"seed_mode":"fixed","duration":5.0,"validated":False,"color_adjustment":{"saturation":100,"contrast":100,"brightness":100}}]}
    wf = {
      "1":{"class_type":"UNETLoader","inputs":{"unet_name":"minimax_h3_ref2va_pruned_int8_convrot.safetensors","weight_dtype":"default"}},
      "2":{"class_type":"CLIPLoader","inputs":{"clip_name":"qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors","type":"minimax","device":"default"}},
      "3":{"class_type":"VAELoader","inputs":{"vae_name":"minimax_h3_video_vae_fp16.safetensors"}},
      "4":{"class_type":"VAELoader","inputs":{"vae_name":"minimax_h3_audio_vae_fp32.safetensors"}},
      "6":{"class_type":"LoadImage","inputs":{"image":"T31_audio_ref.png"}},
      "7":{"class_type":"LoadAudio","inputs":{"audio":"T31_audio_driver_20260907.wav"}},
      "8":{"class_type":"MiniMaxH3ReferencePackBridge","inputs":{"ref_1":["6",0]}},
      "101":{"class_type":"MiniMaxH3Extender","inputs":{"model":["1",0],"clip":["2",0],"vae":["3",0],"audio_vae":["4",0],"ref_audio_1":["7",0],"ref_pack":["8",0],"run_mode":"full_batch","width":768,"height":448,"ref_image_size":"match","steps":20,"sampler_name":"euler","scheduler":"simple","denoise":1.0,"context_length":"22","audio_context_length":24,"clips_json":json.dumps(clips,ensure_ascii=False),"resolution_mode":"manual","megapixels":0.4,"refs_json":json.dumps({"version":2,"refs":[None]*9}),"generation_mode":"ref2va"}},
      "10":{"class_type":"MiniMaxH3MotionContextDiskFinalDecode","inputs":{"cache":["101",0],"vae":["3",0],"audio_vae":["4",0],"fps":24.0,"filename_prefix":"t31_audio_ref_20_probe","output_directory":"/home/sean/projects/ComfyUI/output/video/T31","codec":"H.264","crf":17,"preset":"fast","audio_bitrate":"192k","autoplay":True}}
    }
    pid=post("/prompt",{"prompt":wf,"client_id":"T31-audio-ref-probe"})["prompt_id"]
    print(json.dumps({"prompt_id":pid,"status":"queued"}),flush=True)
    while True:
        time.sleep(5); h=get("/history/"+pid)
        if pid not in h: continue
        st=h[pid].get("status",{})
        if st.get("completed"):
            print(json.dumps({"prompt_id":pid,"status":"completed","outputs":h[pid].get("outputs",{})},ensure_ascii=False),flush=True); return
        if st.get("status_str")=="error" or any(m[0]=="execution_error" for m in st.get("messages",[])):
            print(json.dumps({"prompt_id":pid,"status":"error","details":st},ensure_ascii=False),flush=True); raise SystemExit(2)

if __name__=="__main__": main()
