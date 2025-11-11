# prompt_templates.py
"""
LLM prompt模板
"""
def get_prompt(user_text, emotion, intent_dict):
    """
    构建发送给Qwen2.5模型的Prompt
    """
    prompt = f"""
你是衣物客服机器人。
用户情绪: {emotion}
用户意图: {intent_dict}
用户说: {user_text}

请根据用户意图生成适合的中文回复文本，并推荐对应商品图片与参数表。
"""
    return prompt
