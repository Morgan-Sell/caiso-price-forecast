# Forecasting California's Wholesale Electricity Prices

![Intro](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/re_pic.jpg)

## Table of Contents

1) Executive Summary
2) Data and Processing 
3) Exploratory Data Analysis
4) Model Evaluation and Selection
5) Conclusion and Further Investigation
6) Necessary Packages
7) Sources

## Executive Summary
Behind every lightbulb is a multi-billion-dollar industry based on the production, consumption, and trading of electricity. Hundreds of millions of dollars are exchanged on 5-minute, 15-minute and hourly bases. A great challenge is predicting the price of electricity. Volatility is high, arguably more unpredictable than the weather in the Amazon. 

Energy traders, procurers, and power producers are constantly looking for an edge in how to enhance their forecasting accuracies.  In this project, I assessed the performance of different time-series forecasting techniques, i.e. historic average, autoegressive integrated moving average (ARIMA), and long short-term memory (LSTM).

To compare the modeling approaches, I performed ten-day hourly forecasts of the California Independent System Operator (CAISO) wholesale electricity price in the day-ahead market for each of the main trading hubs, i.e. NP15, SP15, and ZP26. The image below shows how the California electricity market is distributed among these three hubs/regions.

I used the root mean squared error (RMSE) to evaluate the forecasting methods which allows the metric to be same denomination ($/MWh) as the price of electricity. The LSTM outperformed ARIMA for all three hubs. LSTM resulted in a RMSE that was 40% to 50% less than the RMSE achieved by the ARIMA model.

To uphold the "TL;DR" doctrine, I have solely referenced NP-15 (NorCal) throughout the file.

<p align="center">
  <img src="https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/caiso_hubs.png">
</p>

## Data and Processing

The data is comprised of ~11,500 hours starting on March 1, 2019 and ending on May 31, 2020. The data specifically related to California – i.e. hourly price, generation, consumption, and net export – is sourced from the CAISO Open Access Same-time Information System (OASIS). I used the “pyiso” package, created by WattTime, to help with scraping and parsing some of the CAISO OASIS data.

I also included the Henry Hub daily natural gas spot price, which I procured from Federal Reserve Economic Data (FRED). On average, more than 50% of the electricity produced in California is derived from natural gas. <sup>(1)</sup> Therefore, I included the fuel cost as an exogenous variable. The data demonstrated how the CAISO's dependency on natural gass impacts the price.

Additionally, all the initial data was not denominated in hours. For example, the generation and load data were generated on 15-minute bases and the natural gas spot price was on a daily. Also, natural gas prices were not provided for weekend and national holidays. I used Friday or the prior day’s price prior for the days that the natural gas prices were omitted.


## Exploratory Data Analysis

Wholesale electricity markerts are known for their unpredictability. This analysis was performed on the day-ahead market which is normally more “level-headed” than its untamed family members, the 5- and 15-minute markets. In the last year, prices in real-time markets have ranged from -$150 / MWh to $950 / MWh.<sup>(1)</sup>

From March 2019 to May 2020, the NP15, SP15, and ZP26 shared a similar price trend. The scatter plot below shows the NP-15 (NorCal) day-ahead hourly prices. The high prices in February 2019 were caused high natural gas prices at the trade hubs within the CAISO area. Prices at PG&E Citygate and SoCal Citygate increased from $5 to $10/MMBtu and $4 to $8/MMBtu, respectively.<sup>(1)</sup> As mentioned earlier natural gas is the dominant source of energy California. It commands a higher percentage of the generation in the winter, e.g. February, when solar irradiation is limited.


![NP-15 Hourly Price](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/np15_day_ahead_price.png)

The following box plot demonstrates the distribution of NP-15 (NorCal) electricity prices by hour of the day. For those who do not work in the energy sector, you may be questioning why there is a mid-day dip. California is not Spain where mid-day siestas are pastime. And, no, it is not common practice to have mid-day group meditation sessions with gurus. Like other markets, consumption is greatest throughout the day in CAISO.

However, California has been successful in deploying solar energy. On average, solar now provides more than 10% of the electricity consumed by Californians.<sup>(1)</sup> Throughout the day, the state receives an abundance of energy; sometimes, an excesssive ammount causing negative prices in the  real-time wholesale markets. And, unlike natural gas, a solar generator’s fuel – i.e. the sun – is free. Therefore, generators can supply energy at a lower marginal price. 

![NP-15 Price Distribution](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/np15_hourly_distribution.png)

To further evaluate, California’s advancement of renewable energy, the graph below shows the percentage of energy generated from renewable resources, i.e. solar and wind. The chart shows the seasonality, i.e. higher percentage of the generation during the summer due to longer days and less rain. Also, the data demonstrates that starting in mid-March 2020, which coincides with policies being implemented to contain the spread of COVID-19, the state produced a greater percentage of its energy from renewable resources in its history. 

Further research is required to determine the cause. One driver to this increase is that less energy is being produced, i.e. lower denominator, due to a decrease in electricity consumption since the arrival of the pandemic and its correspdoning policies.

![Energy Derived Renew](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/energy_derived_renew.png)


## Model Evaluation and Selection

Prior to developing the forecast models, I tested whether the time-series data was stationary/autocorrelated. The visualizations below are lag plots for each CAISO trading hub. I set the lag to 24 hours 

Each hub’s point cluster is a diagonal line directed to the top-right.  This trend suggests a strong positive correlation between the current hourly price and the price at the same hour the following day, confirming that an autoregressive approach is appropriate.

![Lag Plots](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/lag_plot.png)

As mentioned in the summary, I applied three univariate forecast methods - historic average (baseline), ARIMA, and LSTM.

To evaluate each model’s merit, I forecasted the hourly prices for the last ten days in May 2020. 

The two plots below are the predicted NP-15 day-ahead hourly prices.

The first graph shows the ARIMA model’s results. Initially, the ARIMA model’s predictions were quite accurate. However, the model’s performance diminishes starting on May 24 and only deteriorates further the following days.

On the other hand, the LSTM model lives up to its name. The LSTM model demonstrates its ability to maintain its knowledge of dependencies over a long duration. 
 

![NP-15 10-day Fcst](https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/np15_10_day_fcst.png)


To optimize LSTM performance, I performed various iterations of LSTM. I have two key takeaways:

1) In addition to enhancing computational efficiency, applying `MinMaxScaler()` significantly decreased the RMSE. (When doing so, remember to apply `inv_transform()` to reverse the scaling prior to assessing the prediction results.)

2) Do not overlook simple models. I developed LSTM with various layers that included dropout rates to avoid overfitting. In the end, a LSTM with one hidden layer comprised of 32 nodes produced the most accurate results.

The SP-15 and ZP-26 forecasts produced similar conclusions. Below is the summary of the RMSE for all three trading hubs and all three models.


<p align="center">
  <img src="https://github.com/Morgan-Sell/caiso-price-forecast/blob/master/images/rmse_summary_table.png">
</p>


## Conclusion and Further Exploration

In short, recurrent neural networks, specifically LSTM, demonstrated its value in forecasting. The ability to retain knowledge of long-term dependencies by vausing gates to retain/forget information that is carried along the network's "conveyor belt" is asset when applied to time series. 

Overtime, I will add mutltivariate forecasting strategies to this repo to analyze depedencies among electricity supply/demand, fue resources, price, and other market dynamics.


## Required Packages

- pandas
- numpy
- pyiso
- matplotlib
- tensorflow
- seaborn

## Sources

(1) CAISO