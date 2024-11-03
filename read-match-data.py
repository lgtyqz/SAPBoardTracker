import json
import requests
import sqlite3

con = sqlite3.connect("matches.db")
cur = con.cursor()

import csv
pet_csv = csv.reader(open("pets.tsv", "r"), delimiter="\t")

pet_codes = dict()
for row in pet_csv:
  pet_codes[row[1]] = row[0]

perk_codes = {
  1: "Mushroom",
  2: "Peanut",

  5: "Chili",
  6: "Meat Bone",
  7: "Cherry",
  8: "Honey",
  9: "Garlic",

  12: "Steak",
  13: "Melon",
  14: "Strawberry",

  20: "Croissant",

  22: "Lemon",
  23: "Cheese",

  25: "Banana",

  30: "Chocolate Cake",

  33: "Pita Bread",
  34: "Tomato",
  35: "Pancakes",

  39: "Pie",

  45: "Durian",
  46: "Fig",

  64: "Baguette",

  67: "Caramel",
  68: "Eucalyptus",

  72: "Seaweed"
}
print(pet_codes)

# Insert your auth token here (which you can get by copying the Authorization value of the header of most SAP HTTP requests after you log in)
auth_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6IjEwMGE3YTVlLWNlMTItNDU5MC05ZTEwLTE0MmViOWY3ZTkwMSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiJMR1RZUVoiLCJqdGkiOiJmMDg1NGVhMC0zODgxLTQwMjAtYjkwMC05NzI4YTU4NzNhMGEiLCJleHAiOjE3MjM3ODA1MDAsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3Q6NTAwMCIsImF1ZCI6IioifQ.DF6iUD2iR7l8nlZxBLSLRJtSAmoWG1HzVOsfJpfXN8E"

full_replay_data = requests.get("https://api.teamwood.games/0.35/api/history/fetch", headers={"authority":"", "Authorization": auth_token})

print(full_replay_data.status_code)

games_list = full_replay_data.json()["History"]

# board schema:
# - boardPets
# - toy
#  - toyName
#  - toyLevel

# Pet JSON schema: list of pets (in order)
# Each pet has the following attributes:
# name (string)
# attack (num)
# health (num)
# tempAttack (default 0, num)
# tempHealth (default 0, num)
# level (num)
# perk (string)

def get_pet_info(pet):
  pet_id = str(pet["Enu"] if "Enu" in pet else 0)
  pet_name = pet_codes[pet_id] if pet_id in pet_codes else "Token Pet"
  pet_lvl = pet["Lvl"]
  pet_atk = pet["At"]["Perm"]
  pet_hp = pet["Hp"]["Perm"]
  pet_tmp_atk = 0
  pet_tmp_hp = 0
  if "Temp" in pet["At"]:
    pet_tmp_atk = pet["At"]["Temp"]
  if "Temp" in pet["Hp"]:
    pet_tmp_hp = pet["Hp"]["Temp"]

  perk_id = pet["Perk"] if "Perk" in pet else -1
  # print(perk_id)
  if perk_id == -1:
    return {
      "name": pet_name,
      "attack": pet_atk,
      "health": pet_hp,
      "tempAttack": pet_tmp_atk,
      "tempHealth": pet_tmp_hp,
      "level": pet_lvl,
      "perk": "No Perk"
    }
  else:
    pet_perk = perk_codes[perk_id] if perk_id in perk_codes else "UNKNOWN PERK"
    return {
      "name": pet_name,
      "attack": pet_atk,
      "health": pet_hp,
      "tempAttack": pet_tmp_atk,
      "tempHealth": pet_tmp_hp,
      "level": pet_lvl,
      "perk": pet_perk
    }

for game in games_list:
  game_replay_data = requests.post(
      "https://api.teamwood.games/0.35/api/playback/history", 
      json={
          "HistoryId": game["Id"],
          "Version": 35
      },
      headers={"authority":"", "Authorization": auth_token},
  ).json()
  match_id = game_replay_data["MatchId"]
  actions = game_replay_data["Actions"]
  for a in actions:
    if a["Type"] == 2:
      response_raw = a["Response"]
      if response_raw != "{}":
        response = json.loads(response_raw)
        # Write to db
        # cur.execute(f"INSERT INTO results (match_id, player1_name, player2_name, player1_win) VALUES ({match_id}, {})")
    elif a["Type"] == 0:
      battle = json.loads(a["Battle"])
      player_name = battle["User"]["DisplayName"]
      opponent_name = battle["Opponent"]["DisplayName"]
      turn_number = battle["UserBoard"]["Tur"]
      print(f"{player_name} vs {opponent_name}")
      print(f"Turn {turn_number}")

      player_board = {
        "boardPets": [],
        "toy": {
          "toyName": "",
          "toyLevel": 0
        }
      }

      oppo_board = {
        "boardPets": [],
        "toy": {
          "toyName": "",
          "toyLevel": 0
        }
      }
      player_toy = ""
      oppo_toy = ""
      for pet in battle["UserBoard"]["Mins"]["Items"]:
        # print(pet)
        if pet != None:
          player_board["boardPets"].append(get_pet_info(pet))

      for toy in battle["UserBoard"]["Rel"]:
        if toy != None and "Enu" in toy:
          # print(toy)
          toy_id = str(toy["Enu"])
          player_board["toy"]["toyName"] = pet_codes[toy_id] if toy_id in pet_codes else "UNKNOWN TOY"
          player_board["toy"]["toyLevel"] = toy["Lvl"]

      for pet in battle["OpponentBoard"]["Mins"]["Items"]:
        if pet != None:
          print(oppo_board)
          oppo_board["boardPets"].append(get_pet_info(pet))

      for toy in battle["OpponentBoard"]["Rel"]:
        if toy != None and "Enu" in toy:
          # print(toy)
          toy_id = str(toy["Enu"])
          oppo_board["toy"]["toyName"] = pet_codes[toy_id] if toy_id in pet_codes else "UNKNOWN TOY"
          oppo_board["toy"]["toyLevel"] = toy["Lvl"]

      print(player_board, player_toy)
      print(oppo_board, oppo_toy)

      cur.execute("REPLACE INTO boards (match_id, player_name, player_board, turn_number) VALUES (?, ?, ?, ?)", (match_id, player_name, str(player_board), turn_number))

      cur.execute("REPLACE INTO boards (match_id, player_name, player_board, turn_number) VALUES (?, ?, ?, ?)", (match_id, opponent_name, str(oppo_board), turn_number))

con.commit()




# replay_data = json.load(open("lg-replay-data.json", "r"))

# print(full_replay_data.json())