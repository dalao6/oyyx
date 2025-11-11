# utils_logger.py
import logging
import os
from datetime import datetime

def get_logger(name="DuoMotai", log_dir="logs"):
    """创建或获取一个日志记录器"""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{name}_{datetime.now():%Y%m%d_%H%M%S}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 文件日志
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    fh.setFormatter(file_fmt)

    # 控制台日志
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(console_fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
