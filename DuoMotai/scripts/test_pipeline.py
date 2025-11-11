import os
from modules.asr.asr_service import ASRService
from modules.llm.llm_service import LLMService
from modules.retrieval.product_manager import ProductManager
from modules.vision.vision_display import VisionDisplay
from modules.tts.tts_service import TTSService
from backend.utils_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("=== 启动 DuoMotai 语音多模态测试 ===")

    # 模型路径（直接使用本地缓存）
    asr_model = os.path.expanduser("~/.cache/modelscope/hub/iic/SenseVoiceSmall")
    llm_model = "/home/jiang/.cache/modelscope/hub/Qwen/Qwen2.5-1.5B-Instruct"
    tts_model = os.path.expanduser("~/.cache/modelscope/hub/iic/CosyVoice")

    # 模块初始化
    asr = ASRService(asr_model)
    llm = LLMService(llm_model)
    tts = TTSService(tts_model)
    # 使用基于__file__的绝对路径
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data/product_images")
    spec_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data/product_specs")
    retriever = ProductManager(image_dir=image_dir, spec_dir=spec_dir)
    vision = VisionDisplay()

    # Step 1: 语音输入转文本
    audio_input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data/audio_input/query.wav")
    user_text = asr.transcribe(audio_input)
    print(f"识别结果：{user_text}")

    # Step 2: LLM 生成意图与回复
    reply = llm.generate_response(user_text)
    print(f"Qwen 回复：{reply}")

    # Step 3: 检索并显示图片
    product_name = retriever.find_best_match(user_text)
    if product_name:
        vision.display_product(product_name)

    # Step 4: 回复语音播报
    audio_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data/audio_output/reply.wav")
    tts.synthesize(reply, audio_output)

    logger.info("=== DuoMotai 测试结束 ===")