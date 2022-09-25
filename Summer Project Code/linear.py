
from cmath import exp
from multiprocessing.util import close_all_fds_except
from operator import index


import numpy as np
import scipy.stats as si
import math 
import scipy.optimize as op
import pandas as pd


pd.options.display.float_format = '{:,.3f}'.format

AUDJPY10_Call='AUDJPY10C3M=R'
AUDJPY15_Call='AUDJPY15C3M=R'
AUDJPY20_Call='AUDJPY20C3M=R'
AUDJPY25_Call='AUDJPY25C3M=R'
AUDJPY30_Call='AUDJPY30C3M=R'
AUDJPY35_Call='AUDJPY35C3M=R'
AUDJPY40_Call='AUDJPY40C3M=R'
AUDJPY45_Call='AUDJPY45C3M=R'

AUDJPY10_Put='AUDJPY10P3M=R'
AUDJPY15_Put='AUDJPY15P3M=R'
AUDJPY20_Put='AUDJPY20P3M=R'
AUDJPY25_Put='AUDJPY25P3M=R'
AUDJPY30_Put='AUDJPY30P3M=R'
AUDJPY35_Put='AUDJPY35P3M=R'
AUDJPY40_Put='AUDJPY40P3M=R'
AUDJPY45_Put='AUDJPY45P3M=R'

pd.set_option('display.max_rows', None)

vol=pd.read_excel('VS.xlsx')
vol.Date=pd.to_datetime(vol.Date)
vol =vol.set_index(vol.Date)

ledger=pd.read_excel('OldPositions.xlsx')
ledger.Date=pd.to_datetime(ledger.Date)
ledger= ledger.set_index(ledger.Date)
ledger['newCallDelta']=0.0
ledger['newCallVol']=0.0
ledger['newPutDelta']=0.0
ledger['newPutVol']=0.0

call=pd.read_excel('CallDelta.xlsx')
call.Date=pd.to_datetime(call.Date)
call =call.set_index(call.Date)
put=pd.read_excel("PutDelta.xlsx")
put.Date=pd.to_datetime(put.Date)
put =put.set_index(put.Date)


def linearInt(goal,x1,x2,y1,y2):
    slope=float((y2-y1)/(x2-x1)) # Delta/Strike
    factor= float((goal-x1))  # Difference in Strike between goal and lowest
    return float(slope*factor+y1) # add by initial delta

def nearest(panda, col_name, pivot):

    row= panda.index.get_loc(pivot, method='nearest')
    col=panda.columns.get_loc(col_name)
    value= panda.iloc[row,col]
    return(value)


# print(linearInt(85.667135,85.427889,85.992135,35,30))

for i in ledger.index:
    date=ledger['Date'][i]
    strike=ledger['CallStrike'][i]
    test=nearest(call,'Date',date)
    value= call[call['Date']==test].index.values

    
    callarr=[]
    callarr.append(abs(strike-call.at[test,'10Call']))
    callarr.append(abs(strike-call.at[test,'15Call']))
    callarr.append(abs(strike-call.at[test,'20Call']))
    callarr.append(abs(strike-call.at[test,'25Call']))
    callarr.append(abs(strike-call.at[test,'30Call']))
    callarr.append(abs(strike-call.at[test,'35Call']))
    callarr.append(abs(strike-call.at[test,'40Call']))
    callarr.append(abs(strike-call.at[test,'45Call']))
    callarr.sort()

    min1=callarr[0]
    min2=callarr[1]

    delta=[]
    callstrike=[]

    if(abs(strike-call.at[test,'10Call'])==min1 or abs(strike-call.at[test,'10Call'])==min2):
        delta.append(10)
        callstrike.append(call.at[test,'10Call'])
    
    if(abs(strike-call.at[test,'15Call'])==min1 or abs(strike-call.at[test,'15Call'])==min2):
        delta.append(15)
        callstrike.append(call.at[test,'15Call'])
    
    if(abs(strike-call.at[test,'20Call'])==min1 or abs(strike-call.at[test,'20Call'])==min2):
        delta.append(20)
        callstrike.append(call.at[test,'20Call'])

    if(abs(strike-call.at[test,'25Call'])==min1 or abs(strike-call.at[test,'25Call'])==min2):
        delta.append(25)
        callstrike.append(call.at[test,'25Call'])

    if(abs(strike-call.at[test,'30Call'])==min1 or abs(strike-call.at[test,'30Call'])==min2):
        delta.append(30)
        callstrike.append(call.at[test,'30Call'])
    
    if(abs(strike-call.at[test,'35Call'])==min1 or abs(strike-call.at[test,'35Call'])==min2):
        delta.append(35)
        callstrike.append(call.at[test,'35Call'])
    
    if(abs(strike-call.at[test,'40Call'])==min1 or abs(strike-call.at[test,'40Call'])==min2):
        delta.append(40)
        callstrike.append(call.at[test,'40Call'])
    
    if(abs(strike-call.at[test,'45Call'])==min1 or abs(strike-call.at[test,'45Call'])==min2):
        delta.append(45)
        callstrike.append(call.at[test,'45Call'])

    ledger['newCallDelta'][i]=float(linearInt(strike,callstrike[0],callstrike[1],delta[0],delta[1]))



