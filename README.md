# 🗂️ Smart File Organizer Pro

> AI-powered desktop file management system built with Python and PyQt6

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.7+-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

Smart File Organizer Pro automatically scans, classifies, and organizes files on your computer using local AI and Natural Language Processing — no internet connection or external API required.

---

## ✨ Features

- 🤖 **AI File Classification** — Understands file names and sorts them into categories (Education, Business, Personal, Projects, etc.)
- 🔍 **Natural Language Search** — Search using plain English, e.g. *"show my assignments from last semester"*
- 🧹 **Duplicate File Detector** — Finds and safely removes duplicate files using MD5/SHA-256 hashing
- 📊 **Analytics Dashboard** — Visual insights into file types, storage usage, and productivity
- 💾 **Storage Manager** — Finds large files and helps reclaim disk space
- ⚡ **One-Click Organizer** — Automatically sorts files into smart folders
- 🌙 **Dark / Light Theme** — Modern UI inspired by Windows 11 and Notion

---

## 🖥️ Screenshots

<!-- Add your screenshots here -->
<!-- ![Dashboard](screenshots/dashboard.png) -->
<!-- ![Smart Organizer](screenshots/organizer.png) -->

---

## 🛠️ Tech Stack

| Layer          | Technology         |
|----------------|---------------------|
| UI Framework   | PyQt6                |
| Language       | Python 3.11+         |
| Database       | SQLite 3              |
| AI / NLP       | Keyword-based local classifier |
| Packaging      | PyInstaller + Inno Setup |

---

## 📦 Installation

### Option 1 — Run from source

```bash
# Clone the repository
git clone https://github.com/Mehedi-Ashik/smart-file-organizer-pro.git
cd smart-file-organizer-pro

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 2 — Download the installer

Download the latest Windows installer from the [Releases](../../releases) page and run `SmartFileOrganizerPro_Setup.exe`.

---

## 📁 Project Structure

```
smart_file_organizer/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── src/
    ├── ai/
    │   ├── classifier.py            # NLP file classification engine
    │   └── duplicate_detector.py    # Hash-based duplicate detection
    ├── core/
    │   ├── file_scanner.py          # Directory scanning & metadata
    │   └── organizer.py             # File organization engine
    ├── database/
    │   └── db_manager.py            # SQLite database manager
    ├── ui/
    │   ├── main_window.py           # Main application window
    │   ├── pages/                   # Dashboard, Organizer, Search, etc.
    │   ├── widgets/                 # Reusable UI components
    │   └── styles/                  # Theme & stylesheets
    └── utils/
        ├── config.py                 # App configuration
        └── logger.py                 # Logging system
```

---

## 🗄️ Database Schema

The app uses a normalized SQLite database with tables for `files`, `folders`, `tags`, `file_tags`, `duplicates`, `organization_rules`, `activity_log`, `ai_insights`, `settings`, and `search_history`.

---

## 🚀 Roadmap

- [ ] Cloud sync (Google Drive, OneDrive)
- [ ] Full-text PDF search
- [ ] LLM-powered file summaries
- [ ] Cross-platform builds (macOS, Linux)
- [ ] Plugin system

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Mehedi**
Built as a personal project to learn desktop application development with Python.

---

⭐ If you found this project useful, consider giving it a star on GitHub!
