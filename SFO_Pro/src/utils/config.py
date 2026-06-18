"""Application configuration — saved to ~/.sfo_pro/config.json."""
import json
from pathlib import Path


class AppConfig:
    DEFAULT = {
        "theme": "dark",
        "accent_color": "#6C63FF",
        "auto_organize": False,
        "notifications_enabled": True,
        "startup_scan": False,
    }

    def __init__(self):
        self._dir = Path.home() / ".sfo_pro"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / "config.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self._file.exists():
            try:
                with open(self._file) as f:
                    return {**self.DEFAULT, **json.load(f)}
            except Exception:
                pass
        return dict(self.DEFAULT)

    def save(self):
        with open(self._file, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()
