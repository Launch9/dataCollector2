import matplotlib.pyplot as plt
import json
import numpy as np
import requests
from os import listdir
from os.path import isfile, join
import datetime
import pandas as pd
def reverseMarketName(market):
    firstCoin = ""
    secondCoin = ""
    isOnSecond = False
    for i in market:
        if(i == "-"):
            isOnSecond = True
            continue
        if(not isOnSecond):
            firstCoin = firstCoin + i
        else:
            secondCoin = secondCoin + i
    return secondCoin + "-" + firstCoin

folder = "USD-BTC"
mypath = "./" + folder
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
xBuy = []
xSell = []
yBuy = []
ySell = []

buyOrders = pd.DataFrame(columns=['time', 'rate'])
sellOrders = pd.DataFrame(columns=['time', 'rate'])
smallestTime = 9999999999999
for i in onlyfiles:
    print(i)
    with open(mypath + "/" + i,"r") as infile:
        data = json.load(infile)
        timestamp = data["timestamp"]
        if(timestamp < smallestTime):
            smallestTime = timestamp
        buys = data["data"]["Buys"]
        sells = data["data"]["Sells"]
        for b in buys:
            #if(b["Quantity"] > 3):
            xBuy.append(timestamp)
            yBuy.append(b["Rate"])
            #buyOrders = buyOrders.append({'rate': b["Rate"], 'time':timestamp}, ignore_index=True)
        for b in sells:
            #if(b["Quantity"] > 3):
            xSell.append(timestamp)
            ySell.append(b["Rate"])
            #sellOrders = sellOrders.append({'rate': b["Rate"], 'time':timestamp}, ignore_index=True)
           
buyOrders["time"] = np.asarray(xBuy)
buyOrders["rate"] = np.asarray(yBuy)
sellOrders["time"] = np.asarray(xSell)
sellOrders["rate"] = np.asarray(ySell)
#buyOrders.set_index("time")
#sellOrders.set_index("time")
buyOrders.to_csv("./buyOrders.csv")
sellOrders.to_csv("./sellOrders.csv")
so = pd.read_csv("./sellOrders.csv")
bo = pd.read_csv("./buyOrders.csv")

dt = datetime.datetime.fromtimestamp(smallestTime - 10000)

r = requests.get("https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=" + folder + "&tickInterval=oneMin")
#r = requests.get("https://api.bittrex.com/v3/markets/" + reverseMarketName(folder) + "/candles/MINUTE_1/historical/" + str(dt.year) + "/" + str(dt.month) + "/" + str(dt.day))
candles = r.json()['result']
candX = []
candY = []
dfObj = pd.DataFrame(columns=['close', 'time'])
for i in candles:
    candY.append(i["C"])
    candX.append(datetime.datetime.fromisoformat(i["T"]).timestamp())
dfObj["close"] = np.asarray(candY)
dfObj["time"] = np.asarray(candX)
#so["rate"] = so["rate"] * dfObj["close"][0:len(so["rate"]) - 1]
#bo["rate"] = bo["rate"] * dfObj["close"][0:len(bo["rate"]) - 1]
dfObj = dfObj.set_index(['time'])
dfObj.to_csv("./test.csv")
df = pd.read_csv("./test.csv")
plt.plot(df["time"], df["close"])
plt.scatter(so["time"],so["rate"],alpha=0.04)
plt.scatter(bo["time"],bo["rate"], alpha=0.04)
#plt.plot(candX,candY)
plt.show()