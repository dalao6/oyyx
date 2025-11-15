#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高稳定 VLMInference
- 统一 embedding 匹配
- 多帧累积 3 连识别
- 高精准度衣物识别
"""

import os
import json
import logging
from pathlib import Path
from collections import deque
import numpy as np
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vlm_handler import VLMHandler  # 假设此类提供 get_image_embedding() 方法

class VLMInferenceStable:
    """
    VLM 推理类（稳定版本）
    """

    def __init__(self,
                 model_path="/mnt/data/modelscope_cache/hub/Qwen/Qwen2-VL-2B-Instruct",
                 similarity_threshold=0.85,
                 consecutive_frames=3):
        """
        初始化 VLMInferenceStable

        Args:
            model_path (str): VLM 模型路径
            similarity_threshold (float): 相似度阈值
            consecutive_frames (int): 连续帧触发次数
        """
        self.model_path = model_path
        self.similarity_threshold = similarity_threshold
        self.consecutive_frames = consecutive_frames

        self.vlm_handler = VLMHandler(model_path)
        self.is_loaded = self.vlm_handler.is_loaded

        self.product_data = {}       # {product_name: dict_info}
        self.product_embeddings = {} # {product_name: np.array}

        # 连续帧队列，保存最近 N 帧的识别结果
        self.recent_results = deque(maxlen=self.consecutive_frames)

        self.load_product_data()
        self.precompute_product_embeddings()

    def load_product_data(self):
        """
        加载商品数据 JSON
        """
        try:
            project_root = Path(__file__).parent.parent
            specs_path = project_root / "DuoMotai" / "data" / "product_specs" / "nike_shirt.json"
            with open(specs_path, 'r', encoding='utf-8') as f:
                self.product_data = json.load(f)
            logging.info(f"加载商品数据：{len(self.product_data)} 个")
        except Exception as e:
            logging.error(f"加载商品数据失败: {e}")

    def precompute_product_embeddings(self):
        """
        预计算每个商品的 embedding
        """
        try:
            project_root = Path(__file__).parent.parent
            images_path = project_root / "DuoMotai" / "data" / "product_images"
            
            for product_name, info in self.product_data.items():
                # 根据商品名称查找对应图片文件
                image_filename = f"{product_name}.jpg"
                image_path = images_path / image_filename
                
                # 如果没找到jpg格式，尝试png格式
                if not image_path.exists():
                    image_filename = f"{product_name}.png"
                    image_path = images_path / image_filename
                
                if image_path.exists():
                    embedding = self.vlm_handler.get_image_embedding(str(image_path))
                    self.product_embeddings[product_name] = embedding
                else:
                    logging.warning(f"未找到图片: {image_path}")
            logging.info("商品 embedding 预计算完成")
        except Exception as e:
            logging.error(f"商品 embedding 预计算失败: {e}")

    def infer(self, image_data):
        """
        对单帧图像推理
        Args:
            image_data: OpenCV BGR 图像
        Returns:
            dict: {status: success/error, data: [product_info]}
        """
        if image_data is None:
            return {"status": "error", "message": "输入图像为空"}

        try:
            # 获取当前帧 embedding
            frame_embedding = self.vlm_handler.get_image_embedding(image_data)

            # 遍历商品 embedding，计算余弦相似度
            best_product = None
            best_score = 0
            for pname, pembed in self.product_embeddings.items():
                score = self.cosine_similarity(frame_embedding, pembed)
                if score > best_score:
                    best_score = score
                    best_product = pname

            # 添加当前帧结果到队列
            if best_score >= self.similarity_threshold:
                self.recent_results.append((best_product, best_score))
            else:
                self.recent_results.append(None)

            # 判断是否连续 N 帧同一商品
            final_product, final_score = self.check_consecutive_match()

            if final_product:
                product_info = self.product_data.get(final_product, {}).copy()
                product_info["name"] = final_product
                product_info["similarity"] = final_score
                return {"status": "success", "data": [product_info]}
            else:
                return {"status": "success", "data": []}

        except Exception as e:
            logging.error(f"推理失败: {e}")
            return {"status": "error", "message": str(e)}

    def check_consecutive_match(self):
        """
        检查最近 N 帧是否连续识别到同一商品
        """
        if len(self.recent_results) < self.consecutive_frames:
            return None, 0
        
        first = self.recent_results[0]
        if first is None:
            return None, 0
            
        first_product, first_score = first
        
        # 检查所有帧是否都是同一商品
        for r in self.recent_results:
            if r is None or r[0] != first_product:
                return None, 0
        
        # 返回商品名和平均相似度
        avg_score = sum(r[1] for r in self.recent_results if r is not None) / len(self.recent_results)
        return first_product, avg_score

    @staticmethod
    def cosine_similarity(a, b):
        """
        计算余弦相似度
        """
        a = np.array(a)
        b = np.array(b)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

if __name__ == "__main__":
    import cv2
    vlm = VLMInferenceStable()

    # 测试代码
    test_frame = np.zeros((224, 224, 3), dtype=np.uint8)
    result = vlm.infer(test_frame)
    print(result)