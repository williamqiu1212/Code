
from cmath import log
from turtle import up
import eikon as ek
from jsonschema import RefResolutionError
import refinitiv.data as rd

import numpy as np
import configparser as cp
import pandas as pd
from matplotlib import pyplot as plt
import bsm 

import statsmodels.api as sm
import interest as it
import backtest as bt
import main as p
#import optionIV as op

call25='AUDJPY25C3M=R'
put25='AUDJPY25P3M=R'
call10='AUDJPY10C3M=R'
put10='AUDJPY10P3M=R'
atm='AUDJPY3MO='

def gain(value):
    if value < 0:
        return 0
    else:
        return value

def loss(value):
    if value > 0:
        return 0
    else:
        return abs(value)

def nearest(panda, col_name, pivot):
    row= panda.index.get_loc(pivot, method='nearest')
    col=panda.columns.get_loc(col_name)
    value= panda.iloc[row,col]
    return(value)

opt= pd.read_excel('legData.xlsx')
option=pd.DataFrame()



option=pd.DataFrame()
option['Date']=pd.to_datetime(opt['Date'], format='%Y-%m-%d %I-%p')
option['25Put']=opt['AUDJPY25P3M=R'].astype(float,errors='ignore')
option['25Call']=opt['AUDJPY25C3M=R'].astype(float,errors='ignore')
option['10Put']=opt['AUDJPY10P3M=R'].astype(float,errors='ignore')
option['10Call']=opt['AUDJPY10C3M=R'].astype(float,errors='ignore')
option['50ATM']=opt['AUDJPY3MO='].astype(float,errors='ignore')
option = (opt.dropna()).sort_values(by=['Date'], ascending=True)
option.Date=pd.to_datetime(option.Date)
option =option.set_index(option.Date)


# final=pd.DataFrame()
# final=final.set_index(final.Date)
# final=(option.dropna()).sort_values(by=['Date'], ascending=True)

def IV(Date,Tenor):
    trial= nearest(option ,'Date',Date)
    test=option[Tenor]
    # # row=final_f[final_f['Date'] == trial].index
    # row=final_f.index[final_f["Date"]==trial].tolist()
    # col=final_f.columns.get_loc('interest')
   
    value= test[option['Date']==trial].index.values
    p=test[value][0]
    return p



df=p.input()

# test=pd.DataFrame
# newPos=0
# netProfit=0
deltaExposure=[]
delta=0
deltaPnL=[]

#greek exposure
gammaExposure=[]
gamma=0

vegaExposure=[]
vega=0
impliedVol=[]
iv=0

thetaExposure=[]
theta=0

percentageChange=[]
netProfit=0
pc=0


# option statistics
domesticRate=0
foreignRate=0
CallIV=0
PutIV=0
CallS=0
PutS=0
CallPrice=0
CallClose=0
PutPrice=0
PutClose=0
first=1
initialDollar=0

fxRate=df['AUDJPY'][1]
Maturity=0

result=[]

time=[]


