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

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import FindSomethingController

def main():
    """
    主函数，程序入口点
    """
    print("Find Something Application Starting...")
    print("正在初始化摄像头...")
    
    # 配置日志
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s',
                       handlers=[
                           logging.FileHandler('find_something.log', encoding='utf-8'),
                           logging.StreamHandler()
                       ])
    
    # 初始化控制器
    controller = FindSomethingController()
    controller.start_application()
    
    # 检查摄像头状态
    if controller.camera_available:
        print("摄像头启动成功")
        print("摄像头预览已启用，按ESC键可以临时隐藏预览窗口")
    else:
        print("警告：摄像头不可用，正在使用回退模式")
        print("在回退模式下，系统将使用测试图像代替实际摄像头画面")
    
    print("支持的语音命令：我不要了、搜索、查找、退出、停止、返回主页面、显示摄像头、隐藏摄像头")
    
    try:
        # 保持主线程运行并处理摄像头预览
        while controller.is_running:
            # 持续捕获帧以保持预览显示
            controller.camera.capture_frame()
            import time
            time.sleep(0.03)  # 约30 FPS
            
    except Exception as e:
        logging.error(f"应用程序发生错误: {e}")
        print(f"应用程序发生错误: {e}")
    finally:
        # 停止应用程序
        controller.stop_application()
        print("Find Something Application Stopped")

if __name__ == "__main__":
    main()