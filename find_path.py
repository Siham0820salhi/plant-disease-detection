import sqlite3

conn = sqlite3.connect('mlflow.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    cursor.execute(f'PRAGMA table_info({table})')
    columns = [col[1] for col in cursor.fetchall()]
    for col in columns:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}" WHERE "{col}" LIKE "%Users%LI%"')
            count = cursor.fetchone()[0]
            if count > 0:
                print(f'{table}.{col} : {count} lignes contiennent le chemin')
        except Exception:
            pass

conn.close()
