# modules/vision/vision_utils.py
import os
from PIL import Image
import cv2
from typing import Dict
from backend.utils_logger import get_logger

logger = get_logger(__name__)

def load_image(image_path: str):
    """
    加载图像文件（返回PIL对象）
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return None
    try:
        image = Image.open(image_path)
        logger.info(f"Loaded image: {image_path}")
        return image
    except Exception as e:
        logger.error(f"Failed to load image {image_path}: {e}")
        return None


def load_video(video_path: str):
    """
    加载视频文件（返回OpenCV VideoCapture对象）
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return None
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return None
    logger.info(f"Loaded video: {video_path}")
    return cap


def get_image_info(image_path: str) -> Dict:
    """
    返回图片的基础信息，如尺寸、格式、模式
    """
    if not os.path.exists(image_path):
        logger.error(f"Image not found: {image_path}")
        return {}
    try:
        img = Image.open(image_path)
        info = {
            "filename": os.path.basename(image_path),
            "format": img.format,
            "mode": img.mode,
            "size": img.size
        }
        logger.debug(f"Image info: {info}")
        return info
    except Exception as e:
        logger.error(f"Error reading image info: {e}")
        return {}
