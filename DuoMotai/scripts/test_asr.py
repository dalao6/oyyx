import os
import uuid
import logging
import pyaudio
import numpy as np
import soundfile as sf
import sherpa_onnx
import uvicorn
from fastapi import FastAPI, File, UploadFile
from pathlib import Path
from threading import Thread
import time
import noisereduce as nr
import webrtcvad
import socket
from collections import deque

# =========================
# 日志配置
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# =========================
# 模型路径配置
# =========================
ASR_MODEL_PATH = "/mnt/data/modelscope_cache/hub/xiaowangge/sherpa-onnx-sense-voice-small"

# =========================
# 临时音频存放目录
# =========================
TMP_AUDIO_DIR = Path("./tmp_audio")
TMP_AUDIO_DIR.mkdir(exist_ok=True)

# =========================
# ASR 模型类
# =========================
class STTModel:
    """离线语音识别模型"""
    def __init__(self, model_path: str, sample_rate: int = 16000, num_threads: int = 6):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.num_threads = num_threads
        self.recognizer = None

    def load_model(self):
        model_file = os.path.join(self.model_path, "model.onnx")
        token_file = os.path.join(self.model_path, "tokens.txt")
        if not os.path.exists(model_file) or not os.path.exists(token_file):
            raise FileNotFoundError("模型文件或 tokens.txt 不存在，请检查路径")
        self.recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=model_file,
            tokens=token_file,
            num_threads=self.num_threads,
            sample_rate=self.sample_rate,
            use_itn=True,
            language="auto",
            provider="cpu"
        )
        logger.info(f"✅ ASR model loaded: {model_file}")

    def transcribe(self, audio_data: np.ndarray) -> str:
        if self.recognizer is None:
            raise RuntimeError("Model not loaded")
        stream = self.recognizer.create_stream()
        stream.accept_waveform(self.sample_rate, audio_data)
        self.recognizer.decode_stream(stream)
        return stream.result.text

# =========================
# FastAPI 初始化
# =========================
app = FastAPI(title="Offline ASR Service")
stt_model = STTModel(ASR_MODEL_PATH)
stt_model.load_model()

@app.post("/v1/stt")
async def speech_to_text(file: UploadFile = File(...)):
    tmp_file_path = TMP_AUDIO_DIR / f"{uuid.uuid4()}{Path(file.filename).suffix}"
    try:
        with open(tmp_file_path, "wb") as f:
            f.write(await file.read())
        audio_data, sr = sf.read(tmp_file_path, dtype='int16')
        text = stt_model.transcribe(audio_data)
        return {"code": 200, "msg": "success", "data": {"text": text}}
    except Exception as e:
        logger.error(f"STT error: {e}")
        return {"code": 500, "msg": str(e), "data": None}
    finally:
        if tmp_file_path.exists():
            tmp_file_path.unlink()

# =========================
# VAD + 降噪 + 实时录音
# =========================
RATE = 16000
CHUNK = 1024
FRAME_MS = 20
FRAME_SIZE = int(RATE * FRAME_MS / 1000)
VAD_AGGRESSIVENESS = 2
vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

# 语音检测参数
SPEECH_WINDOW = deque(maxlen=50)  # 检测窗口（1秒左右）
SPEECH_THRESHOLD = 0.6            # 超过多少比例认为是语音
MAX_SILENCE_FRAMES = 50           # 连续静音多少帧后认为说话结束

def is_speech(frame_bytes):
    return vad.is_speech(frame_bytes, RATE)

def record_audio():
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    except Exception as e:
        logger.error(f"❌ 无法打开麦克风: {e}")
        return

    logger.info("🎙️ 开始录音 (Ctrl+C 停止)...")

    frames = []
    silence_counter = 0
    in_speech = False

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            np_data = np.frombuffer(data, dtype=np.int16)

            # 分帧检测
            for i in range(0, len(np_data), FRAME_SIZE):
                frame = np_data[i:i + FRAME_SIZE]
                if len(frame) < FRAME_SIZE:
                    continue
                frame_bytes = frame.tobytes()
                speech_flag = is_speech(frame_bytes)
                SPEECH_WINDOW.append(1 if speech_flag else 0)

                if np.mean(SPEECH_WINDOW) > SPEECH_THRESHOLD:
                    if not in_speech:
                        logger.info("🎤 检测到语音开始")
                        in_speech = True
                        frames = []
                    frames.append(frame)
                    silence_counter = 0
                elif in_speech:
                    silence_counter += 1
                    frames.append(frame)
                    if silence_counter > MAX_SILENCE_FRAMES:
                        logger.info("🛑 检测到语音结束，开始识别...")
                        audio_chunk = np.concatenate(frames)

                        # 降噪
                        enhanced = nr.reduce_noise(y=audio_chunk.astype(np.float32), sr=RATE)
                        enhanced = enhanced.astype(np.int16)

                        # ASR
                        try:
                            text = stt_model.transcribe(enhanced)
                            if text.strip():
                                logger.info(f"🧠 识别结果: {text}")
                            else:
                                logger.info("⚠️ 未识别到有效语音")
                        except Exception as e:
                            logger.error(f"ASR error: {e}")

                        in_speech = False
                        silence_counter = 0
                        frames = []
            time.sleep(0.01)
    except KeyboardInterrupt:
        logger.info("🛑 停止录音")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# =========================
# 自动端口选择
# =========================
def get_free_port(default=7998):
    s = socket.socket()
    try:
        s.bind(("", default))
        port = s.getsockname()[1]
        return port
    except OSError:
        s.bind(("", 0))
        return s.getsockname()[1]
    finally:
        s.close()

def start_api():
    port = get_free_port()
    logger.info(f"🚀 FastAPI 服务启动: http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

# =========================
# 主程序入口
# =========================
if __name__ == "__main__":
    Thread(target=record_audio, daemon=True).start()
    start_api()
