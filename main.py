from flask import Flask,request
from threading import Thread
import time, random,sys

app = Flask(__name__)
clients = {}
servercount = 0
servers = {}
runningserver = {}

@app.route("/")
def hello_world():
  return "Hello World"
@app.route("/<username>/")
def matchmaker(username):
  global servercount, clients, servers, runningserver
  while True:
    if len(servers.keys()) >= 1:
      runningserver[list(servers.keys())[0]] = {
        "Username": [servers[list(servers.keys())[0]]["Username"], username],
      "1": {"left":1, "right":1},
      "2": {"left":1, "right":1},
      "Turn": "1", 
      "Win":None}
      del servers[list(servers.keys())[0]]
      return {"match_id": list(runningserver.keys())[0], "match_found": True}
    else:
      match_id = random.randint(1000000, 9999999)
      if match_id not in servers.keys():
        servers[match_id] = {
          "Username": username,
          "1": {"left":1, "right":1},
          "2": {"left":1,"right":1},
          "Turn": "1",
          "Win":None}
      return {"match_id": match_id, "match_found": False}
@app.route("/match/<int:match_id>/")
def matchcheck(match_id):
  if match_id in runningserver.keys():
    return {"match_found":True}
  else:
    return {"match_found":False}
@app.route("/server/", methods=["GET", "POST"])
def server():
  global runningserver
  if request.method == "GET":
    jsondata = request.json
    try:
      return runningserver[int(jsondata["match_id"])]
    except KeyError:
      return {"kicked":True}
  elif request.method =="POST":
    jsondata = request.json
    if jsondata["move"] == "attack":
      if jsondata["player_num"] == "1": victim_player = "2"
      else: victim_player ="1"
      runningserver[int(jsondata["match_id"])][victim_player][jsondata["victim_hand"]]+=runningserver[int(jsondata["match_id"])][jsondata["player_num"]][jsondata["attack_hand"]]
      if runningserver[int(jsondata["match_id"])][victim_player][jsondata["victim_hand"]] >= 5: 
        runningserver[int(jsondata["match_id"])][victim_player][jsondata["victim_hand"]] = 0
      if runningserver[int(jsondata["match_id"])][victim_player]["right"] == 0 and runningserver[int(jsondata["match_id"])][victim_player]["left"]==0:
        runningserver[int(jsondata["match_id"])]["Win"]=jsondata["player_num"]
        
    elif jsondata["move"] == "transfer":
      if jsondata["sub_hand"] == "left": add_hand = "right"
      else: add_hand = "left"
      runningserver[int(jsondata["match_id"])][jsondata["player_num"]][add_hand]+=jsondata["transfer_amount"]
      runningserver[int(jsondata["match_id"])][jsondata["player_num"]][jsondata["sub_hand"]] -= jsondata["transfer_amount"]
    if jsondata["player_num"] == "1": opp_hand = "2"
    else: opp_hand ="1"
    runningserver[int(jsondata["match_id"])]["Turn"] = opp_hand
    return runningserver[int(jsondata["match_id"])]

@app.route("/check/", methods = ["POST"])
def check():
  global clients
  username = request.json["username"]
  checking=request.json["checking"]
  
  if username in clients.keys() and checking==True:
    return {"Username":False, "Kick":False}
  if username not in clients.keys():
    clients[username] = {"Alive":True, "Kick":False}
    return {"Username":True, "Kick":False}
  clients[username]["Alive"] = True
  if clients[username]["Kick"] == True:
    return {"Username": True, "Kick":True}
  print("Verified,", username)
  return {"Username":True, "Kick":False}
def heartbeat():
  global clients, servers, runningserver
  while True:
    time.sleep(7.5)
    for client in list(clients):
      if clients[client]["Alive"] == False:
        print("Removing", client)
        del clients[client]
        for id in list(servers):
          if client in servers[id]["Username"]:
            del servers[id]
        for id in list(runningserver):
          if client in runningserver[id]["Username"]:
            runningserver[id]["Username"].remove(client)
            clients[runningserver[id]["Username"][0]]["Kick"] = True
            del runningserver[id]
      else:
        clients[client]["Alive"] = False

def run():
  app.run(host = '0.0.0.0', port = 3000, debug = False)

Thread(target = heartbeat).start()
Thread(target = run).start()