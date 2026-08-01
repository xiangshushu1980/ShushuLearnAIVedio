#!/usr/bin/env python3
"""ComfyUI 远程服务调用示例 —— 你的软件可以直接使用的客户端。

用法:
    python3 comfy_client.py "your prompt here"
    python3 comfy_client.py --image my_image.jpg "prompt with image"

依赖: 仅标准库 + requests (pip install requests)
"""
import json
import sys
import time
import urllib.request
import urllib.parse
import argparse


class ComfyClient:
    """极简 ComfyUI API 客户端。"""

    def __init__(self, server="http://127.0.0.1:8188"):
        self.server = server

    def _post(self, path, data):
        req = urllib.request.Request(
            f"{self.server}{path}",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _get(self, path):
        with urllib.request.urlopen(f"{self.server}{path}") as resp:
            return json.loads(resp.read())

    def upload_image(self, image_path):
        """上传一张图片到 ComfyUI input 目录，返回文件名。"""
        import requests
        with open(image_path, "rb") as f:
            resp = requests.post(
                f"{self.server}/upload/image",
                files={"image": f},
                data={"overwrite": "true"},
            )
        return resp.json()["name"]

    def queue_workflow(self, workflow_api: dict) -> str:
        """提交工作流，返回 prompt_id。"""
        result = self._post("/prompt", {"prompt": workflow_api})
        return result["prompt_id"]

    def wait_for_result(self, prompt_id: str, timeout=3600) -> dict:
        """轮询等待任务完成，返回执行结果。"""
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(3)
            hist = self._get(f"/history/{prompt_id}")
            if prompt_id in hist:
                entry = hist[prompt_id]
                status = entry.get("status", {})
                if status.get("completed"):
                    return entry
                if status.get("status_str") == "error":
                    msgs = status.get("messages", [])
                    for m in msgs:
                        if m[0] == "execution_error":
                            raise RuntimeError(m[1].get("exception_message", "未知错误"))
        raise TimeoutError("任务超时")

    def get_output_urls(self, result: dict) -> list:
        """从结果中提取生成文件的 URL。"""
        urls = []
        for node_id, out in result.get("outputs", {}).items():
            for key in ("gifs", "videos", "images", "audio"):
                for item in out.get(key, []):
                    fname = item.get("filename")
                    subfolder = item.get("subfolder", "")
                    url = f"/view?filename={fname}&subfolder={subfolder}&type=output"
                    urls.append(f"{self.server}{url}")
        return urls


def build_wan_i2v_workflow(prompt: str, negative: str, image_name: str,
                           width=512, height=512, length=33, steps=20) -> dict:
    """构建一个 Wan2.1 I2V 工作流（与本地 workflows 目录一致）。"""
    return {
        "52": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "37": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors", "weight_dtype": "default"}},
        "38": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
        "39": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "49": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["38", 0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["38", 0]}},
        "51": {"class_type": "CLIPVisionEncode", "inputs": {
            "clip_vision": ["49", 0], "image": ["52", 0], "crop": "center"}},
        "50": {"class_type": "WanImageToVideo", "inputs": {
            "positive": ["6", 0], "negative": ["7", 0], "vae": ["39", 0],
            "width": width, "height": height, "length": length, "batch_size": 1,
            "clip_vision_output": ["51", 0], "start_image": ["52", 0]}},
        "54": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["37", 0], "shift": 8}},
        "3": {"class_type": "KSampler", "inputs": {
            "model": ["54", 0], "positive": ["50", 0], "negative": ["50", 1],
            "latent_image": ["50", 2], "seed": int(time.time()),
            "steps": steps, "cfg": 6, "sampler_name": "uni_pc",
            "scheduler": "simple", "denoise": 1}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["39", 0]}},
        "55": {"class_type": "CreateVideo", "inputs": {"images": ["8", 0], "fps": 16}},
        "56": {"class_type": "SaveVideo", "inputs": {
            "video": ["55", 0], "filename_prefix": "video/api", "format": "auto", "codec": "auto"}},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ComfyUI 远程调用示例")
    parser.add_argument("prompt", nargs="?", default="a cute anime girl with massive fennec ears and a big fluffy tail turning around")
    parser.add_argument("--image", help="起始图片路径（可选，默认用测试图）")
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--steps", type=int, default=20)
    args = parser.parse_args()

    client = ComfyClient(args.server)

    # 1. 准备起始图片
    image_name = "image_to_video_wan_start_image.png"
    if args.image:
        print(f"上传图片: {args.image}")
        image_name = client.upload_image(args.image)

    # 2. 构建工作流（可以动态改参数）
    negative = "色调艳丽，过曝，静态，细节模糊不清，字幕，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，畸形的"
    workflow = build_wan_i2v_workflow(args.prompt, negative, image_name, steps=args.steps)
    print(f"✅ 工作流已构建，提示词: {args.prompt[:50]}...")

    # 3. 提交
    pid = client.queue_workflow(workflow)
    print(f"✅ 任务已提交: {pid[:8]}...")

    # 4. 等待完成
    result = client.wait_for_result(pid)
    print("🎉 任务完成！")

    # 5. 获取输出
    urls = client.get_output_urls(result)
    for url in urls:
        print(f"  下载: {url}")
