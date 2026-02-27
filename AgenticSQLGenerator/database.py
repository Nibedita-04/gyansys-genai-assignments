import sqlite3
import os

DB_NAME = "database/enterprise.db"
SCHEMA_PATH = "database/schema.sql"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Read schema.sql file
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)

    conn.commit()
    conn.close()