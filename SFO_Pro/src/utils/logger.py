"""Application logger — singleton, writes to ~/.sfo_pro/logs/."""
import logging
import sys
from pathlib import Path
from datetime import datetime


class AppLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        log_dir = Path.home() / ".sfo_pro" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"sfo_{datetime.now():%Y%m%d}.log"

        self.logger = logging.getLogger("SFO")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.INFO)
            fmt = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%H:%M:%S")
            fh.setFormatter(fmt); ch.setFormatter(fmt)
            self.logger.addHandler(fh); self.logger.addHandler(ch)

    def info(self, m):    self.logger.info(m)
    def debug(self, m):   self.logger.debug(m)
    def warning(self, m): self.logger.warning(m)
    def error(self, m):   self.logger.error(m)
