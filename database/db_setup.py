import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'event_management.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Events Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mode TEXT NOT NULL,
        drive_folder_id TEXT
    )
    ''')

    # Event Details Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        venue TEXT,
        time TEXT,
        type TEXT,
        description TEXT,
        expected_participants INTEGER,
        organizers TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    # Event Flow Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_flow (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        round_name TEXT,
        date_time TEXT,
        participants_count INTEGER,
        volunteer_in_charge TEXT,
        faculty_in_charge TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    # Budget Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        item_name TEXT,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    # Budget Bills Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        file_name TEXT,
        drive_file_id TEXT,
        drive_link TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    # Work Status / Tasks Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        task_name TEXT,
        assigned_to TEXT,
        status TEXT DEFAULT 'pending', -- pending, in-progress, completed
        progress_comments TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    # Resources Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        category TEXT, -- poster, content, image, video, document
        file_name TEXT,
        drive_file_id TEXT,
        drive_link TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == '__main__':
    init_db()
