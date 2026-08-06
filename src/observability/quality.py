from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings


import json
from pathlib import Path


def _blank_count(df: pd.DataFrame, column: str, total_rows: int) -> int:
    if column not in df.columns:
        return total_rows
    return int(df[column].fillna("").astype(str).str.strip().eq("").sum())


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Chạy các kiểm tra chất lượng dữ liệu: row count, paper_id unique, title/summary missing và duplicate.
    Ghi kết quả vào thư mục `data/quality/`.
    """
    total_rows = len(df)
    
    # 1. Check paper_id unique
    if 'paper_id' in df.columns:
        canonical_paper_ids = df['paper_id'].fillna('').astype(str).str.strip().str.casefold()
        unique_paper_ids = int(canonical_paper_ids.nunique())
        missing_paper_id_count = int(canonical_paper_ids.eq('').sum())
        duplicate_paper_ids_count = int(canonical_paper_ids.duplicated().sum())
        is_paper_id_unique = missing_paper_id_count == 0 and duplicate_paper_ids_count == 0
    else:
        unique_paper_ids = 0
        is_paper_id_unique = False
        missing_paper_id_count = total_rows
        duplicate_paper_ids_count = 0

    # 2. Check required text fields
    missing_title_count = _blank_count(df, 'title', total_rows)
    missing_summary_count = _blank_count(df, 'summary', total_rows)
    missing_embedding_count = _blank_count(df, 'text_for_embedding', total_rows)
    
    missing_title_rate = float(missing_title_count / total_rows) if total_rows > 0 else 1.0
    missing_summary_rate = float(missing_summary_count / total_rows) if total_rows > 0 else 1.0
    missing_embedding_rate = float(missing_embedding_count / total_rows) if total_rows > 0 else 1.0

    # 3. Check duplicate (overall row duplicates)
    duplicate_rows_count = int(df.astype(str).duplicated().sum()) if total_rows > 0 else 0
    duplicate_rows_rate = float(duplicate_rows_count / total_rows) if total_rows > 0 else 0.0

    # 4. Check age_days (freshness)
    published_col = 'published' if 'published' in df.columns else 'published_date'
    age_days_list = []
    
    invalid_age_days_count = total_rows
    negative_age_days_count = 0
    if 'age_days' in df.columns:
        age_days = pd.to_numeric(df['age_days'], errors='coerce')
        invalid_age_days_count = int(age_days.isna().sum())
        negative_age_days_count = int((age_days < 0).sum())
        age_days_list = age_days.dropna().tolist()
    elif published_col in df.columns and total_rows > 0:
        published_dt = pd.to_datetime(df[published_col], errors='coerce')
        if not published_dt.dropna().empty:
            # Use the latest date in the dataset as the reference instead of assumed current date
            ref_date = published_dt.max()
            age_days_series = (ref_date - published_dt).dt.days
            age_days_list = age_days_series.dropna().tolist()
            
    mean_age_days = float(pd.Series(age_days_list).mean()) if age_days_list else None
    max_age_days = float(pd.Series(age_days_list).max()) if age_days_list else None
    min_age_days = float(pd.Series(age_days_list).min()) if age_days_list else None
    
    # Check length of summary
    summary_lens = df['summary'].dropna().str.len() if 'summary' in df.columns else pd.Series(dtype=int)
    mean_summary_len = float(summary_lens.mean()) if not summary_lens.empty else 0.0
    min_summary_len = float(summary_lens.min()) if not summary_lens.empty else 0.0
    
    # 5. Source Ingestion Timestamp
    source_timestamp = pd.Timestamp.now().isoformat()
    
    # Combine quality metrics
    quality_metrics = {
        "source_timestamp": source_timestamp,
        "row_count": total_rows,
        "paper_id_uniqueness": {
            "unique_count": unique_paper_ids,
            "is_unique": is_paper_id_unique,
            "missing_count": missing_paper_id_count,
            "duplicate_count": duplicate_paper_ids_count
        },
        "missing_fields": {
            "title": {
                "missing_count": missing_title_count,
                "missing_rate": missing_title_rate
            },
            "summary": {
                "missing_count": missing_summary_count,
                "missing_rate": missing_summary_rate
            },
            "text_for_embedding": {
                "missing_count": missing_embedding_count,
                "missing_rate": missing_embedding_rate
            }
        },
        "row_duplicates": {
            "duplicate_count": duplicate_rows_count,
            "duplicate_rate": duplicate_rows_rate
        },
        "age_days": {
            "mean": mean_age_days,
            "max": max_age_days,
            "min": min_age_days,
            "invalid_count": invalid_age_days_count,
            "negative_count": negative_age_days_count
        },
        "summary_length": {
            "mean": mean_summary_len,
            "min": min_summary_len
        },
        "status": "PASSED" if (
            total_rows > 0
            and is_paper_id_unique
            and missing_title_count == 0
            and missing_summary_count == 0
            and missing_embedding_count == 0
            and duplicate_rows_count == 0
            and invalid_age_days_count == 0
            and negative_age_days_count == 0
        ) else "WARNING"
    }
    
    # Save output to quality_dir
    quality_dir = Path(settings.paths.quality_dir)
    quality_dir.mkdir(parents=True, exist_ok=True)
    report_file = quality_dir / f"{report_name}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(quality_metrics, f, indent=4, ensure_ascii=False)
        
    return quality_metrics


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Tổng hợp báo cáo độ tươi mới dữ liệu:
    1. Tìm latest và oldest published date.
    2. Đếm số dòng stale (cũ hơn ngưỡng) dựa trên published hoặc age_days.
    3. Lưu và trả về báo cáo JSON.
    """
    total_rows = len(df)
    published_col = 'published' if 'published' in df.columns else 'published_date'
    
    latest_published = None
    oldest_published = None
    stale_rows = 0
    is_fresh = True
    
    if total_rows > 0:
        if published_col in df.columns:
            published_dt = pd.to_datetime(df[published_col], errors='coerce').dropna()
            if not published_dt.empty:
                latest_published = published_dt.max().isoformat()
                oldest_published = published_dt.min().isoformat()
                
                # If age_days column is present, use it. Otherwise, compute it relative to the latest published date (ref_date)
                if 'age_days' in df.columns:
                    stale_rows = int((df['age_days'] > settings.freshness_threshold_days).sum())
                else:
                    ref_date = published_dt.max()
                    age_days = (ref_date - published_dt).dt.days
                    stale_rows = int((age_days > settings.freshness_threshold_days).sum())
        elif 'age_days' in df.columns:
            stale_rows = int((df['age_days'] > settings.freshness_threshold_days).sum())
            
        is_fresh = stale_rows == 0
            
    freshness_report = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "is_fresh": is_fresh,
        "threshold_days": settings.freshness_threshold_days,
        "source_timestamp": pd.Timestamp.now().isoformat()
    }
    
    # Save output
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(freshness_report, f, indent=4, ensure_ascii=False)
        
    return freshness_report


