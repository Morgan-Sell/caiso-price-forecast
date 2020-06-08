# Forecasting California's Wholesale Electricity Prices

![Intro](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/turbines_panels.jfif)

## Table of Contents

1) Executive Summary
2) VisionZero
3) Data Processing and Feature Engineering
4) Exploratory Data Analysis
5) Model Evaluation and Selection
6) Conclusion and Further Investigation

## Executive Summary
EXECUTIVE SUMMARY
Behind every lightbulb is a multi-billion-dollar industry based on the production, consumption, and trading of electricity. Hundreds of millions of dollars are exchanged on a 5-minute, 15-minute and hourly bases. The challenge is predicting what the price of electricity will be. Price volatility is high, arguably more unpredictable than the weather in the Amazon. Google “California electricity crisis”. We can thank the “smartest guys in the room” for that gift.

Any edge that a trader, an energy procurer or power producer to predict electricity prices more accurately has almost infinite value. 

In this project, we compared the accuracy of different time-series forecasting techniques, i.e. simple, ARIMA, and Long Short-Term Memory (LSTM).

To compare the modeling approaches, I performed a ten-day forecast California Independent System Operator (CAISO) hourly price in the day-ahead market for each of the main trading hubs, i.e. NP15, SP15, and ZP26. The image below shows how California electricity market is distributed among these three hubs/regions.

I used the root mean squared error (RMSE) to evaluate the forecasting methods. The LSTM outperformed ARIMA for all three hubs. The RMSE that resulted form LSTM was 30% to 40% less than RMSE associated with ARIMA. 

For illustrative purposes, I have referenced NP-15 throughout the file; otherwise, the readme file would be 3x longer and provide no additional information. 

![CAISO Hubs](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/caiso_hubs.png)

## Data and Processing
The data is comprised of ~11,500 hours starting on March 1, 2019 and ending on May 31, 2020. The data specifically related to California – i.e. hourly price, generation, consumption, and net export – is sourced from the CAISO Open Access Same-time Information System (OASIS). For some of the data, I used the pyiso library, created by WattTime, to scrape and parse data from CAISO OASIS.

I also included the Henry Hub daily natural gas spot price, which I procured from Federal Reserve Economic Data (FRED). More than 50% of the electricity produced in California is derived from natural gas (1). Therefore, I included the fuel cost as an exogenous variable.

Additionally, all the initial data was not an hourly basis. For example, the generation and load data were on 15-minute basis and the natural gas spot price was on a daily. Also, natural gas prices were not provided for weekend and national holidays. I used Friday or the prior day’s prior for the days that the values were omitted.

## Exploratory Data Analysis

Wholesale electricity markers are known for their unpredictability. This analysis was performed on the day-ahead market which is normally more “level-headed” than its untamed family members, the 5- and 15-sminute market. In the last year, prices in these markets have ranged from -$150 / MWh to $950 / MWh. 
From March 2019 to May 2020, the NP15, SP15, and ZP26 shared a similar price trend. The scatter plot below is NP-15 day-ahead maker hourly prices. The high prices in February 2019 were caused high natural gas prices at the trade hubs within the CAISO area. Prices at PG&E Citygate and SoCal Citygate increased from $5 to $10/MMBtu and $4 to $8/MMBtu, respectively. As mentioned earlier natural gas is dominant source of energy California. It commands a higher percentage of the generation in the winter, e.g. February, when solar irradiation is limited.


![NP-15 Hourly Price](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/np15_day_ahead_price.png)

The following box plot demonstrates the distribution of NP-15 electricity prices by hour of the day. The graph shows two peaks – 7 to 8 am and 6 to pm. Consumption is greatest throughout the day; therefore, prices are expected to be higher when people are working, shopping or attending school. How come prices drop in the middle of the day?

The low mid-day prices are a result of California’s success in deploying solar energy. On average, solar now provides more than 10% of the electricity consumed by Californians. Throughout the day, the state receives an abundance of energy; sometimes, too much energy is produced causing negative prices in the 5- and 15-minute wholesale markets. And, unlike natural gas, a solar project’s fuel – i.e. the sun – is free. Therefore, generators can supply energy at a lower marginal price.


![NP-15 Price Distribution](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/np15_hourly_distribution.png)

To further evaluate, California’s advancement of renewable energy, the graph below shows the percentage of energy generated that has been renewable resources, i.e. solar and wind. The chart shows the seasonality, i.e. higher percentage of the generation during the summer due to longer days and less rain. Also, the data shows that starting in mid-March 2020, which coincides with policies being implemented to contain COVID-19, the state is producing a greater percentage of its energy from renewable resources than ever before. 

Further research is required to determine the cause as one driver to this increase less energy is being produced. If that is true, it could support the argument that the marginal cost to generate energy from wind and solar is less than natural gas in the state of California.


![Energy Derived Renew](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/energy_derived_renew.png)


## Model Evaluation and Selection

Prior to developing the forecast models, I tested whether the time-series data was stationary/autocorrelation. The visualizations below are lag plots for each CAISO trading hub. I set the lag to 24 hours Since each hub’s point cluster is a diagonal line point to the top-right, the data suggests a strong positive correlation between the hourly price and the price at the same hour the following day. 


![Lag Plots](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/lag_plot.png)

I established a baseline model by projecting the historic hourly average. Both the ARIMA and LSTM models are univariate.
To test the merits of each model, I forecasted the hourly prices for the last ten days in May 2020. 

The two plots below are the predicted NP-15 day-ahead hourly prices.

The first graph below shows the results of the ARIMA model. Initially, the ARIMA model’s predictions were quite accurate. However, the model’s performance diminishes starting on May 24 and only deteriorates further the following days.
On the other hand, the LSTM model lives up to its name. The LSTM model demonstrates its ability to carry its information over a longer duration. Excluding two overlooking two outliers, the model’s precision is remarkable. 


![NP-15 10-day Fcst](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/np15_10_day_fcst.png)

The results of both the SP-15 and ZP-26 forecasts produced similar conclusion. Below is the summary of the RMSE for all three trading hubs and all three models.

![RMSE Summary](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/rmse_summary_table.png)

## Conclusion and Further Exploration

In short, recurrent neural networks, specifically LSTM, have demonstrated their value. The ability to predict wholesale electricity more accurately is lucrative. I am also curious how LSTM can be applied to predict electricity supply and demand. California and its poorly behaving utilities should apply all valuable resources.

Furthermore, ass mentioned in the onset, I gathered various exogenous variables, e.g. total generation by fuel type, consumption and price of naturally I would like to forecasting electricity prices using multivariate ARIMA and LSTM to assess the affect that  changes in exogenous variables would have on CAISO’s day-ahead hourly electricity price.
