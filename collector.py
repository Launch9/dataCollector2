from requests import Session  # pip install requests
from signalr import Connection  # pip install signalr-client
import requests
import json
import os
import time
from datetime import datetime
def handle_received(*args, **kwargs):
    # Orderbook snapshot:
    if 'R' in kwargs and type(kwargs['R']) is not bool:
        # kwargs['R'] contains your snapshot
        print("Received message from: " + str(kwargs["R"]["MarketName"]))
        saveData = {"timestamp":datetime.utcnow().timestamp(),"data":kwargs["R"]}
        with open("./crypto/bittrex/orderBook/" + kwargs['R']["MarketName"] + "/" + str(kwargs["R"]["Nonce"]) + ".json",'w') as outfile:
            json.dump(saveData, outfile)
        #print(kwargs['R'])

# You didn't add the message stream
def msg_received(*args, **kwargs):
    # args[0] contains your stream
    print(args[0])
    print("Nothing")

def print_error(error):
    print('error: ', error)

def createDirectories(markets):
    cwd = os.getcwd()
    if(not os.path.isdir(cwd + "/crypto")):
        os.mkdir(cwd + "/crypto")
    if(not os.path.isdir(cwd + "/crypto/bittrex")):
        os.mkdir(cwd + "/crypto/bittrex")
    if(not os.path.isdir(cwd + "/crypto/bittrex/orderBook")):
        os.mkdir(cwd + "/crypto/bittrex/orderBook")
    for i in markets:
        path = cwd + "/crypto/bittrex/orderBook/" + i
        if(not os.path.isdir(path)):
            os.mkdir(path)

def main():
    r = requests.get("https://api.bittrex.com/api/v1.1/public/getmarkets")
    marketData = r.json()["result"]
    markets = []
    for i in marketData:
        if(i["IsRestricted"] == False):
            markets.append(i["MarketName"])
    createDirectories(markets)
    while(-1):
        try:
            with Session() as session:
                print("Restarting connection!")
                connection = Connection("https://socket.bittrex.com/signalr", session)
                chat = connection.register_hub('corehub')
                connection.received += handle_received
                connection.error += print_error
                connection.start()

                # You missed this part
                chat.client.on('updateExchangeState', msg_received)
                for i in range(10):
                    for market in markets:
                        print("Querying: " + market)
                        #chat.server.invoke('SubscribeToExchangeDeltas', market)
                        chat.server.invoke('QueryExchangeState', market)
                    connection.wait(60)

                # Value of 1 will not work, you will get disconnected
                #connection.wait(120000)
        except KeyboardInterrupt:
            break
        except:
            continue


if __name__ == "__main__":
    main()