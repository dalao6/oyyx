# emotion_recognition.py
"""
情绪识别模块
示例仅做演示，可替换为Hugging Face模型
"""
def recognize_emotion(text: str) -> str:
    """
    返回情绪标签: happy, angry, neutral, sad, question
    """
    if not text:
        return "neutral"
    text_lower = text.lower()
    if "不" in text or "差" in text or "气" in text:
        return "angry"
    elif "吗" in text or "？" in text:
        return "question"
    elif "喜欢" in text or "好" in text:
        return "happy"
    else:
        return "neutral"
