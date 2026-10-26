from __future__ import annotations

import base64
import io
import json
import math
import os
import re
import uuid
import wave
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import torch


PROVIDERS = ["BytePlus Seed Speech", "Volcengine Doubao Voice"]
API_CONFIG = {
    "BytePlus Seed Speech": {
        "url": "https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/create",
        "key_name": "BYTEPLUS_SEED_SPEECH_API_KEY",
    },
    "Volcengine Doubao Voice": {
        "url": "https://openspeech.bytedance.com/api/v3/tts/create",
        "key_name": "VOLCENGINE_DOUBAO_VOICE_API_KEY",
    },
}
SAMPLE_RATES = ["8000", "16000", "24000", "32000", "40000", "44100", "48000"]
BYTEPLUS_SAMPLE_RATES = {8000, 16000, 24000, 32000, 44100, 48000}
VOLCENGINE_SAMPLE_RATES = {8000, 16000, 24000, 32000, 40000, 44100, 48000}
FORMATS = ["wav", "mp3", "ogg_opus", "pcm"]
MODES = ["text only", "audio reference", "image reference", "preset voice"]
IMAGE_MIN_PIXELS = 160_000
IMAGE_MAX_PIXELS = 2048 * 2048


def _read_key(key_name: str) -> str:
    value = os.environ.get(key_name, "").strip()
    if value:
        return value
    user_dir = os.environ.get("COMFYUI_USER_DIR", "").strip()
    if not user_dir:
        try:
            import folder_paths

            user_dir = folder_paths.get_user_directory()
        except (ImportError, AttributeError):
            user_dir = "/home/sean/projects/ComfyUI/user"
    env_file = Path(user_dir) / ".env"
    if not env_file.is_file():
        return ""
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() == key_name:
            return value.strip().strip("'\"")
    return ""


def _audio_to_wav(audio: dict) -> bytes:
    if not isinstance(audio, dict) or not isinstance(audio.get("waveform"), torch.Tensor):
        raise ValueError("输入音频必须是 ComfyUI AUDIO 数据")
    waveform = audio["waveform"].detach().cpu().float()
    if waveform.ndim == 3:
        waveform = waveform[0]
    if waveform.ndim != 2:
        raise ValueError("无法识别输入音频的波形维度")
    rate = int(audio.get("sample_rate", audio.get("sampler_rate", 0)))
    if rate <= 0 or waveform.shape[-1] == 0:
        raise ValueError("输入音频缺少有效采样率或采样数据")
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if waveform.shape[-1] / rate > 30:
        raise ValueError("Seed Audio 参考音频最长 30 秒")
    pcm = (waveform.clamp(-1, 1).numpy().T * 32767).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm.tobytes())
    data = buffer.getvalue()
    if len(data) > 10 * 1024 * 1024:
        raise ValueError("Seed Audio 单条参考音频不能超过 10 MB")
    return data


def _image_to_jpeg_b64(image) -> str:
    from PIL import Image

    if not isinstance(image, torch.Tensor):
        raise ValueError("参考图像必须是 ComfyUI IMAGE")
    if image.ndim == 3:
        image = image.unsqueeze(0)
    elif image.ndim == 4:
        image = image[:1]
    else:
        raise ValueError("无法识别参考图像的维度")
    height, width = int(image.shape[1]), int(image.shape[2])
    area = width * height
    if not IMAGE_MIN_PIXELS <= area <= IMAGE_MAX_PIXELS:
        scale = math.sqrt((IMAGE_MIN_PIXELS if area < IMAGE_MIN_PIXELS else IMAGE_MAX_PIXELS) / area)
        if area < IMAGE_MIN_PIXELS:
            new_width, new_height, method = math.ceil(width * scale), math.ceil(height * scale), "lanczos"
        else:
            new_width, new_height, method = max(1, int(width * scale)), max(1, int(height * scale)), "area"
        import comfy.utils

        image = comfy.utils.common_upscale(
            image.movedim(-1, 1), new_width, new_height, method, "disabled"
        ).movedim(1, -1).clamp(0, 1)
    pixels = image[0].detach().cpu().float().clamp(0, 1).numpy()
    buffer = io.BytesIO()
    Image.fromarray((pixels * 255).astype(np.uint8)).convert("RGB").save(
        buffer, format="JPEG", quality=90
    )
    data = buffer.getvalue()
    if len(data) > 10 * 1024 * 1024:
        raise ValueError("Seed Audio 参考图不能超过 10 MB")
    return base64.b64encode(data).decode("ascii")


