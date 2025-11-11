# modules/retrieval/vector_retrieval.py
import numpy as np
from typing import List, Tuple

class VectorRetrieval:
    """
    向量检索模块：可用于语义匹配、知识向量、图片特征向量等。
    """
    def __init__(self):
        self.vectors = []
        self.items = []

    def add_item(self, item_id: str, vector: np.ndarray):
        self.items.append(item_id)
        self.vectors.append(vector)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if not self.vectors:
            return []
        sims = [self._cosine_similarity(query_vec, v) for v in self.vectors]
        ranked = sorted(zip(self.items, sims), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    @staticmethod
    def _cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def clear(self):
        self.vectors.clear()
        self.items.clear()
