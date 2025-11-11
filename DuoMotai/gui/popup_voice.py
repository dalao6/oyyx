# popup_voice.py
import pyttsx3
import threading

class VoicePlayer:
    def __init__(self, rate=150, volume=1.0, voice=None):
        """
        初始化语音播放器
        rate: 语速
        volume: 音量(0.0~1.0)
        voice: 选择语音id（None则使用默认）
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        if voice:
            self.engine.setProperty("voice", voice)

    def play_text(self, text):
        """播放文本"""
        def _play():
            self.engine.say(text)
            self.engine.runAndWait()
        # 在独立线程播放，避免阻塞主程序
        t = threading.Thread(target=_play)
        t.start()
        return t  # 返回线程对象，方便管理或等待播放完成

# 简单封装函数，直接调用即可
_voice_player = VoicePlayer()
def play_voice_popup(text):
    """
    弹窗播放语音
    text: 字符串
    """
    return _voice_player.play_text(text)