def _decode_audio(data: bytes, audio_format: str, sample_rate: int) -> dict:
    if audio_format == "pcm":
        samples = np.frombuffer(data[: len(data) // 2 * 2], dtype="<i2").astype(np.float32) / 32768
        waveform = torch.from_numpy(samples.copy())[None, None, :]
        return {"waveform": waveform, "sample_rate": sample_rate}
    try:
        import av
    except ImportError as exc:
        raise RuntimeError("当前 ComfyUI 环境缺少 PyAV，无法解码 Seed Audio 返回音频") from exc
    chunks = []
    with av.open(io.BytesIO(data)) as container:
        stream = container.streams.audio[0]
        for frame in container.decode(stream):
            array = frame.to_ndarray()
            channels = len(frame.layout.channels)
            if not frame.format.is_planar:
                array = array.reshape(-1, channels).T
            fmt = frame.format.name.rstrip("p")
            scale = {"u8": 128, "s16": 32768, "s32": 2147483648}.get(fmt, 1)
            if fmt == "u8":
                array = (array.astype(np.float32) - 128) / 128
            else:
                array = array.astype(np.float32) / scale
            chunks.append(array)
        if not chunks:
            raise ValueError("Seed Speech 响应中没有可解码的音频帧")
        audio = np.concatenate(chunks, axis=1).copy()
        return {"waveform": torch.from_numpy(audio)[None], "sample_rate": int(stream.rate)}


def _subtitle_to_srt(subtitle: dict) -> str:
    if not isinstance(subtitle, dict):
        return ""
    sentences = subtitle.get("sentences") or subtitle.get("utterances") or []
    blocks = []

    def time_ms(item, ms_key, seconds_key):
        value = item.get(ms_key)
        if isinstance(value, (int, float)) and value >= 0:
            return int(value)
        value = item.get(seconds_key)
        if isinstance(value, (int, float)) and value >= 0:
            return int(round(value * 1000))
        return None

    def srt_time(value):
        hours, remainder = divmod(value, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        seconds, milliseconds = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    for sentence in sentences:
        if not isinstance(sentence, dict):
            continue
        words = [word for word in sentence.get("words", []) if isinstance(word, dict)]
        text = str(sentence.get("text") or "".join(
            str(word.get("word") or word.get("text") or "") for word in words
        )).strip()
        start = time_ms(sentence, "start_time", "startTime")
        end = time_ms(sentence, "end_time", "endTime")
        if start is None and words:
            start = time_ms(words[0], "start_time", "startTime")
        if end is None and words:
            end = time_ms(words[-1], "end_time", "endTime")
        if not text or start is None or end is None:
            continue
        text = text.replace("\r", " ").replace("\n", " ")
        blocks.append(
            f"{len(blocks) + 1}\n{srt_time(start)} --> {srt_time(max(start, end))}\n{text}"
        )
    return "\n\n".join(blocks)


class SeedAudioBytePlus:
    """Generate one Seed Audio 1.0 clip via the first-party Seed Speech API."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_prompt": (
                    "STRING",
                    {"multiline": True, "default": "", "tooltip": "描述声音、表演、环境、音乐与台词；最多 3000 字符。"},
                ),
                "provider": (
                    PROVIDERS,
                    {"default": "Volcengine Doubao Voice", "tooltip": "选择 API 服务与对应控制台签发的独立 API Key。"},
                ),
                "reference_mode": (
                    MODES,
                    {"default": "text only", "tooltip": "选择纯文本、音频参考、图像参考或预设音色；音频和图像参考不能混用。"},
                ),
                "sample_rate": (SAMPLE_RATES, {"default": "24000"}),
                "speech_rate": ("INT", {"default": 0, "min": -50, "max": 100}),
                "loudness_rate": ("INT", {"default": 0, "min": -50, "max": 100}),
                "pitch_rate": ("INT", {"default": 0, "min": -12, "max": 12}),
                "audio_format": (FORMATS, {"default": "wav"}),
                "enable_subtitle": ("BOOLEAN", {"default": False}),
                "audible_watermark": ("BOOLEAN", {"default": False}),
                "metadata_watermark": ("BOOLEAN", {"default": False}),
                "content_producer": ("STRING", {"default": ""}),
                "produce_id": ("STRING", {"default": ""}),
                "content_propagator": ("STRING", {"default": ""}),
                "propagate_id": ("STRING", {"default": ""}),
                "ref_audio_1_source": (
                    "STRING", {"default": "", "tooltip": "第 1 个音频参考：TTS 2.0/克隆 speaker ID，或 http(s) 音频 URL。"}
                ),
                "ref_audio_2_source": (
                    "STRING", {"default": "", "tooltip": "第 2 个音频参考：TTS 2.0/克隆 speaker ID，或 http(s) 音频 URL。"}
                ),
                "ref_audio_3_source": (
                    "STRING", {"default": "", "tooltip": "第 3 个音频参考：TTS 2.0/克隆 speaker ID，或 http(s) 音频 URL。"}
                ),
                "ref_image_url": (
                    "STRING", {"default": "", "tooltip": "图像参考的公开 HTTPS URL；与 reference_image 二选一。"}
                ),
                "preset_voice": (
                    "STRING", {"default": "", "tooltip": "预设模式使用 TTS 2.0 speaker ID 或克隆音色 ID，例如 en_female_stokie_uranus_bigtts。"}
                ),
                "generation_count": ("INT", {"default": 1, "min": 1, "max": 16}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 2147483647}),
            },
            "optional": {
                "reference_audio_1": ("AUDIO", {"tooltip": "音频参考，最长 30 秒、10 MB；prompt 中按槽位标记 @Audio1。"}),
                "reference_audio_2": ("AUDIO", {"tooltip": "音频参考，最长 30 秒、10 MB；prompt 中按槽位标记 @Audio2。"}),
                "reference_audio_3": ("AUDIO", {"tooltip": "音频参考，最长 30 秒、10 MB；prompt 中按槽位标记 @Audio3。"}),
                "reference_image": ("IMAGE", {"tooltip": "单张角色参考图；不可与音频参考混用。"}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING", "STRING", "FLOAT", "FLOAT", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "audio", "subtitle_json", "srt", "duration", "billable_duration", "url", "request_id", "provider_log_id"
    )
    OUTPUT_IS_LIST = (True, True, True, True, True, True, True, True)
    FUNCTION = "generate"
    CATEGORY = "audio/Seed Audio 1.0"
    DESCRIPTION = "项目自有 Seed Audio 1.0 节点；每次执行都会产生 API 请求和费用。"

    def generate(
        self, text_prompt, provider, reference_mode, sample_rate, speech_rate, loudness_rate,
        pitch_rate, audio_format, enable_subtitle, audible_watermark,
        metadata_watermark, content_producer="", produce_id="", content_propagator="",
        propagate_id="", generation_count=1, seed=42, reference_audio_1=None,
        reference_audio_2=None, reference_audio_3=None, ref_audio_1_source="",
        ref_audio_2_source="", ref_audio_3_source="", reference_image=None,
        ref_image_url="", preset_voice="",
    ):
        prompt = (text_prompt or "").strip()
        if not prompt or len(prompt) > 3000:
            raise ValueError("text_prompt 必须为 1–3000 个字符")
        provider_config = API_CONFIG.get(provider)
        if provider_config is None:
            raise ValueError(f"不支持的 API 服务：{provider}")
        if audio_format not in FORMATS:
            raise ValueError(f"不支持的音频格式：{audio_format}")
        rate = int(sample_rate)
        if provider == "Volcengine Doubao Voice":
            if audio_format == "ogg_opus" and rate != 48000:
                raise ValueError("火山引擎豆包语音的 ogg_opus 输出只支持 48000 Hz")
            allowed_rates = VOLCENGINE_SAMPLE_RATES
            if audio_format == "mp3":
                allowed_rates = allowed_rates - {40000}
        else:
            allowed_rates = BYTEPLUS_SAMPLE_RATES
        if rate not in allowed_rates:
            raise ValueError(f"{provider} 不支持采样率 {rate} Hz")
        tags = [int(value) for value in re.findall(r"@Audio(\d+)", prompt, re.IGNORECASE)]
        if reference_mode in ("text only", "image reference", "preset voice") and tags:
            raise ValueError(f"{reference_mode} 模式不支持 @AudioN 标签")
        connected_audio = [reference_audio_1, reference_audio_2, reference_audio_3]
        audio_sources = [ref_audio_1_source.strip(), ref_audio_2_source.strip(), ref_audio_3_source.strip()]
        if reference_mode != "audio reference" and (any(a is not None for a in connected_audio) or any(audio_sources)):
            raise ValueError("参考音频输入只能用于 audio reference 模式")
        if reference_mode != "preset voice" and preset_voice.strip():
            raise ValueError("preset_voice 只能用于 preset voice 模式")
        if reference_mode == "image reference" and reference_image is None and not ref_image_url.strip():
            raise ValueError("image reference 模式需要 reference_image")
        if reference_mode != "image reference" and (reference_image is not None or ref_image_url.strip()):
            raise ValueError("reference_image 只能用于 image reference 模式")

        references = []
        if reference_mode == "audio reference":
            slots = connected_audio
            sources = audio_sources
            if not any(audio is not None or source for audio, source in zip(slots, sources)):
                raise ValueError("audio reference 模式需要连接音频或填写 speaker_id")
            for index, (audio, source) in enumerate(zip(slots, sources), 1):
                if audio is not None and source:
                    raise ValueError(f"第 {index} 个音频槽不能同时连接音频并填写 source")
                if audio is not None:
                    references.append({"audio_data": base64.b64encode(_audio_to_wav(audio)).decode("ascii")})
                elif source:
                    if "://" in source and not source.startswith(("https://", "http://")):
                        raise ValueError(f"第 {index} 个 source 只接受 HTTP(S) URL 或 speaker ID")
                    references.append({"audio_url": source} if source.startswith(("https://", "http://")) else {"speaker": source})
                elif any(slots[index:]) or any(sources[index:]):
                    raise ValueError("参考音频槽需从第 1 槽开始连续填写")
            if tags and max(tags) > len(references):
                raise ValueError("prompt 中 @AudioN 标签超出已连接的参考音频数量")
        elif reference_mode == "image reference":
            if reference_image is not None and ref_image_url.strip():
                raise ValueError("reference_image 与 ref_image_url 只能使用一个")
            if ref_image_url.strip() and not ref_image_url.strip().startswith("https://"):
                raise ValueError("ref_image_url 必须是公开 HTTPS 链接")
            references = ([{"image_data": _image_to_jpeg_b64(reference_image)}]
                          if reference_image is not None else [{"image_url": ref_image_url.strip()}])
        elif reference_mode == "preset voice":
            if not preset_voice.strip():
                raise ValueError("preset voice 模式需在 preset_voice 填入 Seed Speech 预设音色 ID")
            references = [{"speaker": preset_voice.strip()}]
        elif reference_mode != "text only":
            raise ValueError(f"不支持的 reference_mode：{reference_mode}")

        key_name = provider_config["key_name"]
        key = _read_key(key_name)
        if not key:
            raise RuntimeError(
                f"未配置 {key_name}。请在 ComfyUI user/.env 中只配置所选服务对应的 API Key；"
                "ModelArk API Key 不适用。"
            )
        count = int(generation_count)
        if not 1 <= count <= 16:
            raise ValueError("generation_count 必须介于 1 和 16；每个 take 都是单独计费请求")
        outputs = [[], [], [], [], [], [], [], []]
        for _ in range(count):
            request_id = str(uuid.uuid4())
            body = {
                "model": "seed-audio-1.0", "text_prompt": prompt,
                "audio_config": {
                    "format": audio_format, "sample_rate": int(sample_rate),
                    "speech_rate": int(speech_rate), "loudness_rate": int(loudness_rate),
                    "pitch_rate": int(pitch_rate), "enable_subtitle": bool(enable_subtitle),
                },
            }
            if references:
                body["references"] = references
            watermark = {}
            if audible_watermark:
                watermark["aigc_watermark"] = True
            if metadata_watermark:
                metadata = {"enable": True}
                for name, value in (
                    ("content_producer", content_producer), ("produce_id", produce_id),
                    ("content_propagator", content_propagator), ("propagate_id", propagate_id),
                ):
                    if value.strip():
                        metadata[name] = value.strip()
                watermark["aigc_metadata"] = metadata
            if watermark:
                body["watermark"] = watermark

            req = Request(
                provider_config["url"],
                data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                headers={"X-Api-Key": key, "X-Api-Request-Id": request_id, "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlopen(req, timeout=180) as response:
                    result = json.loads(response.read())
                    provider_log_id = response.headers.get("X-Tt-Logid", "")
            except HTTPError as exc:
                detail = exc.read(1000).decode("utf-8", "replace").replace(key, "[redacted]")
                raise RuntimeError(f"Seed Speech HTTP {exc.code}: {detail}") from exc
            except (URLError, TimeoutError) as exc:
                raise RuntimeError(f"Seed Speech 请求失败；request_id={request_id}；{exc}") from exc
            if not isinstance(result, dict):
                raise RuntimeError(f"Seed Speech 返回非 JSON 对象；request_id={request_id}")
            if result.get("code") not in (None, 0, "0", 20000000, "20000000"):
                message = str(result.get("message", "")).replace(key, "[redacted]")
                raise RuntimeError(
                    f"Seed Speech 返回错误 code={result.get('code')} message={message}; "
                    f"request_id={request_id}"
                )
            audio_b64 = result.get("audio")
            if audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
            elif isinstance(result.get("url"), str) and result["url"].startswith("https://"):
                with urlopen(result["url"], timeout=60) as response:
                    audio_bytes = response.read(32 * 1024 * 1024 + 1)
                if len(audio_bytes) > 32 * 1024 * 1024:
                    raise RuntimeError("Seed Speech 返回音频超过 32 MB")
            else:
                raise RuntimeError(f"Seed Speech 响应缺少音频数据；request_id={request_id}")
            output_audio = _decode_audio(audio_bytes, audio_format, int(sample_rate))
            seconds = float(result.get("duration") or 0)
            if not seconds:
                seconds = output_audio["waveform"].shape[-1] / output_audio["sample_rate"]
            billable_seconds = float(result.get("original_duration") or seconds)
            outputs[0].append(output_audio)
            subtitle = result.get("subtitle") or {}
            outputs[1].append(json.dumps(subtitle, ensure_ascii=False))
            outputs[2].append(_subtitle_to_srt(subtitle))
            outputs[3].append(seconds)
            outputs[4].append(billable_seconds)
            outputs[5].append(str(result.get("url") or ""))
            outputs[6].append(request_id)
            outputs[7].append(provider_log_id)
        return tuple(outputs)


NODE_CLASS_MAPPINGS = {"SeedAudioBytePlus": SeedAudioBytePlus}
NODE_DISPLAY_NAME_MAPPINGS = {"SeedAudioBytePlus": "Seed Audio 1.0 (项目自有)"}
