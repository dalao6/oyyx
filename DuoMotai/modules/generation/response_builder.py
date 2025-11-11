# response_builder.py
from .format_utils import format_reply_text
from .fusion_manager import fuse_multimodal_content

def build_response(llm_text, image_path=None, table_data=None):
    """
    构建最终回复，包括文本、图片和参数表
    """
    formatted_text = format_reply_text(llm_text)
    response = fuse_multimodal_content(formatted_text, image_path=image_path, table_data=table_data)
    return response

# 示例用法
if __name__ == "__main__":
    llm_text = "这款短袖采用纯棉材质，适合夏季穿着。"
    image_path = "/home/jiang/DuoMotai/data/product_images/shirt1.jpg"
    table_data = {"材质": "纯棉", "颜色": "蓝色", "尺码": "M/L/XL"}
    response = build_response(llm_text, image_path=image_path, table_data=table_data)
    print(response)
