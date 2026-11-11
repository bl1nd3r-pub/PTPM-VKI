import logging
import sys
from pathlib import Path
from typing import Optional, Union


_configured = False


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
) -> None:
    global _configured
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if _configured:
        return

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file is None:
        project_root = Path(__file__).resolve().parents[2]
        log_file = project_root / "Logs" / "parser.log"
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    _configured = True