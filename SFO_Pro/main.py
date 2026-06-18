"""
Smart File Organizer Pro — main entry point.
Run:  python main.py
"""
import sys
import os

# Make sure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.utils.config import AppConfig
from src.utils.logger import AppLogger
from src.database.db_manager import DatabaseManager
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Smart File Organizer Pro")
    app.setApplicationVersion("1.0.0")
    app.setFont(QFont("Segoe UI", 10))

    config = AppConfig()
    logger = AppLogger()
    db     = DatabaseManager()
    db.initialize()

    logger.info("Smart File Organizer Pro starting…")

    window = MainWindow(config, db, logger)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
