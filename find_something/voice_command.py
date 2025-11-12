#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音命令监听模块（ASR）
"""

import logging
import threading
import time

class VoiceCommandListener:
    """
    语音命令监听类，负责监听并识别用户的语音命令
    """
    
    def __init__(self, model_path="/mnt/data/modelscope_cache/hub/xiaowangge/sherpa-onnx-sense-voice-small"):
        """
        初始化语音命令监听模块
        
        Args:
            model_path (str): ASR模型路径
        """
        self.model_path = model_path
        self.is_listening = False
        self.asr_model = None
        self.callback = None
        self.listen_thread = None
        self.load_asr_model()
        
    def set_command_callback(self, callback):
        """
        设置语音命令回调函数
        
        Args:
            callback (function): 回调函数，接收识别到的命令作为参数
        """
        self.callback = callback
        
    def load_asr_model(self):
        """
        加载ASR模型
        """
        # 检查模型路径是否存在
        try:
            # TODO: 实际加载模型
            # 这里应该使用实际的模型加载方法
            logging.info(f"正在加载ASR模型: {self.model_path}")
            # 模拟模型加载
            self.asr_model = object()  # 占位符
            logging.info("ASR模型加载完成")
        except Exception as e:
            logging.error(f"加载ASR模型失败: {e}")
        
    def start_listening(self):
        """
        开始监听语音命令
        """
        if not self.is_listening:
            self.is_listening = True
            # 在单独的线程中进行监听，避免阻塞主线程
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            logging.info("语音监听已启动")
        
    def stop_listening(self):
        """
        停止监听语音命令
        """
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)  # 等待线程结束，最多等待2秒
        logging.info("语音监听已停止")
        
    def _listen_loop(self):
        """
        语音监听循环
        """
        logging.info("开始语音监听循环")
        while self.is_listening:
            # 模拟获取音频数据
            audio_data = self._capture_audio()
            if audio_data is not None:
                # 识别语音内容
                command = self.recognize_speech(audio_data)
                if command and self.callback:
                    self.callback(command)
            
            # 控制监听频率
            time.sleep(0.1)
            
    def _capture_audio(self):
        """
        捕获音频数据（模拟实现）
        
        Returns:
            bytes: 音频数据
        """
        # 在实际实现中，这里应该从麦克风捕获音频数据
        # 目前只是模拟，随机返回一些数据
        import random
        if random.random() < 0.01:  # 1%概率返回"有效"音频
            return b"audio_data"
        return None
        
    def recognize_speech(self, audio_data):
        """
        识别语音内容
        
        Args:
            audio_data: 音频数据
            
        Returns:
            str: 识别出的文本
        """
        # 在实际实现中，这里应该使用ASR模型识别音频内容
        # 目前是模拟实现，随机返回一些命令
        import random
        commands = ["我不要了", "查找", "搜索", "退出", "停止", "返回主页面", None]
        recognized_text = random.choice(commands)
        if recognized_text:
            logging.info(f"识别到语音命令: {recognized_text}")
        return recognized_text

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