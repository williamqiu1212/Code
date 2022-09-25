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
from scipy.interpolate import interp1d

call25='AUDJPY25C3M=R'
put25='AUDJPY25P3M=R'
call10='AUDJPY10C3M=R'
put10='AUDJPY10P3M=R'
atm='AUDJPY3MO='


pd.set_option('display.max_rows', None)

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


date='2022-08-11'
print(IV(date,call25))
print(IV(date,put25))


# option=option.loc['AUDJPY25P3M=R']


# row=option[option['Date'] == IV()].index.values
# col=option.columns.get_loc('AUDJPY25P3M=R')




