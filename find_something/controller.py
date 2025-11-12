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

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from camera_capture import CameraCapture
from vlm_inference import VLMInference
from gui_display import GUIDisplay
from voice_command import VoiceCommandListener

class FindSomethingController:
    """
    FindSomething控制器类，负责协调各个模块的工作流程
    """
    
    def __init__(self):
        """
        初始化控制器
        """
        self.camera = CameraCapture()
        self.vlm = VLMInference()
        self.gui = GUIDisplay()
        self.voice = VoiceCommandListener()
        self.is_running = False
        self.is_searching = False
        self.search_thread = None
        self.preview_enabled = True
        self.camera_available = False
        
        # 设置GUI关闭回调
        self.gui.set_close_callback(self._on_gui_close)
        
        # 设置语音命令回调
        self.voice.set_command_callback(self._on_voice_command)
        
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
        logging.info("正在停止FindSomething应用程序...")
        self.is_running = False
        self.is_searching = False
        
        # 停止摄像头捕获
        self.camera.stop_capture()
        
        # 停止语音监听
        self.voice.stop_listening()
        
        # 关闭所有GUI窗口
        self.gui.close_all()
        
        logging.info("应用程序已停止")
        
    def _auto_search_loop(self):
        """
        自动搜索循环
        """
        while self.is_running:
            if not self.is_searching:
                # 每隔一段时间自动进行一次搜索
                time.sleep(5)  # 5秒间隔
                if self.is_running:
                    self.process_single_search()
            else:
                time.sleep(1)
                
    def process_single_search(self):
        """
        处理单次搜索请求
        """
        if self.is_searching:
            logging.info("已有搜索正在进行中，跳过本次搜索")
            return
            
        self.is_searching = True
        logging.info("开始处理单次搜索请求")
        
        try:
            # 暂时关闭预览以避免干扰截图
            if self.camera_available:
                preview_state = self.camera.show_preview
                self.camera.toggle_preview(False)
            
            # 捕获图像
            frame = self.camera.capture_frame()
            
            # 恢复预览状态
            if self.camera_available:
                self.camera.toggle_preview(preview_state)
            
            if frame is not None:
                # 使用VLM模型进行推理
                result = self.vlm.infer(frame)
                
                if result.get("status") == "success":
                    # 显示结果
                    products = result.get("data", [])
                    if products:
                        # 只显示第一个产品
                        product = products[0]
                        logging.info(f"找到相似商品: {product['name']}")
                        self.gui.show_product(product)
                    else:
                        logging.info("未找到相似商品")
                else:
                    logging.error("搜索失败: %s", result.get("message", "未知错误"))
            else:
                logging.warning("未能捕获有效图像帧")
        except Exception as e:
            logging.error(f"搜索过程中发生错误: {e}")
        finally:
            self.is_searching = False
            
    def _on_voice_command(self, command):
        """
        处理语音命令回调
        
        Args:
            command (str): 识别到的语音命令
        """
        logging.info(f"接收到语音命令: {command}")
        
        if command in ["我不要了", "关闭", "取消"]:
            # 关闭当前商品窗口
            self.gui.close_all()
        elif command in ["退出", "停止", "quit", "exit"]:
            # 退出应用
            self.stop_application()
        elif command in ["搜索", "查找"]:
            # 立即执行一次搜索
            self.process_single_search()
        elif command in ["返回主页面", "返回主页"]:
            # 返回主页面
            self._return_to_main_page()
        elif command in ["显示摄像头", "打开摄像头"]:
            # 显示摄像头预览
            self.camera.toggle_preview(True)
            logging.info("摄像头预览已开启")
        elif command in ["隐藏摄像头", "关闭摄像头"]:
            # 隐藏摄像头预览
            self.camera.toggle_preview(False)
            logging.info("摄像头预览已关闭")
            
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
            
    def _return_to_main_page(self):
        """
        返回主页面处理
        """
        logging.info("返回主页面")
        # 停止所有模型调用
        self.stop_application()
        # 重新初始化应用
        self.__init__()
        # 重新启动应用
        self.start_application()

def main():
    """
    主函数
    """
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    controller = FindSomethingController()
    controller.start_application()
    
    # 主循环
    try:
        # 保持主线程运行并处理摄像头预览
        while controller.is_running:
            # 持续捕获帧以保持预览显示
            controller.camera.capture_frame()
            time.sleep(0.03)  # 约30 FPS
    except KeyboardInterrupt:
        logging.info("收到中断信号")
    finally:
        controller.stop_application()

if __name__ == "__main__":
    main()