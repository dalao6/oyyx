# modules/vision/vision_display.py
import os
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from backend.utils_logger import get_logger

logger = get_logger(__name__)

class VisionDisplay:
    """
    负责图像与视频的展示与输出。
    该类可用于GUI弹窗或直接在PyCharm中查看可视化内容。
    """

    def __init__(self, image_dir: str = None, video_dir: str = None):
        if image_dir is None:
            image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data/product_images")
        if video_dir is None:
            video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data/product_videos")
            
        self.image_dir = image_dir
        self.video_dir = video_dir

    def show_image(self, image_path: str):
        """
        展示指定图片路径的图像
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return

        image = Image.open(image_path)
        plt.imshow(image)
        plt.axis('off')
        plt.title(f"Displaying: {os.path.basename(image_path)}")
        plt.show()
        logger.info(f"Displayed image: {image_path}")

    def show_video(self, video_path: str):
        """
        播放视频（OpenCV）
        """
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("Cannot open video file.")
            return

        logger.info(f"Playing video: {video_path}")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Video Player", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def display_product(self, product_name: str):
        """
        按产品名显示图片或视频
        """
        img_path = os.path.join(self.image_dir, f"{product_name}.jpg")
        vid_path = os.path.join(self.video_dir, f"{product_name}.mp4")

        if os.path.exists(img_path):
            self.show_image(img_path)
        elif os.path.exists(vid_path):
            self.show_video(vid_path)
        else:
            logger.warning(f"No visual file found for {product_name}.")