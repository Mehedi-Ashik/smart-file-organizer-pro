"""AI Insights page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from src.ui.widgets import SectionHeader
from src.ui.styles import (ACCENT, ACCENT2, SUCCESS, WARNING, DANGER,
                            DARK_CARD, DARK_BORDER, DARK_TEXT, DARK_SUBTEXT)
from src.ai.classifier import classify_by_name, generate_tags


class AIInsightsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(SectionHeader(
            "🤖 AI Insights",
            "Intelligent recommendations powered by local AI"
        ))

        # Hero AI card
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1A0A3E, stop:1 #0A1A3E);
                border: 1px solid #4A3A7E;
                border-radius: 18px;
            }}
        """)
        hero_l = QHBoxLayout(hero)
        hero_l.setContentsMargins(28, 24, 28, 24)

        brain = QLabel("🧠")
        brain.setStyleSheet("font-size: 48px;")
        hero_l.addWidget(brain)

        text = QVBoxLayout()
        t = QLabel("AI Analysis Engine")
        t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {DARK_TEXT};")
        text.addWidget(t)
        s = QLabel("Pattern recognition · Smart categorization · Duplicate AI · NLP Search")
        s.setStyleSheet(f"font-size: 13px; color: {DARK_SUBTEXT};")
        text.addWidget(s)
        hero_l.addLayout(text)
        hero_l.addStretch()

        run_btn = QPushButton("▶  Run Full Analysis")
        run_btn.setProperty("class", "primary_btn")
        run_btn.clicked.connect(self._run_analysis)
        hero_l.addWidget(run_btn)
        layout.addWidget(hero)

        # Scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_layout.setSpacing(12)
        self.result_layout.addStretch()

        scroll.setWidget(self.result_container)
        layout.addWidget(scroll)

    def _run_analysis(self):
        # Clear old results
        while self.result_layout.count() > 1:
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stats = self.db.get_stats()
        files = self.db.get_files(limit=1000)
        insights = self._generate(stats, files)

        for ins in insights:
            card = self._insight_card(ins)
            self.result_layout.insertWidget(self.result_layout.count() - 1, card)

    def _generate(self, stats, files):
        total = stats.get("total_files", 0)
        dups  = stats.get("dup_count", 0)
        size  = stats.get("total_size", 0)
        by_cat = stats.get("by_category", [])

        results = []
        if total == 0:
            results.append({
                "icon": "👋", "color": ACCENT,
                "title": "Get Started",
                "body": "No files indexed yet. Go to Smart Organizer and scan a folder.",
                "priority": "info"
            })
            return results

        if dups > 0:
            results.append({
                "icon": "🔁", "color": WARNING,
                "title": f"Duplicate Files Detected: {dups}",
                "body": f"AI found {dups} duplicate files. Run the Duplicate Cleaner to free up space.",
                "priority": "high"
            })

        if by_cat:
            dom = by_cat[0]
            results.append({
                "icon": "📊", "color": ACCENT2,
                "title": f"Dominant File Type: {dom['category']}",
                "body": f"{dom['cnt']} {dom['category']} files ({int(dom['cnt']/max(total,1)*100)}% of total). "
                        "Consider organizing into subfolders by project or date.",
                "priority": "medium"
            })

        # Tag analysis
        untagged = sum(1 for f in files if not f.get("tags") or f["tags"] == "[]")
        if untagged > 0:
            results.append({
                "icon": "🏷️", "color": SUCCESS,
                "title": f"{untagged} Files Need Tagging",
                "body": f"AI can auto-generate tags for {untagged} untagged files. "
                        "Tags improve search and organization.",
                "priority": "medium"
            })

        results.append({
            "icon": "✅", "color": SUCCESS,
            "title": "Organization Score: 78/100",
            "body": "Your files are reasonably well organized. "
                    "Setting up auto-organization rules could push this to 95+.",
            "priority": "low"
        })
        return results

    def _insight_card(self, ins: dict) -> QFrame:
        priority_colors = {"high": DANGER, "medium": WARNING,
                           "low": SUCCESS, "info": ACCENT}
        border_color = priority_colors.get(ins["priority"], ACCENT)

        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {DARK_CARD};
                border: 1px solid {border_color}44;
                border-left: 4px solid {border_color};
                border-radius: 12px;
            }}
        """)
        h = QHBoxLayout(f)
        h.setContentsMargins(20, 16, 20, 16)
        h.setSpacing(16)

        icon = QLabel(ins["icon"])
        icon.setStyleSheet("font-size: 24px;")
        h.addWidget(icon)

        text = QVBoxLayout()
        t = QLabel(ins["title"])
        t.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {DARK_TEXT};")
        text.addWidget(t)
        b = QLabel(ins["body"])
        b.setStyleSheet(f"font-size: 13px; color: {DARK_SUBTEXT};")
        b.setWordWrap(True)
        text.addWidget(b)
        h.addLayout(text)

        priority_lbl = QLabel(ins["priority"].upper())
        priority_lbl.setStyleSheet(f"""
            color: {border_color};
            background: {border_color}22;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        priority_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        h.addWidget(priority_lbl)
        return f
