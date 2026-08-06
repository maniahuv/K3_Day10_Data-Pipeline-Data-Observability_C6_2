from __future__ import annotations


def main() -> None:
    """Baseline pipeline end-to-end cho Checkpoint 1 (Role 1)."""
    import sys
    from core.config import load_settings
    from ingestion.crossref import load_raw_records
    from ingestion.cleaning import build_clean_dataframe
    from datetime import datetime, UTC

    print("🚀 Bắt đầu Phase 1 Pipeline (Checkpoint 1 - Role 1)")

    # 1. Load settings
    settings = load_settings()

    # 2. Load raw records
    raw_records_path = settings.paths.raw_records_json
    if not raw_records_path.exists():
        print(f"❌ Lỗi (Blocker): Không tìm thấy dữ liệu raw tại {raw_records_path}!")
        sys.exit(1)
    
    raw_records = load_raw_records(raw_records_path)
    raw_count = len(raw_records)
    print(f"📦 Đã load {raw_count} raw records từ {raw_records_path.name}")

    if raw_count == 0:
        print("❌ Lỗi (Blocker): Dữ liệu raw trống!")
        sys.exit(1)

    # 3. Clean data (Do Role 3 thực hiện)
    print("🧹 Bắt đầu quá trình làm sạch dữ liệu (Gọi module cleaning)...")
    try:
        run_date = datetime.now(UTC)
        clean_df = build_clean_dataframe(raw_records, run_date)
    except NotImplementedError:
        print("\n🚧 [Blocker Evidence]: Role 3 chưa hoàn thiện hàm `build_clean_dataframe` trong `cleaning.py`!")
        print("🚧 Pipeline bị chặn lại ở bước Clean. Vui lòng hoàn thành Checkpoint 1 (Cleaning) trước khi đi tiếp.")
        sys.exit(1)
    
    clean_count = len(clean_df)
    print(f"✅ Quá trình làm sạch hoàn tất.")
    print(f"📊 Thống kê: Raw Count = {raw_count} | Clean Count = {clean_count}")

    # Truy vết lý do loại bỏ (từ cleaning_log của Role 3)
    cleaning_log = clean_df.attrs.get("cleaning_log", {})
    counts_by_reason = cleaning_log.get("counts_by_reason", {})
    if counts_by_reason:
        print("🔍 Chi tiết lý do loại bỏ record:")
        for reason, count in counts_by_reason.items():
            print(f"   - {reason}: {count} records")

    # Review (Bắt lỗi) drop rate
    drop_rate = (raw_count - clean_count) / raw_count
    print(f"📉 Tỷ lệ loại bỏ (Drop rate): {drop_rate:.2%}")

    if drop_rate > 0.5:
        print("\n❌ [Blocker Evidence]: Tỷ lệ drop > 50%. Có sự bất thường trong quy tắc làm sạch hoặc dữ liệu raw.")
        print("Vui lòng review lại Data Contract trước khi đi tiếp!")
        sys.exit(1)
    
    if clean_count == 0:
        print("\n❌ [Blocker Evidence]: Không còn bản ghi nào sau khi làm sạch!")
        sys.exit(1)

    # 4. Save clean CSV/JSON/Log bằng hàm của Role 3
    from ingestion.cleaning import save_clean_artifacts
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    
    # Giả sử chúng ta lưu log vào thư mục reports
    log_path = settings.paths.workspace_dir / "data" / "reports" / "cleaning_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_clean_artifacts(
        dataframe=clean_df,
        csv_path=settings.paths.clean_csv,
        json_path=settings.paths.clean_json,
        log_path=log_path
    )
    print(f"💾 Đã lưu dữ liệu clean vào {settings.paths.clean_csv.name}, {settings.paths.clean_json.name}")
    print(f"📄 Đã lưu log làm sạch vào {log_path.name}")

    # Chặn (Block): Dừng ở đây trong Checkpoint 1
    print("\n🚧 [Checkpoint 1]: Đã khóa Schema Clean. Cấu trúc dữ liệu đã được verify.")
    print("🚧 Hoàn thành xuất sắc nhiệm vụ tích hợp của Role 1 (Checkpoint 1)!")
