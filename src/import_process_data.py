import pandas as pd
import numpy as np
import pyiso

def create_price_curves():
    """
    Acquires and cleans the hourly LMP prices for the three CAISO hubs - NP15, SP15, ZP26 - from csv files that were produced using CAISO OATI system.

    Returns
    -------

    np15_lmp_19_20 : dataframe
        Hourly NP15 power prices with time parameters.

     sp15_lmp_19_20 : dataframe
        Hourly SP15 power prices with time parameters.

     zp26_lmp_19_20 : dataframe
        Hourly ZP26 power prices with time paramets.

    """
    # Import monthly csv files from CAISO website.
    lmp_feb19 = pd.read_csv('data/caiso_lmp_nodes/20190201_20190301_PRC_LMP_DAM_20200603_09_30_31_v1.csv')
    lmp_mar19 = pd.read_csv('data/caiso_lmp_nodes/20190301_20190401_PRC_LMP_DAM_20200603_09_21_36_v1.csv')
    lmp_apr19 = pd.read_csv('data/caiso_lmp_nodes/20190401_20190501_PRC_LMP_DAM_20200602_22_44_57_v1.csv')
    lmp_may19 = pd.read_csv('data/caiso_lmp_nodes/20190501_20190601_PRC_LMP_DAM_20200602_22_54_16_v1.csv')
    lmp_jun19 = pd.read_csv('data/caiso_lmp_nodes/20190601_20190701_PRC_LMP_DAM_20200602_23_04_24_v1.csv')
    lmp_jul19 = pd.read_csv('data/caiso_lmp_nodes/20190701_20190801_PRC_LMP_DAM_20200602_23_20_18_v1.csv')
    lmp_aug19 = pd.read_csv('data/caiso_lmp_nodes/20190801_20190901_PRC_LMP_DAM_20200602_23_29_55_v1.csv')
    lmp_sep19 = pd.read_csv('data/caiso_lmp_nodes/20190901_20191001_PRC_LMP_DAM_20200602_23_46_12_v1.csv')
    lmp_oct19 = pd.read_csv('data/caiso_lmp_nodes/20191001_20191101_PRC_LMP_DAM_20200603_00_13_44_v1.csv')
    lmp_nov19 = pd.read_csv('data/caiso_lmp_nodes/20191101_20191201_PRC_LMP_DAM_20200603_00_24_23_v1.csv')
    lmp_dec19 = pd.read_csv('data/caiso_lmp_nodes/20191201_20200101_PRC_LMP_DAM_20200603_00_33_09_v1.csv')
    lmp_jan20 = pd.read_csv('data/caiso_lmp_nodes/20200101_20200201_PRC_LMP_DAM_20200603_08_11_05_v1.csv')
    lmp_feb20 = pd.read_csv('data/caiso_lmp_nodes/20200201_20200301_PRC_LMP_DAM_20200603_08_31_18_v1.csv')
    lmp_mar20 = pd.read_csv('data/caiso_lmp_nodes/20200301_20200401_PRC_LMP_DAM_20200603_08_32_02_v1.csv')
    lmp_apr20 = pd.read_csv('data/caiso_lmp_nodes/20200401_20200501_PRC_LMP_DAM_20200603_08_42_03_v1.csv')
    lmp_may20 = pd.read_csv('data/caiso_lmp_nodes/20200501_20200601_PRC_LMP_DAM_20200603_08_45_10_v1.csv')


    all_lmp_price = [lmp_feb19, lmp_mar19, lmp_apr19, lmp_may19, lmp_jun19, lmp_jul19, lmp_aug19, lmp_sep19, lmp_oct19, lmp_nov19, lmp_dec19,
                 lmp_jan20, lmp_feb20, lmp_mar20, lmp_apr20, lmp_may20]

    lmp_19_20 = pd.concat(all_lmp_price, axis=0).reset_index()
    lmp_19_20 = lmp_19_20[lmp_19_20['LMP_TYPE'] == 'LMP'].copy()
    lmp_19_20.columns=lmp_19_20.columns.str.strip()
    lmp_19_20['interval_start'] =  lmp_19_20['OPR_DT'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    lmp_19_20.sort_values(by=['OPR_DT','OPR_HR'], inplace=True)
    lmp_19_20['INTERVALSTARTTIME_GMT'] = pd.to_datetime(lmp_19_20['INTERVALSTARTTIME_GMT'])
    lmp_19_20['INTERVALENDTIME_GMT'] = pd.to_datetime(lmp_19_20['INTERVALENDTIME_GMT'])
    lmp_19_20['INTERVAL_START_PT'] = lmp_19_20['INTERVALSTARTTIME_GMT'] - timedelta(hours=7)
    lmp_19_20['INTERVAL_END_PT'] = lmp_19_20['INTERVALENDTIME_GMT'] - timedelta(hours=7)
    lmp_19_20_sub = lmp_19_20[['OPR_DT','OPR_HR', 'OPR_INTERVAL', 'NODE_ID', 'GROUP', 'POS', 'MW', 'INTERVAL_START_PT', 'INTERVAL_END_PT']].copy().reset_index()
    lmp_19_20_sub.drop('index', axis=1, inplace=True)
    lmp_19_20_sub.rename({'OPR_DT':'OPR_DT_PT', 'OPR_HR': 'OPR_HR_PT', 'MW':'$_MWH'}, axis=1, inplace=True)

    np15_lmp_19_20 = lmp_19_20_sub[lmp_19_20_sub['NODE_ID'] == 'NP15SLAK_5_N001'].copy()
    sp15_lmp_19_20 = lmp_19_20_sub[lmp_19_20_sub['NODE_ID'] == 'SP26SLAK_5_N001'].copy()
    zp26_lmp_19_20 = lmp_19_20_sub[lmp_19_20_sub['NODE_ID'] == 'ZP26SLAK_5_N001'].copy()

    return np15_lmp_19_20, sp15_lmp_19_20, zp26_lmp_19_20



def scrape_process_caiso_load_data(iso_class, oasis_start, oasis_end):
    """
    Uses pyiso library (created by WattTime) to scrape and parse the hourly energy consumption data from CAISO OASIS system.
    Merges and processes data to necessary format for future use.

    Parameters
    ----------
    iso_class: Class object
        A class object instatiated using pyiso.
        'CAISO' should always be assigned to this class when using this project.

    oasis_start : datetime
        The date to start collecting data. This date is exclusive.

    oasis_end : datetime
        The date to end date collection. This date is inclusive.

    Returns
    -------

    load_pivot : dataframe
        Dataframe comprised of hourly consumption figures for all people/entities that live/operate within California and a portion of Nevada.

    """
    for start, end in zip(oasis_start, oasis_end):
        caiso_load_dict[start] = iso_class.get_load(start_at=start, end_at=end)

    caiso_load_df = pd.DataFrame(columns=['timestamp', 'freq', 'market', 'ba_name', 'load_MW'])

    for date in caiso_load_dict.keys():
        load_temp_df = pd.DataFrame(caiso_load_dict[date])
        caiso_load_df = pd.concat([caiso_load_df, load_temp_df], axis=0, sort=False)

    caiso_load_df.sort_values(by='timestamp', inplace=True)
    caiso_load_df = caiso_load_df.reset_index()
    caiso_load_df.drop(['index', 'ba_name'], axis=1, inplace=True)

    caiso_load_df['date_hour_start'] = caiso_load_df['timestamp'].apply(lambda x: x.replace(microsecond=0,second=0, minute=0))
    load_pivot = caiso_load_df.pivot_table(index='date_hour_start', values='load_MW', aggfunc='sum').reset_index()
    load_pivot['date_hour_start'] = load_pivot['date_hour_start'].apply(lambda x: x.replace(tzinfo=None))
    load_19_20['date_hour_start'] = pd.to_datetime(load_19_20['date_hour_start']).apply(lambda x: x.replace(tzinfo=None))

    return load_pivot

def scrape_process_caiso_generation_data(iso_class, oasis_start, oasis_end) :
    """
    Uses pyiso library (created by WattTime) to scrape and parse the hourly energy consumption data from CAISO OASIS system.
    Merges and processes data to necessary format for future use.

    Parameters
    ----------
    iso_class: Class object
        A class object instatiated using pyiso.
        'CAISO' should always be assigned to this class when using this project.

    oasis_start : datetime
        The date to start collecting data. This date is exclusive.

    oasis_end : datetime
        The date to end date collection. This date is inclusive.

    Returns
    -------

    gen_pivot : dataframe
        Dataframe comprised of hourly generation data of power facilities within in CAISO.
        Generation is broken down by fuel sources, i.e. solar, wind, and other.
    """

    for start, end in zip(oasis_start, oasis_end):
        caiso_gen_dict[start] = iso_class.get_generation(start_at=start, end_at=end)

    caiso_gen_df = pd.DataFrame(columns=['ba_name', 'freq', 'fuel_name', 'gen_MW', 'market', 'timestamp'])
    for date in caiso_gen_dict.keys():
        gen_temp_df = pd.DataFrame(caiso_gen_dict[date])
        caiso_gen_df = pd.concat([caiso_gen_df, gen_temp_df], axis=0)

    caiso_gen_df.sort_values(by='timestamp', inplace=True)
    caiso_gen_df = caiso_gen_df.reset_index()
    caiso_gen_df.drop(['index', 'ba_name'], axis=1, inplace=True)

    caiso_gen_df['date_hour_start'] = caiso_gen_df['timestamp'].apply(lambda x: x.replace(microsecond=0,second=0, minute=0))
    gen_pivot = caiso_gen_df.pivot_table(index='date_hour_start', columns='fuel_name', values='gen_MW', aggfunc='sum').reset_index()
    gen_pivot['date_hour_start'] = gen_pivot['date_hour_start'].apply(lambda x: x.replace(tzinfo=None))
    gen_pivot['total_mw'] = gen_pivot['other'] + gen_pivot['solar'] + gen_pivot['wind']
    gen_pivot['date_hour_start'] = pd.to_datetime(gen_pivot['date_hour_start']).apply(lambda x: x.replace(tzinfo=None))
    gen_pivot.sort_values(by='date_hour_start', inplace=True)

    return gen_pivot

def scrape_process_caiso_net_ex_data(iso_class, oasis_start, oasis_end) :
    """
    Uses pyiso library (created by WattTime) to scrape and parse the hourly net export (exports less imports) data from CAISO OASIS system.
    This power is exported/imported to other sysem operators and/or wholesale markets.
    Merges and processes data to necessary format for future use.

    Parameters
    ----------
    iso_class: Class object
        A class object instatiated using pyiso.
        'CAISO' should always be assigned to this class when using this project.

    oasis_start : datetime
        The date to start collecting data. This date is exclusive.

    oasis_end : datetime
        The date to end date collection. This date is inclusive.

    Returns
    -------

    gen_pivot : dataframe
        Dataframe comprised of hourly net export data and corresponding time parameters.
    """

    caiso_ex_im_dict = {}

    for start, end in zip(oasis_start, oasis_end):
        caiso_ex_im_dict[start] = iso_class.get_trade(start_at=start, end_at=end)

    caiso_net_ex_df = pd.DataFrame(columns=['net_exp_MW', 'timestamp', 'freq', 'market', 'ba_name'])

    for date in caiso_ex_im_dict.keys():
        net_ex_temp_df = pd.DataFrame(caiso_ex_im_dict[date])
        caiso_net_ex_df = pd.concat([caiso_net_ex_df, net_ex_temp_df], axis=0, sort=False)

    caiso_net_ex_df.sort_values(by='timestamp', inplace=True, ascending=True)
    caiso_net_ex_df = caiso_net_ex_df.reset_index()
    caiso_net_ex_df.drop(['index', 'ba_name'], axis=1, inplace=True)

    caiso_net_ex_df['date_hour_start'] = caiso_net_ex_df['timestamp'].apply(lambda x: x.replace(microsecond=0,second=0, minute=0))
    net_ex_pivot = caiso_net_ex_df.pivot_table(index='date_hour_start', values='net_exp_MW', aggfunc='sum').reset_index()
    net_ex_pivot['date_hour_start'] = net_ex_pivot['date_hour_start'].apply(lambda x: x.replace(tzinfo=None))
    net_ex_pivot.sort_values(by='date_hour_start', inplace=True)

    return net_ex_pivot

def obtain_format_hh_natgas_to_df():
    """
    Acquire and cleans daily (not adjusted for season) Henry Hub daily natural gas prices.

    Data source: FRED

    Returns
    -------

    natgas : dataframe
        Dataframe comprise of daily prices and correpsonding dates.
    """

    natgas = pd.read_csv('data/natgas_jan_19_may_20.csv', names=['date', 'HH_$_million_BTU_not_seasonal_adj'], skiprows=1)
    natgas['date'] = natgas_19_20['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    natgas['HH_$_million_BTU_not_seasonal_adj'] = np.where((natgas_19_20['HH_$_million_BTU_not_seasonal_adj'] == '.'),
                                                           np.nan, natgas_19_20['HH_$_million_BTU_not_seasonal_adj'])
    return natgas

def create_caiso_master_df(np15, sp15, zp26, gen, load, net_ex, natgas):
    """
    Merges and process the provided dataframe.
    np15, sp15, zp15, gen, load and net_ex should be hourly data and have the same date ranges.
    natgas is expected to be summarized in data data.
    Applies forward fill for natgas's null values. The null values are weekend and holidays when prices are not produced.


    Parameters
    ----------
    np15 : dataframe
        Historic NP15 wholesale electricity price curve.

    sp15 : dataframe
        Historic SP15 wholesale electricity price curve.

    np15 : dataframe
        Historic ZP26 wholesale electricity price curve.

    gen : dataframe
        Hourly CAISO generation data.

    load : dataframe
        Hourly CAISO consumption data.

    net_ex : dataframe
        Hourly CAISO net export data.

    natgas : datetime
        Daily Henry Hub natural gas spot prices.

    Returns
    -------

    caiso_final : dataframe
        A dataset that almagamated and cleaned all the provided parameters.

    """

    all_lmp = pd.merge(np15, sp15, how='left', on='INTERVAL_START_PT', suffixes=('_np15','_sp15'))
    all_lmp = pd.merge(all_lmp, zp26, how='left', on ='INTERVAL_START_PT')
    all_lmp = all_lmp_19_20[['INTERVAL_START_PT', 'INTERVAL_END_PT', 'OPR_DT_PT', 'OPR_HR_PT', 'OPR_INTERVAL', '$_MWH_np15', '$_MWH_sp15', '$_MWH']].copy()
    all_lmp['INTERVAL_START_PT'] = pd.to_datetime(all_lmp['INTERVAL_START_PT']).apply(lambda x: x.replace(tzinfo=None))
    all_lmp['INTERVAL_END_PT'] = pd.to_datetime(all_lmp['INTERVAL_END_PT']).apply(lambda x: x.replace(tzinfo=None))


    # Merge LMPs and generation/consumption data.
    caiso = pd.merge(all_lmp, gen, how='left', left_on='INTERVAL_START_PT', right_on ='date_hour_start')
    caiso = pd.merge(caiso, load, how='left', left_on ='INTERVAL_START_PT', right_on = 'date_hour_start')
    caiso = pd.merge(caiso_draft, net_ex, how='left', left_on ='INTERVAL_START_PT', right_on = 'date_hour_start', suffixes=('_load', '_net_ex'))
    caiso['OPR_DT_PT'] = pd.to_datetime(caiso_draft['OPR_DT_PT'])

    # Monday = 0
    # Natural gas prices are not provided on Saturdays and Sundays.
    caiso['day_week'] = caiso_draft['OPR_DT_PT'].apply(lambda x: x.weekday())
    caiso = pd.merge(caiso, natgas, how='left', left_on='OPR_DT_PT', right_on='date', validate='m:1')

    # Clean/organize data.
    caiso_filled = caiso.copy()
    caiso_filled['HH_$_million_BTU_not_seasonal_adj'] = caiso_draft_filled['HH_$_million_BTU_not_seasonal_adj'].fillna(method='ffill')
    caiso_final = caiso_filled[['INTERVAL_START_PT', 'INTERVAL_END_PT', 'date_hour_start', 'OPR_DT_PT', 'OPR_HR_PT', 'day_week', 'OPR_INTERVAL', '$_MWH_np15', '$_MWH_sp15', '$_MWH_zp26',
                                  'other', 'solar', 'wind', 'total_mw', 'net_exp_MW', 'load_MW', 'HH_$_million_BTU_not_seasonal_adj']].copy()

    caiso.rename({'HH_$_million_BTU_not_seasonal_adj': 'HH_$_mill_BTU', 'total_mw':'total_gen'},axis=1, inplace=True)
    caiso['HH_$_mill_BTU'] = pd.to_numeric(caiso['HH_$_mill_BTU'])
    caiso['date_hour_start'] = pd.to_datetime(caiso['date_hour_start']).apply(lambda x: x.replace(tzinfo=None))

    caiso['INTERVAL_START_PT'] = pd.to_datetime(caiso['INTERVAL_START_PT']).apply(lambda x: x.replace(tzinfo=None))
    caiso['INTERVAL_END_PT'] = pd.to_datetime(caiso['INTERVAL_END_PT']).apply(lambda x: x.replace(tzinfo=None))
    caiso['date_hour_start'] = pd.to_datetime(caiso['date_hour_start']).apply(lambda x: x.replace(tzinfo=None))
    caiso['OPR_DT_PT'] = pd.to_datetime(caiso['OPR_DT_PT']).apply(lambda x: x.replace(tzinfo=None))
    caiso.rename({'HH_$_million_BTU_not_seasonal_adj': 'HH_$_mill_BTU', 'total_mw':'total_gen'},axis=1, inplace=True)
    caiso['HH_$_mill_BTU'] = pd.to_numeric(caiso['HH_$_mill_BTU'])
    
    caiso_final.set_index('INTERVAL_START_PT', inplace=True)
    caiso_final.sort_index(inplace = True)
    
    return caiso_final

def save_caiso_df_to_csv(dataset, file_name):
    path_csv_name = 'data/' + file_name + '.csv'
    dataset.to_csv(path_csv_name)
    
def import_caiso_dataset(version_name):
    path_csv_name = '../data/' + version_name + '.csv'
    return pd.read_csv(path_csv_name)

if __name__ == '__main__':
    
    oasis_start = pd.date_range(start='2019-01-15', end='2020-05-31', freq='14D')
    oasis_end = pd.date_range(start='2019-01-30', end='2020-06-05', freq='14D')
    
    np15_lmp, sp15_lmp, zp26_lmp = create_price_curve()
    
    caiso = client_factory('CAISO', timeout_seconds=60)
    load_data = scrape_process_caiso_load_data(caiso, oasis_start, oasis_end)
    gen_data = scrape_process_caiso_generation_data(caiso, oasis_start, oasis_end)
    net_ex_data = scrape_process_caiso_net_ex_data(caiso, oasis_start, oasis_end)
    nat_gas = obtain_format_hh_natgas_to_df()
    caiso_master = create_caiso_master_df(np15_lmp, sp15_lmp, zp26_lmp, gen_data, load_data, net_ex_data, nat_gas)
    
    save_caiso_df_to_csv(caiso_master, 'caiso_master_v02')