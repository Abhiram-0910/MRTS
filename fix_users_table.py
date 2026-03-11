import sqlite3

db_path = "C:/Projects/RTP/mirai.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
row = c.fetchone()
print("Existing users table:", row)

c.execute("DROP TABLE IF EXISTS users")
conn.commit()
conn.close()
print("Old users table dropped — SQLAlchemy will recreate with new schema on next startup.")
