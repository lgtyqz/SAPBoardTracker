import sqlite3

con = sqlite3.connect("matches.db")
cur = con.cursor()

# board objects are all JSON strings that need deserialization
cur.execute('''
CREATE TABLE "boards" (
	match_id	TEXT,
	player_name	TEXT,
	player_board	TEXT,
	turn_number	INT,
	board_strength	INTEGER,
	UNIQUE(player_name, player_board, match_id)
);''')

cur.execute('''
CREATE TABLE results(
  match_id TEXT,
  player1_name TEXT,
  player2_name TEXT,
  player1_win INTEGER
)''')