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
from retrieval.agent import build_agent
from retrieval.index import LocalEmbeddingIndex


BASELINE_QUERY = "retrieval augmented generation large language model"


def _result_payload(result) -> dict[str, Any]:
    return {
        "paper_id": result.paper_id,
        "title": result.title,
        "score": result.score,
        "content_preview": result.content[:260],
    }


def _search(index: LocalEmbeddingIndex) -> list[dict[str, Any]]:
    return [_result_payload(item) for item in index.search(BASELINE_QUERY, top_k=3)]


def _load_dataframe(source_path: Path) -> pd.DataFrame:
    if source_path.suffix.lower() == ".csv":
        return pd.read_csv(source_path).fillna("")
    return pd.read_json(source_path).fillna("")


def _load_or_rebuild(settings, embeddings_path: Path, source_path: Path, label: str) -> tuple[LocalEmbeddingIndex, bool]:
    try:
        return LocalEmbeddingIndex.load(settings, embeddings_path), False
    except Exception as exc:
        print(f"{label} collection could not be loaded from Chroma: {exc}")
        print(f"Rebuilding {label} from {source_path}.")
        df = _load_dataframe(source_path)
        return (
            LocalEmbeddingIndex.build(
                df,
                settings=settings,
                embeddings_output_path=embeddings_path,
            ),
            True,
        )


def _message_to_dict(message: Any) -> dict[str, Any]:
    message_type = getattr(message, "type", message.__class__.__name__)
    content = getattr(message, "content", "")
    tool_calls = getattr(message, "tool_calls", None)
    name = getattr(message, "name", None)
    return {
        "type": str(message_type),
        "class": message.__class__.__name__,
        "name": name,
        "has_tool_calls": bool(tool_calls),
        "tool_calls": tool_calls or [],
        "content_preview": str(content)[:600],
    }


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        if parts:
            return "".join(parts)
    return str(content)


def _has_tool_activity(messages: list[Any]) -> bool:
    for message in messages:
        message_type = str(getattr(message, "type", "")).lower()
        class_name = message.__class__.__name__.lower()
        if getattr(message, "tool_calls", None):
            return True
        if message_type == "tool" or "toolmessage" in class_name:
            return True
    return False


def _write_blocked(output_json: Path, output_report: Path, missing_paths: list[Path]) -> None:
    payload = {
        "status": "blocked",
        "reason": "Repaired clean artifact is missing, so role4 cannot build papers-repaired yet.",
        "missing_required_paths": [str(path) for path in missing_paths],
        "role4_next_step": "Run this script again after role3/role1 creates repaired clean data.",
    }
    write_json(output_json, payload)
    lines = [
        "# CP6 - Vai trò 4: Repaired index check",
        "",
        "## Status",
        "",
        "- BLOCKED",
        "- Reason: repaired clean artifact is missing.",
        "",
        "## Required input from other roles",
        "",
    ]
    lines.extend(f"- `{path}`" for path in missing_paths)
    lines.extend(
        [
            "",
            "Role4 chỉ có thể build `papers-repaired` sau khi role cleaning/repair tạo repaired clean dataset.",
            "",
            "## Role4 CP6 will verify",
            "",
            "- Build/load `papers-repaired` từ repaired clean data.",
            "- Chạy cùng baseline query để so sánh `papers-baseline`, `papers-corrupted`, `papers-repaired`.",
            "- Chạy agent smoke và kiểm tra agent dùng tool trước khi trả lời.",
            "- Xuất rõ ba collection/path tách biệt, tái lập được.",
        ]
    )
    write_text(output_report, "\n".join(lines) + "\n")


