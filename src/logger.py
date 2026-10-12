import logging
from pathlib import Path


def get_logger(name="pipeline"):
    """Cấu hình và trả về Logger chuẩn 2 handlers (File logs/pipeline.log (or the name in name variable)
    + Stream Console)."""
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger(name)

    # Tránh gắn lặp handlers khi hàm được gọi nhiều lần trong process
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Handler 1: Ghi ra file với mã hóa UTF-8
    fh = logging.FileHandler("logs/pipeline.log", encoding="utf-8")
    fh.setFormatter(fmt)

    # Handler 2: Xuất ra màn hình console
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger