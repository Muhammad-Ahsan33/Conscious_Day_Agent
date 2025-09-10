import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict

class DatabaseManager:
    def __init__(self, db_path="entries.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            #Entry Schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    journal TEXT,
                    intention TEXT,
                    dream TEXT,
                    priorities TEXT,
                    reflection TEXT,
                    strategy TEXT,
                    dream_interpretation TEXT,
                    mindset_insight TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def save_entry(self, journal: str, dream: str, intention: str, 
                   priorities: str, reflection: str, strategy: str,
                   dream_interpretation: str = "", mindset_insight: str = "") -> Optional[int]:
        """Save a new entry to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Use INSERT OR REPLACE to handle duplicate dates
            cursor.execute('''
                INSERT INTO entries 
                (date, journal, intention, dream, priorities, reflection, strategy, 
                dream_interpretation, mindset_insight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (today, journal, intention, dream, priorities, reflection, 
                strategy, dream_interpretation, mindset_insight))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return entry_id
            
        except Exception as e:
            print(f"Database save error: {e}")
            return None
    
    def get_entry_by_date(self, date: str) -> Optional[Dict]:
        """Get entry by specific date"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM entries WHERE date = ?', (date,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"Database fetch error: {e}")
            return None
    
    def get_all_entries(self) -> List[Dict]:
        """Get all entries ordered by date descending"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM entries ORDER BY date DESC')
            rows = cursor.fetchall()
            
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"Database fetch error: {e}")
            return []