import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import signal
from scipy import stats

import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARIMA


from src.import_process_data import import_caiso_dataset


def fit_moving_average_trend(series, window=6):
#    return pd.rolling_mean(series, window, center=True)
    return series.rolling(window, center=True).mean()

def plot_moving_average_trend(ax, name, series, window=6):
    moving_average_trend = fit_moving_average_trend(series, window)
    plot_trend_data(ax, name, series)
    ax.plot(series.index.date, moving_average_trend)
    
def fit_seasonal_trend(series):
    dummies = create_monthly_dummies(series)
    X = sm.add_constant(dummies.values, prepend=False)
    seasonal_model = sm.OLS(series.values, X).fit()
    return seasonal_model.predict(X)

def plot_seasonal_trend(ax, name, series):
    seasons_average_trend = fit_seasonal_trend(series)
    plot_trend_data(ax, name, series, )
    ax.plot(series.index.date, seasons_average_trend, '-')

def plot_trend_data(ax, name, series):
    ax.plot(series.index.date, series)
    ax.set_title("{} Historic LMP".format(name))

def calc_rmse(actual, pred):
    return np.sqrt(mean_squared_error(actual, pred))

def calc_stats(curve, name):
    avg = round(curve.mean(), 5)
    med = round(curve.median(), 5)
    std = round(curve.std(), 5)
    print (f"{name} avg. price: {avg}")
    print (f"{name} median price: {med}")
    print(f"{name} std. dev.: {std}")
    print('\n')

def calc_stat_summary_for_all_hubs(all_lmp, hub_names):
    '''
    Calculates and prints the mean, median and standard deviation for all the price curves.
    
    Parameters
    ----------
    all_lmp: arr
        An array comprised of historic price curve arrays for all hubs.
    
    hub_names: arr
        An array comprised of strings that are the names of the provided hubs.
    
    Return
    ------
    '''
    
    for curve, hub in zip(all_lmp, hub_names):
        calc_stats(curve, hub)
    
    plt.show();

def plot_shared_yscales(axs, x, ys, titles, hub_name):
    ymiddles =  [ (y.max()+y.min())/2 for y in ys ]
    yrange = max( (y.max()-y.min())/2 for y in ys )
    for ax, y, title, ymiddle in zip(axs, ys, titles, ymiddles):
        ax.plot(x, y)
        ax.set_title(f"{title} - {hub_name}")
        ax.set_ylim((ymiddle-yrange, ymiddle+yrange))
    plt.show();


def plot_seasonal_decomposition(lmp_curve, hub_name, period=1):
    '''
    Deconstructs and plots the price curve into trend, seasonal and residual components.
    
    '''
    
    fig, axs = plt.subplots(4, figsize=(20,12), sharex=True)
    tsr_decomp = sm.tsa.seasonal_decompose(lmp_curve, period)
    
    plot_shared_yscales(axs,
                        series.index,
                        [lmp_curve, tsr_decomp.trend, tsr_decomp.seasonal, tsr_decomp.resid],
                        ["Raw Series", "Trend Component $T_t$", "Seasonal Component $S_t$", "Residual Component $R_t$"],
                        hub_name)
    plt.tight_layout()
    plt.show();

def compute_autocorrelation(series, lag=1):
    truncated = series[lag:]
    lagged = np.copy(series)[:(len(truncated))]
    return np.corrcoef(series, lagged)[0,1]

def plot_lmp_curve_autocorrelation(arr_curves, hub_names, acf_lag=48):
    
    n_hubs = len(hub_names)
    
    diff_dict = dict()
    for curve, name in zip(arr_curves, hub_names):
        diff_dict[name] = curve
    
    fig, axs = plt.subplots(n_hubs, figsize=(20, 3 * n_hubs))

    for i, name, diff in enumerate(diff_dict.items()):
        _ = sm.graphics.tsa.plot_acf(diff, lags=acf_lag, ax=axs[i])
        axs[i].set_title(f"Autocorrelation - {name}")


if __name__ == '__main__':
    
    