import sqlite3
import json

con = sqlite3.connect("matches.db")
cur = con.cursor()

cur.execute("SELECT * FROM boards")
for row in cur:
  match_id = row[0]
  name = row[1]
  board = json.dumps(row[2])
  
  break