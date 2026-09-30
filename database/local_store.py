import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import SQLITE_DB_PATH

class LocalStore:
    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_urls (
                url TEXT PRIMARY KEY,
                platform TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS distress_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE,
                platform TEXT,
                is_distress INTEGER,
                urgency_level TEXT,
                water_level TEXT,
                water_level_code TEXT,
                province TEXT,
                district TEXT,
                subdistrict TEXT,
                village_or_community TEXT,
                landmark_detail TEXT,
                needs_json TEXT,
                headcount TEXT,
                contact_info TEXT,
                summary TEXT,
                case_status TEXT DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()

    def is_url_seen(self, url: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT 1 FROM seen_urls WHERE url = ?", (url,))
            return cur.fetchone() is not None

    def mark_url_seen(self, url: str, platform: str = ""):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO seen_urls (url, platform) VALUES (?, ?)",
                (url, platform)
            )
            conn.commit()

    def save_case(self, case_data: Dict[str, Any]) -> bool:
        needs_str = json.dumps(case_data.get("needs", []), ensure_ascii=False)
        loc = case_data.get("location", {})
        with self._get_connection() as conn:
            try:
                conn.execute("""
                INSERT OR REPLACE INTO distress_cases (
                    source_url, platform, is_distress, urgency_level,
                    water_level, water_level_code, province, district, subdistrict,
                    village_or_community, landmark_detail, needs_json,
                    headcount, contact_info, summary, case_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    case_data.get("source_url"),
                    case_data.get("platform", "Unknown"),
                    1 if case_data.get("is_distress") else 0,
                    case_data.get("urgency_level", "MEDIUM"),
                    case_data.get("water_level", "ไม่ระบุ"),
                    case_data.get("water_level_code", "LEVEL_UNKNOWN"),
                    loc.get("province"),
                    loc.get("district"),
                    loc.get("subdistrict"),
                    loc.get("village_or_community"),
                    loc.get("landmark_detail"),
                    needs_str,
                    case_data.get("headcount", "ไม่ระบุ"),
                    case_data.get("contact_info", "ไม่ระบุ"),
                    case_data.get("summary", ""),
                    case_data.get("case_status", "OPEN")
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error saving to local sqlite: {e}")
                return False

    def get_all_cases(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM distress_cases ORDER BY id DESC")
            rows = cur.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["needs"] = json.loads(item.get("needs_json") or "[]")
                results.append(item)
            return results
