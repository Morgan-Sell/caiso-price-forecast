import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
import seaborn as sns
from pandas.plotting import lag_plot


def import_process_data_for_eda():
    '''
    Prepares CAISO master dataset for EDA by filling in May 1 to 4 with the data from April 27 to 30 and removing the data provided for May 5.
    CAISO OASIS system seems to experienced and error in the beginning of May 2020.
    
    Parameters
    ----------
    caiso : dateframe
        Final CAISO dataset that's comprised of all three hub's LMPs and exogenous variables, e.g. energy generation.
        
    Returns
    -------
    caiso_eda : dataframe
        A dateset that's been prepared for visualizations.
        
    '''
    
    caiso = pd.read_csv('../data/caiso_master.csv')
    caiso.drop('Unnamed: 0', axis=1, inplace=True)
    caiso['INTERVAL_START_PT'] = pd.to_datetime(caiso['INTERVAL_START_PT']).apply(lambda x: x.replace(tzinfo=None))
    caiso['INTERVAL_END_PT'] = pd.to_datetime(caiso['INTERVAL_END_PT']).apply(lambda x: x.replace(tzinfo=None))
    caiso['date_hour_start'] = pd.to_datetime(caiso['date_hour_start']).apply(lambda x: x.replace(tzinfo=None))
    caiso['OPR_DT_PT'] = pd.to_datetime(caiso['OPR_DT_PT'])
    caiso.set_index('INTERVAL_START_PT', inplace=True)
    caiso.rename({'HH_$_million_BTU_not_seasonal_adj': 'HH_$_mill_BTU', 'total_mw':'total_gen'},axis=1, inplace=True)
    caiso['HH_$_mill_BTU'] = pd.to_numeric(caiso['HH_$_mill_BTU'])
    apr_30_20 = caiso[caiso['OPR_DT_PT'] == '2020-04-30']
    end_may20_hrly = pd.concat([apr_30_20, apr_30_20, apr_30_20, apr_30_20], axis=0)
    beg_may_arr = pd.date_range(start='2020-05-01', end='2020-05-05', freq='H')[:-1]
    end_may20_hrly.set_index(beg_may_arr, inplace=True)
    caiso_eda = pd.concat([caiso, end_may20_hrly], axis=0)
    caiso_eda.sort_index()
    caiso_eda['total_re'] = caiso_eda['solar'] + caiso_eda['wind']
    caiso_eda = caiso_eda[caiso_eda['OPR_DT_PT'] != '2020-05-05']
    return caiso_eda

def plot_day_ahead_hourly_prices(date_rng, lmp_curve, hub_name):
    '''
    Graphs the hourly price on a scatter plot.

    Parameters
    ----------
    date_rng : arr
        Data range used for x-axis.

    lmp_curve: arr
        Comprised of the hourly prices from the selected CAISO hub.

    Returns
    -------

    '''
    
    plt.figure(figsize=(18,7))
    ax = sns.scatterplot(x=date_rng, y=lmp_curve)
    ax.set_xlim(date_rng.min(),date_rng.max())
    ax.set_ylabel('$ / MWh', fontsize=12)
    ax.set_title(f'{hub_name} Day-Ahead Hourly Prices', fontsize=24, fontweight='bold')
    plt.tight_layout()
    plt.show();

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
    plt.tight_layout()
    plt.show();

def draw_lag_plots(lmp_curves_list, hub_names, lag=24):
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

    plt.tight_layout()
    plt.show();


def plot_prcnt_re_gen_moving_avg(caiso_data, num_days=14):
    """
    Plots the percentage of energy derived from renewable resources and the moving average based on selected number of days.

    Parameters
    ----------
    caiso_data : dataframe
        CAISO dataframe generated from import_process_data_for_eda().

    num_days : int
        Number of days to use to calculate the moving average.

    Return
    -------
    """
    caiso_daily = caiso_data.groupby('OPR_DT_PT').agg(func='sum').reset_index()
    caiso_daily['total_re_gen'] = caiso_daily['solar'] + caiso_daily['wind'] 
    caiso_daily['daily_prcnt_re_gen'] = caiso_daily['total_re_gen'] / caiso_daily['total_gen']
      
    re_gen_rolling= caiso_daily['total_re_gen'].rolling(num_days).mean()
    total_gen_rolling = caiso_daily['total_gen'].rolling(num_days).mean()
    prcnt_re_gen_rolling = re_gen_rolling / total_gen_rolling
    days_arr = caiso_daily['OPR_DT_PT']

    fig, ax = plt.subplots(figsize=(20,8))
    
    ax.plot(days_arr, caiso_daily['daily_prcnt_re_gen'], color='lightgrey', label='Actual')
    ax.plot(days_arr, prcnt_re_gen_rolling, color='green', linewidth=3, label=f'{num_days}-day Moving Avg')
    ax.set_ylabel('% of Total Generation', fontsize=12)
    ax.set_title('Energy Generation Derived from Renewable Resources', fontsize=22, fontweight='bold')
    ax.set_xlim(days_arr.min(), days_arr.max())
    ax.legend()
    plt.tight_layout()
    plt.show();
   
    
if __name__ == '__main__':

    caiso = import_process_data_for_eda()
    date_arr = caiso.index
    np15_lmp = caiso['$_MWH_np15']
    sp15_lmp = caiso['$_MWH_sp15']
    zp26_lmp = caiso['$_MWH_zp26']
    all_lmp = [np15_lmp, sp15_lmp, zp26_lmp]
    hub_names = ['NP15', 'SP15', 'ZP26']
    
    # NP15 (NorCal) LMP Only
    plot_day_ahead_hourly_prices(date_arr, np15_lmp, 'NP15')
    plot_price_curve_box_plot('OPR_HR_PT', '$_MWH_np15', caiso)
    
    
    # Considers all CAISO trading hubs.
    draw_lag_plots(all_lmp, hub_names, 24)
    
    # Energy generation
    plot_prcnt_re_gen_moving_avg(caiso, 14)
    