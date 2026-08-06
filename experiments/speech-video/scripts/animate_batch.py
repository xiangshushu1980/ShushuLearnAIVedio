#!/usr/bin/env python3
"""批量动画：读 scenes_v3.json + motion_map.json，对每帧跑 Wan2.2 I2V Lightning。
用法: python3 animate_batch.py [--w 832] [--h 480] [--len 73] [--seed BASE]
"""
import json, sys, time, argparse, os, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("af", os.path.join(os.path.dirname(os.path.abspath(__file__)),"animate_frame.py"))
af = importlib.util.module_from_spec(spec); spec.loader.exec_module(af)

API="http://127.0.0.1:8188"
IMG="/home/sean/projects/ComfyUI/output/img_debate4"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--w",type=int,default=832); ap.add_argument("--h",type=int,default=480)
    ap.add_argument("--len",type=int,default=73); ap.add_argument("--seed",type=int,default=20260801); ap.add_argument("--limit",type=int,default=0)
    ap.add_argument("--prefix",default="debate_anim"); ap.add_argument("--only",default="")
    args=ap.parse_args()
    scenes=json.load(open("scenes_v3.json")); motion=json.load(open("motion_map.json"))
    # 排队
    pids={}
    for i,s in enumerate(scenes):
        fid=s["id"]
        if args.only and fid not in args.only.split(","): continue
        if args.limit and i>=args.limit: break
        img=f"{IMG}/{fid}_00001_.png"
        if not os.path.exists(img): print("跳过缺图",fid); continue
        img_name=af.upload(img)
        wf=af.build_wf(img_name, motion[fid], args.w,args.h,args.len, args.seed+i, f"{args.prefix}/{fid}")
        req=urllib.request.Request(f"{API}/prompt", data=json.dumps({"prompt":wf}).encode(), headers={"Content-Type":"application/json"})
        pid=json.loads(urllib.request.urlopen(req).read())["prompt_id"]
        pids[fid]=pid; print(f"enqueued {fid} {pid}")
    print("已入队", len(pids), "帧，等待生成...")
    # 等待所有完成
    t0=time.time()
    while pids:
        time.sleep(10)
        done=[f for f,p in pids.items() if f in json.loads(urllib.request.urlopen(f"{API}/history/{p}").read())]
        for f in done: pids.pop(f)
        if time.time()-t0>7200: print("超时"); break
    print("全部完成，用时", round(time.time()-t0,1),"s")

if __name__=="__main__":
    main()