for i in ledger.index:
    date=ledger['Date'][i]
    strike=ledger['PutStrike'][i]
    test=nearest(put,'Date',date)
    value= put[put['Date']==test].index.values

    
    putarr=[]
    putarr.append(abs(strike-put.at[test,'10Put']))
    putarr.append(abs(strike-put.at[test,'15Put']))
    putarr.append(abs(strike-put.at[test,'20Put']))
    putarr.append(abs(strike-put.at[test,'25Put']))
    putarr.append(abs(strike-put.at[test,'30Put']))
    putarr.append(abs(strike-put.at[test,'35Put']))
    putarr.append(abs(strike-put.at[test,'40Put']))
    putarr.append(abs(strike-put.at[test,'45Put']))
    putarr.sort()

    min1=putarr[0]
    min2=putarr[1]

    deltaP=[]
    putstrike=[]

    if(abs(strike-put.at[test,'10Put'])==min1 or abs(strike-put.at[test,'10Put'])==min2):
        deltaP.append(10)
        putstrike.append(put.at[test,'10Put'])
    
    if(abs(strike-put.at[test,'15Put'])==min1 or abs(strike-put.at[test,'15Put'])==min2):
        deltaP.append(15)
        putstrike.append(put.at[test,'15Put'])

    if(abs(strike-put.at[test,'20Put'])==min1 or abs(strike-put.at[test,'20Put'])==min2):
        deltaP.append(20)
        putstrike.append(put.at[test,'20Put'])

    if(abs(strike-put.at[test,'25Put'])==min1 or abs(strike-put.at[test,'25Put'])==min2):
        deltaP.append(25)
        putstrike.append(put.at[test,'25Put'])
    
    if(abs(strike-put.at[test,'30Put'])==min1 or abs(strike-put.at[test,'30Put'])==min2):
        deltaP.append(30)
        putstrike.append(put.at[test,'30Put'])

    if(abs(strike-put.at[test,'35Put'])==min1 or abs(strike-put.at[test,'35Put'])==min2):
        deltaP.append(35)
        putstrike.append(put.at[test,'35Put'])

    if(abs(strike-put.at[test,'40Put'])==min1 or abs(strike-put.at[test,'40Put'])==min2):
        deltaP.append(40)
        putstrike.append(put.at[test,'40Put'])

    if(abs(strike-put.at[test,'45Put'])==min1 or abs(strike-put.at[test,'45Put'])==min2):
        deltaP.append(45)
        putstrike.append(put.at[test,'45Put'])

   

    ledger['newPutDelta'][i]=float(linearInt(strike,putstrike[0],putstrike[1],deltaP[0],deltaP[1]))
    
    


