# backend/__init__.py

from .config import *
from .utils_logger import setup_logger

# 初始化日志系统
logger = setup_logger("DuoMotai")
logger.info("✅ Backend 初始化完成。")
