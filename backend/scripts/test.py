"""中文命令行工具：便捷查询 Chroma 向量库中的招聘信息。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import chromadb
from openai import OpenAI


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings


def _build_chroma_collection() -> chromadb.api.models.Collection:
    """返回指向项目默认集合的 Chroma collection 实例。"""

    client = chromadb.PersistentClient(path=str(settings.chroma_persist_directory))
    return client.get_or_create_collection(name=settings.chroma_collection_name)


def _build_dashscope_client() -> OpenAI:
    """构造 DashScope OpenAI 客户端，用于生成查询向量。"""

    return OpenAI(api_key=settings.dashscope_api_key, base_url=settings.dashscope_base_url)


def _generate_embedding(client: OpenAI, text: str) -> list[float]:
    response = client.embeddings.create(model="text-embedding-v3", input=text)
    return response.data[0].embedding


def _query_jobs(query: str, top_k: int) -> None:
    collection = _build_chroma_collection()
    dashscope_client = _build_dashscope_client()

    embedding = _generate_embedding(dashscope_client, query)
    results = collection.query(query_embeddings=[embedding], n_results=max(top_k, 1))

    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:
        print("⚠️ 未检索到任何结果，请尝试调整关键词或确认向量库是否已建立。")
        return

    print("🔍 查询结果：")
    for index, (doc, meta) in enumerate(zip(documents[0], metadatas[0]), start=1):
        title = meta.get("title", "(未命名职位)")
        company = meta.get("company", "(未知公司)")
        location = meta.get("location", "(未知地点)")
        deadline = meta.get("deadline", "(未提供截止日期)")

        snippet = (doc or "")[:180]
        print(f"{index}. {title} @ {company} - {location} 截止：{deadline}")
        print("   片段：", snippet)
        print("-" * 40)


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="在命令行里查询向量化的岗位文本")
    parser.add_argument("query", nargs="?", default="找后端工程师岗位", help="要检索的中文关键词")
    parser.add_argument("--top-k", type=int, default=3, metavar="N", help="显示前 N 条结果，默认 3 条")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = _parse_args(argv)
    try:
        _query_jobs(query=args.query, top_k=args.top_k)
    except Exception as exc:  # pragma: no cover - 保障 CLI 友好输出
        print("❌ 检索失败：", exc)


if __name__ == "__main__":  # pragma: no cover - 命令行入口
    main()
