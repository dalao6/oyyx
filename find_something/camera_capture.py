#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
摄像头捕获模块
"""

import cv2
import logging
import os

class CameraCapture:
    """
    摄像头捕获类，负责从摄像头获取图像帧
    """
    
    def __init__(self, camera_index=0):
        """
        初始化摄像头捕获模块
        
        Args:
            camera_index (int): 摄像头索引，默认为0（通常是内置摄像头）
        """
        self.camera_index = camera_index
        self.camera = None
        self.is_capturing = False
        self.show_preview = False
        self.fallback_to_image = False  # 是否回退到图像文件模式
        
    def find_available_cameras(self):
        """
        查找可用的摄像头设备
        Returns:
            list: 可用的摄像头索引列表
        """
        available_cameras = []
        for i in range(10):  # 检查前10个索引
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
            cap.release()
        logging.info(f"找到可用摄像头: {available_cameras}")
        return available_cameras
        
    def start_capture(self, show_preview=False):
        """
        开始捕获摄像头画面
        
        Args:
            show_preview (bool): 是否显示预览窗口
        """
        try:
            # 首先尝试使用指定索引打开摄像头
            self.camera = cv2.VideoCapture(self.camera_index)
            
            # 检查摄像头是否成功打开
            if not self.camera.isOpened():
                logging.warning(f"无法打开索引为 {self.camera_index} 的摄像头")
                
                # 尝试查找其他可用的摄像头
                available_cameras = self.find_available_cameras()
                if available_cameras:
                    logging.info(f"尝试使用第一个可用摄像头: {available_cameras[0]}")
                    self.camera = cv2.VideoCapture(available_cameras[0])
                    
            # 再次检查摄像头是否成功打开
            if not self.camera.isOpened():
                logging.error("无法打开任何摄像头设备")
                # 回退到使用图像文件模式
                self.fallback_to_image = True
                logging.info("回退到图像文件模式")
                return False
                
            self.is_capturing = True
            self.show_preview = show_preview
            logging.info("摄像头捕获已启动")
            return True
        except Exception as e:
            logging.error(f"启动摄像头失败: {e}")
            self.is_capturing = False
            # 出错时也回退到图像文件模式
            self.fallback_to_image = True
            return False
        
    def stop_capture(self):
        """
        停止捕获摄像头画面
        """
        self.is_capturing = False
        if self.camera:
            self.camera.release()
        # 关闭所有OpenCV窗口
        cv2.destroyAllWindows()
        logging.info("摄像头捕获已停止")
        
    def capture_frame(self):
        """
        捕获单帧图像
        Returns:
            frame: 图像帧数据
        """
        # 如果回退到图像文件模式，则生成测试图像
        if self.fallback_to_image:
            import numpy as np
            # 创建一个带颜色的测试图像
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # 添加一些颜色和文字
            frame[:, :] = [100, 150, 200]  # 蓝色背景
            
            # 在图像上添加文字
            cv2.putText(frame, "Camera Not Available", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Using Fallback Mode", (50, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # 如果需要显示预览，则显示当前帧
            if self.show_preview and frame is not None:
                cv2.imshow('Camera Preview - Fallback Mode (Press ESC to hide)', frame)
                # 等待1毫秒并检查按键
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC键
                    self.show_preview = False
                    cv2.destroyWindow('Camera Preview - Fallback Mode (Press ESC to hide)')
                    
            return frame
            
        frame = None
        if self.is_capturing and self.camera:
            ret, frame = self.camera.read()
            if not ret:
                logging.warning("无法读取摄像头帧")
                return None
                
            # 如果需要显示预览，则显示当前帧
            if self.show_preview and frame is not None:
                cv2.imshow('Camera Preview - Press ESC to hide', frame)
                # 等待1毫秒并检查按键
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC键
                    self.show_preview = False
                    cv2.destroyWindow('Camera Preview - Press ESC to hide')
                    
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

if __name__ == "__main__":
    # 测试代码
    import time
    capture = CameraCapture()
    success = capture.start_capture(show_preview=True)
    
    if success:
        print("摄像头启动成功")
    else:
        print("摄像头启动失败，使用回退模式")
    
    # 捕获几帧图像
    print("显示摄像头预览，按ESC键隐藏预览窗口")
    for i in range(1000):  # 运行更长时间
        frame = capture.capture_frame()
        if frame is not None:
            pass
        time.sleep(0.05)
        
    capture.stop_capture()
    print("测试完成")