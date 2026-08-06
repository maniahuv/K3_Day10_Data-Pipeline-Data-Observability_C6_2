from __future__ import annotations

import hashlib
from functools import lru_cache
from typing import Any


class EmbeddingsBase:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


@lru_cache(maxsize=4)
def _fallback_embedding(text: str) -> tuple[float, ...]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = []
    for byte in digest:
        values.append(byte / 255.0)
    return tuple(values)


class MiniLMEmbeddings(EmbeddingsBase):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def _embed_text(self, text: str) -> list[float]:
        vector = list(_fallback_embedding(text))
        # Normalize to unit length to keep retrieval scores stable enough.
        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return [0.0] * len(vector)
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_text(text)
