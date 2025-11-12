"""
Find Something 包初始化文件

该包提供了一个完整的购物辅助系统，包含以下模块：
- camera_capture: 摄像头捕获模块
- vlm_inference: VLM模型推理模块
- gui_display: GUI显示模块
- voice_command: 语音命令处理模块
- controller: 系统控制器模块
- main_find: 主入口模块

作者: Assistant
版本: 1.0
"""

# 从各个模块导入主要类
from .camera_capture import CameraCapture
from .vlm_inference import VLMInference
from .gui_display import GUIDisplay
from .voice_command import VoiceCommandListener
from .controller import FindSomethingController

# 定义包的公开接口
__all__ = [
    "CameraCapture",
    "VLMInference", 
    "GUIDisplay",
    "VoiceCommandListener",
    "FindSomethingController"
]

# 包版本信息
__version__ = "1.0"
__author__ = "Assistant"