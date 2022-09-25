
from cmath import log
from turtle import up
from unittest.loader import VALID_MODULE_NAME
import eikon as ek
from jsonschema import RefResolutionError
import refinitiv.data as rd

import numpy as np
import configparser as cp
import pandas as pd
from matplotlib import pyplot as plt

import statsmodels.api as sm

import main as p

df=p.input()
percentage_change = []
netProfit=0
PnL=[]

spotPnL=0
fxRate=df['AUDJPY'][1]
        
for i in df.index:
    close = df["AUDJPY"][i]
    date = df['Date'][i]
    position=df['position'][i]
    if(position==1):
     pc = (close-fxRate)/fxRate*100
     percentage_change.append(pc)
     netProfit=netProfit +(close-fxRate)
     fxRate=close
    elif(position==-1):
     pc = (fxRate-close)/fxRate*100
     percentage_change.append(pc)
     netProfit=netProfit +(fxRate+close)
     fxRate=close
    else:
     fxRate=close
     pc=0
     percentage_change.append(pc)
   # PnL.append(netProfit)
gains = 0
ng = 0
losses = 0
nl = 0
totalR = 1

for i in percentage_change:
    if(i > 0):
        gains += i
        ng += 1
    elif(i<0):
        losses += i
        nl += 1
    totalR = totalR * ((i/100)+1)
    PnL.append(totalR)

totalR = round((totalR-1)*100, 2)

if(ng > 0):
    avgGain = round(gains/ng, 2)
    maxR = round(max(percentage_change), 2)
else:
    avgGain = 0
    maxR = "undefined"

if(nl > 0):
    avgLoss = round(losses/nl, 2)
    maxL = round(min(percentage_change), 2)
else:
    avgLoss = 0
    maxL = "undefined"

if(ng > 0 or nl > 0):
    win_rate = round((ng/(ng+nl))*100, 2)
else:
    win_rate = 0



print()
print('Evaluation Metrics:')
print('-----------------------------------')
print(f"Number of Trades: {ng+nl}")
print(f"Number of Gains: {ng}")
print(f"Number of Losses: {nl}")
print(f"Total Returns: {totalR}%")
print(f"Win Rate: {win_rate}%")
print(f"Average Gain: {avgGain}%")
print(f"Average Loss: {avgLoss}%")
print(f"Max Return: {maxR}%")
print(f"Max Loss: {maxL}%")


long=(df.loc[df['position']==1])
short=(df.loc[df['position']==-1])

q=long['AUDJPY']
w=long["Date"]
e=short['AUDJPY']
r=short["Date"]
x=df["Date"]
y=df['AUDJPY']

plt.figure(figsize=(10,2.5))
plt.plot(x,y)
plt.plot_date(w,q,marker='^', ms='6',color = 'g')
plt.plot_date(r,e,marker='v',ms='6',color = 'r')
plt.xlabel('Date')
plt.ylabel('AUD/JPY FX Rate')



plt.figure(figsize=(10,2.5))
plt.plot(df.Date,PnL)
plt.xlabel('Date')
plt.ylabel('AUD/JPY Delta PnL')

plt.show()
