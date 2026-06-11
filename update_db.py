import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE requirement_groups
        ADD COLUMN project_name TEXT
    """)

    conn.commit()
    print("Column project_name added successfully")
except Exception as e:
    print("Error:", e)

conn.close()