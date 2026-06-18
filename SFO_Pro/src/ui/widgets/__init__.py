"""Reusable custom widgets."""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from src.ui.styles import DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT, ACCENT


def add_shadow(widget: QWidget, color="#000000", blur=20, offset=4, opacity=0.3):
    shadow = QGraphicsDropShadowEffect()
    shadow.setColor(QColor(color))
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset)
    shadow.setColor(QColor(color + "4D"))
    widget.setGraphicsEffect(shadow)


class StatCard(QFrame):
    """Dashboard stat card with icon, value, label."""
    def __init__(self, title: str, value: str, icon: str, color: str,
                 parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.color = color
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 16px;
            }}
        """)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Top row: icon + title
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"""
            font-size: 22px;
            background: {color}22;
            border-radius: 10px;
            padding: 6px 10px;
        """)
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(icon_lbl)
        top.addStretch()

        trend_lbl = QLabel("↑ Live")
        trend_lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
        top.addWidget(trend_lbl)
        layout.addLayout(top)

        # Value
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"""
            font-size: 26px; font-weight: bold; color: {DARK_TEXT};
        """)
        layout.addWidget(self.value_lbl)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 12px; color: {DARK_SUBTEXT};")
        layout.addWidget(title_lbl)

    def update_value(self, value: str):
        self.value_lbl.setText(value)


class ActivityItem(QFrame):
    """Single row in the activity feed."""
    def __init__(self, icon: str, title: str, subtitle: str,
                 time_str: str, color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{ background: transparent; border-bottom: 1px solid {DARK_BORDER}; }}
            QFrame:hover {{ background: #FFFFFF08; }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        # Icon circle
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background: {color}22; border-radius: 18px;
            font-size: 16px;
        """)
        layout.addWidget(icon_lbl)

        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"font-size: 13px; color: {DARK_TEXT}; font-weight: 500;")
        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet(f"font-size: 11px; color: {DARK_SUBTEXT};")
        s_lbl.setWordWrap(True)
        text_layout.addWidget(t_lbl)
        text_layout.addWidget(s_lbl)
        layout.addLayout(text_layout)
        layout.addStretch()

        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet(f"font-size: 11px; color: {DARK_SUBTEXT};")
        layout.addWidget(time_lbl)


class GlassCard(QFrame):
    """Glassmorphism-style card."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba(22, 33, 62, 0.8);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
            }}
        """)


class SectionHeader(QWidget):
    """Section title + subtitle block."""
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {DARK_TEXT};")
        layout.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(f"font-size: 13px; color: {DARK_SUBTEXT};")
            layout.addWidget(s)


class TagBadge(QLabel):
    """Colored tag pill."""
    def __init__(self, text: str, color: str = ACCENT, parent=None):
        super().__init__(f"  {text}  ", parent)
        self.setStyleSheet(f"""
            background: {color}22;
            color: {color};
            border: 1px solid {color}44;
            border-radius: 10px;
            padding: 2px 0;
            font-size: 11px;
            font-weight: bold;
        """)
        self.setFixedHeight(22)


class CircularProgress(QWidget):
    """Circular progress indicator."""
    def __init__(self, size=80, color=ACCENT, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._value = 0
        self._color = QColor(color)
        self._bg_color = QColor(DARK_BORDER)

    def set_value(self, v: int):
        self._value = max(0, min(100, v))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        margin = 8
        pen = QPen(self._bg_color, 8, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(margin, margin, w-2*margin, w-2*margin, 0, 360*16)

        pen2 = QPen(self._color, 8, Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap)
        p.setPen(pen2)
        span = int(-self._value / 100 * 360 * 16)
        p.drawArc(margin, margin, w-2*margin, w-2*margin, 90*16, span)

        p.setPen(QColor(DARK_TEXT))
        font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                   f"{self._value}%")
