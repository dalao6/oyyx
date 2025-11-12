#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主入口文件 - 点击后执行的界面逻辑
启动后会自动调用笔记本前置摄像头，并在屏幕上显示摄像头画面
用户可以通过以下方式与系统交互：
- 系统每5秒自动识别一次衣物
- 点击"我不要了"按钮或说出"我不要了"，关闭当前窗口并继续识别
- 点击"返回主页面"按钮，停止所有模型调用并返回初始状态
- 语音命令"显示摄像头"/"隐藏摄像头"可以控制摄像头画面显示
- 按ESC键可以临时隐藏摄像头预览窗口

如果摄像头不可用，系统将使用回退模式运行
"""

import sys
import os
import logging
import tkinter as tk
import cv2

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import FindSomethingController

def main():
    """
    主函数，程序入口点
    """
    print("Find Something Application Starting...")
    print("正在初始化摄像头...")
    
    # 配置日志 - 只显示INFO及以上级别的日志，避免刷屏
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                       handlers=[
                           logging.FileHandler('find_something.log', encoding='utf-8'),
                           logging.StreamHandler()
                       ])
    
    # 创建主窗口
    root = tk.Tk()
    root.title("Find Something")
    root.geometry("400x300")
    root.withdraw()  # 隐藏主窗口
    
    # 初始化控制器
    controller = FindSomethingController(root)
    
    def start_app():
        controller.start_application()
        # 启动摄像头预览循环
        def camera_loop():
            if controller.is_running:
                try:
                    # 持续捕获帧以保持预览显示
                    controller.camera.capture_frame()
                except Exception as e:
                    logging.error(f"摄像头捕获错误: {e}")
                # 继续循环，控制帧率
                root.after(30, camera_loop)  # 约33 FPS
        
        camera_loop()
    
    # 在GUI线程中启动应用
    root.after(100, start_app)
    
    print("摄像头预览已启用，按ESC键可以临时隐藏预览窗口")
    print("支持的语音命令：我不要了、搜索、查找、退出、停止、返回主页面、显示摄像头、隐藏摄像头")
    print("Find Something Application Started")
    
    try:
        # 启动GUI主循环
        root.mainloop()
    except Exception as e:
        logging.error(f"应用程序发生错误: {e}")
        print(f"应用程序发生错误: {e}")
    finally:
        # 停止应用程序
        controller.stop_application()
        # 确保所有OpenCV窗口都被关闭
        cv2.destroyAllWindows()
        print("Find Something Application Stopped")

if __name__ == "__main__":
    main()