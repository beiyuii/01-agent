"""知识库检索接口，提供岗位查询与列表功能。"""

from fastapi import APIRouter, Query, HTTPException

from app.core.config import settings
from app.services import get_vector_store

router = APIRouter(prefix="/kb", tags=["Knowledge base"])

@router.get("/query")
def query_jobs(q: str = Query(..., description="搜索关键词"), top_k: int = 5):
    """按照关键词检索岗位信息。

    Args:
        q (str): 搜索关键词。
        top_k (int): 返回的岗位数量。

    Returns:
        dict: 包含检索关键词与命中结果。
    """

    vector_store = get_vector_store()
    try:
        docs = vector_store.similarity_search(q, k=top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"向量检索失败: {exc}") from exc

    output = []
    for item in docs:
        meta = item.metadata or {}
        output.append({
            "job_id": meta.get("job_id"),
            "company": meta.get("company"),
            "title": meta.get("title"),
            "location": meta.get("location"),
            "deadline": meta.get("deadline"),
            "batch": meta.get("batch"),
            "industry": meta.get("industry"),
            "document": item.page_content,
        })

    return {"query": q, "results": output}


@router.get("/list")
def list_jobs(limit: int = 10):
    """列出向量库中的岗位元数据。

    Args:
        limit (int): 返回记录数量上限。

    Returns:
        list: 岗位 ID 与元数据列表。
    """

    vector_store = get_vector_store()
    try:
        data = vector_store._collection.peek(limit=limit)  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"无法读取向量库: {exc}") from exc
    return [{"id": i, "meta": m} for i, m in zip(data["ids"], data["metadatas"])]
