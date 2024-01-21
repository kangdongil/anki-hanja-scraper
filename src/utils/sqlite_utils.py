import sqlite3
import os


class SQLiteDB:
    """
    SQLite database context manager.

    :param db_path: Path to the SQLite database file.
    :type db_path: str
    """

    def __init__(self, db_path):
        """
        Initialize the SQLiteDB instance.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        """
        self.path = db_path
        self.check_db_exist()
        self.conn = None
        self.cursor = None

    def check_db_exist(self):
        """Check if the SQLite database file exists."""
        if not os.path.isfile(self.path):
            raise ValueError(f"The database file '{self.path}' does not exist.")

    def __enter__(self):
        """
        Class Method which is called when entering a 'with' block and returns connection and cursor.

        :return: Tuple containing the SQLite connection and cursor.
        :rtype: tuple
        """
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Class Method which is called when exiting the 'with' block when there is no exception

        :param exc_type: Type of the exception (or None if no exception).
        :type exc_type: type
        :param exc_value: The exception value (or None if no exception).
        :param traceback: The traceback object (or None if no exception).

        :return: True if no exception should propagate, False otherwise.
        :rtype: bool
        """
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        self.conn.close()

        return exc_type is None


# Schema Definition for the 'hanjas' table
hanja_schema = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "hanja": "TEXT NOT NULL",
    "meaning": "TEXT NOT NULL",
    "meaning_official": "TEXT",
    "radical": "TEXT",
    "stroke_count": "INTEGER",
    "formation_letter": "TEXT",
    "grade": "INTEGER",
    "usage": "TEXT",
    "unicode": "TEXT",
    "reference_idx": "TEXT",
    "naver_dict_update_date": "TEXT",
    "naver_hanja_id": "TEXT",
}

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

hanja_db = SQLiteDB("data/db/hanja.db")
# hanja_table = SQLiteTable(hanja_db, "hanjas", hanja_schema)

# Connect to SQLite database
with hanja_db as (conn, cursor):
    # Create the 'hanjas' table if it doesn't exist
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS hanjas (
            {', '.join([f'{column} {options}' for column, options in hanja_schema.items()])}
        )
        """
    )

    # Insert the hanja data into the 'hanjas' table
    cursor.execute(
        f"""
        INSERT INTO hanjas 
        ({', '.join(hanja_data.keys())})
        VALUES ({', '.join(['?' for _ in hanja_data])})
        """,
        tuple(hanja_data.values()),
    )
