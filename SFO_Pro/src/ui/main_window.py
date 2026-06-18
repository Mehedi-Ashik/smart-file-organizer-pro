"""Main application window — sidebar nav + stacked pages."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QSizePolicy, QLineEdit, QStatusBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from src.ui.styles import (DARK_BG, DARK_SIDEBAR, DARK_SURFACE, DARK_CARD,
                            DARK_BORDER, DARK_TEXT, DARK_SUBTEXT, DARK_HOVER,
                            ACCENT, ACCENT2, SUCCESS, WARNING, DARK_THEME)
from src.ui.pages.dashboard        import DashboardPage
from src.ui.pages.organizer        import OrganizerPage
from src.ui.pages.search           import SearchPage
from src.ui.pages.analytics        import AnalyticsPage
from src.ui.pages.duplicate_cleaner import DuplicatePage
from src.ui.pages.settings         import SettingsPage
from src.ui.pages.ai_insights      import AIInsightsPage


NAV_ITEMS = [
    ("🏠", "Dashboard",        "dashboard"),
    ("📁", "Smart Organizer",  "organizer"),
    ("🤖", "AI Insights",      "ai"),
    ("🔍", "Smart Search",     "search"),
    ("📊", "Analytics",        "analytics"),
    ("🧹", "Duplicate Cleaner","duplicates"),
    ("⚙️", "Settings",         "settings"),
]


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setText(f"  {icon}  {label}")
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {DARK_SUBTEXT};
                border: none;
                border-radius: 10px;
                padding: 0 14px;
                text-align: left;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {DARK_HOVER};
                color: {DARK_TEXT};
            }}
            QPushButton:checked {{
                background: {ACCENT}22;
                color: {ACCENT};
                font-weight: bold;
            }}
        """)


class MainWindow(QMainWindow):
    def __init__(self, config, db, logger):
        super().__init__()
        self.config = config
        self.db = db
        self.logger = logger

        self.setWindowTitle("Smart File Organizer Pro")
        self.setMinimumSize(1200, 750)
        self.resize(1440, 900)

        # Apply theme
        self.setStyleSheet(DARK_THEME)

        self._build_ui()
        self._nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        # Logo
        logo_row = QHBoxLayout()
        logo_icon = QLabel("🗂️")
        logo_icon.setStyleSheet("font-size: 26px;")
        logo_text = QVBoxLayout()
        logo_title = QLabel("SFO Pro")
        logo_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {DARK_TEXT};")
        logo_sub = QLabel("Smart File Organizer")
        logo_sub.setStyleSheet(f"font-size: 10px; color: {DARK_SUBTEXT};")
        logo_text.addWidget(logo_title)
        logo_text.addWidget(logo_sub)
        logo_text.setSpacing(0)
        logo_row.addWidget(logo_icon)
        logo_row.addLayout(logo_text)
        logo_row.addStretch()
        sidebar_layout.addLayout(logo_row)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {DARK_BORDER};")
        sidebar_layout.addWidget(div)
        sidebar_layout.addSpacing(8)

        # Nav buttons
        self._nav_buttons = []
        for icon, label, key in NAV_ITEMS:
            btn = NavButton(icon, label)
            btn.clicked.connect(
                lambda checked, k=key: self._on_nav(k)
            )
            sidebar_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Version badge
        ver = QLabel("v1.0.0 • AI Powered")
        ver.setStyleSheet(f"font-size: 10px; color: {DARK_SUBTEXT}; padding: 4px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(ver)
        root.addWidget(sidebar)

        # ── Main area ────────────────────────────────────────────────────────
        main_area = QWidget()
        main_area.setObjectName("main_content")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        top_bar = QFrame()
        top_bar.setObjectName("top_bar")
        top_bar.setFixedHeight(56)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {DARK_TEXT};"
        )
        top_layout.addWidget(self.page_title)
        top_layout.addStretch()

        # Quick search in top bar
        qs = QLineEdit()
        qs.setPlaceholderText("Quick search…")
        qs.setFixedWidth(220)
        qs.setFixedHeight(34)
        top_layout.addWidget(qs)

        # Status indicator
        status_dot = QLabel("● Connected")
        status_dot.setStyleSheet(f"font-size: 11px; color: {SUCCESS};")
        top_layout.addWidget(status_dot)

        main_layout.addWidget(top_bar)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {DARK_BG};")

        self._dashboard   = DashboardPage(self.db)
        self._organizer   = OrganizerPage(self.db, self.logger)
        self._ai          = AIInsightsPage(self.db)
        self._search      = SearchPage(self.db)
        self._analytics   = AnalyticsPage(self.db)
        self._duplicates  = DuplicatePage(self.db, self.logger)
        self._settings    = SettingsPage(self.config)

        for page in [self._dashboard, self._organizer, self._ai,
                     self._search, self._analytics, self._duplicates, self._settings]:
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack)
        root.addWidget(main_area)

        # Status bar
        sb = QStatusBar()
        sb.setStyleSheet(f"""
            QStatusBar {{
                background: {DARK_SURFACE};
                color: {DARK_SUBTEXT};
                font-size: 11px;
                border-top: 1px solid {DARK_BORDER};
            }}
        """)
        sb.showMessage("Ready  •  Smart File Organizer Pro v1.0.0")
        self.setStatusBar(sb)

    _PAGE_MAP = {
        "dashboard":  0, "organizer": 1, "ai":        2,
        "search":     3, "analytics": 4, "duplicates": 5,
        "settings":   6,
    }
    _TITLES = {
        "dashboard": "📊 Dashboard",       "organizer": "📁 Smart Organizer",
        "ai": "🤖 AI Insights",            "search": "🔍 Smart Search",
        "analytics": "📈 Analytics",       "duplicates": "🧹 Duplicate Cleaner",
        "settings": "⚙️ Settings",
    }

    def _on_nav(self, key: str):
        idx = self._PAGE_MAP.get(key, 0)
        self.stack.setCurrentIndex(idx)
        self.page_title.setText(self._TITLES.get(key, ""))

        # Uncheck all, check active
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == idx)
