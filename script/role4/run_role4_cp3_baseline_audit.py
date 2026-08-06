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
from core.utils import read_json, write_json, write_text
from retrieval.index import LocalEmbeddingIndex


def _search_payload(result) -> dict[str, Any]:
    return {
        "paper_id": result.paper_id,
        "title": result.title,
        "score": result.score,
        "content_preview": result.content[:300],
    }


def main() -> int:
    settings = load_settings(ROOT)
    clean_path = settings.paths.clean_csv
    manifest_path = settings.paths.embeddings_json
    agent_smoke_path = settings.paths.project_dir / "data" / "results" / "role4_cp2_agent_smoke.json"

    if not clean_path.exists():
        print(f"Missing clean CSV: {clean_path}")
        return 1
    if not manifest_path.exists():
        print(f"Missing embedding manifest: {manifest_path}")
        return 1

    clean_df = pd.read_csv(clean_path).fillna("")
    manifest = read_json(manifest_path)
    documents = manifest.get("documents", [])

    clean_ids = [str(item).lower() for item in clean_df["paper_id"].tolist()]
    manifest_ids = [str(document["paper_id"]).lower() for document in documents]
    missing_from_manifest = sorted(set(clean_ids) - set(manifest_ids))
    extra_in_manifest = sorted(set(manifest_ids) - set(clean_ids))

    index = LocalEmbeddingIndex.load(settings)
    query = "retrieval augmented generation large language model"
    search_results = index.search(query, top_k=3)
    first_doc = index.documents[0]
    lookup_by_id = index.lookup(first_doc["paper_id"])
    lookup_by_title = index.lookup(first_doc["title"])

    agent_evidence = read_json(agent_smoke_path) if agent_smoke_path.exists() else {}
    agent_used_tool = bool(agent_evidence.get("used_tool_before_answer"))
    agent_status = agent_evidence.get("status")

    checks = {
        "clean_rows": len(clean_df),
        "manifest_documents": len(documents),
        "row_count_matches": len(clean_df) == len(documents),
        "paper_ids_match": not missing_from_manifest and not extra_in_manifest,
        "manifest_collection_name": manifest.get("collection_name"),
        "expected_collection_name": settings.baseline_collection_name,
        "collection_name_matches": manifest.get("collection_name") == settings.baseline_collection_name,
        "loaded_collection_name": index.collection_name,
        "loaded_collection_matches": index.collection_name == settings.baseline_collection_name,
        "embedding_model": manifest.get("embedding_model"),
        "expected_embedding_model": settings.embedding_model,
        "embedding_model_matches": manifest.get("embedding_model") == settings.embedding_model,
        "semantic_search_has_results": bool(search_results),
        "lookup_by_paper_id_passed": lookup_by_id is not None and lookup_by_id["paper_id"] == first_doc["paper_id"],
        "lookup_by_title_passed": lookup_by_title is not None and lookup_by_title["paper_id"] == first_doc["paper_id"],
        "agent_smoke_status": agent_status,
        "agent_used_tool_before_answer": agent_used_tool,
    }
    status = "pass" if all(
        [
            checks["row_count_matches"],
            checks["paper_ids_match"],
            checks["collection_name_matches"],
            checks["loaded_collection_matches"],
            checks["embedding_model_matches"],
            checks["semantic_search_has_results"],
            checks["lookup_by_paper_id_passed"],
            checks["lookup_by_title_passed"],
            agent_status == "pass",
            agent_used_tool,
        ]
    ) else "fail"

    payload = {
        "status": status,
        "checks": checks,
        "missing_from_manifest": missing_from_manifest,
        "extra_in_manifest": extra_in_manifest,
        "semantic_search_demo": {
            "query": query,
            "top_k": 3,
            "results": [_search_payload(item) for item in search_results],
        },
        "exact_lookup_demo": {
            "paper_id": first_doc["paper_id"],
            "title": first_doc["title"],
            "lookup_by_paper_id": lookup_by_id,
            "lookup_by_title": lookup_by_title,
        },
        "agent_evidence_path": str(agent_smoke_path),
    }

    output_json = settings.paths.project_dir / "data" / "results" / "role4_cp3_baseline_audit.json"
    write_json(output_json, payload)

    output_report = settings.paths.project_dir / "report" / "role4" / "role4_cp3_baseline_audit.md"
    lines = [
        "# CP3 - Vai trò 4: Baseline RAG audit",
        "",
        "## Kết quả",
        "",
        f"- Status: {status.upper()}",
        f"- Clean rows: {len(clean_df)}",
        f"- Manifest documents: {len(documents)}",
        f"- Collection: `{index.collection_name}`",
        f"- Embedding model: `{manifest.get('embedding_model')}`",
        f"- JSON evidence: `{output_json}`",
        "",
        "## Audit manifest/index",
        "",
        f"- Row count matches: `{checks['row_count_matches']}`",
        f"- Paper IDs match: `{checks['paper_ids_match']}`",
        f"- Collection name matches `papers-baseline`: `{checks['collection_name_matches']}`",
        f"- Loaded Chroma collection matches: `{checks['loaded_collection_matches']}`",
        f"- Embedding model matches settings: `{checks['embedding_model_matches']}`",
        "",
        "## Demo semantic search",
        "",
        f"- Query: `{query}`",
    ]
    for rank, item in enumerate(search_results, start=1):
        lines.append(f"- Top {rank}: `{item.paper_id}` | score={item.score:.4f} | {item.title}")

    lines.extend(
        [
            "",
            "## Demo exact lookup",
            "",
            f"- Lookup paper_id `{first_doc['paper_id']}`: `{'PASS' if checks['lookup_by_paper_id_passed'] else 'FAIL'}`",
            f"- Lookup exact title: `{'PASS' if checks['lookup_by_title_passed'] else 'FAIL'}`",
            "",
            "## Agent factual answer evidence",
            "",
            f"- Agent smoke status: `{agent_status}`",
            f"- Used tool before answer: `{agent_used_tool}`",
            f"- Evidence path: `{agent_smoke_path}`",
            "",
            "## Ghi chú",
            "",
            "CP3 role4 chỉ audit baseline RAG artifacts và demo retrieval/agent evidence. Baseline metrics/report toàn pipeline phụ thuộc role evaluation/observability/integrator.",
        ]
    )
    write_text(output_report, "\n".join(lines) + "\n")

    print(f"Status: {status.upper()}")
    print(f"Clean rows: {len(clean_df)}")
    print(f"Manifest docs: {len(documents)}")
    print(f"Collection: {index.collection_name}")
    print(f"Semantic search top1: {search_results[0].paper_id} | {search_results[0].title}")
    print(f"Lookup by paper_id: {checks['lookup_by_paper_id_passed']}")
    print(f"Lookup by title: {checks['lookup_by_title_passed']}")
    print(f"Agent used tool before answer: {agent_used_tool}")
    print(f"Wrote JSON: {output_json}")
    print(f"Wrote report: {output_report}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
