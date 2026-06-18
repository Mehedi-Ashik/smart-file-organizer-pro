"""File scanning engine — walks directories and indexes metadata."""
import os
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List, Dict
from PyQt6.QtCore import QThread, pyqtSignal


FILE_TYPE_MAP = {
    # Documents
    ".pdf": ("Document", "PDF"),
    ".doc": ("Document", "Word"), ".docx": ("Document", "Word"),
    ".xls": ("Document", "Excel"), ".xlsx": ("Document", "Excel"),
    ".ppt": ("Document", "PowerPoint"), ".pptx": ("Document", "PowerPoint"),
    ".txt": ("Document", "Text"), ".md": ("Document", "Markdown"),
    ".odt": ("Document", "OpenDoc"), ".ods": ("Document", "OpenDoc"),
    # Images
    ".jpg": ("Image", "JPEG"), ".jpeg": ("Image", "JPEG"),
    ".png": ("Image", "PNG"), ".gif": ("Image", "GIF"),
    ".bmp": ("Image", "Bitmap"), ".svg": ("Image", "Vector"),
    ".webp": ("Image", "WebP"), ".tiff": ("Image", "TIFF"),
    ".ico": ("Image", "Icon"), ".heic": ("Image", "HEIC"),
    # Videos
    ".mp4": ("Video", "MP4"), ".mkv": ("Video", "MKV"),
    ".avi": ("Video", "AVI"), ".mov": ("Video", "MOV"),
    ".wmv": ("Video", "WMV"), ".flv": ("Video", "FLV"),
    ".webm": ("Video", "WebM"),
    # Audio
    ".mp3": ("Audio", "MP3"), ".wav": ("Audio", "WAV"),
    ".flac": ("Audio", "FLAC"), ".aac": ("Audio", "AAC"),
    ".ogg": ("Audio", "OGG"), ".m4a": ("Audio", "M4A"),
    # Code
    ".py": ("Code", "Python"), ".js": ("Code", "JavaScript"),
    ".ts": ("Code", "TypeScript"), ".html": ("Code", "HTML"),
    ".css": ("Code", "CSS"), ".java": ("Code", "Java"),
    ".cpp": ("Code", "C++"), ".c": ("Code", "C"),
    ".cs": ("Code", "C#"), ".php": ("Code", "PHP"),
    ".rb": ("Code", "Ruby"), ".go": ("Code", "Go"),
    ".rs": ("Code", "Rust"), ".swift": ("Code", "Swift"),
    ".kt": ("Code", "Kotlin"), ".sql": ("Code", "SQL"),
    ".sh": ("Code", "Shell"), ".bat": ("Code", "Batch"),
    ".json": ("Code", "JSON"), ".xml": ("Code", "XML"),
    ".yaml": ("Code", "YAML"), ".yml": ("Code", "YAML"),
    # Archives
    ".zip": ("Archive", "ZIP"), ".rar": ("Archive", "RAR"),
    ".7z": ("Archive", "7-Zip"), ".tar": ("Archive", "TAR"),
    ".gz": ("Archive", "GZIP"), ".bz2": ("Archive", "BZIP2"),
    # Installers
    ".exe": ("Installer", "EXE"), ".msi": ("Installer", "MSI"),
    ".dmg": ("Installer", "DMG"), ".deb": ("Installer", "DEB"),
    ".rpm": ("Installer", "RPM"), ".appimage": ("Installer", "AppImage"),
}


def get_file_hash(filepath: str, chunk_size: int = 65536) -> Optional[str]:
    """MD5 hash of first 1MB of file for fast duplicate detection."""
    try:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            chunk = f.read(chunk_size)
            h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return None


def classify_file(filepath: str) -> Dict:
    """Return file metadata dict ready for DB insertion."""
    path = Path(filepath)
    ext = path.suffix.lower()
    type_info = FILE_TYPE_MAP.get(ext, ("Other", ext.lstrip(".").upper() or "Unknown"))

    try:
        stat = path.stat()
        size = stat.st_size
        created = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
    except OSError:
        size, created, modified = 0, None, None

    return {
        "filename": path.name,
        "filepath": str(path.resolve()),
        "extension": ext,
        "file_type": type_info[0],
        "size_bytes": size,
        "created_at": created,
        "modified_at": modified,
    }


class FileScanWorker(QThread):
    """Background thread that scans a directory recursively."""
    progress = pyqtSignal(int, int)          # (scanned, total)
    file_found = pyqtSignal(dict)            # file metadata
    finished = pyqtSignal(int, float)        # (count, elapsed_seconds)
    error = pyqtSignal(str)

    def __init__(self, scan_path: str, compute_hash: bool = True):
        super().__init__()
        self.scan_path = scan_path
        self.compute_hash = compute_hash
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        import time
        start = time.time()
        try:
            all_files: List[str] = []
            for root, dirs, files in os.walk(self.scan_path):
                # Skip hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for f in files:
                    if not f.startswith("."):
                        all_files.append(os.path.join(root, f))

            total = len(all_files)
            count = 0
            for fp in all_files:
                if self._cancel:
                    break
                meta = classify_file(fp)
                if self.compute_hash:
                    meta["hash_md5"] = get_file_hash(fp)
                self.file_found.emit(meta)
                count += 1
                if count % 50 == 0:
                    self.progress.emit(count, total)

            elapsed = time.time() - start
            self.finished.emit(count, elapsed)
        except Exception as e:
            self.error.emit(str(e))
