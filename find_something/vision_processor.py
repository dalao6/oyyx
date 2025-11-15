#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像特征提取和相似度匹配模块
负责从摄像头帧中提取特征，并与产品图像进行相似度匹配
"""

import os
import time
import numpy as np
import cv2
import logging
from pathlib import Path
import json
from collections import deque

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vlm_handler import VLMHandler

logger = logging.getLogger("vision_processor")

# 配置：商品图片路径和规格信息路径
PRODUCT_DIR = os.path.join("DuoMotai", "data", "product_images")
PRODUCT_SPECS_DIR = os.path.join("DuoMotai", "data", "product_specs")

class VisionProcessor:
    def __init__(self, device=None):
        self.device = device or "cpu"
        logger.info(f"[VisionProcessor] device={self.device}")
        
        # 初始化VLM处理器，强制使用模拟模式
        self.vlm_handler = VLMHandler(simulate=True)
        logger.info("[VisionProcessor] 使用VLM模型（模拟模式）")
        
        # 控制识别频率
        self.last_recognition_time = 0
        self.recognition_interval = 1.0  # 每隔1秒识别一次
        
        # 滑动平均滤波：连续3帧识别为同一商品才确认
        self.recognition_history = deque(maxlen=3)
        
        # 连续帧确认机制
        self.consecutive_frames = 3
        self.similarity_threshold = 0.85
        self.recent_results = deque(maxlen=self.consecutive_frames)
        
        # 记录上一个已确认的商品，避免重复输出
        self.last_product = None
        
        # 构建商品嵌入索引库
        self.product_files = []
        self.prod_embeddings = None
        self.names = []
        self._build_index()

    def _img_to_embedding(self, img_bgr):
        """
        使用VLM模型获取图像embedding
        """
        try:
            # 使用VLMHandler获取图像embedding
            embedding = self.vlm_handler.get_image_embedding(img_bgr)
            return embedding
        except Exception as e:
            logger.error(f"获取图像embedding时出错: {e}")
            # 出错时返回零向量
            return np.zeros(512)

    def _build_index(self):
        project_root = Path(__file__).parent.parent
        product_dir = project_root / PRODUCT_DIR
        
        if not product_dir.exists():
            logger.warning(f"商品图片目录不存在: {product_dir}")
            self.prod_embeddings = np.zeros((0, 512))  # VLM embedding维度
            return
            
        files = [f for f in product_dir.iterdir() if f.suffix.lower() in [".jpg", ".png"]]
        embeddings = []
        
        for file_path in files:
            try:
                # 读取图像
                img = cv2.imread(str(file_path))
                if img is None:
                    logger.warning(f"无法读取图像: {file_path}")
                    continue
                    
                emb = self._img_to_embedding(img)
                embeddings.append(emb)
                self.names.append(file_path.stem)  # 文件名（不含扩展名）
                self.product_files.append(str(file_path))
            except Exception as e:
                logger.warning(f"处理图像时出错 {file_path}: {e}")
                
        if embeddings:
            self.prod_embeddings = np.vstack(embeddings)
        else:
            self.prod_embeddings = np.zeros((0, 512))  # VLM embedding维度
            
        logger.info(f"[VisionProcessor] 已索引 {len(self.product_files)} 个商品图像")
        
    def get_product_info(self, product_name):
        """
        读取商品的文字信息。
        
        Args:
            product_name (str): 商品名称（来自图片文件名）
            
        Returns:
            dict: 商品信息
        """
        try:
            project_root = Path(__file__).parent.parent
            specs_dir = project_root / PRODUCT_SPECS_DIR
            spec_file = specs_dir / "nike_shirt.json"
            
            if not spec_file.exists():
                logger.warning(f"商品规格文件不存在: {spec_file}")
                return {"name": product_name, "description": "暂无详细信息", "price": "未知"}

            with open(spec_file, "r", encoding="utf-8") as f:
                all_products = json.load(f)

            # 优先级匹配：精确 > 模糊 > 语义特征
            match_strategies = [
                lambda: next(((name, info) for name, info in all_products.items() if name == product_name), None),
                lambda: next(((name, info) for name, info in all_products.items() if product_name in name or name in product_name), None),
                lambda: next(((name, info) for name, info in all_products.items() 
                            if (("耐克" in product_name and "耐克" in name) or ("安踏" in product_name and "安踏" in name)) 
                            and any(t in product_name and t in name for t in ["短袖", "长袖", "长裤"])), None)
            ]

            for strategy in match_strategies:
                match = strategy()
                if match:
                    name, info = match
                    product_info = {
                        "name": name,
                        "description": info.get("description", "暂无描述"),
                        "price": info.get("price", "¥0")
                    }
                    if "tags" in info:
                        product_info["tags"] = info["tags"]
                    return product_info

            logger.warning(f"未找到匹配的商品信息: {product_name}")
            return {"name": product_name, "description": "暂无详细信息", "price": "未知"}
            
        except Exception as e:
            logger.error(f"读取商品信息失败: {e}")
            return {"name": product_name, "description": "信息读取失败", "price": "未知"}

    def frame_to_embedding(self, frame_bgr):
        return self._img_to_embedding(frame_bgr)

    def find_most_similar(self, frame, topk=3):
        if self.prod_embeddings.shape[0] == 0 or frame is None:
            return None, 0.0
            
        emb = self.frame_to_embedding(frame)
        
        # 计算余弦相似度
        # 注意：由于我们现在使用的是改进的模拟embedding，需要确保向量已归一化
        emb_norm = np.linalg.norm(emb)
        if emb_norm > 0:
            emb = emb / emb_norm
            
        prod_norms = np.linalg.norm(self.prod_embeddings, axis=1)
        # 避免除零错误
        prod_norms[prod_norms == 0] = 1
        
        # 计算余弦相似度
        sims = np.dot(self.prod_embeddings, emb) / prod_norms
        
        if len(sims) == 0:
            return None, 0.0
            
        # 获取top-k最相似的结果
        top_indices = np.argsort(sims)[::-1][:topk]
        top_scores = sims[top_indices]
        
        idx = top_indices[0]
        score = float(top_scores[0])
        
        result = {
            "name": self.names[idx],
            "image": self.product_files[idx],
            "score": score
        }
        
        logger.info(f"最佳匹配: {result['name']} (相似度: {score:.3f})")
        return result['name'], score
    
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
        
        # 检查所有帧是否都是同一商品且相似度达标
        for r in self.recent_results:
            if r is None or r[0] != first_product or r[1] < self.similarity_threshold:
                return None, 0
        
        # 返回商品名和平均相似度
        avg_score = sum(r[1] for r in self.recent_results if r is not None) / len(self.recent_results)
        return first_product, avg_score

    def find_most_similar_stable(self, frame):
        """
        稳定版本的相似商品查找，使用连续帧确认机制
        """
        if self.prod_embeddings.shape[0] == 0 or frame is None:
            return None, 0.0
            
        emb = self.frame_to_embedding(frame)
        
        # 计算余弦相似度
        # 注意：由于我们现在使用的是改进的模拟embedding，需要确保向量已归一化
        emb_norm = np.linalg.norm(emb)
        if emb_norm > 0:
            emb = emb / emb_norm
            
        prod_norms = np.linalg.norm(self.prod_embeddings, axis=1)
        # 避免除零错误
        prod_norms[prod_norms == 0] = 1
        
        # 计算余弦相似度
        sims = np.dot(self.prod_embeddings, emb) / prod_norms
        
        if len(sims) == 0:
            self.recent_results.append(None)
            return self.check_consecutive_match()
            
        # 获取最佳匹配
        best_idx = np.argmax(sims)
        best_score = float(sims[best_idx])
        best_product = self.names[best_idx]
        
        logger.info(f"当前帧匹配: {best_product} (相似度: {best_score:.3f})")
        
        # 添加当前帧结果到队列
        if best_score >= self.similarity_threshold:
            self.recent_results.append((best_product, best_score))
        else:
            self.recent_results.append(None)
        
        # 检查是否连续N帧识别到同一商品
        return self.check_consecutive_match()