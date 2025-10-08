"""LangChain helpers for DashScope embeddings and shared Chroma vector store."""

from __future__ import annotations

from typing import Iterable, List, Optional

from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI

from app.core.config import settings
from app.utils.retry import run_with_retry


class DashscopeEmbeddings(Embeddings):
    """LangChain embeddings wrapper around DashScope-compatible OpenAI client."""

    def __init__(self, model: Optional[str] = None) -> None:
        self._client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )
        self._model = model or settings.dashscope_embedding_model

    def embed_documents(self, texts: Iterable[str]) -> List[List[float]]:
        batch = list(texts)
        if not batch:
            return []
        embeddings: List[List[float]] = []
        max_batch = 10
        for start in range(0, len(batch), max_batch):
            chunk = batch[start : start + max_batch]
            response = run_with_retry(
                self._client.embeddings.create,
                model=self._model,
                input=chunk,
            )
            embeddings.extend(item.embedding for item in response.data)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = run_with_retry(
            self._client.embeddings.create,
            model=self._model,
            input=text,
        )
        return response.data[0].embedding


def get_vector_store(
    embedding_model: Optional[str] = None,
    persist_directory: Optional[str] = None,
) -> Chroma:
    """Return a persistent Chroma store configured for this project."""

    embeddings = DashscopeEmbeddings(model=embedding_model)
    directory = persist_directory or str(settings.chroma_persist_directory)
    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=embeddings,
        persist_directory=directory,
    )
