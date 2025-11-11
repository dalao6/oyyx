import os
from backend.config import *
from utils_logger import setup_logger

# 导入模块功能
from modules.asr.asr_service import ASRService
from modules.llm.llm_service import LLMService
from modules.retrieval.product_manager import ProductManager
from modules.tts.tts_service import TTSService

logger = setup_logger("PipelineManager")

class PipelineManager:
    """
    主控制流水线：语音识别 → 语义理解 → 检索 → 回复生成 → 语音合成
    """
    def __init__(self):
        logger.info("🚀 初始化语音客服流水线中...")

        # 初始化各模块
        self.asr = ASRService(model_path=ASR_MODEL_PATH)
        self.llm = LLMService(model_path=LLM_MODEL_PATH)
        self.retrieval = ProductManager(
            image_dir=PRODUCT_IMAGE_DIR,
            text_dir=PRODUCT_TEXT_DIR,
            spec_dir=PRODUCT_SPEC_DIR
        )
        self.tts = TTSService(model_path=TTS_MODEL_PATH)

        logger.info("✅ 流水线模块加载完成。")

    # ------------------------------
    # Step 1: 语音识别
    # ------------------------------
    def run_asr(self):
        logger.info("🎙️ 开始录音与识别语音...")
        text = self.asr.record_and_transcribe(INPUT_AUDIO_FILE)
        if not text:
            logger.warning("⚠️ 语音识别为空。")
        return text

    # ------------------------------
    # Step 2: LLM语义理解 + 检索
    # ------------------------------
    def run_llm(self, user_text):
        logger.info("🧠 进入语义理解与商品检索流程...")
        intent, reply_text = self.llm.analyze_intent_and_reply(user_text)

        # 根据意图从商品库中检索
        product_info = self.retrieval.search_product(intent)
        if product_info:
            logger.info(f"🔍 检索到相关商品: {product_info.get('name', '未知')}")
        else:
            logger.warning("未检索到相关商品。")

        return reply_text, product_info

    # ------------------------------
    # Step 3: 文本转语音
    # ------------------------------
    def run_tts(self, reply_text):
        if not reply_text:
            logger.warning("⚠️ 没有回复文本，跳过TTS。")
            return
        logger.info("🔊 开始语音合成...")
        self.tts.text_to_speech(reply_text, OUTPUT_AUDIO_FILE)
        logger.info("🎧 播放语音回复完成。")
