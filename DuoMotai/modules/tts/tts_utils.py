# modules/tts/tts_utils.py
import io
import pyttsx3
from gtts import gTTS
from pydub import AudioSegment
from typing import Optional, List
import os

def synthesize_with_pyttsx3(text: str, voice: Optional[str] = None, rate: int = 180):
    """
    使用 pyttsx3 离线语音合成
    返回二进制音频数据（WAV）
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    if voice:
        engine.setProperty('voice', voice)

    buffer = io.BytesIO()
    engine.save_to_file(text, "temp_tts.wav")
    engine.runAndWait()
    with open("temp_tts.wav", "rb") as f:
        buffer.write(f.read())
    return buffer.getvalue()


def synthesize_with_gtts(text: str, output_path: str, lang: str = "zh-cn"):
    """
    使用 Google gTTS 在线语音合成
    """
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    print(f"[TTS] gTTS synthesis completed → {output_path}")


def save_audio(audio_data: bytes, output_path: str):
    """
    保存音频数据为文件
    """
    with open(output_path, "wb") as f:
        f.write(audio_data)


def list_voices() -> List[str]:
    """
    获取 pyttsx3 可用语音列表
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    return [v.id for v in voices]