"""Smart Search page with natural language support."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from src.ui.widgets import SectionHeader, TagBadge
from src.ui.styles import ACCENT, DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT
from src.ai.classifier import natural_language_search
import os, json


COLS = ["Filename", "Type", "Category", "Size", "Modified", "Tags", "Path"]


class SearchPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._all_files = []
        self._build_ui()
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._do_search)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(SectionHeader(
            "🔍 Smart Search",
            "Search files by name, type, tag or natural language query"
        ))

        # Search bar
        search_card = QFrame()
        search_card.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 14px;
            }}
        """)
        sc_layout = QHBoxLayout(search_card)
        sc_layout.setContentsMargins(16, 12, 16, 12)
        sc_layout.setSpacing(12)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 18px;")
        sc_layout.addWidget(search_icon)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search files… try 'AI assignments from last semester' or 'budget reports'"
        )
        self.search_box.setStyleSheet(
            "border: none; background: transparent; font-size: 14px;"
        )
        self.search_box.textChanged.connect(lambda: self._debounce.start(300))
        sc_layout.addWidget(self.search_box)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Document", "Image", "Video",
                                    "Audio", "Code", "Archive", "Other"])
        self.type_filter.setFixedWidth(130)
        self.type_filter.currentIndexChanged.connect(self._do_search)
        sc_layout.addWidget(self.type_filter)

        layout.addWidget(search_card)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Status
        self.status_lbl = QLabel("Type to search your indexed files")
        self.status_lbl.setStyleSheet(f"color: {DARK_SUBTEXT}; font-size: 12px;")
        layout.addWidget(self.status_lbl)

    def _do_search(self):
        query = self.search_box.text().strip()
        type_filter = self.type_filter.currentText()

        if not query:
            self.table.setRowCount(0)
            self.status_lbl.setText("Type to search your indexed files")
            return

        # Try natural language first, fall back to DB search
        if len(query.split()) > 2:
            all_files = self.db.get_files(limit=2000)
            results = natural_language_search(query, all_files)
        else:
            results = self.db.search_files(query, limit=500)

        # Apply type filter
        if type_filter != "All Types":
            results = [f for f in results if f.get("file_type") == type_filter]

        self._populate_table(results)
        self.status_lbl.setText(f"Found {len(results):,} results for '{query}'")

    def _populate_table(self, files):
        self.table.setRowCount(0)
        self.table.setRowCount(len(files))

        type_icons = {
            "Document": "📄", "Image": "🖼️", "Video": "🎬",
            "Audio": "🎵", "Code": "💻", "Archive": "🗜️",
            "Installer": "⚙️", "Other": "📦"
        }
        cat_colors = {
            "Education": "#6C63FF", "Business": "#3498DB",
            "Personal": "#2ECC71", "Creative": "#F39C12",
            "Development": "#E91E8C", "Media": "#E74C3C",
            "Uncategorized": "#8888AA"
        }

        for row, f in enumerate(files):
            ft = f.get("file_type", "Other")
            icon = type_icons.get(ft, "📄")
            fname = f.get("filename", "")
            cat = f.get("category", "")

            items = [
                f"{icon}  {fname}",
                ft,
                cat,
                _human_size(f.get("size_bytes", 0)),
                (f.get("modified_at") or "")[:10],
                ", ".join(json.loads(f.get("tags") or "[]")),
                f.get("filepath", ""),
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setForeground(QColor(DARK_TEXT))
                if col == 2 and cat in cat_colors:
                    item.setForeground(QColor(cat_colors[cat]))
                self.table.setItem(row, col, item)

        self.table.resizeRowsToContents()

    def refresh(self):
        """Called when switching to this tab."""
        pass


def _human_size(b: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"
