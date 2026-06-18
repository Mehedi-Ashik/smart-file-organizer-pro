"""Centralised style constants + dark/light theme stylesheets."""

# ── Accent colours ──────────────────────────────────────────────────────────
ACCENT   = "#6C63FF"
ACCENT2  = "#4ECDC4"
SUCCESS  = "#2ECC71"
WARNING  = "#F39C12"
DANGER   = "#E74C3C"
INFO     = "#3498DB"

# ── Dark palette ─────────────────────────────────────────────────────────────
DARK_BG      = "#0F0F1A"
DARK_SURFACE = "#1A1A2E"
DARK_CARD    = "#16213E"
DARK_BORDER  = "#2D2D4E"
DARK_TEXT    = "#E8E8F0"
DARK_SUBTEXT = "#8888AA"
DARK_HOVER   = "#252545"
DARK_SIDEBAR = "#12122A"

# ── Light palette ────────────────────────────────────────────────────────────
LIGHT_BG      = "#F4F6FA"
LIGHT_SURFACE = "#FFFFFF"
LIGHT_CARD    = "#FFFFFF"
LIGHT_BORDER  = "#E1E5EB"
LIGHT_TEXT    = "#1A1A2E"
LIGHT_SUBTEXT = "#6B7280"
LIGHT_SIDEBAR = "#FFFFFF"

# ── Full dark theme stylesheet ────────────────────────────────────────────────
DARK_THEME = f"""
QMainWindow, QDialog, QWidget {{
    background: {DARK_BG};
    color: {DARK_TEXT};
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 13px;
}}

/* Sidebar */
#sidebar {{
    background: {DARK_SIDEBAR};
    border-right: 1px solid {DARK_BORDER};
}}
#top_bar {{
    background: {DARK_SURFACE};
    border-bottom: 1px solid {DARK_BORDER};
}}

/* Cards / Frames */
QFrame#card {{
    background: {DARK_CARD};
    border: 1px solid {DARK_BORDER};
    border-radius: 14px;
}}

/* Inputs */
QLineEdit {{
    background: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {DARK_TEXT};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}

/* Buttons */
QPushButton[class="primary_btn"] {{
    background: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: 600;
}}
QPushButton[class="primary_btn"]:hover {{
    background: #7B74FF;
}}
QPushButton[class="primary_btn"]:pressed {{
    background: #5A52E0;
}}
QPushButton[class="secondary_btn"] {{
    background: {DARK_SURFACE};
    color: {DARK_TEXT};
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    padding: 9px 20px;
}}
QPushButton[class="secondary_btn"]:hover {{
    background: {DARK_HOVER};
}}
QPushButton[class="danger_btn"] {{
    background: {DANGER};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: 600;
}}

/* ComboBox */
QComboBox {{
    background: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    color: {DARK_TEXT};
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    color: {DARK_TEXT};
    selection-background-color: {ACCENT}44;
}}

/* Tables */
QTableWidget {{
    background: {DARK_CARD};
    border: 1px solid {DARK_BORDER};
    border-radius: 10px;
    gridline-color: {DARK_BORDER};
    color: {DARK_TEXT};
    outline: 0;
}}
QTableWidget::item:selected {{
    background: {ACCENT}33;
    color: {DARK_TEXT};
}}
QHeaderView::section {{
    background: {DARK_SURFACE};
    color: {DARK_SUBTEXT};
    border: none;
    border-bottom: 1px solid {DARK_BORDER};
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Progress bar */
QProgressBar {{
    background: {DARK_BORDER};
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 {ACCENT2});
    border-radius: 4px;
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: {DARK_BG};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {DARK_BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* Checkboxes */
QCheckBox {{ spacing: 8px; color: {DARK_TEXT}; }}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid {DARK_BORDER};
    border-radius: 4px;
    background: {DARK_SURFACE};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* Status bar */
QStatusBar {{
    background: {DARK_SURFACE};
    color: {DARK_SUBTEXT};
    border-top: 1px solid {DARK_BORDER};
}}

QMessageBox {{ background: {DARK_SURFACE}; }}
QToolTip {{
    background: {DARK_CARD};
    color: {DARK_TEXT};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 4px 8px;
}}
"""
