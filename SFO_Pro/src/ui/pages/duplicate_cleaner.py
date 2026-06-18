"""Duplicate Cleaner page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.ui.widgets import SectionHeader
from src.ui.styles import (DANGER, WARNING, SUCCESS, ACCENT,
                            DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT)
from src.ai.duplicate_detector import find_hash_duplicates, calculate_duplicate_savings
import os


class DuplicatePage(QWidget):
    def __init__(self, db, logger, parent=None):
        super().__init__(parent)
        self.db = db
        self.logger = logger
        self._duplicates = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(SectionHeader(
            "🧹 Duplicate Cleaner",
            "Find and safely remove duplicate files"
        ))

        # Info bar
        info = QFrame()
        info.setStyleSheet(f"""
            QFrame {{
                background: {WARNING}11;
                border: 1px solid {WARNING}44;
                border-radius: 10px;
            }}
        """)
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(16, 12, 16, 12)

        self.info_lbl = QLabel("🔁 Click 'Scan Duplicates' to detect duplicate files in your indexed collection.")
        self.info_lbl.setStyleSheet(f"font-size: 13px; color: {DARK_TEXT};")
        info_layout.addWidget(self.info_lbl)
        info_layout.addStretch()

        scan_btn = QPushButton("🔍 Scan Duplicates")
        scan_btn.setProperty("class", "primary_btn")
        scan_btn.clicked.connect(self._scan_duplicates)
        info_layout.addWidget(scan_btn)
        layout.addWidget(info)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Size", "Path", "Hash", "Status"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Action bar
        action_row = QHBoxLayout()
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setProperty("class", "secondary_btn")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_selected)

        self.select_all_btn = QPushButton("Select All Duplicates")
        self.select_all_btn.setProperty("class", "secondary_btn")
        self.select_all_btn.clicked.connect(self._select_all_duplicates)

        self.savings_lbl = QLabel("")
        self.savings_lbl.setStyleSheet(f"color: {SUCCESS}; font-weight: bold; font-size: 13px;")

        action_row.addWidget(self.select_all_btn)
        action_row.addWidget(self.delete_btn)
        action_row.addStretch()
        action_row.addWidget(self.savings_lbl)
        layout.addLayout(action_row)

    def _scan_duplicates(self):
        files = self.db.get_files(limit=5000)
        groups = find_hash_duplicates(files)
        savings = calculate_duplicate_savings(groups)

        self._duplicates = []
        for grp in groups:
            for i, f in enumerate(grp):
                is_original = (i == 0)
                f["_is_original"] = is_original
                self._duplicates.append(f)

        self._populate_table()
        self.savings_lbl.setText(f"💾 Potential savings: {_hs(savings)}")
        self.info_lbl.setText(
            f"Found {len(groups)} duplicate groups ({len(self._duplicates)} total files). "
            f"Select duplicates to delete."
        )
        self.delete_btn.setEnabled(True)

    def _populate_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self._duplicates))

        for row, f in enumerate(self._duplicates):
            is_orig = f.get("_is_original", False)
            status = "✅ Original" if is_orig else "🔁 Duplicate"
            color  = DARK_TEXT if is_orig else WARNING

            items = [
                f.get("filename", ""),
                _hs(f.get("size_bytes", 0)),
                f.get("filepath", ""),
                (f.get("hash_md5") or "")[:16] + "…",
                status,
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setForeground(QColor(color))
                self.table.setItem(row, col, item)

    def _select_all_duplicates(self):
        for row, f in enumerate(self._duplicates):
            if not f.get("_is_original"):
                self.table.selectRow(row)

    def _delete_selected(self):
        rows = set(i.row() for i in self.table.selectedItems())
        if not rows:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(rows)} files permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted = 0
        for row in sorted(rows, reverse=True):
            f = self._duplicates[row]
            if not f.get("_is_original"):
                try:
                    os.remove(f["filepath"])
                    deleted += 1
                    self.db.log_activity("delete", f"Deleted duplicate: {f['filename']}",
                                         old_path=f["filepath"])
                except Exception as ex:
                    self.logger.error(f"Delete failed: {ex}")

        QMessageBox.information(self, "Done", f"Deleted {deleted} duplicate files.")
        self._scan_duplicates()


def _hs(b: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"
