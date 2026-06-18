"""Dashboard page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from src.ui.widgets import StatCard, ActivityItem, SectionHeader, CircularProgress
from src.ui.styles import ACCENT, ACCENT2, SUCCESS, WARNING, DANGER, INFO
from src.ui.styles import DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT
import math


class DashboardPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self._refresh()
        # Auto-refresh every 30 seconds
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(30000)

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()
        title_block = SectionHeader(
            "📊 Dashboard",
            "Your intelligent file management overview"
        )
        header.addWidget(title_block)
        header.addStretch()
        refresh_btn = QPushButton("⟳ Refresh")
        refresh_btn.setProperty("class", "secondary_btn")
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        self.stat_files   = StatCard("Total Files",   "—", "📄", ACCENT)
        self.stat_folders = StatCard("Folders",       "—", "📁", ACCENT2)
        self.stat_size    = StatCard("Storage Used",  "—", "💾", SUCCESS)
        self.stat_dups    = StatCard("Duplicates",    "—", "🔁", WARNING)
        for i, card in enumerate([self.stat_files, self.stat_folders,
                                   self.stat_size,  self.stat_dups]):
            stats_grid.addWidget(card, 0, i)
        layout.addLayout(stats_grid)

        # Middle row: storage breakdown + recent activity
        mid = QHBoxLayout()
        mid.setSpacing(20)

        # Storage breakdown
        storage_card = self._make_storage_card()
        mid.addWidget(storage_card, 55)

        # Recent activity
        activity_card = self._make_activity_card()
        mid.addWidget(activity_card, 45)

        layout.addLayout(mid)

        # AI Recommendations
        ai_card = self._make_ai_card()
        layout.addWidget(ai_card)

        layout.addStretch()

    def _make_storage_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("📂 Files by Category")
        title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {DARK_TEXT};")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.cat_layout = QVBoxLayout()
        self.cat_layout.setSpacing(10)
        layout.addLayout(self.cat_layout)
        return card

    def _make_activity_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)

        title = QLabel("⚡ Recent Activity")
        title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {DARK_TEXT}; padding: 0 20px;")
        layout.addWidget(title)

        self.activity_layout = QVBoxLayout()
        self.activity_layout.setSpacing(0)
        self.activity_layout.setContentsMargins(0, 12, 0, 0)
        layout.addLayout(self.activity_layout)
        layout.addStretch()
        return card

    def _make_ai_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1A1A3E, stop:1 #1E1A3A);
                border: 1px solid #3D3D7A;
                border-radius: 16px;
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        text_layout = QVBoxLayout()
        t = QLabel("🤖 AI Recommendations")
        t.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {DARK_TEXT};")
        text_layout.addWidget(t)

        self.ai_rec_label = QLabel("Analyzing your files...")
        self.ai_rec_label.setStyleSheet(f"font-size: 13px; color: {DARK_SUBTEXT};")
        self.ai_rec_label.setWordWrap(True)
        text_layout.addWidget(self.ai_rec_label)
        layout.addLayout(text_layout)
        layout.addStretch()

        scan_btn = QPushButton("Run AI Analysis →")
        scan_btn.setProperty("class", "primary_btn")
        layout.addWidget(scan_btn)
        return card

    def _refresh(self):
        try:
            stats = self.db.get_stats()
            self.stat_files.update_value(f"{stats.get('total_files', 0):,}")
            self.stat_folders.update_value(f"{stats.get('folder_count', 0):,}")
            total_size = stats.get("total_size", 0)
            self.stat_size.update_value(_human_size(total_size))
            self.stat_dups.update_value(f"{stats.get('dup_count', 0):,}")

            # Category bars
            while self.cat_layout.count():
                item = self.cat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            by_cat = stats.get("by_category", [])
            max_cnt = max((c["cnt"] for c in by_cat), default=1)

            cat_icons = {
                "Document": "📄", "Image": "🖼️", "Video": "🎬",
                "Audio": "🎵", "Code": "💻", "Archive": "🗜️",
                "Installer": "⚙️", "Other": "📦"
            }
            cat_colors = {
                "Document": ACCENT, "Image": ACCENT2, "Video": DANGER,
                "Audio": SUCCESS, "Code": WARNING, "Archive": INFO,
                "Installer": "#E91E8C", "Other": DARK_SUBTEXT
            }

            for cat in by_cat[:6]:
                row = QHBoxLayout()
                icon = cat_icons.get(cat["category"], "📄")
                name = QLabel(f"{icon} {cat['category']}")
                name.setFixedWidth(120)
                name.setStyleSheet(f"font-size: 12px; color: {DARK_TEXT};")

                bar = QFrame()
                bar_color = cat_colors.get(cat["category"], ACCENT)
                pct = int(cat["cnt"] / max_cnt * 100)
                bar.setFixedHeight(6)
                bar.setStyleSheet(f"""
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {bar_color}, stop:{pct/100:.2f} {bar_color},
                        stop:{pct/100:.2f} #2D2D4E, stop:1 #2D2D4E);
                    border-radius: 3px;
                """)
                count_lbl = QLabel(f"{cat['cnt']:,}")
                count_lbl.setFixedWidth(50)
                count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
                count_lbl.setStyleSheet(f"font-size: 12px; color: {DARK_SUBTEXT};")

                row.addWidget(name)
                row.addWidget(bar)
                row.addWidget(count_lbl)

                wrapper = QWidget()
                wrapper.setLayout(row)
                self.cat_layout.addWidget(wrapper)

            # Activity
            while self.activity_layout.count():
                item = self.activity_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            activities = self.db.get_recent_activity(8)
            action_icons = {
                "organize": ("📁", SUCCESS),
                "scan": ("🔍", ACCENT),
                "delete": ("🗑️", DANGER),
                "move": ("✂️", WARNING),
            }
            for act in activities:
                icon, color = action_icons.get(
                    act.get("action_type", "scan"), ("📋", ACCENT)
                )
                performed = act.get("performed_at", "")[:16].replace("T", " ")
                item = ActivityItem(
                    icon=icon,
                    title=act.get("action_type", "Action").title(),
                    subtitle=act.get("description", ""),
                    time_str=performed,
                    color=color
                )
                self.activity_layout.addWidget(item)

            if not activities:
                placeholder = QLabel("No activity yet. Start scanning files!")
                placeholder.setStyleSheet(f"color: {DARK_SUBTEXT}; font-size: 13px; padding: 20px;")
                self.activity_layout.addWidget(placeholder)

            # AI recommendation
            total = stats.get("total_files", 0)
            dups  = stats.get("dup_count", 0)
            if dups > 10:
                self.ai_rec_label.setText(
                    f"🔁 Found {dups} duplicate files wasting "
                    f"{_human_size(stats.get('dup_size', 0))}. "
                    "Run Duplicate Cleaner to free space."
                )
            elif total == 0:
                self.ai_rec_label.setText(
                    "👋 Welcome! Scan a folder to get started with intelligent organization."
                )
            else:
                self.ai_rec_label.setText(
                    f"✅ Your {total:,} files look well-organized. "
                    "Consider setting up auto-organization rules."
                )
        except Exception as e:
            pass


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
