from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


project_dir = Path(__file__).resolve().parents[1]
src_dir = project_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.config import load_settings
from core.utils import read_json, write_json
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report


def _read_json_if_exists(path: Path) -> dict:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def _numeric_delta(baseline: object, corrupted: object) -> dict:
    if not isinstance(baseline, (int, float)) or not isinstance(corrupted, (int, float)):
        return {"baseline": baseline, "corrupted": corrupted, "delta": None, "status": "not_evaluated"}
    delta = float(corrupted) - float(baseline)
    if abs(delta) < 1e-12:
        status = "unchanged"
    elif delta < 0:
        status = "decreased"
    else:
        status = "increased"
    return {
        "baseline": baseline,
        "corrupted": corrupted,
        "delta": delta,
        "status": status,
    }


def main() -> None:
    settings = load_settings(project_dir)

    if not settings.paths.corrupted_clean_json.exists():
        raise FileNotFoundError(
            f"Corrupted dataset not found: {settings.paths.corrupted_clean_json}"
        )
    if not settings.paths.baseline_metrics.exists():
        raise FileNotFoundError(
            f"Baseline metrics not found: {settings.paths.baseline_metrics}"
        )
    if not settings.paths.corrupted_metrics.exists():
        raise FileNotFoundError(
            f"Corrupted metrics not found: {settings.paths.corrupted_metrics}"
        )

    corrupted_df = pd.read_json(settings.paths.corrupted_clean_json, orient="records")
    corrupted_quality = run_data_quality_checks(
        corrupted_df,
        settings,
        report_name="corrupted_quality",
    )
    corrupted_freshness = build_freshness_report(
        corrupted_df,
        settings,
        report_path=settings.paths.quality_dir / "corrupted_freshness_report.json",
    )

    baseline_quality = _read_json_if_exists(settings.paths.quality_dir / "baseline_quality.json")
    baseline_freshness = _read_json_if_exists(settings.paths.freshness_report)
    corruption_log = _read_json_if_exists(settings.paths.corruption_log)

    corrupted_quality["baseline_row_count"] = baseline_quality.get("row_count")
    corrupted_quality["baseline_paper_id_uniqueness"] = baseline_quality.get(
        "paper_id_uniqueness",
        {},
    )
    corrupted_quality["baseline_missing_fields"] = baseline_quality.get("missing_fields", {})
    corrupted_quality["baseline_row_duplicates"] = baseline_quality.get("row_duplicates", {})
    corrupted_quality["baseline_age_days"] = baseline_quality.get("age_days", {})
    corrupted_quality["corruption_counts_by_type"] = corruption_log.get("counts_by_type", {})
    corrupted_quality["corruption_event_count"] = len(corruption_log.get("events", []))

    corrupted_freshness["baseline_stale_rows"] = baseline_freshness.get("stale_rows")
    corrupted_freshness["baseline_is_fresh"] = baseline_freshness.get("is_fresh")

    baseline_metrics = _read_json_if_exists(settings.paths.baseline_metrics)
    corrupted_metrics = _read_json_if_exists(settings.paths.corrupted_metrics)

    evidence_path = settings.paths.quality_dir / "corrupted_signal_evidence.json"
    evidence_payload = {
        "artifact_type": "corrupted_quality_metric_evidence",
        "corruption_log_path": str(settings.paths.corruption_log),
        "corruption_counts_by_type": corruption_log.get("counts_by_type", {}),
        "corruption_event_count": len(corruption_log.get("events", [])),
        "quality_signal_deltas": {
            "row_count": _numeric_delta(
                baseline_quality.get("row_count"),
                corrupted_quality.get("row_count"),
            ),
            "summary_missing_rate": _numeric_delta(
                baseline_quality.get("missing_fields", {}).get("summary", {}).get("missing_rate"),
                corrupted_quality.get("missing_fields", {}).get("summary", {}).get("missing_rate"),
            ),
            "paper_id_duplicate_count": _numeric_delta(
                baseline_quality.get("paper_id_uniqueness", {}).get("duplicate_count"),
                corrupted_quality.get("paper_id_uniqueness", {}).get("duplicate_count"),
            ),
            "row_duplicate_rate": _numeric_delta(
                baseline_quality.get("row_duplicates", {}).get("duplicate_rate"),
                corrupted_quality.get("row_duplicates", {}).get("duplicate_rate"),
            ),
            "max_age_days": _numeric_delta(
                baseline_quality.get("age_days", {}).get("max"),
                corrupted_quality.get("age_days", {}).get("max"),
            ),
            "freshness_stale_rows": _numeric_delta(
                baseline_freshness.get("stale_rows"),
                corrupted_freshness.get("stale_rows"),
            ),
            "text_for_embedding_missing_rate": _numeric_delta(
                baseline_quality.get("missing_fields", {})
                .get("text_for_embedding", {})
                .get("missing_rate"),
                corrupted_quality.get("missing_fields", {})
                .get("text_for_embedding", {})
                .get("missing_rate"),
            ),
        },
        "rag_metric_deltas": {
            "retrieval_hit_rate": _numeric_delta(
                baseline_metrics.get("retrieval_hit_rate"),
                corrupted_metrics.get("retrieval_hit_rate"),
            ),
            "mean_token_f1": _numeric_delta(
                baseline_metrics.get("mean_token_f1"),
                corrupted_metrics.get("mean_token_f1"),
            ),
            "judge_accuracy": _numeric_delta(
                baseline_metrics.get("judge_accuracy"),
                corrupted_metrics.get("judge_accuracy"),
            ),
            "mean_judge_score": _numeric_delta(
                baseline_metrics.get("mean_judge_score"),
                corrupted_metrics.get("mean_judge_score"),
            ),
        },
        "unchanged_signals": [
            "text_for_embedding_missing_rate",
            "retrieval_hit_rate",
        ],
        "interpretation_guardrail": (
            "Only metrics with measured deltas are treated as changed; unchanged signals are "
            "listed explicitly to avoid over-claiming."
        ),
    }
    write_json(evidence_path, evidence_payload)

    repaired_metrics = _read_json_if_exists(settings.paths.repaired_metrics)
    repaired_quality = _read_json_if_exists(settings.paths.quality_dir / "repaired_quality.json")
    repaired_freshness = _read_json_if_exists(
        settings.paths.quality_dir / "repaired_freshness_report.json"
    )

    generate_corruption_report(
        settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_metrics,
        repaired_metrics=repaired_metrics,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )

    print(f"Corrupted quality report: {settings.paths.quality_dir / 'corrupted_quality.json'}")
    print(
        "Corrupted freshness report: "
        f"{settings.paths.quality_dir / 'corrupted_freshness_report.json'}"
    )
    print(f"Corrupted signal evidence JSON: {evidence_path}")
    print(f"Corrupted impact report: {settings.paths.comparison_report}")


if __name__ == "__main__":
    main()
