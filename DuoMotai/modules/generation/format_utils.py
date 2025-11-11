# format_utils.py
def format_reply_text(text):
    """
    格式化 LLM 输出文本
    例如去掉多余空格、换行或标点
    """
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\n", " ")
    text = " ".join(text.split())  # 多空格转单空格
    return text
