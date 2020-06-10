import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
import tensorflow as tf
keras = tf.keras
from datetime import datetime

def calc_rmse(actual, pred):
    """
    Calculates the root mean squared error.

    Parameters
    ----------
    actual : arr
       Actural prices from a valid dataset.

    pred : arr
        Forecasted prices derived from one of the time series models.

    Returns
    -------

    rmse : float
        RMSE for the two provided price curves.
    """
    return np.sqrt(mean_squared_error(actual, pred))

# BASELINE MODEL
def baseline_fcst(lmp_curve, n_periods_fcst):
    """
    Calculated a baseline forecast based on average historic price.

    Parameters
    ----------
    lmp_curve : arr
       Historic electricity price curves

    n_periods_fcst : int
        Number of periods to forecast.

    Returns
    -------

    ARIMA : object
        A fitted model to be used for predicting hourly electricity prices.
    """

    avg = lmp_curve.mean()
    return np.full(n_periods_fcst, avg)

# ARIMA MODEL
def arima_uni_var_train_valid_split(lmp_curve, date_rng, train_split_idx):
    """
    Splits the provided priced curve - i.e. lmp_curve - into train and validation for us in the ARIMA model.

    Parameters
    ----------
    lmp_curve : arr
       Historic hourly prices for either NP15, SP15 or ZP26

    date_rng : arr
        Values are hourly timestamps that correspond to hourly prices

    train_split_index : int
        The index that is used to split the univarite time series into train and validation datasets.

    Returns
    -------

    lmp_train_curve : arr
        Prices used to train ARIMA model.

    lmp_valid_curve : arr
        Prices used to validate ARIMA model's hourly price forecast.

    date_train_rng : arr
        Dates and times used to train ARIMA model.

    date_valid_rng : arr
        Dates used to validate ARIMA model's hourly price forecast.
    """

    lmp_train_curve = lmp_curve[:train_split_idx]
    lmp_valid_curve = lmp_curve[train_split_idx:]
    date_train_rng = date_rng[:train_split_idx]
    date_valid_rng = date_rng[train_split_idx:]
    return lmp_train_curve, lmp_valid_curve, date_train_rng, date_valid_rng

def arima_uni_var_fit(lmp_train, date_rng, p, d, q):
    """
    Fits a univariate ARIMA model

    Parameters
    ----------
    lmp_train : arr
       Prices used to train ARIMA model.

    date_rng : arr
        Dates and times used to train ARIMA model.

    p : int
        The number of lag observations included in the model, commonly referred to as the lag order.

    d : int
        The number of times that the raw observations are differenced, commonly referred to as the degree of differencing.

    q : int
        The size of the moving average window.

    Returns
    -------

    ARIMA : object
        A fitted model to be used for predicting hourly electricity prices.
    """

    return ARIMA(endog=lmp_train, dates=date_rng, order=(p, d, q), freq='H').fit()

def arima_uni_var_predict(model, n_period_fcst):
    """
    Fits a univariate ARIMA model

    Parameters
    ----------
    model : object
       A fitted ARIMA model used to forecast hourly prices.

    n_period_fcst : int
        Number of hours to forecast

    Returns
    --------

    Prediction: arr
        An array of forecasted electricity prices
    """

    return model.forecast(steps=n_period_fcst)[0]

# LSTM MODEL
def windowize_data(data, n_prev):
    """
    Creates the sliding time sequence that delineates the dependent and independent variables.

    Parameters
    ----------
    data : arr
        Value will be one of the lmp curves.

    n_prev : int
        The number of values that comprise a sequence/window.

    Return
    ------
    x : arr
        Indepedent variables to be used in the LSTM model.
    y : arr
        Dependent variables to be used in the LSTM model.
    """

    n_predictions = len(data) - n_prev
    y = data[n_prev:]
    # this might be too clever
    indices = np.arange(n_prev) + np.arange(n_predictions)[:, None]
    x = data[indices, None]
    return x, y

def split_and_windowize(data, n_prev, fraction_valid):
    """
    Splits the dataset into test and validation.
    Creates the sequences/windows to process for LSTM model.

    Parameters
    ----------
    data : arr
        Value will be one of the lmp curves.

    n_prev : int
        The number of values that comprise a sequence/window.

    fraction_valid : float
        The percentage of the dataset that should be allocated to the validation data set.

    Return
    ------
    x_train : arr
        Indepedent variables to be used to train the LSTM model.

    x_valid : arr
        Indepdent variables to be used when using the LSTM to forecast electricity prices.

    y_train : arr
        Dependent variables to be used to train the LSTM model.

    y_valid : arr
        Dependent variables to be used to assess the LSTM model's predictions.

    """
    n_predictions = len(data) - 2*n_prev

    n_test  = int(fraction_valid * n_predictions)
    n_train = n_predictions - n_test

    x_train, y_train = windowize_data(data[:n_train], n_prev)
    x_valid, y_valid = windowize_data(data[n_train:], n_prev)
    return x_train, x_valid, y_train, y_valid



def compile_and_fit_lstm_uni_var(X_train, y_train, batch_size, n_nodes=32, n_epochs=20):
    """
    Compiles and fits a three-layered univariate LSTM model

    Parameters
    ----------
    X_train : arr
        Indepedent variable, i.e. historic price, that has been windowized.

    y_train : arr
        Depedent variable, i.e. historic price, that has been windowized.

    batch_size : int
        Number of train examples used in each iteration.

    n_nodes : nodes
        Number of notes at each layer.

    n_epocs : int
        Number times that the LSTM model will work through the entire training dataset.

    Returns
    -------

    lstm_uni : object
        A compiled and trained LSTM model.
    """
    n_features = X_train.shape[2]

    lstm_uni = keras.Sequential()
    lstm_uni.add(keras.layers.LSTM(n_nodes, input_shape=(batch_size, n_features), return_sequences=True))
    lstm_uni.add(keras.layers.LSTM(n_nodes, return_sequences=True))
    lstm_uni.add(keras.layers.LSTM(n_nodes, return_sequences=False))
    lstm_uni.add(keras.layers.Dense(1, activation='linear'))
    lstm_uni.compile(optimizer='adam',loss='mse')

    lstm_uni.fit(X_train, y_train, batch_size, n_epochs)

    return lstm_uni

# COMPARATIVE PLOT
def plot_actual_arima_baselie_lstm(date_rng, y_true, arima_pred, baseline_pred, lstm_pred,  plot_title):
    """
    Comparative plot of actual and predicted prices for each forecasting method.

    Parameters
    ----------
    date_rng : arr
       A range of the datetime objects for forecast period.

    y_true : arr
        Actual price prices for the forecast period.

    arima_pred: arr
        Forecasted prices derived from an ARIMA model.

    baseline_pred: arr
        Forecasted prices derived from baseline model.

    lstm_pred : arr
        Forecasted prices derived from LSTM.

    plot_title : str
        Title for the plot.

    Returns
    -------

    """
    fig, ax = plt.subplots(figsize=(20,7))
    ax.plot(date_rng, baseline_pred, 'grey', linestyle='--', label='Baseline', lw=3, alpha=0.7)
    ax.plot(date_rng, arima_pred, 'g-', label='ARIMA', lw=3, alpha=0.7)
    ax.plot(date_rng, lstm_pred, 'b--', label='LSTM', lw=3, alpha=0.7)
    ax.plot(date_rng, y_true, 'r.', label='Actual', markersize=12, alpha=0.6)
    ax.set_title(plot_title, fontsize=22, fontweight='bold')
    ax.set_ylabel('$/MWh', fontsize=14)
    ax.legend()
