from gettext import npgettext
from operator import index
from tkinter import Misc
import numpy as np
import pandas as pd
import datetime

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))
        


# def nearest(panda,col_name, pivot):
    

# index_no = df.columns.get_loc(col_name)


misc= pd.read_excel('misc.xlsx')
misc.insert(0, 'index', range(0, 0 + len(misc)))
leg= pd.read_excel('legData.xlsx')
leg = (leg.dropna()).sort_values(by=['Date'], ascending=True)

domestic=pd.DataFrame()
domestic['Date']=pd.to_datetime(misc['Date'], format='%Y-%m-%d %I-%p')
domestic['interest']=misc['AUCBIR=ECI'].astype(int,errors='ignore')
final_d = (domestic.dropna()).sort_values(by=['Date'], ascending=True)
foreign=pd.DataFrame()
foreign['Date']=pd.to_datetime(misc['Date'], format='%Y-%m-%d %I-%p')
foreign['interest']=misc['JPINTN=ECI'].astype(int,errors='ignore')
final_f = (foreign.dropna()).sort_values(by=['Date'], ascending=True)

final_d.Date=pd.to_datetime(final_d.Date)
final_f.Date=pd.to_datetime(final_f.Date)
final_f=final_f.set_index(final_f.Date)
final_d=final_d.set_index(final_d.Date)
#all_days = pd.date_range(final_f.index.min(), final_f.index.max(), freq='D')
#final_f.reindex(all_days)


final_f['test']=final_f.Date-datetime.timedelta(days=1)


def nearest(panda, col_name, pivot):

    row= panda.index.get_loc(pivot, method='nearest')
    col=panda.columns.get_loc(col_name)
    value= panda.iloc[row,col]
    return(value)
    
    


# final_f=final_f.set_index(final_f.Date)
# test= final_f.index.get_loc('2017-09-08', method='nearest')

# index_no = final_f.columns.get_loc('interest')
# index_na = final_f.columns.get_loc('Date')
# value= final_f.iloc[test,index_no]
# value2=final_f.iloc[test,index_na]


trial= nearest(final_f,'Date','2017-09-08')

# print(value2,value)
# print(final_f)
# print(final_d)

def foreignRate(Date):
    trial= nearest(final_f,'Date',Date)
    # # row=final_f[final_f['Date'] == trial].index
    # row=final_f.index[final_f["Date"]==trial].tolist()
    # col=final_f.columns.get_loc('interest')
    test=final_f['interest']
    value= test[final_f['Date']==trial].index.values
    p=final_f['interest'][value]
    return float(p[0])

def domesticRate(Date):
    trial= nearest(final_d,'Date',Date)
    # # row=final_f[final_f['Date'] == trial].index
    # row=final_f.index[final_f["Date"]==trial].tolist()
    # col=final_f.columns.get_loc('interest')
    test=final_d['interest']
    value= test[final_d['Date']==trial].index.values
    p=final_d['interest'][value]
    return float(p[0])

date='2021-03-25'
# print(domesticRate(date))
# print(foreignRate(date))



#test= pd.merge_asof(final_d,final_f,on='Date',by='interest',tolerance= pd.Timedelta(days=3))
#domestic['Date']=misc['Date']
#domestic['interest']=misc['EURIBOR 6m']
#domestic= pd.DataFrame(misc['Date'],misc['EURIBOR 6m'])
#foreign=pd.DataFrame()
#foreign=np.array(([libor],[liborDate]))
#print(test)
#final_f=final_f.reindex(np.array(foreign.Date),fill_value=final_f.tail(1))
