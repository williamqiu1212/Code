
from cProfile import label
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
import backtest as bt


plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')

eur= pd.read_excel('riskreversalAUD.xlsx')
eur=eur.sort_values('Date')

eur['3mChange'] = (eur['threeMonth'] / eur['threeMonth'].shift(1) - 1).fillna(0)
eur['balticChange'] = (eur['baltic'] / eur['baltic'].shift(1) - 1).fillna(0)


eurStats=eur.describe()
length=len(eur)


pd.set_option('display.max_rows', None)

date=eur.Date
eur3Mrr=eur.threeMonth
baltic=eur.baltic
eur3MrrLog=eur['3mChange']

eur3M_ent=[]
eur3M_ext=[]
mean=eur3Mrr.mean()


k = eur['baltic'].ewm(span=12, adjust=False, min_periods=12).mean()
# Get the 12-day EMA of the closing price
d = eur['baltic'].ewm(span=26, adjust=False, min_periods=26).mean()
# Subtract the 26-day EMA from the 12-Day EMA to get the MACD
macd = pd.DataFrame(k - d)
# Get the 9-Day EMA of the MACD for the Trigger line
macd_s = pd.DataFrame(macd.ewm(span=9, adjust=False, min_periods=9).mean())
# Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
macd_h = pd.DataFrame(macd - macd_s)

frames = [date]
df = pd.concat(frames, join = 'inner', axis = 1)
df['baltic']=baltic
df['threeMonth']=eur3Mrr
df['macd']=macd
df['macd_s']=macd_s
df['macd_h']=macd_h
df['AUDJPY']=eur.AUDJPY
df['ATM']=eur.ATM


df["7d_vol"] = df["baltic"].pct_change().rolling(20).std()



df['up']=(df.macd>=df.macd_s).astype(int)
df['down']=(df.macd<=df.macd_s).astype(int)
df['buy']=(((df['up'].shift(1))==1)&(df['down']==1))
df['sell']=((df['down'].shift(1))==1)&(df['up']==1)
df['moment']=((df['up'].shift(1))==df['up']).astype(int)

length=len(df.moment)
counter=[]
col = df["moment"].values.tolist()
count =0 
for i in range(length):
  
    if(col[i])==col[i-1]:
            count=count+1
            counter.append(count)
    else:
         count=1
         counter.append(count)
df['track']=counter
df['max']=1

a = df["macd_h"].values.tolist()
b = df["track"].values.tolist()
d = df["moment"].values.tolist()
c=[]

max=0
#monitors max of histogram 
for i in range(length):
    if(d[i]==0):
        max=0
    if(b[i]>=1):
        if(abs(a[i])>max):
            max=abs(a[i])
        c.append(max)
    else:
        c.append(max)
df['max']=c

f=df['max'].values.tolist()
filler=[]

#detects entry signals
for i in range(length):
    # mult=0.35
    # if(b[i]==1):
    #     mult=0.35
    if(d[i]==0):
        filler.append(0)
    elif(a[i]>=0):
        if(a[i]<=(f[i])*0.35):
            filler.append(1)
            
        else:
            filler.append(0)
    elif(a[i]<=0):
        if(-1*(a[i])<=(f[i])*0.35):
            filler.append(1)
        else:
            filler.append(0)
    else:
        filler.append(0)
df['newMom']=filler
df['newMom']=df['newMom']&(df['7d_vol']>=0.02)
df['newBuy']=(((df['macd_h']>0)&(df['newMom']==True)))&(df['track'].shift(1)>=7)
df['newSell']=(((df['macd_h']<0)&(df['newMom']==True)))&(df['track'].shift(1)>=7)



entry=(df.loc[df['newBuy']])
exit=(df.loc[df['newSell']])
# entry=(df.loc[df['buy']])
# exit=(df.loc[df['sell']])

a=entry['threeMonth']
b=entry["Date"]
c=exit['threeMonth']
d=exit["Date"]


x=df["Date"]
y=df['threeMonth']





early=bt.early(df)
df['early']=early
earlyLong=(df.loc[df['early']==1])
earlyShort=(df.loc[df['early']==-1])
df['position']=bt.positionB(df)


# ut=pd.DataFrame
# ut['Date']=pd.DataFrame(a)
# ut['Ledger']=pd.DataFrame(b)
# a=bt.position(df)
# b=bt.positionB(df)


plt.figure(figsize=(10,2.5))
plt.plot(x,y)
plt.plot_date(b,a,marker='^', ms='6',color = 'g',label='long')
plt.plot_date(d,c,marker='v',ms='6',color = 'r',label='short')
plt.plot_date(earlyLong.Date,earlyLong.threeMonth,marker='v',ms='6',color = 'blue',label='selling early')
plt.plot_date(earlyShort.Date,earlyShort.threeMonth,marker='^',ms='6',color = 'orange',label='covering early')
plt.xlabel('Date')
plt.ylabel('AUDJPY 3M RR')
plt.grid(True)
plt.legend()

plt.figure(figsize=(10,2.5))
plt.plot(df.Date,df.baltic)
plt.xlabel('Date')
plt.ylabel('BDI')
plt.title('BDI ')
plt.legend()

# plot correspondingRSI values and significant levels
plt.figure(figsize=(10,2.5))
plt.plot(df['Date'], df['macd'].fillna(0),label='macd line')
plt.plot(df['Date'], df['macd_s'].fillna(0),label='signal line')
plt.plot(df['Date'], df['macd_h'].fillna(0),label='histogram')
plt.bar(df['Date'], df['macd_h'].fillna(0), width=0.5, snap=False)
plt.title('BDI MACD')
plt.xlabel('Date')
plt.ylabel('BDI')
plt.legend()



bt.backtest_dollarValue(df)
 


# plt.show()



def input():
    return df

def po():
    return df.position

