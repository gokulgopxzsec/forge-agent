import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "forge.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            name TEXT NOT NULL,
            website TEXT,
            phone TEXT,
            email TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            postcode TEXT,
            source TEXT,
            source_id TEXT,
            status TEXT DEFAULT 'discovered',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (run_id)
                REFERENCES research_runs(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            evidence_type TEXT,
            source_url TEXT,
            data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (candidate_id)
                REFERENCES candidates(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            model TEXT,
            analysis TEXT,
            score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (candidate_id)
                REFERENCES candidates(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":

    initialize_database()

    print("=" * 70)
    print("FORGE DATABASE")
    print("=" * 70)

    print()
    print("Database initialized:")
    print(DB_PATH)