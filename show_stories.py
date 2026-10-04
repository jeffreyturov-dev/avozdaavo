import sqlite3
c = sqlite3.connect("/opt/data/projet/avozdaavo/data/avo.db")
for r in c.execute("SELECT id, title, text FROM stories"):
    print("ID:", r[0], "| TITLE:", r[1])
    print("TEXT:", r[2])
    print("-" * 60)
