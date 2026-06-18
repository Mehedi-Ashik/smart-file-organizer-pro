"""Smart Organizer page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QProgressBar, QFileDialog, QMessageBox,
    QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from src.ui.widgets import SectionHeader
from src.ui.styles import (ACCENT, SUCCESS, WARNING, DANGER,
                            DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT)
from src.core.file_scanner import FileScanWorker
from src.core.organizer import OrganizerWorker
from src.ai.classifier import classify_by_name, generate_tags, generate_summary
import os


class OrganizerPage(QWidget):
    def __init__(self, db, logger, parent=None):
        super().__init__(parent)
        self.db = db
        self.logger = logger
        self._scan_worker = None
        self._org_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(SectionHeader(
            "📁 Smart Organizer",
            "Scan, classify and organize files with one click"
        ))

        # Source / Destination row
        path_card = self._card()
        pc_layout = QVBoxLayout(path_card)
        pc_layout.setContentsMargins(20, 20, 20, 20)
        pc_layout.setSpacing(14)

        # Source folder
        src_row = QHBoxLayout()
        src_lbl = QLabel("📂 Source Folder")
        src_lbl.setFixedWidth(130)
        src_lbl.setStyleSheet(f"color: {DARK_SUBTEXT}; font-size: 13px;")
        self.src_edit = QLineEdit()
        self.src_edit.setPlaceholderText("Select folder to scan and organize…")
        src_btn = QPushButton("Browse")
        src_btn.setProperty("class", "secondary_btn")
        src_btn.setFixedWidth(80)
        src_btn.clicked.connect(lambda: self._browse(self.src_edit))
        src_row.addWidget(src_lbl)
        src_row.addWidget(self.src_edit)
        src_row.addWidget(src_btn)
        pc_layout.addLayout(src_row)

        # Destination folder
        dst_row = QHBoxLayout()
        dst_lbl = QLabel("📁 Destination Folder")
        dst_lbl.setFixedWidth(130)
        dst_lbl.setStyleSheet(f"color: {DARK_SUBTEXT}; font-size: 13px;")
        self.dst_edit = QLineEdit()
        self.dst_edit.setPlaceholderText("Where to place organized files (leave blank for in-place)…")
        dst_btn = QPushButton("Browse")
        dst_btn.setProperty("class", "secondary_btn")
        dst_btn.setFixedWidth(80)
        dst_btn.clicked.connect(lambda: self._browse(self.dst_edit))
        dst_row.addWidget(dst_lbl)
        dst_row.addWidget(self.dst_edit)
        dst_row.addWidget(dst_btn)
        pc_layout.addLayout(dst_row)

        layout.addWidget(path_card)

        # Options card
        opt_card = self._card()
        opt_layout = QHBoxLayout(opt_card)
        opt_layout.setContentsMargins(20, 16, 20, 16)
        opt_layout.setSpacing(24)

        self.cb_copy   = QCheckBox("Copy files (keep originals)")
        self.cb_hash   = QCheckBox("Compute file hashes")
        self.cb_ai     = QCheckBox("AI classification")
        self.cb_index  = QCheckBox("Index in database")
        for cb in [self.cb_copy, self.cb_hash, self.cb_ai, self.cb_index]:
            cb.setChecked(True)
            opt_layout.addWidget(cb)
        opt_layout.addStretch()
        layout.addWidget(opt_card)

        # Action buttons
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("🔍  Scan Folder")
        self.scan_btn.setProperty("class", "primary_btn")
        self.scan_btn.setFixedHeight(44)
        self.scan_btn.clicked.connect(self._start_scan)

        self.org_btn = QPushButton("⚡  Organize Files")
        self.org_btn.setProperty("class", "primary_btn")
        self.org_btn.setFixedHeight(44)
        self.org_btn.setEnabled(False)
        self.org_btn.clicked.connect(self._start_organize)

        self.cancel_btn = QPushButton("✕  Cancel")
        self.cancel_btn.setProperty("class", "secondary_btn")
        self.cancel_btn.setFixedHeight(44)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)

        btn_row.addWidget(self.scan_btn)
        btn_row.addWidget(self.org_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        # Progress
        self.progress_lbl = QLabel("Ready")
        self.progress_lbl.setStyleSheet(f"color: {DARK_SUBTEXT}; font-size: 13px;")
        layout.addWidget(self.progress_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Result card
        self.result_card = self._card()
        res_layout = QVBoxLayout(self.result_card)
        res_layout.setContentsMargins(20, 16, 20, 16)
        self.result_lbl = QLabel("Scan results will appear here…")
        self.result_lbl.setStyleSheet(f"color: {DARK_SUBTEXT}; font-size: 13px;")
        self.result_lbl.setWordWrap(True)
        res_layout.addWidget(self.result_lbl)
        self.result_card.setVisible(False)
        layout.addWidget(self.result_card)

        layout.addStretch()

    def _card(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 14px;
            }}
        """)
        return f

    def _browse(self, target: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            target.setText(folder)

    def _start_scan(self):
        src = self.src_edit.text().strip()
        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, "No Folder", "Please select a valid source folder.")
            return

        self.scan_btn.setEnabled(False)
        self.org_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_lbl.setText("Scanning…")
        self._files_found = []

        self._scan_worker = FileScanWorker(src, compute_hash=self.cb_hash.isChecked())
        self._scan_worker.progress.connect(self._on_scan_progress)
        self._scan_worker.file_found.connect(self._on_file_found)
        self._scan_worker.finished.connect(self._on_scan_done)
        self._scan_worker.error.connect(self._on_error)
        self._scan_worker.start()

    def _on_scan_progress(self, done, total):
        if total > 0:
            self.progress_bar.setValue(int(done / total * 100))
        self.progress_lbl.setText(f"Scanning… {done:,} / {total:,} files")

    def _on_file_found(self, meta):
        if self.cb_ai.isChecked():
            cat, conf = classify_by_name(meta["filename"])
            meta["category"] = cat
            tags = generate_tags(meta["filename"])
            import json
            meta["tags"] = json.dumps(tags)
            meta["ai_summary"] = generate_summary(
                meta["filename"], meta.get("file_type", ""), meta.get("size_bytes", 0)
            )
        if self.cb_index.isChecked():
            try:
                self.db.upsert_file(meta)
            except Exception:
                pass
        self._files_found.append(meta)

    def _on_scan_done(self, count, elapsed):
        self.progress_bar.setValue(100)
        self.progress_lbl.setText(f"✅ Scan complete: {count:,} files in {elapsed:.1f}s")
        self.scan_btn.setEnabled(True)
        self.org_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.result_card.setVisible(True)
        self.result_lbl.setText(
            f"Found <b>{count:,}</b> files in <b>{elapsed:.1f}s</b>.\n"
            f"Click 'Organize Files' to sort them by category."
        )
        self.db.log_activity("scan", f"Scanned {count} files from {self.src_edit.text()}")
        self.logger.info(f"Scan complete: {count} files")

    def _start_organize(self):
        src = self.src_edit.text().strip()
        dst = self.dst_edit.text().strip() or src

        self.org_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_lbl.setText("Organizing…")
        self.progress_bar.setValue(0)

        self._org_worker = OrganizerWorker(
            src, dst,
            copy_mode=self.cb_copy.isChecked()
        )
        self._org_worker.progress.connect(
            lambda d, t: self.progress_bar.setValue(int(d/t*100)) if t else None
        )
        self._org_worker.finished.connect(self._on_org_done)
        self._org_worker.error.connect(self._on_error)
        self._org_worker.start()

    def _on_org_done(self, moved):
        self.progress_bar.setValue(100)
        self.progress_lbl.setText(f"✅ Organized {moved:,} files")
        self.org_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.result_lbl.setText(f"✅ Successfully organized <b>{moved:,}</b> files.")
        self.db.log_activity("organize", f"Organized {moved} files to {self.dst_edit.text()}")

    def _cancel(self):
        if self._scan_worker:
            self._scan_worker.cancel()
        if self._org_worker:
            self._org_worker.cancel()
        self.scan_btn.setEnabled(True)
        self.org_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_lbl.setText("Cancelled.")

    def _on_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
        self.scan_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
