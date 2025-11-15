#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VLM模型处理模块（稳定版本）
- 支持获取图像embedding
- 可用于连续帧识别
- 支持模拟模式和真实模型接口
"""

import logging
import os
import cv2
from pathlib import Path
import numpy as np

class VLMHandler:
    """
    VLM (Vision-Language Model) 处理器类
    """

    def __init__(self, model_path="/mnt/data/modelscope_cache/hub/Qwen/Qwen2-VL-2B-Instruct", simulate=False):
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        self.simulate_mode = simulate
        self.load_model()

    def load_model(self):
        """
        加载VLM模型
        """
        # 如果已经强制设置为模拟模式，则直接返回
        if self.simulate_mode:
            self.is_loaded = True
            return
            
        try:
            if os.path.exists(self.model_path):
                # TODO: 真实模型加载逻辑
                logging.info(f"VLM模型路径存在: {self.model_path}")
                self.is_loaded = True
            else:
                logging.warning(f"VLM模型路径不存在: {self.model_path}，启用模拟模式")
                self.simulate_mode = True
                self.is_loaded = True
        except Exception as e:
            logging.error(f"加载VLM模型出错: {e}")
            self.simulate_mode = True
            self.is_loaded = True

    def get_image_embedding(self, frame_or_path):
        """
        获取图像 embedding，可用于相似度计算
        
        Args:
            frame_or_path: OpenCV 图像或图片路径
            
        Returns:
            np.array: embedding向量
        """
        if isinstance(frame_or_path, str):
            if not os.path.exists(frame_or_path):
                logging.warning(f"图片路径不存在: {frame_or_path}")
                return np.zeros(512)
            frame = cv2.imread(frame_or_path)
        else:
            frame = frame_or_path

        if frame is None:
            logging.warning("输入图像为空")
            return np.zeros(512)

        if self.simulate_mode:
            # 改进的模拟 embedding：基于更复杂的图像特征生成向量
            # 调整图像大小以统一处理
            resized = cv2.resize(frame, (224, 224))
            
            # 计算颜色直方图特征（更细致）
            hist_b = cv2.calcHist([resized], [0], None, [32], [0, 256]).flatten()
            hist_g = cv2.calcHist([resized], [1], None, [32], [0, 256]).flatten()
            hist_r = cv2.calcHist([resized], [2], None, [32], [0, 256]).flatten()
            
            # 计算均值和标准差作为额外特征
            mean, std = cv2.meanStdDev(resized)
            color_features = np.concatenate([mean.flatten(), std.flatten()])
            
            # 计算图像梯度特征
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_features = np.array([np.mean(grad_x), np.std(grad_x), np.mean(grad_y), np.std(grad_y)])
            
            # 组合所有特征
            combined_features = np.concatenate([hist_b, hist_g, hist_r, color_features, grad_features])
            
            # 归一化特征向量
            norm = np.linalg.norm(combined_features)
            if norm > 0:
                combined_features = combined_features / norm
            
            # 如果特征向量维度不足512，用0补齐；如果超过512，截取前512个
            if len(combined_features) < 512:
                embedding = np.pad(combined_features, (0, 512 - len(combined_features)), 'constant')
            else:
                embedding = combined_features[:512]
                
            return embedding
        else:
            # TODO: 使用真实模型计算 embedding
            # 例如 self.model.get_embedding(frame)
            raise NotImplementedError("真实模型embedding接口未实现")

    def recognize_image(self, frame):
        """
        返回VLM识别文本（模拟或真实）
        
        Args:
            frame: OpenCV图像
            
        Returns:
            str: 文本描述
        """
        if frame is None:
            return ""

        if self.simulate_mode:
            # 模拟识别逻辑
            avg_color = frame.mean(axis=0).mean(axis=0)
            b, g, r = avg_color
            if r > g and r > b:
                color = "红色"
            elif g > r and g > b:
                color = "绿色"
            elif b > r and b > g:
                color = "蓝色"
            elif abs(r-g)<20 and abs(r-b)<20 and abs(g-b)<20:
                color = "白色" if r>128 else "黑色"
            else:
                color = "彩色"
            ratio = frame.shape[1] / frame.shape[0]
            if ratio > 1.2:
                clothing_type = "长袖"
            elif ratio < 0.8:
                clothing_type = "长裤"
            else:
                clothing_type = "短袖"
            result = f"这是一件{color}的{clothing_type}"
            logging.info(f"VLM模拟识别结果: {result}")
            return result
        else:
            # TODO: 调用真实模型返回文本描述
            raise NotImplementedError("真实VLM识别接口未实现")


if __name__ == "__main__":
    import numpy as np
    vlm = VLMHandler()
    test_frame = np.ones((224,224,3), dtype=np.uint8) * 255
    print("Embedding shape:", vlm.get_image_embedding(test_frame).shape)
    print("识别结果:", vlm.recognize_image(test_frame))