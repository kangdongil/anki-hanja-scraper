import sqlite3

# Sample hanja data
hanja_data = {
    "hanja": "示",
    "meaning": "볼 시",
    "meaning_official": "볼 시",
    "radical": "⺭",
    "stroke_count": 5,
    "formation_letter": "二+小",
    "grade": 5,
    "usage": "중학용,읽기5급,쓰기4급,대법원인명용",
    "unicode": "U+793A",
    "reference_idx": "1_137",
    "naver_dict_update_date": "2024-01-21",
    "naver_hanja_id": "2367ab9f300841eebcb8a76db1f91654",
}

# Connect to SQLite database
conn = sqlite3.connect("data/db/hanja.db")
cursor = conn.cursor()

# Connect to SQLite database
cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS hanjas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hanja TEXT NOT NULL,
            meaning TEXT NOT NULL,
            meaning_official TEXT,
            radical TEXT,
            stroke_count INTEGER,
            formation_letter TEXT,
            grade INTEGER,
            usage TEXT,
            unicode TEXT,
            reference_idx TEXT,
            naver_dict_update_date TEXT,
            naver_hanja_id TEXT
        )
    """
)

# Insert the hanja data into the 'hanjas' table
cursor.execute(
    """
    INSERT INTO hanjas 
    (hanja, meaning, meaning_official, radical, stroke_count, formation_letter, 
    grade, usage, unicode, reference_idx, naver_dict_update_date, naver_hanja_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
    tuple(hanja_data.values()),
)

# Commit the changes and close the connection
conn.commit()
conn.close()
