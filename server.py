import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}
newPlayer = {}
def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      
      if addr in clients:
         data = json.loads(data)
         if data['heartbeat'] == "heartbeat":
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['position'] = data['playerLocation']

      else:
         data = str(data)
         if 'connect' in data:

            newPlayer['id'] = str(addr)
            newPlayer['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}

            NewPlayer = {"cmd": 0, "newPlayer" : newPlayer, "players": []}
            for c in clients:
               player = {}
               player['id'] = str(c)
               player['color'] = clients[c]['color']
               player['position'] = clients[c]['position']
               NewPlayer['players'].append(player)
               
            m2 = json.dumps(NewPlayer)
            sock.sendto(bytes(m2, 'utf8'), addr)

            newPlayerMes = {"cmd": 0, "newPlayer" : newPlayer}
            m = json.dumps(newPlayerMes)

            for c in clients:
               sock.sendto(bytes(m,'utf8'), c)

            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
            clients[addr]['position'] = 0

            uniqueID = {"cmd": 3, "uniqueID" : str(addr)}
            uniqueIDm = json.dumps(uniqueID)

            sock.sendto(bytes(uniqueIDm, 'utf8'), addr)

def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)

            DiePlayer = {"cmd": 2,"lostPlayer":{"id":str(c)}}
            m = json.dumps(DiePlayer)

            clients_lock.acquire()
            del clients[c]
            clients_lock.release()

            for c in clients:
               sock.sendto(bytes(m,'utf8'), c)
               
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         player = {}
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         player['position'] = clients[c]['position']

         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)

      for c in clients:
         sock.sendto(bytes(s,'utf8'), c)
      clients_lock.release()
      time.sleep(1 / 144)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
