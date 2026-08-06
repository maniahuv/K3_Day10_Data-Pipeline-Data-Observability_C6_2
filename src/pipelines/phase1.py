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

    # 3. Clean data (Giao cho Role 3 thực hiện, hàm này có thể văng NotImplementedError)
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

    # 4. Save clean CSV/JSON
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(settings.paths.clean_csv, index=False)
    clean_df.to_json(settings.paths.clean_json, orient="records", lines=True)
    print(f"💾 Đã lưu dữ liệu clean vào {settings.paths.clean_csv.name} và {settings.paths.clean_json.name}")

    # Chặn (Block): Dừng ở đây trong Checkpoint 1
    print("\n🚧 [Checkpoint 1]: Đã khóa Schema Clean. Chưa gọi Test Set/Index.")
    print("🚧 Hoàn thành xuất sắc nhiệm vụ tích hợp của Role 1!")
