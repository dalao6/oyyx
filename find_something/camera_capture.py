#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
摄像头捕获模块
负责从摄像头捕获图像帧
"""

import cv2
import logging
import time
from pathlib import Path
import numpy as np

logger = logging.getLogger("camera_capture")

class CameraCapture:
    """
    摄像头捕获类，负责打开摄像头并捕获图像帧
    """
    
    def __init__(self, camera_index=0):
        """
        初始化摄像头捕获器
        
        Args:
            camera_index (int): 摄像头索引，默认为0
        """
        self.camera_index = camera_index
        self.cap = None
        self.show_preview = False
        self.fallback_mode = False
        self.fallback_image = None
        self.last_frame_time = 0
        self.frame_interval = 0.1  # 最大帧率10fps
        
    def find_available_cameras(self, max_cameras=10):
        """
        查找可用的摄像头设备
        
        Args:
            max_cameras (int): 最大检查的摄像头数量
            
        Returns:
            list: 可用摄像头索引列表
        """
        available_cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
            cap.release()
        return available_cameras
        
    def start_capture(self, show_preview=True):
        """
        启动摄像头捕获
        
        Args:
            show_preview (bool): 是否显示预览
            
        Returns:
            bool: 是否成功启动摄像头
        """
        self.show_preview = show_preview
        
        # 尝试打开指定的摄像头
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # 如果指定摄像头无法打开，尝试查找其他可用摄像头
        if not self.cap.isOpened():
            logger.warning(f"无法打开摄像头 {self.camera_index}，正在查找其他可用摄像头...")
            available_cameras = self.find_available_cameras()
            
            if available_cameras:
                logger.info(f"找到可用摄像头: {available_cameras}，使用第一个可用的摄像头 {available_cameras[0]}")
                self.camera_index = available_cameras[0]
                self.cap = cv2.VideoCapture(self.camera_index)
            else:
                logger.warning("未找到任何可用的摄像头")
                self._enable_fallback_mode()
                return False
        
        if not self.cap.isOpened():
            logger.warning(f"无法打开摄像头 {self.camera_index}")
            self._enable_fallback_mode()
            return False
            
        # 设置摄像头分辨率为720p
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # 降低帧率以提高稳定性
        self.cap.set(cv2.CAP_PROP_FPS, 10)
        
        logger.info(f"摄像头 {self.camera_index} 已启动，分辨率设置为720p，最大帧率10fps")
        return True
        
    def _enable_fallback_mode(self):
        """
        启用回退模式
        """
        logger.info("启用回退模式")
        self.fallback_mode = True
        
        # 创建一个测试图像
        self.fallback_image = np.ones((720, 1280, 3), dtype=np.uint8) * 128
        cv2.putText(
            self.fallback_image, 
            'Camera Unavailable - Fallback Mode', 
            (50, 360), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (255, 255, 255), 
            2
        )
        cv2.putText(
            self.fallback_image, 
            'Contact administrator to check camera connection', 
            (50, 400), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            (255, 255, 255), 
            1
        )
        
    def capture_frame(self):
        """
        捕获一帧图像
        
        Returns:
            numpy.ndarray: 图像帧，如果失败则返回None
        """
        # 控制帧率
        current_time = time.time()
        if current_time - self.last_frame_time < self.frame_interval:
            # 如果时间间隔太短，跳过此次捕获
            return None
        self.last_frame_time = current_time
        
        if self.fallback_mode:
            return self.fallback_image.copy()
            
        if not self.cap or not self.cap.isOpened():
            logger.warning("摄像头未初始化或已关闭")
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("无法读取摄像头帧")
            return None
            
        # 如果启用了预览，显示图像
        if self.show_preview:
            cv2.imshow("Camera Preview - Press ESC to hide", frame)
            # 处理按键事件，支持ESC键隐藏预览
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC键
                self.show_preview = False
                cv2.destroyWindow("Camera Preview - Press ESC to hide")
            
        return frame
        
    def toggle_preview(self, show=None):
        """
        切换预览显示状态
        
        Args:
            show (bool, optional): 是否显示预览，如果不提供则切换当前状态
        """
        if show is None:
            self.show_preview = not self.show_preview
        else:
            self.show_preview = show
            
    def stop_capture(self):
        """
        停止摄像头捕获
        """
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
        # 关闭所有OpenCV窗口
        cv2.destroyAllWindows()
        
        logger.info("摄像头已停止捕获")