import sqlite3
import os

DB_NAME = "database/enterprise.db"
SCHEMA_PATH = "database/schema.sql"

# makes a connection to the database
def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Read schema.sql file
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)

    conn.commit()
    conn.close()

# gets all the table names from the database
def get_schema_metadata():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        schema[table] = columns

    conn.close()
    return schema

# fetches all the adjacency nodes and creates a graph from it
def get_foreign_key_graph():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)
    tables = [row[0] for row in cursor.fetchall()]

    graph = {table: [] for table in tables}
    join_conditions = {}

    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fks = cursor.fetchall()

        for fk in fks:
            referenced_table = fk[2]
            from_col = fk[3]
            to_col = fk[4]

            graph[table].append(referenced_table)
            graph[referenced_table].append(table)

            condition = f"{table}.{from_col} = {referenced_table}.{to_col}"
            join_conditions[(table, referenced_table)] = condition
            join_conditions[(referenced_table, table)] = condition

    conn.close()
    return graph, join_conditions