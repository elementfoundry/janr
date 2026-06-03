# janr_logger.py

from datetime import datetime
from pathlib import Path


class JANRLogger:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

    def __init__(self, file="/run/janr/log/blocklist.log"):

        self.file = Path(file)
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, msg, lvl=INFO):

        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{lvl}] {msg}\n"
        with open(self.file, "a") as f:
            f.write(line)


logger = JANRLogger()
