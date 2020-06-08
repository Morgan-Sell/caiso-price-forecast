import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
%matplotlib inline
import seaborn as sns


def plot_day_ahead_hourly_prices(date_rng, lmp_curve, hub_name):
    """
    Graphs the hourly price on a scatter plot.

    Parameters
    ----------
    date_rng : arr
        Data range used for x-axis.

    lmp_curve: arr
        Comprised of the hourly prices from the selected CAISO hub.

    Returns
    -------

    """
    plt.figure(figsize=(18,7))
    ax = sns.scatterplot(x=date_rng, y=lmp_curve)
    ax.set_xlim(date_rng.min(),date_rng.max())
    ax.set_ylabel('$ / MWh', fontsize=12)
    ax.set_title(f'{hub_name} Day-Ahead Hourly Prices', fontsize=24, fontweight='bold')
    plt.tight_layout();

def plot_price_curve_box_plot(hours_day, lmp_curve, df):
    """
    Shows the distribution of hourly prices for each our of the day for the provided duration.

    Parameters
    ----------
    lmp_hour : str
        Name of the column in the provided dataframe that contains the hourly prices.

    hours_day : str
        Name of the column in the provided dataframe that contains the hour ending for each of the provided historic prices.

    df : dataframe
        Dataframe that contains historic electricity prices.

    Return
    -------

    """

    plt.figure(figsize=(20,8))

    ax = sns.boxplot(x=hours_day, y=lmp_curve, palette='Set3', data=df)
    ax.set_title('Distribution of NP-15 Wholesale Electricity Prices', fontsize=24, fontweight='bold')
    ax.set_ylabel('$ / MWh', fontsize=12)
    ax.set_xlabel('Hour Ending', fontsize=16)
    ax.set_xlim(-0.5, 23.5)
    plt.tight_layout();

def draw_lag_plots(lmp_curves_list, hub_names, lag=1):
    """
    Plots the lag plot to evaluate the time-series data's autocorrelation.

    Parameters
    ----------
    lmp_curves_list : list of arrays
        A list comprised of historic price curves.

    hub_names : list of strings
        Names of the CAISO hubs.

    lag : int
        The difference in time of the two datapoints that are being evaluated for correlation.

    """
    fig, axs = plt.subplots(nrows=1, ncols=len(hub_names), sharey=True, figsize=(20,6))

    for i, curve, h in zip(range(len(hub_names)), lmp_curves_list, hub_names):
        lag_plot(curve, ax=axs[i], c='green', alpha=0.5, lag=24)
        axs[i].set_title(f"{h} Lag Plot - 24 Hours", fontsize=16, fontweight='bold')

    plt.tight_layout();


def draw_moving_avg_plot(prcnt_re_gen, daily_date_rng, num_days):
    """
    Plots the percentage of energy derived from renewable resources and the 14-day moving average.

    Parameters
    ----------
    prcnt_re_gen : arr
        Each data point is the daily percentage of energy that was derived from renewable resources.

    daily_date_rng : arr
        Date range that  will make up the x-axis. Values should be daily.

    num_days : int
        Number of days to use to calculate the moving average.

    Return
    -------
    """

    fig, ax = plt.subplots(figsize=(18,8))

    rolling = caiso_daily['prcnt_re_gen'].rolling(num_days).mean()
    daily_date_arr = caiso_daily['OPR_DT_PT']

    ax.plot(daily_date_rng, caiso_daily['prcnt_re_gen'], color='lightgrey', label='Actual')
    ax.plot(daily_date_rng, rolling, color='green', linewidth=3, label=f'{num_days}-day Moving Avg.')
    ax.set_ylabel('% of Total Generation', fontsize=12)
    ax.set_title('Energy Generation Derived from Renewable Resources', fontsize=22, fontweight='bold')
    ax.set_xlim(daily_date_rng.min(), daily_date_rng.max())
    ax.legend()
    plt.tight_layout();
