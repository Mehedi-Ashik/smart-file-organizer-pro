"""Analytics page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from src.ui.widgets import SectionHeader, StatCard, CircularProgress
from src.ui.styles import (ACCENT, ACCENT2, SUCCESS, WARNING, DANGER, INFO,
                            DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT)


class SimpleBarChart(QWidget):
    """Mini bar chart drawn with QPainter."""
    def __init__(self, data: list, colors: list, labels: list, parent=None):
        super().__init__(parent)
        self.data = data
        self.colors = colors
        self.labels = labels
        self.setMinimumHeight(160)

    def paintEvent(self, e):
        if not self.data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        max_val = max(self.data) or 1
        bar_width = (w - 40) / len(self.data) * 0.6
        gap = (w - 40) / len(self.data) * 0.4
        bottom = h - 30

        for i, val in enumerate(self.data):
            x = 20 + i * (bar_width + gap)
            bar_h = (val / max_val) * (bottom - 20)
            y = bottom - bar_h

            color = QColor(self.colors[i % len(self.colors)])
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            # rounded top
            p.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_h), 4, 4)

            # label
            p.setPen(QColor(DARK_SUBTEXT))
            font = QFont("Segoe UI", 9)
            p.setFont(font)
            p.drawText(int(x), bottom + 16, self.labels[i][:8] if self.labels else "")

            # value
            p.setPen(QColor(DARK_TEXT))
            p.drawText(int(x), int(y) - 4, str(val))

        p.end()


class AnalyticsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        layout.addWidget(SectionHeader(
            "📊 Analytics",
            "Insights into your file ecosystem"
        ))

        # Top stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        stats = self.db.get_stats()
        total = stats.get("total_files", 0)
        total_size = stats.get("total_size", 0)
        dup_count = stats.get("dup_count", 0)
        dup_size = stats.get("dup_size", 0)

        self.card_total = StatCard("Total Files", f"{total:,}", "📄", ACCENT)
        self.card_size  = StatCard("Total Size",  _hs(total_size), "💾", ACCENT2)
        self.card_dups  = StatCard("Duplicates",  f"{dup_count}", "🔁", WARNING)
        savings_pct = int(dup_size / total_size * 100) if total_size else 0
        self.card_save  = StatCard("Potential Savings", _hs(dup_size), "💡", SUCCESS)

        for c in [self.card_total, self.card_size, self.card_dups, self.card_save]:
            stats_row.addWidget(c)
        layout.addLayout(stats_row)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # File type breakdown chart
        type_card = self._card("📈 Files by Type")
        by_cat = stats.get("by_category", [])
        cats   = [c["category"] for c in by_cat[:7]]
        counts = [c["cnt"] for c in by_cat[:7]]
        colors = [ACCENT, ACCENT2, SUCCESS, WARNING, DANGER, INFO, "#E91E8C"]
        chart  = SimpleBarChart(counts, colors, cats)
        type_card.layout().addWidget(chart)
        charts_row.addWidget(type_card, 60)

        # Storage circle
        storage_card = self._circle_card(
            "💾 Storage Health",
            savings_pct,
            f"{savings_pct}% Wasted\nby Duplicates",
            DANGER if savings_pct > 10 else SUCCESS
        )
        charts_row.addWidget(storage_card, 40)
        layout.addLayout(charts_row)

        # Insights grid
        insights_lbl = QLabel("🤖 AI Insights")
        insights_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {DARK_TEXT};"
        )
        layout.addWidget(insights_lbl)

        grid = QGridLayout()
        grid.setSpacing(16)
        insights_data = self._generate_insights(stats)
        for i, ins in enumerate(insights_data):
            card = self._insight_card(ins)
            grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(grid)
        layout.addStretch()

    def _card(self, title: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 14px;
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(20, 16, 20, 16)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {DARK_TEXT};")
        v.addWidget(t)
        return f

    def _circle_card(self, title, pct, caption, color):
        f = self._card(title)
        row = QHBoxLayout()
        circ = CircularProgress(90, color)
        circ.set_value(pct)
        row.addWidget(circ)
        cap = QLabel(caption)
        cap.setStyleSheet(f"font-size: 13px; color: {DARK_SUBTEXT};")
        row.addWidget(cap)
        row.addStretch()
        f.layout().addLayout(row)
        return f

    def _insight_card(self, ins: dict) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 12px;
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(6)

        top = QHBoxLayout()
        icon = QLabel(ins["icon"])
        icon.setStyleSheet("font-size: 20px;")
        top.addWidget(icon)
        title = QLabel(ins["title"])
        title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {DARK_TEXT};")
        top.addWidget(title)
        top.addStretch()
        v.addLayout(top)

        desc = QLabel(ins["desc"])
        desc.setStyleSheet(f"font-size: 12px; color: {DARK_SUBTEXT};")
        desc.setWordWrap(True)
        v.addWidget(desc)
        return f

    def _generate_insights(self, stats):
        total = stats.get("total_files", 0)
        dups  = stats.get("dup_count", 0)
        size  = stats.get("total_size", 0)
        cats  = stats.get("by_category", [])
        dom   = cats[0]["category"] if cats else "Unknown"

        return [
            {"icon": "📁", "title": "Most Common File Type",
             "desc": f"{dom} files dominate your collection."},
            {"icon": "🔁", "title": "Duplicate Files",
             "desc": f"{dups} duplicate files detected. Run Duplicate Cleaner to reclaim space."},
            {"icon": "💾", "title": "Average File Size",
             "desc": f"Average: {_hs(size // max(total,1))} per file." if total else "No files scanned yet."},
            {"icon": "📈", "title": "Organization Score",
             "desc": "Score: 78/100 — Well organized! Minor improvements possible."},
        ]


def _hs(b: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"
