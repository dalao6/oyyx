#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调用VLM模型识别相似衣物模块
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入新创建的模块
from vision_processor import VisionProcessor
from vlm_handler import VLMHandler

class VLMInference:
    """
    VLM (Vision-Language Model) 推理类，用于识别相似衣物
    """
    
    def __init__(self, model_path="/mnt/data/modelscope_cache/hub/Qwen/Qwen2-VL-2B-Instruct"):
        """
        初始化VLM推理模块
        
        Args:
            model_path (str): VLM模型路径
        """
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        self.product_data = {}
        
        # 初始化新模块
        self.vision_processor = VisionProcessor()
        self.vlm_handler = VLMHandler(model_path)
        
        self.load_product_data()
        self.load_model()
        
    def load_product_data(self):
        """
        加载产品数据
        """
        try:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent
            specs_path = project_root / "DuoMotai" / "data" / "product_specs" / "nike_shirt.json"
            
            with open(specs_path, 'r', encoding='utf-8') as f:
                self.product_data = json.load(f)
            logging.info(f"成功加载 {len(self.product_data)} 个产品数据")
        except Exception as e:
            logging.error(f"加载产品数据失败: {e}")
            
    def load_model(self):
        """
        加载VLM模型
        """
        # 直接使用VLMHandler处理模型加载
        self.is_loaded = self.vlm_handler.is_loaded
        if self.is_loaded:
            logging.info("VLM推理模块初始化完成")
        else:
            logging.error("VLM推理模块初始化失败")
        
    def infer(self, image_data, query=None):
        """
        对图像进行推理，查找相似衣物
        
        Args:
            image_data: 输入的图像数据（OpenCV格式的帧）
            query (str, optional): 查询语句
            
        Returns:
            dict: 包含相似衣物信息的结果
        """
        try:
            if image_data is None:
                logging.warning("输入图像数据为空")
                return {
                    "status": "error",
                    "message": "输入图像数据为空"
                }
            
            # 使用视觉处理器找到最相似的商品
            product_name, similarity_score = self.vision_processor.find_most_similar(image_data)
            
            if product_name is None or similarity_score < 0.5:  # 设置相似度阈值
                logging.info("未找到足够相似的商品")
                # 作为备选方案，使用VLM文本识别
                vlm_result = self.vlm_handler.recognize_image(image_data)
                logging.info(f"VLM识别结果: {vlm_result}")
                
                # 尝试根据VLM结果匹配商品
                matched_product = self._match_product_by_vlm_result(vlm_result)
                if matched_product:
                    product_name = matched_product
                    similarity_score = 0.7  # 假定的相似度
                else:
                    return {
                        "status": "success",
                        "data": []
                    }
            
            # 获取产品详细信息
            product_info = self.vision_processor.get_product_info(product_name)
            if product_info is None:
                logging.error(f"无法获取产品信息: {product_name}")
                return {
                    "status": "error",
                    "message": f"无法获取产品信息: {product_name}"
                }
                
            # 添加相似度信息
            product_info["similarity"] = similarity_score
            
            result = {
                "status": "success",
                "data": [product_info]  # 只返回最相似的一个商品
            }
            
            logging.info(f"识别到商品: {product_name} (相似度: {similarity_score:.4f})")
            return result
            
        except Exception as e:
            logging.error(f"推理过程中发生错误: {e}")
            result = {
                "status": "error",
                "message": str(e)
            }
            return result
            
    def _match_product_by_vlm_result(self, vlm_result):
        """
        根据VLM识别结果匹配商品
        
        Args:
            vlm_result (str): VLM识别结果文本
            
        Returns:
            str or None: 匹配到的产品名称
        """
        if not vlm_result:
            return None
            
        # 简单的关键词匹配逻辑
        # 在实际应用中，这可以使用更复杂的NLP技术
        keywords = vlm_result.lower()
        
        # 遍历所有产品，寻找最佳匹配
        best_match = None
        best_score = 0
        
        for product_name in self.product_data.keys():
            # 计算匹配分数
            score = 0
            product_lower = product_name.lower()
            
            # 简单的关键词匹配
            if "红色" in keywords and "红色" in product_lower:
                score += 1
            if "蓝色" in keywords and "蓝色" in product_lower:
                score += 1
            if "绿色" in keywords and "绿色" in product_lower:
                score += 1
            if "白色" in keywords and "白色" in product_lower:
                score += 1
            if "黑色" in keywords and "黑色" in product_lower:
                score += 1
            if "黄色" in keywords and "黄色" in product_lower:
                score += 1
            if "灰色" in keywords and "灰色" in product_lower:
                score += 1
                
            if "短袖" in keywords and "短袖" in product_lower:
                score += 1
            if "长袖" in keywords and "长袖" in product_lower:
                score += 1
            if "长裤" in keywords and "长裤" in product_lower:
                score += 1
                
            if score > best_score:
                best_score = score
                best_match = product_name
                
        return best_match if best_score > 0 else None

if __name__ == "__main__":
    # 测试代码
    vlm = VLMInference()
    
    # 创建一个测试图像（纯黑色）
    import numpy as np
    test_frame = np.zeros((224, 224, 3), dtype=np.uint8)
    result = vlm.infer(test_frame)
    print(result)