from cmath import exp
from multiprocessing.util import close_all_fds_except
from operator import index


import numpy as np
import scipy.stats as si
import math 
import scipy.optimize as op
import pandas as pd

pd.set_option('display.max_rows', None)


df= pd.read_excel('testdata.xlsx')
volData=pd.read_excel('VS.xlsx')


position=pd.read_excel('OldPositions.xlsx')
#list=pd.read_excel('CallDelta.xlsx')
volData=volData.sort_values('Date')

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


#df=df.sort_values('Date')



def nearest(panda, col_name, pivot):

    row= panda.index.get_loc(pivot, method='nearest')
    col=panda.columns.get_loc(col_name)
    value= panda.iloc[row,col]
    return(value)



def GoalSeek(fun,goal,x0,fTol=0.0001,MaxIter=1000):
    # Goal Seek function of Excel
    #   via use of Line Search and Bisection Methods

    # Inputs
    #   fun     : Function to be evaluated
    #   goal    : Expected result/output
    #   x0      : Initial estimate/Starting point

    # Initial check
    if fun(x0)==goal:
        print('Exact solution found')
        return x0

    # Line Search Method
    step_sizes=np.logspace(-1,4,6)
    scopes=np.logspace(1,5,5)

    vFun=np.vectorize(fun)

    for scope in scopes:
        break_nested=False
        for step_size in step_sizes:

            cApos=np.linspace(x0,x0+0.5*step_size*scope,int(scope))
            cAneg=np.linspace(x0,x0-0.5*step_size*scope,int(scope))

            cA=np.concatenate((cAneg[::-1],cApos[1:]),axis=0)

            fA=vFun(cA)-goal

            if np.any(np.diff(np.sign(fA))):

                index_lb=np.nonzero(np.diff(np.sign(fA)))

                if len(index_lb[0])==1:

                    index_ub=index_lb+np.array([1])
                    

                    x_lb=(np.array(cA)[index_lb][0]).item()
                    x_ub=(np.array(cA)[index_ub][0]).item()
                    break_nested=True
                    break
                else: # Two or more roots possible

                    index_ub=index_lb+np.array([1])

                    print('Other solution possible at around, x0 = ', np.array(cA)[index_lb[0][1]])

                    x_lb=(np.array(cA)[index_lb[0][0]]).item()
                    x_ub=(np.array(cA)[index_ub[0][0]]).item()
                    break_nested=True
                    break

        if break_nested:
            break
    if not x_lb or not x_ub:
        print('No Solution Found')
        return

    # Bisection Method
    iter_num=0
    error=100

    while iter_num<MaxIter and fTol<error:
        
        x_m=(x_lb+x_ub)/2
        f_m=fun(x_m)-goal

        error=abs(f_m)

        if (fun(x_lb)-goal)*(f_m)<0:
            x_ub=x_m
        elif (fun(x_ub)-goal)*(f_m)<0:
            x_lb=x_m
        elif f_m==0:
            print('Exact spolution found')
            return x_m
        else:
            print('Failure in Bisection Method')
        
        iter_num+=1

    return x_m

def PolanitzerNormsdist(x):
    PolanitzerNormsdist = si.norm.cdf(x,0.0,1.0)
    return(PolanitzerNormsdist)

