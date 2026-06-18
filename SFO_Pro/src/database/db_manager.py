"""SQLite Database Manager for Smart File Organizer Pro."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class DatabaseManager:
    def __init__(self):
        self.db_dir = Path.home() / ".sfo_pro"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "sfo_database.db"
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def initialize(self):
        """Create all tables and indexes."""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                filename      TEXT NOT NULL,
                filepath      TEXT NOT NULL UNIQUE,
                extension     TEXT,
                file_type     TEXT,
                size_bytes    INTEGER DEFAULT 0,
                created_at    DATETIME,
                modified_at   DATETIME,
                indexed_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                category      TEXT,
                subcategory   TEXT,
                tags          TEXT DEFAULT '[]',
                ai_summary    TEXT,
                hash_md5      TEXT,
                is_duplicate  INTEGER DEFAULT 0,
                duplicate_of  INTEGER REFERENCES files(id),
                is_deleted    INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS folders (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path   TEXT NOT NULL UNIQUE,
                folder_name   TEXT NOT NULL,
                parent_id     INTEGER REFERENCES folders(id),
                file_count    INTEGER DEFAULT 0,
                total_size    INTEGER DEFAULT 0,
                last_scanned  DATETIME,
                is_watched    INTEGER DEFAULT 0,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS organize_rules (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name     TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_value TEXT NOT NULL,
                action_type   TEXT NOT NULL,
                action_value  TEXT NOT NULL,
                is_active     INTEGER DEFAULT 1,
                priority      INTEGER DEFAULT 0,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS activity_log (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type   TEXT NOT NULL,
                description   TEXT,
                file_id       INTEGER REFERENCES files(id),
                old_path      TEXT,
                new_path      TEXT,
                performed_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                can_undo      INTEGER DEFAULT 1,
                undone        INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS tags (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL UNIQUE,
                color         TEXT DEFAULT '#6C63FF',
                usage_count   INTEGER DEFAULT 0,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS file_tags (
                file_id       INTEGER REFERENCES files(id) ON DELETE CASCADE,
                tag_id        INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (file_id, tag_id)
            );

            CREATE TABLE IF NOT EXISTS storage_snapshots (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                total_size    INTEGER DEFAULT 0,
                file_count    INTEGER DEFAULT 0,
                dup_size      INTEGER DEFAULT 0,
                dup_count     INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS ai_insights (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type  TEXT NOT NULL,
                title         TEXT NOT NULL,
                description   TEXT,
                recommendation TEXT,
                priority      TEXT DEFAULT 'medium',
                is_dismissed  INTEGER DEFAULT 0,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scan_history (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_path     TEXT NOT NULL,
                files_found   INTEGER DEFAULT 0,
                files_new     INTEGER DEFAULT 0,
                files_updated INTEGER DEFAULT 0,
                duration_sec  REAL DEFAULT 0,
                scanned_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_files_path      ON files(filepath);
            CREATE INDEX IF NOT EXISTS idx_files_type      ON files(file_type);
            CREATE INDEX IF NOT EXISTS idx_files_category  ON files(category);
            CREATE INDEX IF NOT EXISTS idx_files_hash      ON files(hash_md5);
            CREATE INDEX IF NOT EXISTS idx_files_dup       ON files(is_duplicate);
            CREATE INDEX IF NOT EXISTS idx_activity_date   ON activity_log(performed_at);
        """)
        conn.commit()

    # ── File CRUD ──────────────────────────────────────────────────────────────
    def upsert_file(self, data: Dict[str, Any]) -> int:
        conn = self._get_conn()
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ",".join(["?"] * len(cols))
        col_str = ",".join(cols)
        update_str = ",".join(f"{c}=excluded.{c}" for c in cols if c != "filepath")
        sql = f"""
            INSERT INTO files ({col_str}) VALUES ({placeholders})
            ON CONFLICT(filepath) DO UPDATE SET {update_str}
        """
        cur = conn.execute(sql, vals)
        conn.commit()
        return cur.lastrowid

    def get_files(self, category: str = None, file_type: str = None,
                  limit: int = 500, offset: int = 0) -> List[Dict]:
        conn = self._get_conn()
        where_parts, params = ["is_deleted=0"], []
        if category:
            where_parts.append("category=?"); params.append(category)
        if file_type:
            where_parts.append("file_type=?"); params.append(file_type)
        where = " AND ".join(where_parts)
        rows = conn.execute(
            f"SELECT * FROM files WHERE {where} ORDER BY indexed_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        return [dict(r) for r in rows]

    def search_files(self, query: str, limit: int = 200) -> List[Dict]:
        conn = self._get_conn()
        like = f"%{query}%"
        rows = conn.execute("""
            SELECT * FROM files
            WHERE is_deleted=0 AND (
                filename LIKE ? OR filepath LIKE ? OR
                category LIKE ? OR tags LIKE ? OR ai_summary LIKE ?
            )
            ORDER BY modified_at DESC LIMIT ?
        """, [like]*5 + [limit]).fetchall()
        return [dict(r) for r in rows]

    def get_duplicates(self) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT * FROM files
            WHERE is_deleted=0 AND is_duplicate=1
            ORDER BY size_bytes DESC
        """).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> Dict:
        conn = self._get_conn()
        stats = {}
        row = conn.execute("""
            SELECT COUNT(*) as total_files,
                   COALESCE(SUM(size_bytes),0) as total_size,
                   COUNT(CASE WHEN is_duplicate=1 THEN 1 END) as dup_count,
                   COALESCE(SUM(CASE WHEN is_duplicate=1 THEN size_bytes ELSE 0 END),0) as dup_size
            FROM files WHERE is_deleted=0
        """).fetchone()
        stats.update(dict(row))

        folder_row = conn.execute("SELECT COUNT(*) as folder_count FROM folders").fetchone()
        stats["folder_count"] = folder_row["folder_count"]

        cat_rows = conn.execute("""
            SELECT category, COUNT(*) as cnt, COALESCE(SUM(size_bytes),0) as sz
            FROM files WHERE is_deleted=0 AND category IS NOT NULL
            GROUP BY category ORDER BY cnt DESC
        """).fetchall()
        stats["by_category"] = [dict(r) for r in cat_rows]
        return stats

    # ── Activity Log ──────────────────────────────────────────────────────────
    def log_activity(self, action_type: str, description: str,
                     file_id: int = None, old_path: str = None,
                     new_path: str = None, can_undo: bool = True):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO activity_log
                (action_type, description, file_id, old_path, new_path, can_undo)
            VALUES (?,?,?,?,?,?)
        """, [action_type, description, file_id, old_path, new_path, int(can_undo)])
        conn.commit()

    def get_recent_activity(self, limit: int = 50) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT * FROM activity_log ORDER BY performed_at DESC LIMIT ?
        """, [limit]).fetchall()
        return [dict(r) for r in rows]

    # ── Insights ──────────────────────────────────────────────────────────────
    def add_insight(self, insight_type: str, title: str,
                    description: str, recommendation: str, priority: str = "medium"):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO ai_insights
                (insight_type, title, description, recommendation, priority)
            VALUES (?,?,?,?,?)
        """, [insight_type, title, description, recommendation, priority])
        conn.commit()

    def get_insights(self, dismissed: bool = False) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT * FROM ai_insights WHERE is_dismissed=?
            ORDER BY created_at DESC LIMIT 20
        """, [int(dismissed)]).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
