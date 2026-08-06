from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from core.config import load_settings
from core.utils import write_json, write_text
from retrieval.index import LocalEmbeddingIndex
from retrieval.qa import answer_question


def _pick_query(df: pd.DataFrame) -> str:
    title = str(df.iloc[0]["title"])
    if "retrieval" in title.lower() or "rag" in title.lower():
        return "retrieval augmented generation large language model"
    return "large language model agent retrieval"


def _summarize_result(result) -> dict[str, Any]:
    return {
        "paper_id": result.paper_id,
        "title": result.title,
        "score": result.score,
        "content_preview": result.content[:260],
    }


def main() -> int:
    settings = load_settings(ROOT)
    clean_path = settings.paths.clean_csv
    if not clean_path.exists():
        print(f"Missing clean CSV: {clean_path}")
        return 1

    df = pd.read_csv(clean_path).fillna("")
    print(f"Loaded clean dataframe: {clean_path}")
    print(f"Rows: {len(df)}")

    print("\nBuilding baseline MiniLM embeddings + Chroma collection...")
    index = LocalEmbeddingIndex.build(
        df,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json,
    )
    print(f"Built collection: {index.collection_name}")
    print(f"Persist path: {index.persist_path}")
    print(f"Manifest: {settings.paths.embeddings_json}")

    query = _pick_query(df)
    search_results = index.search(query, top_k=3)
    if not search_results:
        print("Semantic search returned no results.")
        return 1

    first_doc = index.documents[0]
    lookup_by_id = index.lookup(first_doc["paper_id"])
    lookup_by_title = index.lookup(first_doc["title"])
    if lookup_by_id is None:
        print("Lookup by paper_id failed.")
        return 1
    if lookup_by_title is None:
        print("Lookup by exact title failed.")
        return 1

    qa_question = f"What is the paper '{first_doc['title']}' about?"
    qa_result = answer_question(qa_question, settings=settings, index=index)
    if not qa_result.retrieved_doc_ids:
        print("QA smoke test retrieved no documents.")
        return 1

    smoke_payload = {
        "status": "pass",
        "clean_rows": len(df),
        "embedding_model": settings.embedding_model,
        "embedding_backend": index.embedding_backend,
        "collection_name": index.collection_name,
        "persist_path": str(index.persist_path),
        "embeddings_manifest": str(settings.paths.embeddings_json),
        "semantic_search": {
            "query": query,
            "top_k": 3,
            "results": [_summarize_result(item) for item in search_results],
        },
        "lookup": {
            "paper_id": first_doc["paper_id"],
            "title": first_doc["title"],
            "lookup_by_paper_id_passed": lookup_by_id["paper_id"] == first_doc["paper_id"],
            "lookup_by_title_passed": lookup_by_title["paper_id"] == first_doc["paper_id"],
        },
        "qa_smoke": {
            "question": qa_question,
            "answer": qa_result.answer,
            "retrieved_doc_ids": qa_result.retrieved_doc_ids,
            "retrieved_titles": qa_result.retrieved_titles,
        },
    }

    smoke_path = settings.paths.project_dir / "data" / "results" / "role4_cp2_smoke.json"
    write_json(smoke_path, smoke_payload)

    report_path = settings.paths.project_dir / "report" / "role4" / "role4_cp2_rag_smoke.md"
    lines = [
        "# CP2 - Vai trò 4: RAG index & smoke test",
        "",
        "## Kết quả",
        "",
        "- Status: PASS",
        f"- Clean rows: {len(df)}",
        f"- Embedding model: `{settings.embedding_model}`",
        f"- Chroma collection: `{index.collection_name}`",
        f"- Persist path: `{index.persist_path}`",
        f"- Embedding manifest: `{settings.paths.embeddings_json}`",
        f"- Smoke artifact: `{smoke_path}`",
        "",
        "## Semantic search",
        "",
        f"- Query: `{query}`",
    ]
    for rank, item in enumerate(search_results, start=1):
        lines.append(f"- Top {rank}: `{item.paper_id}` | score={item.score:.4f} | {item.title}")

    lines.extend(
        [
            "",
            "## Exact lookup",
            "",
            f"- Lookup by paper_id: {'PASS' if lookup_by_id else 'FAIL'}",
            f"- Lookup by exact title: {'PASS' if lookup_by_title else 'FAIL'}",
            f"- Tested paper_id: `{first_doc['paper_id']}`",
            "",
            "## QA smoke test",
            "",
            f"- Question: `{qa_question}`",
            f"- Retrieved first doc: `{qa_result.retrieved_doc_ids[0]}`",
            f"- Answer preview: {qa_result.answer[:300]}",
            "",
            "## Ghi chú",
            "",
            "CP2 đã build baseline collection thật. Agent LLM thật có thể test sau khi provider key trong `.env` sẵn sàng; smoke test hiện dùng retrieval + QA rule-based nên không cần API key.",
        ]
    )
    write_text(report_path, "\n".join(lines) + "\n")

    print("\nSemantic search results:")
    for rank, item in enumerate(search_results, start=1):
        print(f"{rank}. {item.paper_id} | score={item.score:.4f} | {item.title}")

    print("\nLookup:")
    print(f"paper_id lookup: PASS ({lookup_by_id['paper_id']})")
    print(f"title lookup: PASS ({lookup_by_title['paper_id']})")

    print("\nQA smoke:")
    print(f"question: {qa_question}")
    print(f"retrieved_doc_ids: {qa_result.retrieved_doc_ids}")
    print(f"answer: {qa_result.answer[:300]}")

    print(f"\nWrote smoke JSON: {smoke_path}")
    print(f"Wrote report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
