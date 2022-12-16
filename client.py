from flask import Flask,request
from threading import Thread
import time, random, requests


r = requests.get("https://Online-Chopsticks-Game.proryan.repl.co/Ryan")


print(r.json())
r2 = requests.get("https://Online-Chopsticks-Game.proryan.repl.co/match/"+str(r.json()["match_id"])).json()["match_found"]
while r2 == False:
  r2 = requests.get("https://Online-Chopsticks-Game.proryan.repl.co/match/"+str(r.json()["match_id"])).json()["match_found"]
r3 = requests.post("https://Online-Chopsticks-Game.proryan.repl.co/server/", json={"match_id":r.json()["match_id"], "player_num": "1"})
print(r3.json())

  