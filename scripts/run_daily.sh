#!/usr/bin/env bash
set -euo pipefail

# 1. Xác định đường dẫn thư mục gốc dự án theo vị trí file script
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 2. Tạo thư mục logs nếu chưa tồn tại
mkdir -p logs

# 3. Kích hoạt môi trường ảo Python
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi

# 4. Định nghĩa file log theo ngày
LOG_FILE="logs/pipeline_$(date +%Y%m%d).log"
echo "=== Starting Daily Pipeline: $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$LOG_FILE"

# 5. Thực thi pipeline với cấu hình chuẩn và ghi log đồng thời
python -m src.pipeline --source both --input-dir data/incremental/day_2026-07-01 --refresh-mart 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

# 6. Kiểm tra mã kết thúc và thông báo trạng thái
if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Pipeline Completed Successfully at $(date '+%Y-%m-%d %H:%M:%S') (exit 0) ===" | tee -a "$LOG_FILE"
else
    echo "=== Pipeline Failed with Exit Code $EXIT_CODE at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE