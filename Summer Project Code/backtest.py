from cmath import log
from turtle import up
import eikon as ek
from jsonschema import RefResolutionError
import refinitiv.data as rd

import numpy as np
import configparser as cp
import pandas as pd
from matplotlib import pyplot as plt
import interest as it
import bsm as bsm
import math as math
call25='AUDJPY25C3M=R'
put25='AUDJPY25P3M=R'
call10='AUDJPY10C3M=R'
put10='AUDJPY10P3M=R'
atm='AUDJPY3MO='


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

def backtest_dataframe(df):
    position = 0
    counter=0
    net_profit = 0
    positionPnL=[]
    maturity=90
    newPos=[]
    
    earlyExit=[]
    trades=[]
    PnL=0
    sell_price=0
    buy_price=0
    cover_price=0
    short_price=0
    
    percentage_change = []
    df['buy_date'] = ''
    df['sell_date'] = ''
    df['short_date'] = ''
    df['cover_date']=''
    df['newPos']=0
    for i in df.index:
        close = df["threeMonth"][i]
        date = df['Date'][i]
        #if(position)
        # Buy action
        if (df["newBuy"][i] == 1):
            if(position==0):
             df['newPos'][i]=1
             counter=counter+1
             buy_price = close
             position = 1
             df.at[i, 'buy_date'] = date
             print('new')
             print(f"Buying at {str(buy_price)} on {str(date)}")
             trades.append("raw long")
             
            elif(position==1):#liquidating long with new long
                df['newPos'][i]=1
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price) 
                position=1
                buy_price=close
                df.at[i,'sell_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}") 
                trades.append("Rolling Long")  
            elif(position==-1): #covering short
                df['newPos'][i]=1
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=1
                buy_price=close
                df.at[i,'cover_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}")
                trades.append("Covering Short")
        elif(df["newSell"][i]==1):
            if(position==0):
                df['newPos'][i]=1
                counter=counter+1
                short_price=close
                position=-1
                df.at[i,'short_date'] = date
                print('new')
                print(f"Shorting at {str(short_price)} on {str(date)}")
                trades.append("raw short")
            elif(position==1): # liquidating long 
                df['newPos'][i]=1
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price)
                position=-1
                short_price=close
                df.at[i,'sell_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
                trades.append("Selling long + short")
            elif(position==-1): #covering short
                df['newPos'][i]=1
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=-1
                short_price=close
                df.at[i,'cover_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
                trades.append("rolling short")
        elif(position!=0):
            if(position==1):
                PnL=-(close-buy_price)/buy_price*100
                if(PnL>=20):
                    df['newPos'][i]=1
                    sell_price=close
                    pc = -(sell_price-buy_price)/buy_price*100
                    percentage_change.append(pc)
                    net_profit += (sell_price - buy_price) 
                    print('new')
                    print(f"Old buying at {str(buy_price)} on {str(date)}")
                    print("old profit", pc)
                    print(f"Early Selling at {str(sell_price)} on {str(date)}")
                    earlyExit.append(date)
                    position=0
            elif(position==-1):
                PnL=-(short_price-close)/short_price*100
                if(PnL>=50):
                    df['newPos'][i]=1
                    cover_price=close
                    pc = -(short_price-cover_price)/short_price*100
                    #short -cover )/ short sell 
                    percentage_change.append(pc)
                    net_profit += (short_price - cover_price)
                    print('new')
                    print(f"Old Shorting at {str(short_price)} on {str(date)}")
                    print("old profit", pc)
                    print(f"Early covering at {str(cover_price)} on {str(date)}")
                    position=0
                    earlyExit.append(date)  
        else:
            
            percentage_change.append(0)
                
        # Calculate trade statistics
    
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
    print(earlyExit)
    
    
    
    #3#####akshdlasjd

def backtest_Return(df):
    position = 0
    net_profit = 0
    sell_price=0
    buy_price=0
    cover_price=0
    short_price=0
    pc=0
    PnL=[]
    percentage_change = []
    df['buy_date'] = ''
    df['sell_date'] = ''
    df['short_date'] = ''
    df['cover_date']=''

    for i in df.index:
        close = df["threeMonth"][i]
        date = df['Date'][i]
        if(i!=0):
            change= (close - df["threeMonth"][i-1])/df["threeMonth"][i-1]
        #if(position)
        # Buy action
        if (df["newBuy"][i] == 1):
            if(position==0):
             buy_price = close
             position = 1
             df.at[i, 'buy_date'] = date
             print('new')
             print(f"Buying at {str(buy_price)} on {str(date)}")
            elif(position==1):#liquidating long
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price) 
                position=1
                buy_price=close
                df.at[i,'sell_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}")   
            elif(position==-1): #covering short
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=1
                buy_price=close
                df.at[i,'cover_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}")
        elif(df["newSell"][i]==1):
            if(position==0):
                short_price=close
                position=-1
                df.at[i,'short_date'] = date 
                print('new')
                print(f"Shorting at {str(short_price)} on {str(date)}")
            elif(position==1): # liquidating long 
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price)
                position=-1
                short_price=close
                df.at[i,'sell_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
            elif(position==-1): #covering short
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=-1
                short_price=close
                df.at[i,'cover_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
            else:
                pc=0
        PnL.append(net_profit)
                
        # Calculate trade statistics
    return PnL

#         #3#####akshdlasjd
        

# def backtest_ret(df):
#     position = 0
#     counter=0
#     net_profit = 0
    
#     earlyExit=[]
#     trades=[]
#     ret=[]
    
#     sell_price=0
#     buy_price=0
#     cover_price=0
#     short_price=0
    
#     percentage_change = []
#     df['buy_date'] = ''
#     df['sell_date'] = ''
#     df['short_date'] = ''
#     df['cover_date']=''

  
    

#     for i in df.index:
#         close = df["threeMonth"][i]
#         date = df['Date'][i]
      
        
#         #if(position)
#         # Buy action
#         if (df["newBuy"][i] == 1):
#             if(position==0):
#              counter=counter+1
#              buy_price = close
#              position = 1
#              df.at[i, 'buy_date'] = date
#              print('new')
#              print(f"Buying at {str(buy_price)} on {str(date)}")
#              trades.append("raw long")
             
#             elif(position==1):#liquidating long with new long
#                 counter=counter+1
#                 sell_price=close
#                 pc = -(sell_price-buy_price)/buy_price*100
#                 percentage_change.append(pc)
#                 net_profit += (sell_price - buy_price) 
#                 position=1
#                 buy_price=close
#                 df.at[i,'sell_date']=date
#                 df.at[i,'buy_date'] = date
#                 print('new')
#                 print(f"Old Selling at {str(sell_price)} on {str(date)}")
#                 print("old profit", pc)
#                 print(f"New Buying at {str(buy_price)} on {str(date)}") 
#                 trades.append("Rolling Long")  
#             elif(position==-1): #covering short
#                 counter=counter+1
#                 cover_price=close
#                 pc = -(short_price-cover_price)/short_price*100
#                 #short -cover )/ short sell 
#                 percentage_change.append(pc)
#                 net_profit += (short_price - cover_price)
#                 position=1
#                 buy_price=close
#                 df.at[i,'cover_date']=date
#                 df.at[i,'buy_date'] = date
#                 print('new')
#                 print(f"Old Covering at {str(cover_price)} on {str(date)}")
#                 print("old profit", pc)
#                 print(f"New Buying at {str(buy_price)} on {str(date)}")
#                 trades.append("Covering Short")
#         elif(df["newSell"][i]==1):
#             if(position==0):
#                 counter=counter+1
#                 short_price=close
#                 position=-1
#                 df.at[i,'short_date'] = date
#                 print('new')
#                 print(f"Shorting at {str(short_price)} on {str(date)}")
#                 trades.append("raw short")
#             elif(position==1): # liquidating long 
#                 counter=counter+1
#                 sell_price=close
#                 pc = -(sell_price-buy_price)/buy_price*100
#                 percentage_change.append(pc)
#                 net_profit += (sell_price - buy_price)
#                 position=-1
#                 short_price=close
#                 df.at[i,'sell_date']=date
#                 df.at[i,'short_date'] = date
#                 print('new')
#                 print(f"Old Selling at {str(sell_price)} on {str(date)}")
#                 print("old profit", pc)
#                 print(f"New Shorting at {str(short_price)} on {str(date)}")
#                 trades.append("Selling long + short")
#             elif(position==-1): #covering short
#                 counter=counter+1
#                 cover_price=close
#                 pc = -(short_price-cover_price)/short_price*100
#                 #short -cover )/ short sell 
#                 percentage_change.append(pc)
#                 net_profit += (short_price - cover_price)
#                 position=-1
#                 short_price=close
#                 df.at[i,'cover_date']=date
#                 df.at[i,'short_date'] = date
#                 print('new')
#                 print(f"Old Covering at {str(cover_price)} on {str(date)}")
#                 print("old profit", pc)
#                 print(f"New Shorting at {str(short_price)} on {str(date)}")
#                 trades.append("rolling short")
#         elif(position!=0):
#             if(position==1):
#                 PnL=-(close-buy_price)/buy_price*100
#                 if(PnL>=20):
#                     sell_price=close
#                     pc = -(sell_price-buy_price)/buy_price*100
#                     percentage_change.append(pc)
#                     net_profit += (sell_price - buy_price) 
#                     print('new')
#                     print(f"Old buying at {str(buy_price)} on {str(date)}")
#                     print("old profit", pc)
#                     print(f"Early Selling at {str(sell_price)} on {str(date)}")
#                     earlyExit.append(date)
#                     position=0
#             elif(position==-1):
#                 PnL=-(short_price-close)/short_price*100
#                 if(PnL>=50):
#                     cover_price=close
#                     pc = -(short_price-cover_price)/short_price*100
#                     #short -cover )/ short sell 
#                     percentage_change.append(pc)
#                     net_profit += (short_price - cover_price)
#                     print('new')
#                     print(f"Old Shorting at {str(short_price)} on {str(date)}")
#                     print("old profit", pc)
#                     print(f"Early covering at {str(cover_price)} on {str(date)}")
#                     position=0
#                     earlyExit.append(date)
#         else:
#             pc=0
#             percentage_change.append(0)
        
                
#         # Calculate trade statistics
#     gains = 0
#     ng = 0
#     losses = 0
#     nl = 0
#     totalR = 1

#     for i in percentage_change:
#         if(i > 0):
#             gains += i
#             ng += 1
#         elif(i<0):
#             losses += i
#             nl += 1
#         totalR = totalR * ((i/100)+1)
#         ret.append(totalR)

#     totalR = round((totalR-1)*100, 2)

#     if(ng > 0):
#         avgGain = round(gains/ng, 2)
#         maxR = round(max(percentage_change), 2)
#     else:
#         avgGain = 0
#         maxR = "undefined"

#     if(nl > 0):
#         avgLoss = round(losses/nl, 2)
#         maxL = round(min(percentage_change), 2)
#     else:
#         avgLoss = 0
#         maxL = "undefined"

#     if(ng > 0 or nl > 0):
#         win_rate = round((ng/(ng+nl))*100, 2)
#     else:
#         win_rate = 0
#     return ret


    

def early(df):
    position = 0
    counter=0
    net_profit = 0
    positionPnL=[]
    earlyExit=[]
    trades=[]
    PnL=0
    sell_price=0
    buy_price=0
    cover_price=0
    short_price=0
    
    percentage_change = []
    df['buy_date'] = ''
    df['sell_date'] = ''
    df['short_date'] = ''
    df['cover_date']=''
    df['earlyExit']=0
   

  
    

    for i in df.index:
        close = df["threeMonth"][i]
        date = df['Date'][i]
      
        
        #if(position)
        # Buy action
        if (df["newBuy"][i] == 1):
            if(position==0):
             counter=counter+1
             buy_price = close
             position = 1
             df.at[i, 'buy_date'] = date
            #  print('new')
            #  print(f"Buying at {str(buy_price)} on {str(date)}")
            #  trades.append("raw long")
             
            elif(position==1):#liquidating long with new long
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price) 
                position=1
                buy_price=close
                df.at[i,'sell_date']=date
                df.at[i,'buy_date'] = date
                # print('new')
                # print(f"Old Selling at {str(sell_price)} on {str(date)}")
                # print("old profit", pc)
                # print(f"New Buying at {str(buy_price)} on {str(date)}") 
                # trades.append("Rolling Long")  
            elif(position==-1): #covering short
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=1
                buy_price=close
                df.at[i,'cover_date']=date
                df.at[i,'buy_date'] = date
                # print('new')
                # print(f"Old Covering at {str(cover_price)} on {str(date)}")
                # print("old profit", pc)
                # print(f"New Buying at {str(buy_price)} on {str(date)}")
                # trades.append("Covering Short")
        elif(df["newSell"][i]==1):
            if(position==0):
                counter=counter+1
                short_price=close
                position=-1
                df.at[i,'short_date'] = date
                # print('new')
                # print(f"Shorting at {str(short_price)} on {str(date)}")
                # trades.append("raw short")
            elif(position==1): # liquidating long 
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price)
                position=-1
                short_price=close
                df.at[i,'sell_date']=date
                df.at[i,'short_date'] = date
                # print('new')
                # print(f"Old Selling at {str(sell_price)} on {str(date)}")
                # print("old profit", pc)
                # print(f"New Shorting at {str(short_price)} on {str(date)}")
                # trades.append("Selling long + short")
            elif(position==-1): #covering short
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=-1
                short_price=close
                df.at[i,'cover_date']=date
                df.at[i,'short_date'] = date
                # print('new')
                # print(f"Old Covering at {str(cover_price)} on {str(date)}")
                # print("old profit", pc)
                # print(f"New Shorting at {str(short_price)} on {str(date)}")
                # trades.append("rolling short")
        elif(position!=0):
            if(position==1):
                PnL=-(close-buy_price)/buy_price*100
                if(PnL>=30):
                    sell_price=close
                    pc = -(sell_price-buy_price)/buy_price*100
                    percentage_change.append(pc)
                    net_profit += (sell_price - buy_price) 
                    # print('new')
                    # print(f"Old buying at {str(buy_price)} on {str(date)}")
                    # print("old profit", pc)
                    # print(f"Early Selling at {str(sell_price)} on {str(date)}")
                    df['earlyExit'][i]=1
                    position=0
            elif(position==-1):
                PnL=-(short_price-close)/short_price*100
                if(PnL>=70):
                    cover_price=close
                    pc = -(short_price-cover_price)/short_price*100
                    #short -cover )/ short sell 
                    percentage_change.append(pc)
                    net_profit += (short_price - cover_price)
                    # print('new')
                    # print(f"Old Shorting at {str(short_price)} on {str(date)}")
                    # print("old profit", pc)
                    # print(f"Early covering at {str(cover_price)} on {str(date)}")
                    position=0
                    df['earlyExit'][i]=-1  
        else:
            percentage_change.append(0)

    return(df.earlyExit)

    #3#####akshdlasjd


def position(df):
    position = 0
    counter=0
    net_profit = 0
    positionPnL=[]
    earlyExit=[]
    trades=[]
    PnL=0
    sell_price=0
    buy_price=0
    cover_price=0
    short_price=0
    
    percentage_change = []
    df['buy_date'] = ''
    df['sell_date'] = ''
    df['short_date'] = ''
    df['cover_date']=''
    df['ledger']=''

  
    

    for i in df.index:
        close = df["threeMonth"][i]
        date = df['Date'][i]
        
        #if(position)
        # Buy action
        if (df["newBuy"][i] == 1):
            if(position==0):
             counter=counter+1
             buy_price = close
             position = 1
             df.at[i, 'buy_date'] = date
             print('new')
             print(f"Buying at {str(buy_price)} on {str(date)}")
             trades.append("raw long")
             
            elif(position==1):#liquidating long with new long
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price) 
                position=1
                buy_price=close
                df.at[i,'sell_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}") 
                trades.append("Rolling Long")  
            elif(position==-1): #covering short
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=1
                buy_price=close
                df.at[i,'cover_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}")
                trades.append("Covering Short")
        elif(df["newSell"][i]==1):
            if(position==0):
                counter=counter+1
                short_price=close
                position=-1
                df.at[i,'short_date'] = date
                print('new')
                print(f"Shorting at {str(short_price)} on {str(date)}")
                trades.append("raw short")
            elif(position==1): # liquidating long 
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price)
                position=-1
                short_price=close
                df.at[i,'sell_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
                trades.append("Selling long + short")
            elif(position==-1): #covering short
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=-1
                short_price=close
                df.at[i,'cover_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
                trades.append("rolling short")
        elif(position!=0):
            if(position==1):
                PnL=-(close-buy_price)/buy_price*100
                if(PnL>=20):
                    sell_price=close
                    pc = -(sell_price-buy_price)/buy_price*100
                    percentage_change.append(pc)
                    net_profit += (sell_price - buy_price) 
                    print('new')
                    print(f"Old buying at {str(buy_price)} on {str(date)}")
                    print("old profit", pc)
                    print(f"Early Selling at {str(sell_price)} on {str(date)}")
                    earlyExit.append(date)
                    position=0
            elif(position==-1):
                PnL=-(short_price-close)/short_price*100
                if(PnL>=50):
                    cover_price=close
                    pc = -(short_price-cover_price)/short_price*100
                    #short -cover )/ short sell 
                    percentage_change.append(pc)
                    net_profit += (short_price - cover_price)
                    print('new')
                    print(f"Old Shorting at {str(short_price)} on {str(date)}")
                    print("old profit", pc)
                    print(f"Early covering at {str(cover_price)} on {str(date)}")
                    position=0
                    earlyExit.append(date)
            df['ledger'][i]=position 
        else:
            percentage_change.append(0)
            
    
    a=df['Date']
    
    return a

#sdjhakj

def positionB(df):
    position = 0
    counter=0
    net_profit = 0
    positionPnL=[]
    earlyExit=[]
    trades=[]
    PnL=0
    sell_price=0
    buy_price=0
    cover_price=0
    short_price=0
    
    percentage_change = []
    df['buy_date'] = ''
    df['sell_date'] = ''
    df['short_date'] = ''
    df['cover_date']=''
    df['ledger']=''

  
    

    for i in df.index:
        close = df["threeMonth"][i]
        date = df['Date'][i]
        
        #if(position)
        # Buy action
        if (df["newBuy"][i] == 1):
            if(position==0):
             counter=counter+1
             buy_price = close
             position = 1
             df.at[i, 'buy_date'] = date
             print('new')
             print(f"Buying at {str(buy_price)} on {str(date)}")
             trades.append("raw long")
             
            elif(position==1):#liquidating long with new long
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price) 
                position=1
                buy_price=close
                df.at[i,'sell_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}") 
                trades.append("Rolling Long")  
            elif(position==-1): #covering short
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=1
                buy_price=close
                df.at[i,'cover_date']=date
                df.at[i,'buy_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}")
                trades.append("Covering Short")
        elif(df["newSell"][i]==1):
            if(position==0):
                counter=counter+1
                short_price=close
                position=-1
                df.at[i,'short_date'] = date
                print('new')
                print(f"Shorting at {str(short_price)} on {str(date)}")
                trades.append("raw short")
            elif(position==1): # liquidating long 
                counter=counter+1
                sell_price=close
                pc = -(sell_price-buy_price)/buy_price*100
                percentage_change.append(pc)
                net_profit += (sell_price - buy_price)
                position=-1
                short_price=close
                df.at[i,'sell_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
                trades.append("Selling long + short")
            elif(position==-1): #covering short
                counter=counter+1
                cover_price=close
                pc = -(short_price-cover_price)/short_price*100
                #short -cover )/ short sell 
                percentage_change.append(pc)
                net_profit += (short_price - cover_price)
                position=-1
                short_price=close
                df.at[i,'cover_date']=date
                df.at[i,'short_date'] = date
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")
                trades.append("rolling short")
        elif(position!=0):
            if(position==1):
                PnL=-(close-buy_price)/buy_price*100
                if(PnL>=20):
                    sell_price=close
                    pc = -(sell_price-buy_price)/buy_price*100
                    percentage_change.append(pc)
                    net_profit += (sell_price - buy_price) 
                    df.at[i,'sell_date']=date
                    print('new')
                    print(f"Old buying at {str(buy_price)} on {str(date)}")
                    print("old profit", pc)
                    print(f"Early Selling at {str(sell_price)} on {str(date)}")
                    earlyExit.append(date)
                    position=0
            elif(position==-1):
                PnL=-(short_price-close)/short_price*100
                if(PnL>=50):
                    cover_price=close
                    pc = -(short_price-cover_price)/short_price*100
                    #short -cover )/ short sell 
                    percentage_change.append(pc)
                    net_profit += (short_price - cover_price)
                    df.at[i,'cover_date']=date
                    print('new')
                    print(f"Old Shorting at {str(short_price)} on {str(date)}")
                    print("old profit", pc)
                    print(f"Early covering at {str(cover_price)} on {str(date)}")
                    position=0
                    earlyExit.append(date) 
        else:
            percentage_change.append(0)
        df['ledger'][i]=position 
    a=df['ledger']

    
    return a
                
   
    #######





def backtest_dollarValue(df):
    position = 0
    counter=0
    net_profit = 0
    fxRate=df['AUDJPY'][1]
    Maturity=0

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
        

    #price=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
    earlyExit=[]
    trades=[]
    PnL=0
    sell_price=0
    buy_price=0
    sell_priceIV=0
    buy_priceIV=0
    cover_price=0
    short_price=0
    shortOption=0
    capital=1.0
    
    percentage_change = []
    df['buy_date'] = ''
    df['sell_date'] = ''
    df['short_date'] = ''
    df['cover_date']=''
    df['newPos']=0

    for i in df.index:
        
        date = df['Date'][i]
        Maturity=Maturity-1
        fxRate=df['AUDJPY'][i]
        date = df['Date'][i]
        CallIV=IV(date,call25)/100
        PutIV=IV(date,put25)/100
        domesticRate=it.domesticRate(date)
        foreignRate=it.foreignRate(date)
        
       
        newPos=df['newPos'][i]
        closeIV = df['threeMonth'][i]
        
       
        # CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity,domesticRate,foreignRate,CallIV)
        # PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity,domesticRate,foreignRate,PutIV)

        #if(position)
        # Buy action
        if (df["newBuy"][i] == 1):
            if(position==0):
             Maturity=90
             CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
             PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)
             CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
             PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)

             
             close=CallClose-PutClose

             df['newPos'][i]=1
             counter=counter+1
             buy_price = close

            #  sell_price=0
            #  cover_price=0
            #  short_price=0
            

             buy_priceIV = closeIV
             position = 1
             close=0

             df.at[i, 'buy_date'] = date
             print('new')
             print(f"Buying at {str(buy_price)} on {str(date)}")
             print('raw')
             trades.append("raw long")
             
            elif(position==1):#liquidating long with new long
                #Calculate Change in Option Price Bought Earlier
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
              
                close=CallClose-PutClose
                sell_price=close
                

                
                
                if(sell_price>=buy_price):
                    pc=abs((sell_price-buy_price)/buy_price)
                else:
                    pc=-abs((sell_price-buy_price)/buy_price)

                if(math.isnan(pc)==False):
                    percentage_change.append(pc)
                else:
                    percentage_change.append(0)
                net_profit += (sell_price - buy_price) 
                capital=capital*(1+pc)

                #Calculate New Option Price (Rolling Long)
                Maturity=90
                CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
                PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
               
                close=CallClose-PutClose

                buy_price=close
                # sell_price=0
                # cover_price=0
                # short_price=0
                close=0
                
                buy_priceIV = closeIV

                df['newPos'][i]=1
                counter=counter+1
                position=1
                

                df.at[i,'sell_date']=date
                df.at[i,'buy_date'] = date

                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}") 
                
                trades.append("Rolling Long")  

            elif(position==-1): #covering short
                #Calculating Change in Option Price Shorted Earlier
                
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
                close=PutClose-CallClose
                
                cover_price=close

                if(short_price>=cover_price):
                    pc=abs((short_price-cover_price)/short_price)
                else:
                    pc=-abs((short_price-cover_price)/short_price)
    
                if(math.isnan(pc)==False):
                    percentage_change.append(pc)
                else:
                    percentage_change.append(0)
                net_profit += (short_price - cover_price) 
                capital=capital*(1+pc)


                #Calculate New Option Price (Rolling Long)
        

                Maturity=90
                CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
                PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
                
                close=CallClose-PutClose
                buy_price=close
                close=0
                # sell_price=0
                # cover_price=0
                # short_price=0
                
                buy_priceIV = closeIV

                df['newPos'][i]=1
                counter=counter+1
                position=1
              
                
                df.at[i,'cover_date']=date
                df.at[i,'buy_date'] = date

                
                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Buying at {str(buy_price)} on {str(date)}")

                trades.append("Covering Short")

        elif(df["newSell"][i]==1):
            if(position==0):
                Maturity=90
                CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
                PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)

                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
                
                close=PutClose-CallClose


                df['newPos'][i]=1
                counter=counter+1
                short_price=close
                close=0
                # sell_price=0
                # cover_price=0
                # buy_price=0

                short_priceIV=closeIV

                position=-1

                df.at[i,'short_date'] = date

                print('new')
                print(f"Shorting at {str(short_price)} on {str(date)}")
                print('raw')
                trades.append("raw short")

            elif(position==1): # liquidating long 
                #Calculate Change in Option Price bought Earlier
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
              
                close=CallClose-PutClose
                sell_price=close    

                if(sell_price>=buy_price):
                    pc=abs((sell_price-buy_price)/buy_price)
                else:
                    pc=-abs((sell_price-buy_price)/buy_price)
                capital=capital*(1+pc)

                
                if(math.isnan(pc)==False):
                    percentage_change.append(pc)
                else:
                    percentage_change.append(0)
                net_profit += (sell_price - buy_price)

                #Calculate New Option Statistics
                Maturity=90
                CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
                PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
               
                close=PutClose-CallClose
                short_price=close
                close=0

                short_priceIV=closeIV

                df['newPos'][i]=1
                counter=counter+1
                position=-1
                
                

                df.at[i,'sell_date']=date
                df.at[i,'short_date'] = date

                print('new')
                print(f"Old Selling at {str(sell_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")

                trades.append("Selling long + short")

            elif(position==-1): #covering short
                #Calculating old trade statistics
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
                
                close=PutClose-CallClose
                cover_price=close

                

                if(short_price>=cover_price):
                    pc=abs((short_price-cover_price)/short_price)
                else:
                    pc=-abs((short_price-cover_price)/short_price)

                if(math.isnan(pc)==False):
                    percentage_change.append(pc)
                else:
                    percentage_change.append(0)
                net_profit += (short_price - cover_price)
                
                


                # New Trade Statistics
                Maturity=90
                CallS=bsm.CallStrike(fxRate,0.25,Maturity,domesticRate,foreignRate,CallIV)
                PutS=bsm.PutStrike(fxRate,-0.25,Maturity,domesticRate,foreignRate,PutIV)
                CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
                PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
                

                close=PutClose-CallClose
                short_price=close
                close=0

                short_priceIV=closeIV


                df['newPos'][i]=1
                counter=counter+1
                position=-1
               
                df.at[i,'cover_date']=date
                df.at[i,'short_date'] = date

                print('new')
                print(f"Old Covering at {str(cover_price)} on {str(date)}")
                print("old profit", pc)
                print(f"New Shorting at {str(short_price)} on {str(date)}")

                trades.append("rolling short")

        # elif(position!=0):
        #     if(position==1):
        #         PnL=-(closeIV-buy_priceIV)/buy_priceIV*100
        #         if(PnL>=20):
        #             df['newPos'][i]=1

        #             ## calculating early exit statistics 
        #             CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
        #             PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
        #             close=CallClose-PutClose
        #             sell_price=close

        #             if(sell_price>=buy_price):
        #                 pc=abs((sell_price-buy_price)/buy_price*100)
        #             else:
        #                 pc=-abs((sell_price-buy_price)/buy_price*100)
                  
        #             if(math.isnan(pc)==False):
        #                 percentage_change.append(pc)
        #             else:
        #                 percentage_change.append(0)
        #             net_profit += (sell_price - buy_price) 

        #             Maturity=0
        #             earlyExit.append(date)
        #             position=0

        #             print('new')      
        #             print(f"Old buying at {str(buy_price)} on {str(date)}")
        #             print("old profit", pc)
        #             print(f"Early Selling at {str(sell_price)} on {str(date)}")
                    
        #     elif(position==-1):
        #         PnL=-(short_priceIV-closeIV)/short_priceIV*100
        #         if(PnL>=50):
        #             df['newPos'][i]=1
        #             ## Calculating early exit statistics 
        #             CallClose=bsm.PolanitzerGarmanKohlhagenCall(fxRate,CallS,Maturity/365,domesticRate,foreignRate,CallIV)
        #             PutClose=bsm.PolanitzerGarmanKohlhagenPut(fxRate,PutS,Maturity/365,domesticRate,foreignRate,PutIV)
        #             close=PutClose-CallClose
        #             cover_price=close
        #             if(short_price>=cover_price):
        #                 pc=abs((short_price-cover_price)/short_price*100)
        #             else:
        #                 pc=-abs((short_price-cover_price)/short_price*100)
                    
        #             if(math.isnan(pc)==False):
        #                 percentage_change.append(pc)
        #             else:
        #                 percentage_change.append(0)
        #             net_profit += (short_price - cover_price)

        #             Maturity=0
        #             position=0
        #             earlyExit.append(date)  
        #             print('new')
        #             print(f"Old Shorting at {str(short_price)} on {str(date)}")
        #             print("old profit", pc)
        #             print(f"Early covering at {str(cover_price)} on {str(date)}")
                    
        # else:
        #     percentage_change.append(0)
                
        # Calculate trade statistics
    
    gains = 0
    ng = 0
    losses = 0
    nl = 0
    totalR = 1
    percentage_change = [0 if math.isnan(x) else x for x in percentage_change]
    
    for i in percentage_change:
        if(i > 0):
            gains += i
            ng += 1
        elif(i<0):
            losses += i
            nl += 1
        totalR = totalR * ((i)+1)

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
    print(f"Total Returns: ${totalR}")
    print(f"Win Rate: {win_rate}%")
    print(f"Average Gain: ${avgGain}")
    print(f"Average Loss: ${avgLoss}")
    print(f"Max Return: ${maxR}%")
    print(f"Max Loss: ${maxL}%")
    print(f"Net Dollar Profit:${net_profit}")
    print(capital)