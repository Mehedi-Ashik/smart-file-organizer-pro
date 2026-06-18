"""File Organizer Engine — moves/copies files according to rules."""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from src.core.file_scanner import FILE_TYPE_MAP


CATEGORY_FOLDERS = {
    "Document":  "Documents",
    "Image":     "Images",
    "Video":     "Videos",
    "Audio":     "Music",
    "Code":      "Code",
    "Archive":   "Archives",
    "Installer": "Installers",
    "Other":     "Miscellaneous",
}


class OrganizerWorker(QThread):
    """Background thread for organizing files."""
    progress = pyqtSignal(int, int)
    file_moved = pyqtSignal(str, str)     # old_path, new_path
    finished = pyqtSignal(int)            # count moved
    error = pyqtSignal(str)

    def __init__(self, source_dir: str, dest_dir: str,
                 rules: List[Dict] = None, copy_mode: bool = False):
        super().__init__()
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.rules = rules or []
        self.copy_mode = copy_mode
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _apply_rules(self, filepath: str) -> Optional[str]:
        """Return destination subfolder if a rule matches, else None."""
        ext = Path(filepath).suffix.lower()
        name = Path(filepath).name.lower()
        for rule in self.rules:
            ctype = rule.get("condition_type", "")
            cval  = rule.get("condition_value", "").lower()
            aval  = rule.get("action_value", "")
            if ctype == "extension" and ext == cval:
                return aval
            if ctype == "name_contains" and cval in name:
                return aval
        return None

    def run(self):
        try:
            files = list(Path(self.source_dir).rglob("*"))
            files = [f for f in files if f.is_file() and not f.name.startswith(".")]
            total = len(files)
            moved = 0

            for idx, fp in enumerate(files):
                if self._cancel:
                    break

                ext = fp.suffix.lower()
                type_info = FILE_TYPE_MAP.get(ext, ("Other", "Unknown"))
                file_type = type_info[0]

                # Custom rule first, then default category folder
                rule_dest = self._apply_rules(str(fp))
                if rule_dest:
                    dest_folder = Path(self.dest_dir) / rule_dest
                else:
                    dest_folder = Path(self.dest_dir) / CATEGORY_FOLDERS.get(file_type, "Miscellaneous")

                dest_folder.mkdir(parents=True, exist_ok=True)
                dest_path = dest_folder / fp.name

                # Avoid overwrite: rename if exists
                counter = 1
                while dest_path.exists():
                    stem, suf = fp.stem, fp.suffix
                    dest_path = dest_folder / f"{stem}_{counter}{suf}"
                    counter += 1

                try:
                    if self.copy_mode:
                        shutil.copy2(str(fp), str(dest_path))
                    else:
                        shutil.move(str(fp), str(dest_path))
                    moved += 1
                    self.file_moved.emit(str(fp), str(dest_path))
                except (PermissionError, OSError):
                    pass

                self.progress.emit(idx + 1, total)

            self.finished.emit(moved)
        except Exception as e:
            self.error.emit(str(e))
