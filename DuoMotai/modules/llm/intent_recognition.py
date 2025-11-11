# intent_recognition.py
"""
意图识别模块
可基于规则或LLM生成
"""
def recognize_intent(text: str) -> dict:
    """
    返回意图字典，例如:
    {'intent': 'buy', 'product_type': 'short_sleeve', 'color': 'blue'}
    """
    intent = {"intent": "unknown", "product_type": None, "color": None}

    text_lower = text.lower()
    if "短袖" in text_lower or "T恤" in text_lower:
        intent["product_type"] = "short_sleeve"
    elif "裤子" in text_lower:
        intent["product_type"] = "pants"

    if "蓝" in text_lower:
        intent["color"] = "blue"
    elif "红" in text_lower:
        intent["color"] = "red"

    if "买" in text_lower or "推荐" in text_lower:
        intent["intent"] = "buy"
    elif "尺码" in text_lower:
        intent["intent"] = "query_size"

    return intent