for i in df.index:
    Maturity=Maturity-1
    fxRate=df['AUDJPY'][i]
    date = df['Date'][i]
    CallIV=IV(date,call25)/100
    PutIV=IV(date,put25)/100
    domesticRate=it.domesticRate(date)
    foreignRate=it.foreignRate(date)
    position=df['position'][i]
    newPos=df['newPos'][i]
    


    if(newPos==1&position!=0):
        Maturity=90
        # domesticRate=0.02
        # foreignRate=0.02
        # CallIV=0.02
        # PutIV=0.02xs
        CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
        PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)

        CallPrice=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        PutPrice=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        if(first==1&position==1):
            initialDollar=CallPrice-PutPrice
            first=0
        if(first==1&position==-1):
            initialDollar=PutPrice-CallPrice
            first=0
        # test=bsm.CallDelta(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
    elif(position==0):
        CallS=0
        PutS=0
        Maturity=0
    
    if(position==1):
        delta=bsm.CallDelta(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)-bsm.PutDelta(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        deltaExposure.append(delta)
        gamma=bsm.CallGamma(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)-bsm.PutGamma(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        gammaExposure.append(gamma)
        vega=bsm.CallVega(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)-bsm.PutVega(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        vegaExposure.append(vega)
        theta=bsm.CallTheta(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)-bsm.PutTheta(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        thetaExposure.append(theta)

        # CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        # PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)

        # netProfit=netProfit+(CallClose-PutClose)-(CallPrice-PutPrice)
        # profit=(CallClose-PutClose)-(CallPrice-PutPrice)
        # change=((CallClose-PutClose)-(CallPrice-PutPrice))/(CallPrice-PutPrice)
        # if(profit>=0):
        #     percentageChange.append(abs(change))
        # else:
        #     percentageChange.append(-abs(change))
        

        time.append(Maturity)
    elif(position==-1):
        delta=bsm.PutDelta(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)-bsm.CallDelta(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        deltaExposure.append(delta)
        gamma=bsm.PutGamma(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)-bsm.CallGamma(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        gammaExposure.append(gamma)
        vega=bsm.PutVega(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)-bsm.CallVega(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        vegaExposure.append(vega)
        theta=bsm.PutTheta(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)-bsm.CallTheta(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        thetaExposure.append(theta)
        

        CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)
        
        profit=(PutClose-CallClose)-(PutPrice-CallPrice)
        change=((PutClose-CallClose)-(PutPrice-CallPrice))/(PutPrice-CallPrice)
        if(profit>=0):
            percentageChange.append(abs(change))
        else:
            percentageChange.append(-abs(change))

        netProfit=netProfit+(PutClose-CallClose)-(PutPrice-CallPrice)
        

        time.append(Maturity)
    else:
        deltaExposure.append(0)
        gammaExposure.append(0)
        vegaExposure.append(0)
        thetaExposure.append(0)
        time.append(Maturity)
        percentageChange.append(0)
        CallPrice=0
        PutPrice=0



# print(netProfit)
# print(initialDollar)
df['time']=time


x=df.Date
y=deltaExposure
z=df['AUDJPY']


gains = 0
ng = 0
losses = 0
nl = 0
totalR = 1

for i in percentageChange:
    if(i > 0):
        gains += i
        ng += 1
    elif(i<0):
        losses += i
        nl += 1
    totalR = totalR * ((i/100)+1)

totalR = round((totalR-1)*100, 2)

if(ng > 0):
    avgGain = round(gains/ng, 2)
    maxR = round(max(percentageChange), 2)
else:
    avgGain = 0
    maxR = "undefined"

if(nl > 0):
    avgLoss = round(losses/nl, 2)
    maxL = round(min(percentageChange), 2)
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

# fig, ax = plt.subplots()

# # Plot linear sequence, and set tick labels to the same color
# ax.plot(x,y, color='red')


# # Generate a new Axes instance, on the twin-X axes (same position)
# ax2 = ax.twinx()

# # Plot exponential sequence, set scale to logarithmic and change tick color
# ax2.plot(x,z, color='green')
# ax2.tick_params(axis='y', labelcolor='green')






# plt.figure(figsize=(10,2.5))
# plt.plot(x,deltaExposure)
# plt.plot(x,z)
# plt.xlabel('Date')
# plt.ylabel('Delta')
# plt.title('Delta Position')



plt.figure(figsize=(10,2.5))
plt.plot(x,gammaExposure)

plt.xlabel('Date')
plt.ylabel('Gamma')
plt.title('Gamma Position')

plt.figure(figsize=(10,2.5))
plt.plot(x,vegaExposure)

plt.xlabel('Date')
plt.ylabel('vega')
plt.title('Vega Position')

plt.figure(figsize=(10,2.5))
plt.plot(x,thetaExposure)

plt.xlabel('Date')
plt.ylabel('Theta')
plt.title('Theta Position')

plt.show()






