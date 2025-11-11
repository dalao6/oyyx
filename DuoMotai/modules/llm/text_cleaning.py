# text_cleaning.py
import re
import jieba

STOP_WORDS = set(["的", "啊", "嗯", "呢", "吧"])  # 简单停用词示例

def clean_text(text: str) -> str:
    """
    文本清洗：去掉语气词、噪声、重复空格
    """
    if not text:
        return ""
    # 去掉非文字字符
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", "", text)
    # jieba分词去停用词
    words = [w for w in jieba.lcut(text) if w not in STOP_WORDS]
    cleaned = "".join(words)
    return cleaned