def main() -> int:
    settings = load_settings(ROOT)
    output_json = settings.paths.project_dir / "data" / "results" / "role4_cp6_repaired_index_check.json"
    output_report = settings.paths.project_dir / "report" / "role4" / "role4_cp6_repaired_index_check.md"
    repaired_candidates = [
        settings.paths.repaired_clean_csv,
        settings.paths.repaired_clean_json,
        settings.paths.project_dir / "data" / "clean" / "repaired_papers.csv",
        settings.paths.project_dir / "data" / "clean" / "repaired_papers.json",
    ]
    repaired_source = next((path for path in repaired_candidates if path.exists()), None)

    required_inputs = [
        settings.paths.clean_csv,
        settings.paths.corrupted_clean_csv,
    ]
    missing_paths = [path for path in required_inputs if not path.exists()]
    if repaired_source is None:
        missing_paths.append(settings.paths.repaired_clean_csv)
    if missing_paths:
        _write_blocked(output_json, output_report, missing_paths)
        print("BLOCKED: repaired/baseline/corrupted clean artifact is missing.")
        for path in missing_paths:
            print(f"Missing: {path}")
        print(f"Wrote JSON: {output_json}")
        print(f"Wrote report: {output_report}")
        return 2

    baseline_index, baseline_rebuilt = _load_or_rebuild(
        settings,
        settings.paths.embeddings_json,
        settings.paths.clean_csv,
        "papers-baseline",
    )
    corrupted_index, corrupted_rebuilt = _load_or_rebuild(
        settings,
        settings.paths.corrupted_embeddings_json,
        settings.paths.corrupted_clean_csv,
        "papers-corrupted",
    )

    assert repaired_source is not None
    repaired_df = _load_dataframe(repaired_source)
    repaired_index = LocalEmbeddingIndex.build(
        repaired_df,
        settings=settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json,
    )

    baseline_results = _search(baseline_index)
    corrupted_results = _search(corrupted_index)
    repaired_results = _search(repaired_index)

    repaired_first = repaired_index.documents[0]
    repaired_lookup = repaired_index.lookup(repaired_first["paper_id"])

    question = f"Who authored '{repaired_first['title']}'?"
    agent = build_agent(settings=settings, index=repaired_index)
    agent_result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = agent_result.get("messages", [])
    final_answer = _message_content_to_text(getattr(messages[-1], "content", "")) if messages else ""
    agent_used_tool = _has_tool_activity(messages)
    tool_messages = [
        _message_to_dict(message)
        for message in messages
        if str(getattr(message, "type", "")).lower() == "tool"
        or "toolmessage" in message.__class__.__name__.lower()
    ]
    agent_returned_repaired_doc = any(repaired_first["paper_id"] in item["content_preview"] for item in tool_messages)

    expected_collections = {
        "baseline": settings.baseline_collection_name,
        "corrupted": settings.corrupted_collection_name,
        "repaired": settings.repaired_collection_name,
    }
    actual_collections = {
        "baseline": baseline_index.collection_name,
        "corrupted": corrupted_index.collection_name,
        "repaired": repaired_index.collection_name,
    }
    collections_ok = actual_collections == expected_collections
    paths_distinct = len(
        {
            str(settings.paths.embeddings_json),
            str(settings.paths.corrupted_embeddings_json),
            str(settings.paths.repaired_embeddings_json),
        }
    ) == 3
    status = "pass" if collections_ok and paths_distinct and repaired_lookup and agent_used_tool and agent_returned_repaired_doc else "fail"

    payload = {
        "status": status,
        "query": BASELINE_QUERY,
        "baseline_rebuilt": baseline_rebuilt,
        "corrupted_rebuilt": corrupted_rebuilt,
        "repaired_source": str(repaired_source),
        "repaired_rows": len(repaired_df),
        "collections": actual_collections,
        "embedding_manifest_paths": {
            "baseline": str(settings.paths.embeddings_json),
            "corrupted": str(settings.paths.corrupted_embeddings_json),
            "repaired": str(settings.paths.repaired_embeddings_json),
        },
        "collections_ok": collections_ok,
        "paths_distinct": paths_distinct,
        "baseline_top_ids": [item["paper_id"] for item in baseline_results],
        "corrupted_top_ids": [item["paper_id"] for item in corrupted_results],
        "repaired_top_ids": [item["paper_id"] for item in repaired_results],
        "baseline_results": baseline_results,
        "corrupted_results": corrupted_results,
        "repaired_results": repaired_results,
        "repaired_lookup": {
            "paper_id": repaired_first["paper_id"],
            "title": repaired_first["title"],
            "found": repaired_lookup is not None,
        },
        "agent_smoke": {
            "llm_provider": settings.llm_provider,
            "llm_model": settings.model_name,
            "question": question,
            "used_tool_before_answer": agent_used_tool,
            "returned_repaired_doc": agent_returned_repaired_doc,
            "final_answer": final_answer,
            "messages": [_message_to_dict(message) for message in messages],
        },
    }
    write_json(output_json, payload)

    lines = [
        "# CP6 - Vai trò 4: Repaired index check",
        "",
        "## Kết quả",
        "",
        f"- Status: {status.upper()}",
        f"- Repaired source: `{repaired_source}`",
        f"- Repaired rows: {len(repaired_df)}",
        f"- Collections OK: `{collections_ok}`",
        f"- Embedding paths distinct: `{paths_distinct}`",
        f"- Agent used tool before answer: `{agent_used_tool}`",
        f"- Agent tool returned repaired doc: `{agent_returned_repaired_doc}`",
        f"- Evidence JSON: `{output_json}`",
        "",
        "## Collections / paths",
        "",
        f"- Baseline: `{baseline_index.collection_name}` -> `{settings.paths.embeddings_json}`",
        f"- Corrupted: `{corrupted_index.collection_name}` -> `{settings.paths.corrupted_embeddings_json}`",
        f"- Repaired: `{repaired_index.collection_name}` -> `{settings.paths.repaired_embeddings_json}`",
        "",
        "## Baseline query",
        "",
        f"`{BASELINE_QUERY}`",
        "",
        "## Baseline top IDs",
        "",
    ]
    lines.extend(f"- `{paper_id}`" for paper_id in payload["baseline_top_ids"])
    lines.extend(["", "## Corrupted top IDs", ""])
    lines.extend(f"- `{paper_id}`" for paper_id in payload["corrupted_top_ids"])
    lines.extend(["", "## Repaired top IDs", ""])
    lines.extend(f"- `{paper_id}`" for paper_id in payload["repaired_top_ids"])
    lines.extend(
        [
            "",
            "## Agent smoke",
            "",
            f"- Question: `{question}`",
            f"- Used tool before answer: `{agent_used_tool}`",
            f"- Tool returned repaired doc: `{agent_returned_repaired_doc}`",
            "",
            "### Final answer",
            "",
            str(final_answer),
        ]
    )
    write_text(output_report, "\n".join(lines) + "\n")

    print(f"Status: {status.upper()}")
    print(f"Repaired collection: {repaired_index.collection_name}")
    print(f"Agent used tool before answer: {agent_used_tool}")
    print(f"Agent returned repaired doc: {agent_returned_repaired_doc}")
    print(f"Wrote JSON: {output_json}")
    print(f"Wrote report: {output_report}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
