from fastapi import APIRouter

from app.services.embedding_utils import get_embedding_cache_stats
from app.api.routes_match import get_match_cache_stats

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"status": "ok"}


@router.get("/diagnostics/cache")
async def cache_diagnostics():
    """返回服务端缓存命中情况，便于观察策略效果。"""
    return {
        "embedding": get_embedding_cache_stats(),
        "match": get_match_cache_stats(),
    }
