import sys
from pathlib import Path
import pandas as pd

# Add src/ to python path
project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from core.config import load_settings
from observability.quality import run_data_quality_checks, build_freshness_report

def main():
    settings = load_settings(project_dir)
    
    # Path to clean baseline data
    clean_csv_path = settings.paths.clean_csv
    if not clean_csv_path.exists():
        print(f"Error: Clean dataset not found at {clean_csv_path}")
        return
        
    print(f"Loading clean baseline dataset from {clean_csv_path}...")
    df = pd.read_csv(clean_csv_path)
    
    # Ensure directories exist
    settings.paths.quality_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Run quality checks for baseline
    print("Running baseline data quality checks...")
    quality_report = run_data_quality_checks(df, settings, "baseline_quality_checks")
    print(f"Quality checks completed successfully. Report saved to {settings.paths.quality_dir}/baseline_quality_checks.json")
    
    # 2. Build freshness report
    print("Building baseline freshness report...")
    freshness_report = build_freshness_report(df, settings, settings.paths.freshness_report)
    print(f"Freshness report completed successfully. Report saved to {settings.paths.freshness_report}")
    
    # Display summary
    print("\n--- Baseline Observability Summary ---")
    print(f"Total Rows: {quality_report['row_count']}")
    print(f"Paper ID Uniqueness: Unique={quality_report['paper_id_uniqueness']['unique_count']}, IsUnique={quality_report['paper_id_uniqueness']['is_unique']}")
    print(f"Missing Fields Rates: Title={quality_report['missing_fields']['title']['missing_rate']:.2%}, Summary={quality_report['missing_fields']['summary']['missing_rate']:.2%}")
    print(f"Duplicate Rate: {quality_report['row_duplicates']['duplicate_rate']:.2%}")
    print(f"Age Days: Mean={quality_report['age_days']['mean']}, Max={quality_report['age_days']['max']}, Min={quality_report['age_days']['min']}")
    print(f"Freshness Status: IsFresh={freshness_report['is_fresh']}, Stale Rows={freshness_report['stale_rows']}")

if __name__ == "__main__":
    main()
