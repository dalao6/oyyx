# modules/retrieval/knowledge_retrieval.py
from typing import List, Dict
import numpy as np

class KnowledgeRetrieval:
    """
    知识检索模块：基于语义向量或关键词匹配。
    """
    def __init__(self, knowledge_base: List[Dict[str, str]], embedder):
        """
        knowledge_base: [{'title': 'xx', 'content': 'xxx'}, ...]
        embedder: 文本向量模型
        """
        self.knowledge_base = knowledge_base
        self.embedder = embedder
        self.embeddings = [embedder(k['content']) for k in knowledge_base]

    def search(self, query: str, top_k: int = 3):
        query_vec = self.embedder(query)
        sims = [self._cosine_similarity(query_vec, e) for e in self.embeddings]
        ranked = sorted(zip(self.knowledge_base, sims), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    @staticmethod
    def _cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
