# modules/asr/asr_service.py
import os
import torch
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class ASRService:
    def __init__(self,
                 model_name_or_path="damo/speech_funasr_asr_conformer_tiny",
                 cache_dir="/dev/nvme0n1p8/modelscope/funasr",
                 device="cuda" if torch.cuda.is_available() else "cpu"):
        """
        使用 ModelScope 官方 FunASR 模型进行语音识别。
        模型会自动下载到指定 cache_dir。
        """
        self.model_name_or_path = model_name_or_path
        self.cache_dir = cache_dir
        self.device = device

        os.makedirs(cache_dir, exist_ok=True)
        os.environ["MODELSCOPE_CACHE"] = cache_dir

        print(f"🖥️ 使用设备: {self.device}")
        print(f"📦 模型路径/名称: {self.model_name_or_path}")
        print(f"💾 缓存目录: {self.cache_dir}")

        # 初始化 ASR pipeline
        self.asr_pipeline = pipeline(
            task=Tasks.auto_speech_recognition,
            model=self.model_name_or_path,
            device=self.device,
            cache_dir=self.cache_dir
        )

    def transcribe(self, audio_path: str) -> str:
        """对音频文件进行识别"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        print(f"🎧 正在识别音频: {audio_path}")
        result = self.asr_pipeline(audio_in=audio_path)
        text = result.get("text", "")
        print(f"📝 识别结果: {text}")
        return text


