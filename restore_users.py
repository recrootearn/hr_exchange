import sqlite3

conn = sqlite3.connect("instance/database.db")
cur = conn.cursor()

# Delete any existing users (optional)
cur.execute("DELETE FROM user")

# Get common columns between user and user_old
new_cols = [r[1] for r in cur.execute("PRAGMA table_info(user)").fetchall()]
old_cols = [r[1] for r in cur.execute("PRAGMA table_info(user_old)").fetchall()]

common = [c for c in old_cols if c in new_cols]

cols = ",".join(common)

cur.execute(f"""
INSERT INTO user ({cols})
SELECT {cols}
FROM user_old
""")

conn.commit()

print("Users restored successfully!")

conn.close()