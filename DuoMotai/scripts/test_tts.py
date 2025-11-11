from modules.tts.tts_service import TTSService

if __name__ == "__main__":
    tts = TTSService(model_dir="/home/jiang/.cache/modelscope/hub/iic/CosyVoice")
    text = "你好，这是一条来自多模态客服系统的语音测试。"
    output_path = "data/audio_output/test_tts.wav"

    print(">>> 正在合成语音...")
    tts.synthesize(text, output_path)
    print(f"TTS 完成！已保存到: {output_path}")
