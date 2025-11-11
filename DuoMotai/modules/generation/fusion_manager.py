# fusion_manager.py
"""
多模态融合模块
将文本回复与图片、参数表结合
"""
def fuse_multimodal_content(reply_text, image_path=None, table_data=None):
    """
    reply_text: LLM生成文本
    image_path: 商品图片路径
    table_data: 商品参数字典
    return: 结构化响应字典
    """
    response = {
        "reply_text": reply_text,
        "image": image_path,
        "table": table_data or {}
    }
    return response
