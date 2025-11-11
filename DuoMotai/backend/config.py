import os

# ====== 根目录 ======
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ====== 模型路径 ======
ASR_MODEL_PATH = "/home/jiang/.cache/modelscope/hub/iic/SenseVoiceSmall"
LLM_MODEL_PATH = "/home/jiang/.cache/modelscope/hub/._____temp/Qwen/Qwen2-VL-2B-Instruct"
TTS_MODEL_PATH = os.path.join(PROJECT_ROOT, "models_local", "CosyVoice")
SENTENCE_BERT_PATH = os.path.join(PROJECT_ROOT, "models_local", "SentenceBERT")

# ====== 数据路径 ======
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
AUDIO_INPUT_DIR = os.path.join(DATA_DIR, "audio_input")
AUDIO_OUTPUT_DIR = os.path.join(DATA_DIR, "audio_output")
PRODUCT_IMAGE_DIR = os.path.join(DATA_DIR, "product_images")
PRODUCT_TEXT_DIR = os.path.join(DATA_DIR, "product_texts")
PRODUCT_VIDEO_DIR = os.path.join(DATA_DIR, "product_videos")
PRODUCT_SPEC_DIR = os.path.join(DATA_DIR, "product_specs")
LOG_DIR = os.path.join(DATA_DIR, "logs")

# ====== 系统参数 ======
DEVICE = "cuda"  # or "cpu"
LANGUAGE = "zh"
RETRIEVAL_TOP_K = 3

# ====== 语音输入录制参数 ======
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
RECORD_SECONDS = 5
INPUT_AUDIO_FILE = os.path.join(AUDIO_INPUT_DIR, "latest_input.wav")
OUTPUT_AUDIO_FILE = os.path.join(AUDIO_OUTPUT_DIR, "latest_reply.wav")

# ====== 初始化路径 ======
for d in [AUDIO_INPUT_DIR, AUDIO_OUTPUT_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)