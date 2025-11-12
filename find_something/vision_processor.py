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

logger = logging.getLogger("vision_processor")

# 配置：商品图片路径和规格信息路径
PRODUCT_DIR = os.path.join("DuoMotai", "data", "product_images")
PRODUCT_SPECS_DIR = os.path.join("DuoMotai", "data", "product_specs")

class VisionProcessor:
    def __init__(self, device=None):
        self.device = device or "cpu"
        logger.info(f"[VisionProcessor] device={self.device}")
        # 模拟CLIP模型，实际项目中应替换为真实模型
        logger.info("[VisionProcessor] 使用模拟CLIP模型")
        
        # 控制识别频率
        self.last_recognition_time = 0
        self.recognition_interval = 1.0  # 每隔1秒识别一次
        
        # 滑动平均滤波：连续3帧识别为同一商品才确认
        self.recognition_history = deque(maxlen=3)
        
        # 记录上一个已确认的商品，避免重复输出
        self.last_product = None
        
        # 构建商品嵌入索引库
        self.product_files = []
        self.prod_embeddings = None
        self.names = []
        self._build_index()

    def _img_to_embedding(self, img_bgr):
        # 模拟图像特征提取过程
        # 实际项目中应使用CLIP模型提取真实特征
        resized = cv2.resize(img_bgr, (224, 224))
        # 简单的特征提取方法：计算颜色直方图
        hist_b = cv2.calcHist([resized], [0], None, [8], [0, 256])
        hist_g = cv2.calcHist([resized], [1], None, [8], [0, 256])
        hist_r = cv2.calcHist([resized], [2], None, [8], [0, 256])
        
        # 将直方图展平并归一化
        feature = np.concatenate([hist_b, hist_g, hist_r]).flatten()
        norm = np.linalg.norm(feature)
        if norm > 0:
            feature = feature / norm
        return feature

    def _build_index(self):
        project_root = Path(__file__).parent.parent
        product_dir = project_root / PRODUCT_DIR
        
        if not product_dir.exists():
            logger.warning(f"商品图片目录不存在: {product_dir}")
            self.prod_embeddings = np.zeros((0, 24))  # 8*3 个特征
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
            self.prod_embeddings = np.zeros((0, 24))  # 8*3 个特征
            
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
        
        # 计算余弦相似度（因为特征已归一化，所以直接点积）
        sims = np.dot(self.prod_embeddings, emb)
        
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
        return result, score