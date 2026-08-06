from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings


import json
from pathlib import Path

def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Chạy các kiểm tra chất lượng dữ liệu: row count, null, duplicate, age_days, source timestamp.
    Ghi kết quả vào thư mục `data/quality/`.
    """
    # 1. Row count
    total_rows = len(df)
    
    # 2. Check null
    null_counts = df[['paper_id', 'title', 'summary', 'text_for_embedding']].isnull().sum().to_dict()
    null_rates = df[['paper_id', 'title', 'summary', 'text_for_embedding']].isnull().mean().to_dict()
    
    # 3. Check duplicates
    duplicate_count = int(df.duplicated(subset=['paper_id']).sum()) if total_rows > 0 else 0
    duplicate_rate = float(duplicate_count / total_rows) if total_rows > 0 else 0.0
    
    # 4. Check age_days (freshness)
    # Convert published column if it exists, otherwise use nan
    published_col = 'published' if 'published' in df.columns else 'published_date'
    age_days_list = []
    if published_col in df.columns and total_rows > 0:
        published_dt = pd.to_datetime(df[published_col], errors='coerce')
        current_time = pd.Timestamp.now()
        age_days_series = (current_time - published_dt).dt.days
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
    
    # Combine signals
    quality_metrics = {
        "source_timestamp": source_timestamp,
        "row_count": total_rows,
        "null_counts": {k: int(v) for k, v in null_counts.items()},
        "null_rates": {k: float(v) for k, v in null_rates.items()},
        "duplicate_count": duplicate_count,
        "duplicate_rate": duplicate_rate,
        "age_days": {
            "mean": mean_age_days,
            "max": max_age_days,
            "min": min_age_days
        },
        "summary_length": {
            "mean": mean_summary_len,
            "min": min_summary_len
        },
        "status": "PASSED" if null_rates.get("paper_id", 0) == 0 and duplicate_rate == 0 and total_rows > 0 else "WARNING"
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
    2. Đếm số dòng stale (cũ hơn ngưỡng).
    3. Lưu và trả về báo cáo JSON.
    """
    total_rows = len(df)
    published_col = 'published' if 'published' in df.columns else 'published_date'
    
    latest_published = None
    oldest_published = None
    stale_rows = 0
    is_fresh = True
    
    if published_col in df.columns and total_rows > 0:
        published_dt = pd.to_datetime(df[published_col], errors='coerce').dropna()
        if not published_dt.empty:
            latest_published = published_dt.max().isoformat()
            oldest_published = published_dt.min().isoformat()
            
            # Stale condition based on threshold
            current_time = pd.Timestamp.now()
            age_days = (current_time - published_dt).dt.days
            stale_rows = int((age_days > settings.freshness_threshold_days).sum())
            
            # If any stale row or average age too old
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

