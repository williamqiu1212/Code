import numpy as np
import matplotlib.pyplot as plt
from pandas import Series
import pandas as pd
from hurst import compute_Hc, random_walk


eur= pd.read_excel('riskreversalAUD.xlsx')
series=np.array(eur.threeMonth)

def get_hurst_exponent(time_series, max_lag=20):
    
    lags = range(2, max_lag)

    # variances of the lagged differences
    tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]

    # calculate the slope of the log plot -> the Hurst Exponent
    reg = np.polyfit(np.log(lags), np.log(tau), 1)

    return reg[0]

for lag in [20, 100, 300, 500, 1000]:
    hurst_exp = get_hurst_exponent(series, lag)
    print(f"Hurst exponent with {lag} lags: {hurst_exp:.4f}")