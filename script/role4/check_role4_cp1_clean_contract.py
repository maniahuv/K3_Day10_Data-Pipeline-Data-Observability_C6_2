from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    import pandas as pd
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: pandas. Install the project environment first, then rerun:\n"
        "  uv sync\n"
        "  uv run python script/role4/check_role4_cp1_clean_contract.py\n"
        "or with venv:\n"
        "  python -m pip install -e .\n"
        "  python script/role4/check_role4_cp1_clean_contract.py"
    ) from exc


REQUIRED_COLUMNS = [
    "paper_id",
    "title",
    "text_for_embedding",
    "published",
    "authors_joined",
    "categories_joined",
    "summary",
    "abs_url",
    "pdf_url",
]


def _read_clean_dataframe(clean_csv: Path, clean_json: Path) -> tuple[pd.DataFrame, Path]:
    if clean_csv.exists():
        return pd.read_csv(clean_csv).fillna(""), clean_csv
    if clean_json.exists():
        return pd.read_json(clean_json).fillna(""), clean_json
    raise FileNotFoundError(
        f"Clean artifact not found. Expected either {clean_csv} or {clean_json}. "
        "CP1 role4 is blocked until cleaning owner writes the cleaned dataset."
    )


def _empty_count(df: pd.DataFrame, column: str) -> int:
    return int(df[column].astype(str).str.strip().eq("").sum())


def _print_sample_text(df: pd.DataFrame, limit: int = 3) -> None:
    print("\nSample text_for_embedding:")
    sample = df[["paper_id", "title", "text_for_embedding"]].head(limit)
    for idx, row in sample.iterrows():
        text = str(row["text_for_embedding"]).replace("\n", " ").strip()
        preview = text[:320] + ("..." if len(text) > 320 else "")
        print(f"\n[{idx}] paper_id={row['paper_id']}")
        print(f"title={row['title']}")
        print(f"text_chars={len(text)}")
        print(preview)


def main() -> int:
    project_root = PROJECT_ROOT
    clean_csv = project_root / "data" / "clean" / "papers_clean.csv"
    clean_json = project_root / "data" / "clean" / "papers_clean.json"
    embeddings_manifest = project_root / "data" / "embeddings" / "papers_embeddings.json"
    chroma_dir = project_root / "data" / "chroma"
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    baseline_collection = "papers-baseline"

    df, source_path = _read_clean_dataframe(clean_csv, clean_json)

    print(f"Clean source: {source_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        print(f"\nFAIL: Missing required columns for LocalEmbeddingIndex: {', '.join(missing)}")
        return 1

    failures: list[str] = []
    if len(df) == 0:
        failures.append("clean dataframe has zero rows")

    duplicate_paper_ids = int(df["paper_id"].astype(str).str.lower().duplicated().sum())
    if duplicate_paper_ids:
        failures.append(f"paper_id has {duplicate_paper_ids} duplicate row(s)")

    for column in ["paper_id", "title", "text_for_embedding", "summary"]:
        empty = _empty_count(df, column)
        if empty:
            failures.append(f"{column} has {empty} empty row(s)")

    too_short = int(df["text_for_embedding"].astype(str).str.strip().str.len().lt(80).sum())
    if too_short:
        failures.append(f"text_for_embedding has {too_short} row(s) shorter than 80 characters")

    _print_sample_text(df)

    print("\nIndex config prepared, but collection is not built in CP1:")
    print(f"embedding_model={embedding_model}")
    print(f"clean_csv={clean_csv}")
    print(f"embeddings_manifest={embeddings_manifest}")
    print(f"chroma_dir={chroma_dir}")
    print(f"baseline_collection={baseline_collection}")

    if failures:
        print("\nFAIL:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("\nPASS: cleaned dataframe satisfies role4 CP1 retrieval/index contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
