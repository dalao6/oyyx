#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音命令监听模块（ASR）
"""

import threading
import time
import logging

logger = logging.getLogger("voice")

class VoiceCommandListener:
    def __init__(self):
        self.command_callback = None
        self._stop_event = threading.Event()
        self.listen_thread = None

    def set_command_callback(self, callback):
        self.command_callback = callback

    def _listen_loop(self):
        # 这里用真实 ASR 或模拟 input() ，示例用模拟
        while not self._stop_event.is_set():
            # replace with real ASR streaming read
            try:
                # 模拟语音命令输入
                # 在实际应用中，这里应该替换为真实的ASR识别逻辑
                time.sleep(1)  # 避免过于频繁的检查
            except Exception:
                continue
                
        logger.info("语音线程退出")

    def start_listening(self):
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        logger.info("语音监听已启动")

    def stop_listening(self):
        self._stop_event.set()
        # 不要在监听线程内部 join 自己
        if (self.listen_thread and 
            threading.current_thread() is not self.listen_thread and 
            self.listen_thread.is_alive()):
            self.listen_thread.join(timeout=2)
        logger.info("语音监听已停止")
        
    def simulate_command(self, command):
        """
        模拟接收语音命令，用于测试
        
        Args:
            command (str): 模拟的语音命令
        """
        if self.command_callback:
            self.command_callback(command)

if __name__ == "__main__":
    # 测试代码
    def command_callback(command):
        print(f"接收到命令: {command}")
        
    listener = VoiceCommandListener()
    listener.set_command_callback(command_callback)
    listener.start_listening()
    
    # 运行10秒用于测试
    time.sleep(10)
    
    listener.stop_listening()
    print("测试完成")