import logging
import os
import sys
from pathlib import Path
from datetime import datetime

root = Path(__file__).parents[1].resolve()
LOG_ROOT = root / "logs"

def get_logger(name: str, folder: str = "system"):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    LOG_ROOT.mkdir(exist_ok=True)

    log_dir = LOG_ROOT / folder
    log_dir.mkdir(parents=True , exist_ok=True)

    filename = f"{name.lower()}_{datetime.now():%Y-%m-%d}.log"

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # Console
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    # File
    file = logging.FileHandler(log_dir / filename, encoding="utf-8")
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    logger.propagate = False

    return logger

if __name__ == "__main__" :
    print(LOG_ROOT)