"""
embedding_utils.py
统一封装阿里云百炼 Embedding 与常用向量工具
"""

from typing import Any

from openai import OpenAI
from app.core.config import settings
from app.utils.retry import run_with_retry
from app.utils.cache import TTLCache
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# 初始化百炼 Embedding 客户端
embedding_client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url=settings.dashscope_base_url
)

_embedding_cache = TTLCache(ttl_seconds=settings.cache_ttl)


def get_embedding(text: str) -> list[float]:
    """生成文本的 embedding 向量"""
    cached = _embedding_cache.get(text)
    if cached is not None:
        return cached

    resp = run_with_retry(
        embedding_client.embeddings.create,
        model=settings.dashscope_embedding_model,
        input=text,
    )
    embedding = resp.data[0].embedding
    _embedding_cache.set(text, embedding)
    return embedding


def compute_similarity(vec1, vec2) -> float:
    """计算两个 embedding 向量的余弦相似度"""
    v1 = np.array(vec1).reshape(1, -1)
    v2 = np.array(vec2).reshape(1, -1)
    return float(cosine_similarity(v1, v2)[0][0])


def get_embedding_cache_stats() -> dict[str, Any]:
    """返回 embedding 缓存统计信息。"""
    return _embedding_cache.stats()