for i in ledger.index:
    date=ledger['Date'][i]
    newCallDelta=float(ledger['newCallDelta'][i])

    
    test=nearest(vol,'Date',date)
    value= vol[vol['Date']==test].index.values

    
    callarr=[]

    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY10_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY15_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY20_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY25_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY30_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY35_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY40_Call])))
    callarr.append(float(abs(newCallDelta-vol.at[test,AUDJPY45_Call])))

    callarr.sort()

    min1=callarr[0]
    min2=callarr[1]

    delta=[]
    callvol=[]

    if(abs(newCallDelta-vol.at[test,AUDJPY10_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY10_Call])==min2):
        delta.append(10.0)
        callvol.append(float(vol.at[test,AUDJPY10_Call]))
    
    if(abs(newCallDelta-vol.at[test,AUDJPY15_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY15_Call])==min2):
        delta.append(15.0)
        callvol.append(float(vol.at[test,AUDJPY15_Call]))
    
    if(abs(newCallDelta-vol.at[test,AUDJPY20_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY20_Call])==min2):
        delta.append(20.0)
        callvol.append(float(vol.at[test,AUDJPY20_Call]))
    
    if(abs(newCallDelta-vol.at[test,AUDJPY25_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY25_Call])==min2):
        delta.append(25.0)
        callvol.append(float(vol.at[test,AUDJPY25_Call]))
  
    if(abs(newCallDelta-vol.at[test,AUDJPY30_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY30_Call])==min2):
        delta.append(30.0)
        callvol.append(float(vol.at[test,AUDJPY30_Call]))
    
    if(abs(newCallDelta-vol.at[test,AUDJPY35_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY35_Call])==min2):
        delta.append(35.0)
        callvol.append(float(vol.at[test,AUDJPY35_Call]))
    
    if(abs(newCallDelta-vol.at[test,AUDJPY40_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY40_Call])==min2):
        delta.append(40.0)
        callvol.append(float(vol.at[test,AUDJPY40_Call]))
    
    if(abs(newCallDelta-vol.at[test,AUDJPY45_Call])==min1 or abs(newCallDelta-vol.at[test,AUDJPY45_Call])==min2):
        delta.append(45.0)
        callvol.append(float(vol.at[test,AUDJPY45_Call]))
    #vol / delta


    ledger['newCallVol'][i]=float(linearInt(newCallDelta,delta[1],delta[0],callvol[1],callvol[0]))


for i in ledger.index:
    date=ledger['Date'][i]
    newPutDelta=(ledger['newPutDelta'][i].astype(float))
    
    test=nearest(vol,'Date',date)
    value= vol[vol['Date']==test].index.values

    
    putarr=[]

    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY10_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY15_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY20_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY25_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY30_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY35_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY40_Put])))
    putarr.append(float(abs(newPutDelta-vol.at[test,AUDJPY45_Put])))
   
   

    putarr.sort()

    min1=putarr[0]
    min2=putarr[1]

    delta=[]
    putvol=[]

    if(abs(newPutDelta-vol.at[test,AUDJPY10_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY10_Put])==min2):
        delta.append(10)
        putvol.append(float(vol.at[test,AUDJPY10_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY15_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY15_Put])==min2):
        delta.append(15)
        putvol.append(float(vol.at[test,AUDJPY15_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY20_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY20_Put])==min2):
        delta.append(20)
        putvol.append(float(vol.at[test,AUDJPY20_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY25_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY25_Put])==min2):
        delta.append(25)
        putvol.append(float(vol.at[test,AUDJPY25_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY30_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY30_Put])==min2):
        delta.append(30)
        putvol.append(float(vol.at[test,AUDJPY30_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY35_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY35_Put])==min2):
        delta.append(35)
        putvol.append(float(vol.at[test,AUDJPY35_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY40_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY40_Put])==min2):
        delta.append(40)
        putvol.append(float(vol.at[test,AUDJPY40_Put]))

    if(abs(newPutDelta-vol.at[test,AUDJPY45_Put])==min1 or abs(newPutDelta-vol.at[test,AUDJPY45_Put])==min2):
        delta.append(45)
        putvol.append(float(vol.at[test,AUDJPY45_Put]))
    

    ledger['newPutVol'][i]=float(linearInt(newPutDelta,delta[0],delta[1],putvol[0],putvol[1]))
   


print(ledger)







# print(ledger['newCallVol'].astype(float))
# print(vol)
# print(vol.at[test,AUDJPY35_Put])
    # print(call[value][0])

# def IV(Date,Tenor):
#     trial= nearest(option ,'Date',Date).to
#     test=option[Tenor]
#     # # row=final_f[final_f['Date'] == trial].index
#     # row=final_f.index[final_f["Date"]==trial].tolist()
#     # col=final_f.columns.get_loc('interest')
   
#     value= test[option['Date']==trial].index.values
#     p=test[value][0]
#     return p



