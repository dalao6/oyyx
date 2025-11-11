# modules/retrieval/image_retrieval.py
import os
import logging
import torch
from PIL import Image
import numpy as np

# 确保 open_clip 已安装
import open_clip

# -----------------------------
# 日志配置
# -----------------------------
logger = logging.getLogger("ImageRetrieval")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ImageRetrieval:
    def __init__(self, image_dir: str, model_path: str, device: str = "cuda"):
        self.image_dir = image_dir
        self.model_path = model_path
        self.device = device if torch.cuda.is_available() else "cpu"

        self.model = None
        self.preprocess = None
        self.image_embeddings = {}
        self.image_paths = []

        self._load_model()
        self._index_images()

    def _load_model(self):
        try:
            logger.info(f"[ImageRetrieval] 🚀 使用设备: {self.device}")
            outputs = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained=self.model_path, device=self.device
            )
            if len(outputs) == 3:
                self.model, _, self.preprocess = outputs
            else:
                self.model, self.preprocess = outputs
            self.model.eval()
            logger.info(f"[ImageRetrieval] ✅ 模型加载成功: {self.model_path}")
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.warning(
                    f"[ImageRetrieval] ⚠️ CUDA 显存不足，自动切换为 CPU 模式: {e}"
                )
                self.device = "cpu"
                torch.cuda.empty_cache()
                outputs = open_clip.create_model_and_transforms(
                    "ViT-B-32", pretrained=self.model_path, device=self.device
                )
                if len(outputs) == 3:
                    self.model, _, self.preprocess = outputs
                else:
                    self.model, self.preprocess = outputs
                self.model.eval()
            else:
                logger.error(f"[ImageRetrieval] ❌ 模型加载失败: {e}")
                raise e

    def _index_images(self):
        """将 image_dir 下所有图片进行特征提取"""
        if not os.path.exists(self.image_dir):
            logger.warning(f"[ImageRetrieval] ⚠️ 图片目录不存在: {self.image_dir}")
            return

        self.image_paths = [
            os.path.join(self.image_dir, f)
            for f in os.listdir(self.image_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not self.image_paths:
            logger.warning("[ImageRetrieval] ⚠️ 未找到图片用于索引")
            return

        logger.info(f"[ImageRetrieval] 🔹 索引 {len(self.image_paths)} 张图片...")

        with torch.no_grad():
            for path in self.image_paths:
                try:
                    img = Image.open(path).convert("RGB")
                    img_tensor = self.preprocess(img).unsqueeze(0).to(self.device)
                    embedding = self.model.encode_image(img_tensor)
                    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
                    self.image_embeddings[path] = embedding.cpu()
                except Exception as e:
                    logger.warning(f"[ImageRetrieval] ⚠️ 图片索引失败: {path}, {e}")

        logger.info("[ImageRetrieval] ✅ 图片索引完成")

    def search(self, query: str, top_k: int = 1):
        """根据文本 query 检索图片"""
        if not self.image_embeddings:
            logger.warning("[ImageRetrieval] ⚠️ 尚未有图片索引，无法检索")
            return []

        try:
            with torch.no_grad():
                text_tokens = open_clip.tokenize([query]).to(self.device)
                text_embedding = self.model.encode_text(text_tokens)
                text_embedding = text_embedding / text_embedding.norm(dim=-1, keepdim=True)

                scores = {}
                for path, img_emb in self.image_embeddings.items():
                    score = (img_emb.to(self.device) @ text_embedding.T).item()
                    scores[path] = score

                # 按相似度排序
                sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                top_results = [{"image": path, "score": score} for path, score in sorted_results[:top_k]]
                logger.info(f"[ImageRetrieval] ✅ 检索完成, query='{query}', top_k={top_k}")
                return top_results

        except Exception as e:
            logger.error(f"[ImageRetrieval] ❌ 检索失败: {e}")
            return []