def PolanitzerGarmanKohlhagenCall(SpotRate, StrikeRate, Maturity, DomesticRiskFreeRate, ForeignRiskFreeRate, Volatility):
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRiskFreeRate-ForeignRiskFreeRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    d2 = (np.log(SpotRate/StrikeRate)+(DomesticRiskFreeRate-ForeignRiskFreeRate-0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    PolanitzerGarmanKohlhagenCall = SpotRate*np.exp(-ForeignRiskFreeRate*Maturity)*PolanitzerNormsdist(d1)-StrikeRate*np.exp(-DomesticRiskFreeRate*Maturity)*PolanitzerNormsdist(d2)
    return(PolanitzerGarmanKohlhagenCall)

def PolanitzerGarmanKohlhagenPut(SpotRate, StrikeRate, Maturity, DomesticRiskFreeRate, ForeignRiskFreeRate, Volatility):
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRiskFreeRate-ForeignRiskFreeRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    d2 = (np.log(SpotRate/StrikeRate)+(DomesticRiskFreeRate-ForeignRiskFreeRate-0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    PolanitzerGarmanKohlhagenPut = StrikeRate*np.exp(-DomesticRiskFreeRate*Maturity)*PolanitzerNormsdist(-d2)-SpotRate*np.exp(-ForeignRiskFreeRate*Maturity)*PolanitzerNormsdist(-d1)
    return(PolanitzerGarmanKohlhagenPut)

def CallDelta(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    N_d1=PolanitzerNormsdist(d1)
    return math.exp(-ForeignRate*Maturity)*N_d1

def PutDelta(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    N_d1=PolanitzerNormsdist(-d1)
    return -(math.exp(-ForeignRate*Maturity)*N_d1)

def CallStrike(SpotRate, Delta, Maturity, DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    goal=Delta      
    x0=SpotRate
    def Strike(Strike):
        d1 = (np.log(SpotRate/Strike)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
        N_d1=PolanitzerNormsdist(d1)
        return (math.exp(-ForeignRate*Maturity)*N_d1)

    Result_Example1=GoalSeek(Strike,goal,x0)
    return Result_Example1

def PutStrike(SpotRate, Delta, Maturity, DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    goal=Delta      
    x0=SpotRate
    def Strike(Strike):
        d1 = (np.log(SpotRate/Strike)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
        N_d1=PolanitzerNormsdist(-d1)
        return -(math.exp(-ForeignRate*Maturity)*N_d1)

    Result_Example1=GoalSeek(Strike,goal,x0)
    return Result_Example1

def CallGamma(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    n_d1=1/math.sqrt(2*math.pi)* math.exp(-(d1**2)/2)
    numerator=math.exp(-ForeignRate*Maturity)
    denominator=SpotRate*Volatility*math.sqrt(Maturity)
    return numerator/denominator*n_d1

def PutGamma(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    n_d1=1/math.sqrt(2*math.pi)* math.exp(-(d1**2)/2)
    numerator=math.exp(-ForeignRate*Maturity)
    denominator=SpotRate*Volatility*math.sqrt(Maturity)
    return numerator/denominator*n_d1


def CallTheta(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    n_d1=1/math.sqrt(2*math.pi)* math.exp(-(d1**2)/2)
    firstTerm=SpotRate*math.exp(-ForeignRate*Maturity)*ForeignRate*PolanitzerNormsdist(d1)
    secondTerm=StrikeRate*math.exp(-DomesticRate*Maturity)*DomesticRate*PolanitzerNormsdist(d1-Volatility*math.sqrt(Maturity))
    thirdTerm=(SpotRate*math.exp(-ForeignRate*Maturity)*Volatility*n_d1)/(2*math.sqrt(Maturity))
    return firstTerm - secondTerm - thirdTerm

def PutTheta(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    n_d1=1/math.sqrt(2*math.pi)* math.exp(-(d1**2)/2)
    firstTerm=SpotRate*math.exp(-ForeignRate*Maturity)*ForeignRate*PolanitzerNormsdist(-d1)
    secondTerm=StrikeRate*math.exp(-DomesticRate*Maturity)*DomesticRate*PolanitzerNormsdist(-d1+Volatility*math.sqrt(Maturity))
    thirdTerm=(SpotRate*math.exp(-ForeignRate*Maturity)*Volatility*n_d1)/(2*math.sqrt(Maturity))
    return -firstTerm + secondTerm - thirdTerm

def CallVega(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    n_d1=1/math.sqrt(2*math.pi)* math.exp(-(d1**2)/2)
    return SpotRate*math.exp(-ForeignRate*Maturity)*math.sqrt(Maturity)*n_d1

def PutVega(SpotRate,StrikeRate,Maturity,DomesticRate,ForeignRate,Volatility):
    Maturity=Maturity/365
    d1 = (np.log(SpotRate/StrikeRate)+(DomesticRate-ForeignRate+0.5*Volatility**2)*Maturity)/(Volatility*np.sqrt(Maturity))
    n_d1=1/math.sqrt(2*math.pi)* math.exp(-(d1**2)/2)
    return SpotRate*math.exp(-ForeignRate*Maturity)*math.sqrt(Maturity)*n_d1

# fxRate=df['FX Rate']
# dRate=df['DomesticRate']
# fRate=df['Foreign Rate']
# callIV=(df['Call IV'])/100
# putIV=(df['Put IV'])/100

# test=[]
# test1=[]
# Call=[]
# Put=[]

# for i in df.index:
#     fxRate=df['FX Rate'][i]
#     dRate=df['DomesticRate'][i]
#     fRate=df['Foreign Rate'][i]
#     callIV=(df['Call IV'])[i]/100
#     putIV=(df['Put IV'])[i]/100
#     CallStrikeSeries=(CallStrike(fxRate,0.25,90,dRate,fRate,callIV))
#     PutStrikeSeries=(PutStrike(fxRate,-0.25,90,dRate,fRate,putIV))
#     test.append(CallStrikeSeries)
#     test1.append(PutStrikeSeries)
#     a=PolanitzerGarmanKohlhagenCall(fxRate,CallStrikeSeries,90/365,dRate,fRate,callIV)
#     b=PolanitzerGarmanKohlhagenPut(fxRate,PutStrikeSeries,90/365,dRate,fRate,putIV)
#     Call.append(a)
#     Put.append(b)
# df['CallStrike']=test
# df['PutStrike']=test1
# df['callPrice']=Call
# df['putPrice']=Put

# print(df)











call_10=[]
call_15=[]
call_20=[]
call_25=[]
call_30=[]
call_35=[]
call_40=[]
call_45=[]

put_10=[]
put_15=[]
put_20=[]
put_25=[]
put_30=[]
put_35=[]
put_40=[]
put_45=[]

fxRate=0
dRate=0
fRate=0
callVol=pd.DataFrame


for i in volData.index:
    
    fxRate=volData['AUDJPY'][i]
    dRate=volData['AUD3MOIS='][i]
    fRate=volData['JPY3MOIS='][i]
    Call10=volData[AUDJPY10_Call][i]/100
    Call15=volData[AUDJPY15_Call][i]/100
    Call20=volData[AUDJPY20_Call][i]/100  
    Call25=volData[AUDJPY25_Call][i]/100   
    Call30=volData[AUDJPY30_Call][i]/100
    Call35=volData[AUDJPY35_Call][i]/100
    Call40=volData[AUDJPY40_Call][i]/100
    Call45=volData[AUDJPY45_Call][i]/100

    Put10=volData[AUDJPY10_Put][i]/100
    Put15=volData[AUDJPY15_Put][i]/100
    Put20=volData[AUDJPY20_Put][i]/100  
    Put25=volData[AUDJPY25_Put][i]/100   
    Put30=volData[AUDJPY30_Put][i]/100
    Put35=volData[AUDJPY35_Put][i]/100
    Put40=volData[AUDJPY40_Put][i]/100
    Put45=volData[AUDJPY45_Put][i]/100

    call_10.append(CallStrike(fxRate,0.10,90,dRate,fRate,Call10))
    call_15.append(CallStrike(fxRate,0.15,90,dRate,fRate,Call15))
    call_20.append(CallStrike(fxRate,0.20,90,dRate,fRate,Call20))
    call_25.append(CallStrike(fxRate,0.25,90,dRate,fRate,Call25))
    call_30.append(CallStrike(fxRate,0.30,90,dRate,fRate,Call30))
    call_35.append(CallStrike(fxRate,0.35,90,dRate,fRate,Call35))
    call_40.append(CallStrike(fxRate,0.40,90,dRate,fRate,Call40))
    call_45.append(CallStrike(fxRate,0.45,90,dRate,fRate,Call45))

    put_10.append(PutStrike(fxRate,-0.10,90,dRate,fRate,Put10))
    put_15.append(PutStrike(fxRate,-0.15,90,dRate,fRate,Put15))
    put_20.append(PutStrike(fxRate,-0.20,90,dRate,fRate,Put20))
    put_25.append(PutStrike(fxRate,-0.25,90,dRate,fRate,Put25))
    put_30.append(PutStrike(fxRate,-0.30,90,dRate,fRate,Put30))
    put_35.append(PutStrike(fxRate,-0.35,90,dRate,fRate,Put35))
    put_40.append(PutStrike(fxRate,-0.40,90,dRate,fRate,Put40))
    put_45.append(PutStrike(fxRate,-0.45,90,dRate,fRate,Put45))

# st1 = range(100)
# lst2 = range(100)
# lst3 = range(100)
list = pd.DataFrame(
    {'Date': (volData.Date),
     '10': call_10,
     '15': call_15,
     '20': call_20,
     '25': call_25,
     '30': call_30,
     '35': call_35,
     '40': call_40,
     '45': call_45
    })



list2=pd.DataFrame(
    {'Date': (volData.Date),
     '10': put_10,
     '15': put_15,
     '20': put_20,
     '25': put_25,
     '30': put_30,
     '35': put_35,
     '40': put_40,
     '45': put_45
    })






# list.Date=pd.to_datetime(list.Date)
# position.Date=pd.to_datetime(position.Date)
# list=list.set_index(list.Date)
# position=position.set_index(position.Date)

print(list)
print(list2)


# def nearestStrike(Date,Strike):
#     time= nearest(list,'Date',Date)
#     series=list.loc[list['Date'] == time].index.values
#     min=0
#     locator=0
#     for i in range(len(list.columns)):
#         value=list[series][i]
#         if(abs(Strike-value)<min):
#             min=abs(Strike-value)
#             locator=i
#     return min


#     # # row=final_f[final_f['Date'] == trial].index
#     # row=final_f.index[final_f["Date"]==trial].tolist()
#     # col=final_f.columns.get_loc('interest')
# test=nearestStrike('2022-07-26',102)
# print(test)



    







#df['Callstrike']= CallStrike(df['FX Rate'].astype(float),0.25.astype(float),df['Maturity'].astype(float),df['DomesticRate'].astype(float),df['Foreign Rate'].astype(float),df['Call IV'].astype(float))

Spot=83.72
Strike=85.667
Maturity=90/365
DomesticRate=0.001
ForeignRate=-0.001
Volatility=0.0957
Delta=0.3



# Delta= CallDelta(Spot,Strike,Maturity,DomesticRate,ForeignRate,Volatility)

# vega= CallVega(Spot,Strike,Maturity,DomesticRate,ForeignRate,Volatility)



# CalculatedStrike=CallStrike(Spot,Delta,Maturity,DomesticRate,ForeignRate,Volatility)

#print(CalculatedStrike)





# callprice=PolanitzerGarmanKohlhagenCall(Spot,Strike,Maturity,DomesticRate,ForeignRate,Volatility)
# PutPrice=PolanitzerGarmanKohlhagenPut(Spot,Strike,Maturity,DomesticRate,ForeignRate,Volatility)





# print(CalculatedStrike)
# print(Delta)
# print(callprice)
# print(PutPrice)






# delta(call) = exp(-rf*Time) * pnorm(d1v)
# delta(put) = exp(-rf*Time) * pnorm(d1v) - 1
# d1 = (log(spot/strike)+(rf+(sigma^2)/2)*Time)/(sigma*sqrt(Time))
# so, solve for d1 first:
# d1(call) = qnorm(delta/exp(-rf*Time))
# d1(put) = qnorm(delta/exp(-rf*Time) + 1)
# and then solve for the strike:
# strike = exp( d1 - (rf+(sigma^2)/2)*Time)/(sigma*sqrt(Time) )