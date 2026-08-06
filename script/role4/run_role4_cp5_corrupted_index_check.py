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


def _load_or_rebuild_baseline(settings) -> tuple[LocalEmbeddingIndex, bool]:
    try:
        return LocalEmbeddingIndex.load(settings, settings.paths.embeddings_json), False
    except Exception as exc:
        print(f"Baseline collection could not be loaded from Chroma: {exc}")
        print("Rebuilding papers-baseline from clean CSV so CP5 can verify baseline is readable.")
        clean_df = pd.read_csv(settings.paths.clean_csv).fillna("")
        return (
            LocalEmbeddingIndex.build(
                clean_df,
                settings=settings,
                embeddings_output_path=settings.paths.embeddings_json,
            ),
            True,
        )


def main() -> int:
    settings = load_settings(ROOT)
    corrupted_csv = settings.paths.corrupted_clean_csv
    corrupted_json = settings.paths.corrupted_clean_json
    corruption_log_path = settings.paths.corruption_log
    output_json = settings.paths.project_dir / "data" / "results" / "role4_cp5_corrupted_index_check.json"
    output_report = settings.paths.project_dir / "report" / "role4" / "role4_cp5_corrupted_index_check.md"

    if not corrupted_csv.exists() and not corrupted_json.exists():
        blocker = {
            "status": "blocked",
            "reason": "Corrupted clean artifact is missing.",
            "expected_any_of": [str(corrupted_csv), str(corrupted_json)],
            "role4_next_step": "Run this script again after role3/role1 creates corrupted clean data.",
        }
        write_json(output_json, blocker)
        write_text(
            output_report,
            "\n".join(
                [
                    "# CP5 - Vai trò 4: Corrupted index check",
                    "",
                    "## Status",
                    "",
                    "- BLOCKED",
                    "- Reason: corrupted clean artifact is missing.",
                    "",
                    "## Expected input",
                    "",
                    f"- `{corrupted_csv}`",
                    f"- `{corrupted_json}`",
                    "",
                    "Role4 can build `papers-corrupted` only after the corrupted clean dataset exists.",
                ]
            )
            + "\n",
        )
        print("BLOCKED: corrupted clean artifact is missing.")
        print(f"Expected: {corrupted_csv} or {corrupted_json}")
        return 2

    source_path = corrupted_csv if corrupted_csv.exists() else corrupted_json
    if source_path.suffix.lower() == ".csv":
        corrupted_df = pd.read_csv(source_path).fillna("")
    else:
        corrupted_df = pd.read_json(source_path).fillna("")

    print(f"Loaded corrupted clean data: {source_path}")
    print(f"Rows: {len(corrupted_df)}")

    baseline_index, baseline_rebuilt_before_check = _load_or_rebuild_baseline(settings)
    baseline_results = _search(baseline_index)

    corrupted_index = LocalEmbeddingIndex.build(
        corrupted_df,
        settings=settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json,
    )
    corrupted_results = _search(corrupted_index)

    baseline_reloaded, baseline_rebuilt_after_corrupted_build = _load_or_rebuild_baseline(settings)
    baseline_after_results = _search(baseline_reloaded)

    baseline_still_readable = baseline_reloaded.collection_name == settings.baseline_collection_name
    baseline_top_ids_before = [item["paper_id"] for item in baseline_results]
    baseline_top_ids_after = [item["paper_id"] for item in baseline_after_results]
    baseline_not_mutated = baseline_top_ids_before == baseline_top_ids_after

    corruption_log = read_json(corruption_log_path) if corruption_log_path.exists() else {}
    dropped_ids = [
        event["record_id"]
        for event in corruption_log.get("events", [])
        if event.get("type") == "drop_latest_record"
    ]
    dropped_lookup_examples = []
    for paper_id in dropped_ids[:3]:
        baseline_record = baseline_reloaded.lookup(paper_id)
        corrupted_record = corrupted_index.lookup(paper_id)
        dropped_lookup_examples.append(
            {
                "paper_id": paper_id,
                "baseline_lookup_found": baseline_record is not None,
                "corrupted_lookup_found": corrupted_record is not None,
                "baseline_title": baseline_record["title"] if baseline_record else "",
            }
        )

    payload = {
        "status": "pass" if baseline_still_readable and baseline_not_mutated else "fail",
        "query": BASELINE_QUERY,
        "corrupted_source": str(source_path),
        "corrupted_rows": len(corrupted_df),
        "baseline_collection": baseline_reloaded.collection_name,
        "corrupted_collection": corrupted_index.collection_name,
        "baseline_rebuilt_before_check": baseline_rebuilt_before_check,
        "baseline_rebuilt_after_corrupted_build": baseline_rebuilt_after_corrupted_build,
        "baseline_still_readable": baseline_still_readable,
        "baseline_not_mutated": baseline_not_mutated,
        "baseline_results_before": baseline_results,
        "corrupted_results": corrupted_results,
        "baseline_results_after": baseline_after_results,
        "baseline_top_ids_before": baseline_top_ids_before,
        "corrupted_top_ids": [item["paper_id"] for item in corrupted_results],
        "baseline_top_ids_after": baseline_top_ids_after,
        "dropped_lookup_examples": dropped_lookup_examples,
    }
    write_json(output_json, payload)

    lines = [
        "# CP5 - Vai trò 4: Corrupted index check",
        "",
        "## Kết quả",
        "",
        f"- Status: {payload['status'].upper()}",
        f"- Corrupted source: `{source_path}`",
        f"- Corrupted rows: {len(corrupted_df)}",
        f"- Baseline collection: `{baseline_reloaded.collection_name}`",
        f"- Corrupted collection: `{corrupted_index.collection_name}`",
        f"- Baseline rebuilt before check: `{baseline_rebuilt_before_check}`",
        f"- Baseline rebuilt after corrupted build: `{baseline_rebuilt_after_corrupted_build}`",
        f"- Baseline still readable: `{baseline_still_readable}`",
        f"- Baseline not mutated: `{baseline_not_mutated}`",
        "",
        "## Baseline query",
        "",
        f"`{BASELINE_QUERY}`",
        "",
        "## Baseline top IDs before",
        "",
    ]
    lines.extend(f"- `{paper_id}`" for paper_id in baseline_top_ids_before)
    lines.extend(["", "## Corrupted top IDs", ""])
    lines.extend(f"- `{paper_id}`" for paper_id in payload["corrupted_top_ids"])
    lines.extend(["", "## Baseline top IDs after", ""])
    lines.extend(f"- `{paper_id}`" for paper_id in baseline_top_ids_after)
    lines.extend(["", "## Dropped-record lookup check", ""])
    if dropped_lookup_examples:
        for item in dropped_lookup_examples:
            lines.append(
                f"- `{item['paper_id']}` baseline_found=`{item['baseline_lookup_found']}`, "
                f"corrupted_found=`{item['corrupted_lookup_found']}`"
            )
    else:
        lines.append("- No `drop_latest_record` events found in corruption log.")
    write_text(output_report, "\n".join(lines) + "\n")

    print(f"Status: {payload['status'].upper()}")
    print(f"Corrupted collection: {corrupted_index.collection_name}")
    print(f"Baseline still readable: {baseline_still_readable}")
    print(f"Baseline not mutated: {baseline_not_mutated}")
    print(f"Wrote JSON: {output_json}")
    print(f"Wrote report: {output_report}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
