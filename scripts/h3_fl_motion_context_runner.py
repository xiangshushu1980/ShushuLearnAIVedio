#!/usr/bin/env python3
"""FL2VA + NativeAudioLock + H3 Motion Context 两段链测试。"""
import json, os, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
OUT = "/home/sean/projects/ComfyUI/output"

def api(path, data=None):
    req = urllib.request.Request(HOST + path, data=json.dumps(data).encode() if data is not None else None,
        headers={"Content-Type": "application/json"} if data is not None else {})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)

def build(c):
    wf = {
      "1":{"class_type":"UNETLoader","inputs":{"unet_name":"minimax_h3_fl2va_pruned_int8_convrot.safetensors","weight_dtype":"default"}},
      "2":{"class_type":"CLIPLoader","inputs":{"clip_name":"qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors","type":"minimax","device":"default"}},
      "3":{"class_type":"VAELoader","inputs":{"vae_name":"minimax_h3_video_vae_fp16.safetensors"}},
      "4":{"class_type":"VAELoader","inputs":{"vae_name":"minimax_h3_audio_vae_fp32.safetensors"}},
      "6":{"class_type":"MiniMaxH3ImageToVideo","inputs":{"clip":["2",0],"vae":["3",0],"prompt":c.get("prompt", ""),"width":768,"height":448,"length":c["length"]}},
      "7":{"class_type":"KSamplerSelect","inputs":{"sampler_name":"euler"}},
      "8":{"class_type":"BasicScheduler","inputs":{"model":["1",0],"scheduler":"simple","steps":8,"denoise":1.0}},
      "10":{"class_type":"RandomNoise","inputs":{"noise_seed":c["seed"]}},
      "16":{"class_type":"LoadAudio","inputs":{"audio":c["audio"]}},
      "18":{"class_type":"MiniMaxH3PDDAccApply","inputs":{"model":["1",0],"pdd_file":"minimax_h3_fl2va_pdd_acc_8step_comfyui.safetensors","nfe":"8","lora_strength":1.0,"head_strength":1.0,"on_off_grid":"error"}},
      "17":{"class_type":"MiniMaxH3NativeAudioLock","inputs":{"model":["18",0],"av_latent":["6",1],"audio_vae":["4",0],"audio":["16",0]}},
      "9":{"class_type":"BasicGuider","inputs":{"model":["17",0],"conditioning":["6",0]}},
      "11":{"class_type":"SamplerCustomAdvanced","inputs":{"noise":["10",0],"guider":["9",0],"sampler":["7",0],"sigmas":["18",1],"latent_image":["17",1]}},
      "12":{"class_type":"VAEDecode","inputs":{"samples":["11",0],"vae":["3",0]}},
      "13":{"class_type":"VAEDecodeAudio","inputs":{"samples":["11",0],"vae":["4",0]}}
    }
    if c.get("first_frame", True):
        wf["5"]={"class_type":"LoadImage","inputs":{"image":c.get("image", "h3_avatar/anchor_host_krea_hands_4k_16x9.png")}}
        wf["6"]["inputs"]["first_frame"]=["5",0]
    if c.get("mc"):
        wf["19"]={"class_type":"MiniMaxH3MotionContextLoadLatent","inputs":{"latent_path":c["mc"]["latent_path"],"clip_index":1}}
        wf["20"]={"class_type":"MiniMaxH3MotionContext","inputs":{"conditioning":["6",0],"vae":["3",0],"latent":["17",1],"context_length":str(c.get("context_length",22)),"audio_context_length":24,"context_latent":["19",0]}}
        wf["9"]["inputs"]["conditioning"]=["20",0]
        if c.get("trim", True):
            wf["21"]={"class_type":"MiniMaxH3MotionContextTrim","inputs":{"images":["12",0],"trim_frames":c.get("trim_frames_override",["20",1]),"audio":["13",0],"fps":24.0,"match_tail":True}}
            wf["14"]={"class_type":"CreateVideo","inputs":{"images":["21",0],"fps":24,"audio":["21",1],"bit_depth":8}}
        else:
            wf["14"]={"class_type":"CreateVideo","inputs":{"images":["12",0],"fps":24,"audio":["13",0],"bit_depth":8}}
    else:
        wf["14"]={"class_type":"CreateVideo","inputs":{"images":["12",0],"fps":24,"audio":["13",0],"bit_depth":8}}
    wf["15"]={"class_type":"SaveVideo","inputs":{"video":["14",0],"filename_prefix":c["prefix"],"format":"mp4","codec":"auto"}}
    if c.get("save_latent"):
        wf["22"]={"class_type":"MiniMaxH3MotionContextSaveLatent","inputs":{"latent":["11",0],"filename_prefix":c["save_latent"]["latent_path"],"clip_index":1}}
    return wf

def wait(pid):
    t=time.time()
    while True:
        time.sleep(8)
        h=api("/history/"+pid)
        if pid not in h: continue
        e=h[pid]; st=e.get("status",{})
        if st.get("completed") or st.get("status_str")=="error":
            errs=[m[1].get("exception_message","") for m in st.get("messages",[]) if m[0]=="execution_error"]
            return round(time.time()-t), errs[0] if errs else None

def main():
    cases=json.load(open(sys.argv[1])); results=[]
    for c in cases:
        print("提交",c["name"],flush=True)
        try: pid=api("/prompt",{"prompt":build(c),"client_id":"h3-fl-mc"})["prompt_id"]
        except urllib.error.HTTPError as e:
            results.append({"name":c["name"],"error":e.read().decode()[:500]}); print("失败",results[-1],flush=True); continue
        sec,err=wait(pid); rec={"name":c["name"],"seconds":sec,"error":err,"prefix":c["prefix"]}; results.append(rec)
        print(c["name"],"❌" if err else "✅",sec,"s",err or "",flush=True)
    out=sys.argv[1]+".results.json"; json.dump(results,open(out,"w"),indent=2,ensure_ascii=False); print(out)

if __name__=="__main__": main()
