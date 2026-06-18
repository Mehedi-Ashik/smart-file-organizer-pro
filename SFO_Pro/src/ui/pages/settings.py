"""Settings page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QCheckBox, QSlider, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.ui.widgets import SectionHeader
from src.ui.styles import (ACCENT, DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT)


class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(SectionHeader(
            "⚙️ Settings",
            "Customize Smart File Organizer Pro"
        ))

        # Appearance
        layout.addWidget(self._section("🎨 Appearance"))
        app_card = self._card()
        ac_layout = QVBoxLayout(app_card)
        ac_layout.setContentsMargins(20, 16, 20, 20)
        ac_layout.setSpacing(16)

        # Theme
        theme_row = QHBoxLayout()
        theme_row.addWidget(self._label("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.config.get("theme", "dark"))
        self.theme_combo.setFixedWidth(160)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        ac_layout.addLayout(theme_row)

        # Accent color
        acc_row = QHBoxLayout()
        acc_row.addWidget(self._label("Accent Color"))
        for color, name in [("#6C63FF","Violet"),("#4ECDC4","Teal"),
                             ("#E74C3C","Red"),("#2ECC71","Green"),
                             ("#F39C12","Amber")]:
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; border-radius: 14px; border: 2px solid transparent;
                }}
                QPushButton:hover {{ border-color: white; }}
            """)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, c=color: self.config.set("accent_color", c))
            acc_row.addWidget(btn)
        acc_row.addStretch()
        ac_layout.addLayout(acc_row)
        layout.addWidget(app_card)

        # Behaviour
        layout.addWidget(self._section("⚡ Behaviour"))
        beh_card = self._card()
        bh_layout = QVBoxLayout(beh_card)
        bh_layout.setContentsMargins(20, 16, 20, 20)
        bh_layout.setSpacing(14)

        self.cb_auto_org = QCheckBox("Auto-organize files on startup")
        self.cb_auto_org.setChecked(self.config.get("auto_organize", False))
        bh_layout.addWidget(self.cb_auto_org)

        self.cb_notifs = QCheckBox("Enable notifications")
        self.cb_notifs.setChecked(self.config.get("notifications_enabled", True))
        bh_layout.addWidget(self.cb_notifs)

        self.cb_startup = QCheckBox("Scan on startup")
        self.cb_startup.setChecked(self.config.get("startup_scan", False))
        bh_layout.addWidget(self.cb_startup)
        layout.addWidget(beh_card)

        # Save button
        save_btn = QPushButton("💾  Save Settings")
        save_btn.setProperty("class", "primary_btn")
        save_btn.setFixedWidth(180)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
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

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {DARK_TEXT};"
            "margin-top: 4px;"
        )
        return lbl

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFixedWidth(160)
        lbl.setStyleSheet(f"font-size: 13px; color: {DARK_SUBTEXT};")
        return lbl

    def _save(self):
        self.config.set("theme", self.theme_combo.currentText())
        self.config.set("auto_organize", self.cb_auto_org.isChecked())
        self.config.set("notifications_enabled", self.cb_notifs.isChecked())
        self.config.set("startup_scan", self.cb_startup.isChecked())
        QMessageBox.information(self, "Saved", "Settings saved. Restart to apply theme changes.")
        self.theme_changed.emit(self.theme_combo.currentText())
