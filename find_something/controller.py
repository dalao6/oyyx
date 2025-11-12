#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程控制模块（协调各模块逻辑）
"""

import logging
import sys
import os
import time
import threading
import tkinter as tk
from pathlib import Path
import json
import numpy as np
import cv2

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from camera_capture import CameraCapture
from vision_processor import VisionProcessor
from gui_display import GUIDisplay
from voice_command import VoiceCommandListener

logger = logging.getLogger("controller")

class FindSomethingController:
    """
    FindSomething控制器类，负责协调各个模块的工作流程
    """
    
    def __init__(self, root=None):
        """
        初始化控制器
        
        Args:
            root: Tkinter主窗口，用于调度GUI更新
        """
        self.root = root or tk.Tk()
        self.camera = CameraCapture()
        self.vp = VisionProcessor()
        self.gui = GUIDisplay()
        self.voice = VoiceCommandListener()
        self.voice.set_command_callback(self._on_voice_command)
        
        self.last_shown = None
        self.last_shown_time = 0
        self.min_display_interval = 3.0  # 秒
        self.search_lock = threading.Lock()
        self.is_running = False
        self.search_thread = None
        self.current_window = None
        self.camera_available = False
        self.preview_enabled = True  # 添加缺失的属性，启用摄像头预览
        
        # 新增：用于存储最近几次识别结果的缓冲区
        self.detection_buffer = []  # 存储最近3次的检测结果
        self.confidence_buffer = []  # 存储最近3次的置信度
        self.embedding_buffer = []   # 存储最近3次的嵌入向量
        
        # 新增：用于跟踪识别状态
        self.stable_detection_count = 0
        self.is_detecting_stable = False
        
        # 设置GUI关闭回调
        self.gui.set_close_callback(self._on_gui_close)
        
    def start_application(self):
        """
        启动应用程序
        """
        logging.info("正在启动FindSomething应用程序...")
        self.is_running = True
        
        # 启动摄像头捕获（启用预览）
        self.camera_available = self.camera.start_capture(show_preview=self.preview_enabled)
        if not self.camera_available:
            logging.warning("摄像头不可用，将在回退模式下运行")
        
        # 启动语音监听
        self.voice.start_listening()
        
        # 启动自动搜索线程
        self.search_thread = threading.Thread(target=self._auto_search_loop, daemon=True)
        self.search_thread.start()
        
        logging.info("应用程序已启动")
        
    def stop_application(self):
        """
        停止应用程序
        """
        logger.info("正在停止FindSomething应用程序...")
        self.is_running = False
        
        # 停止语音监听
        self.voice.stop_listening()
        
        # 停止摄像头捕获
        self.camera.stop_capture()
        
        # 等待搜索线程结束
        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join(timeout=2)
        
        # 确保任何UI关闭都在主线程中运行
        self.root.after(0, self._cleanup_ui)

    def _cleanup_ui(self):
        self.gui.close_all()
        logger.info("应用已停止")
        
    def _auto_search_loop(self):
        """
        自动搜索循环
        """
        logger.info("识别循环开始")
        while self.is_running:
            # 先加简单去重锁，避免并发搜索
            if not self.search_lock.acquire(False):
                time.sleep(0.05)
                continue
            try:
                if not self.camera_available:
                    time.sleep(0.05)
                    continue
                    
                # 暂时关闭预览以避免干扰截图
                preview_state = self.camera.show_preview
                self.camera.toggle_preview(False)
                
                frame = self.camera.capture_frame()
                
                # 恢复预览状态
                self.camera.toggle_preview(preview_state)
                
                if frame is None:
                    time.sleep(0.05)
                    continue
                    
                # 图像增强：亮度与对比度调节
                enhanced_frame = self._enhance_image(frame)
                
                # 使用VisionProcessor模型进行推理
                result, score = self.vp.find_most_similar(enhanced_frame)
                
                # 更新检测缓冲区
                self._update_detection_buffers(result, score, enhanced_frame)
                
                # 显示检测中提示
                if len(self.detection_buffer) > 0 and len(self.detection_buffer) < 3:
                    self.root.after(0, self.gui.show_detecting)
                
                # 检查是否满足稳定的识别条件
                if self._is_stable_detection():
                    name = result['name']
                    now = time.time()
                    if name != self.last_shown or (now - self.last_shown_time) > self.min_display_interval:
                        self.last_shown = name
                        self.last_shown_time = now
                        # 在主线程创建弹窗
                        self.root.after(0, lambda r=result, s=score: self._show_product(r, s))
                        # 重置检测状态
                        self._reset_detection_state()
                elif len(self.detection_buffer) >= 3:
                    # 如果缓冲区满了但仍未满足稳定条件，则重置状态
                    self._reset_detection_state()
                    self.root.after(0, self.gui.hide_detecting)
                else:
                    # 继续检测，保持检测中提示
                    pass
                        
                # 控制识别频率，每3秒识别一次
                time.sleep(3.0)
            except Exception as e:
                logger.error(f"搜索过程中发生错误: {e}")
                # 遇到错误时隐藏检测中提示
                self.root.after(0, self.gui.hide_detecting)
            finally:
                self.search_lock.release()
        logger.info("识别循环结束")
            
    def _enhance_image(self, img):
        """
        图像增强：调整亮度和对比度
        """
        return cv2.convertScaleAbs(img, alpha=1.2, beta=15)
        
    def _update_detection_buffers(self, result, score, frame):
        """
        更新检测缓冲区
        """
        if result is not None:
            # 添加结果到缓冲区
            self.detection_buffer.append(result['name'])
            self.confidence_buffer.append(score)
            
            # 限制缓冲区大小为3
            if len(self.detection_buffer) > 3:
                self.detection_buffer.pop(0)
            if len(self.confidence_buffer) > 3:
                self.confidence_buffer.pop(0)
                
            # 计算并存储嵌入向量
            embedding = self.vp.frame_to_embedding(frame)
            self.embedding_buffer.append(embedding)
            if len(self.embedding_buffer) > 3:
                self.embedding_buffer.pop(0)
        else:
            # 如果没有检测到结果，清空缓冲区
            self.detection_buffer.clear()
            self.confidence_buffer.clear()
            self.embedding_buffer.clear()
            
    def _is_stable_detection(self):
        """
        判断是否为稳定的检测结果
        """
        # 检查缓冲区是否已满
        if len(self.detection_buffer) < 3:
            return False
            
        # 检查置信度：最近3帧置信度平均值 ≥ 0.85 (临时降低阈值以便测试)
        avg_conf = np.mean(self.confidence_buffer[-3:])
        if avg_conf < 0.85:
            return False
            
        # 检查类别一致性：最近3帧Top-1类别ID一致
        if len(set(self.detection_buffer[-3:])) == 1:
            return True
            
        # 检查嵌入向量相似度（如果可用）
        if len(self.embedding_buffer) >= 3:
            # 计算余弦相似度
            embed1, embed2, embed3 = self.embedding_buffer[-3:]
            # 防止除零错误
            norm1, norm2, norm3 = np.linalg.norm(embed1), np.linalg.norm(embed2), np.linalg.norm(embed3)
            if norm1 > 0 and norm2 > 0 and norm3 > 0:
                sim12 = np.dot(embed1, embed2) / (norm1 * norm2)
                sim23 = np.dot(embed2, embed3) / (norm2 * norm3)
                
                # 嵌入向量相似度验证（如≥0.90，临时降低阈值以便测试）
                if sim12 > 0.90 and sim23 > 0.90:
                    return True
                
        return False
        
    def _reset_detection_state(self):
        """
        重置检测状态
        """
        self.detection_buffer.clear()
        self.confidence_buffer.clear()
        self.embedding_buffer.clear()
            
    def _on_voice_command(self, text):
        """
        处理语音命令回调
        
        Args:
            text (str): 识别到的语音命令
        """
        logger.info(f"识别到语音命令: {text}")
        # 使用更精确的匹配方式，避免误触发
        commands = [cmd.strip() for cmd in text.split('，') + text.split(',') + [text]]
        
        for cmd in commands:
            if any(keyword in cmd for keyword in ["我不要了", "关闭", "取消"]):
                # 要在主线程关闭窗口
                self.root.after(0, lambda: self.gui.close_all())
                # 清除上次检测记录，允许重新检测
                self.last_shown = None
                # 尝试清除 VisionProcessor 中的识别历史（如果存在）
                if hasattr(self.vp, 'recognition_history'):
                    self.vp.recognition_history.clear()
                logger.info("通过语音关闭当前窗口并清除识别历史")
                break
                
            elif any(keyword in cmd for keyword in ["停止", "退出", "quit", "exit", "返回主页面", "返回主页"]):
                self.stop_application()
                break
            
    def _on_gui_close(self, action=None):
        """
        GUI窗口关闭回调
        
        Args:
            action (str): 关闭动作
        """
        if action == "return_to_main":
            self._return_to_main_page()
        else:
            logging.info("商品窗口已关闭")
            # 清除上次检测记录，允许重新检测
            self.last_shown = None
            # 同时尝试清除视觉处理器中的识别历史
            if hasattr(self.vp, 'recognition_history'):
                self.vp.recognition_history.clear()
            
    def _return_to_main_page(self):
        """
        返回主页面处理
        """
        logging.info("返回主页面")
        # 在主线程中执行清理和重启
        self.root.after(0, self._cleanup_and_restart)
    
    def _cleanup_and_restart(self):
        """在主线程中清理并重启应用"""
        self.stop_application()
        # 重新初始化应用状态
        self.__init__(self.root)
        self.start_application()
    
    def _show_product(self, result, score):
        """显示产品信息"""
        try:
            if not result or 'name' not in result:
                logger.warning("无效的识别结果")
                return
                
            # 获取完整的产品信息
            product_info = self.vp.get_product_info(result['name'])
            if not product_info:
                logger.warning(f"未找到产品信息: {result['name']}")
                return
            
            # 确保必要的字段存在
            product_info = product_info.copy()  # 避免修改原始数据
            
            # 添加图像路径和相似度信息
            product_info["image_path"] = result.get('image', '')
            product_info["similarity"] = float(score)
            product_info["name"] = result['name']
            
            # 处理价格信息
            if "price" in product_info:
                price = product_info["price"]
                if isinstance(price, str):
                    # 移除货币符号和其他非数字字符（保留小数点）
                    cleaned_price = ''.join(c for c in price if c.isdigit() or c == '.')
                    try:
                        product_info["price"] = float(cleaned_price) if cleaned_price else 0.0
                    except ValueError:
                        logger.warning(f"价格转换失败: {price}")
                        product_info["price"] = 0.0
                elif not isinstance(price, (int, float)):
                    product_info["price"] = 0.0
                    
            # 确保价格字段存在
            if "price" not in product_info:
                product_info["price"] = 0.0
                
            logger.info(f"显示产品: {product_info['name']}, 相似度: {score:.3f}, 价格: ¥{product_info['price']}")
            
            # 在主线程中更新GUI
            self.gui.show_product(product_info)
            self.root.after(0, lambda: self.gui.show_product_window(self.root))
            
        except Exception as e:
            logger.error(f"显示产品信息时出错: {e}", exc_info=True)

def main():
    """
    主函数
    """
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建主Tk窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    controller = FindSomethingController(root)
    controller.start_application()
    
    # 主循环
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        controller.stop_application()

if __name__ == "__main__":
    main()