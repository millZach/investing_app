import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data
import seaborn as sns


def stock_data_grab(tickers, start_date, end_date):
    df_dict = {}

    for ticker in tickers:
        df_dict[f'{ticker}'] = data.DataReader(ticker, 'yahoo', start_date, end_date)

    return df_dict


def returns(df_dict):
    for key in df_dict.keys():
        df_dict[key]['Returns'] = df_dict[key]['Adj Close'].pct_change()
        df_dict[key].dropna(inplace=True)

    return df_dict


def key_statistics(df_dict, target_vol, bond):
    df_lst = []
    stats_dict = {}
    view_stats = {}
    for key in df_dict.keys():
        df_lst.append(df_dict[key])
        stats_dict[f'Stdev_{key}'] = round(df_dict[key]['Returns'].std(), 4)
        view_stats[f'Stdev {key}'] = stats_dict[f'Stdev_{key}']
        stats_dict[f'Volitility_{key}'] = stats_dict[f'Stdev_{key}'] * np.sqrt(252)
        view_stats[f'Volitility {key} (%)'] = stats_dict[f'Volitility_{key}'] * 100

        if key != bond:
            stats_dict['Allocation_ETF'] = target_vol / stats_dict[f'Volitility_{key}']
            view_stats[f'Allocation {key} (%)'] = stats_dict['Allocation_ETF'] * 100
        else:
            stats_dict[f'Allocation_{key}'] = 1 - stats_dict['Allocation_ETF']
            view_stats[f'Allocation {key} (%)'] = stats_dict[f'Allocation_{key}'] * 100

    df_merged = pd.concat(df_lst, axis=1)
    stats_dict['Returns Correlated'] = round(
        df_merged['Returns'].corr().iloc[0].iloc[1], 4)
    view_stats['Returns Correlated'] = stats_dict['Returns Correlated']
    stats_df = pd.DataFrame(stats_dict, index=['Statistics']).transpose()
    view_stats_df = pd.DataFrame(view_stats, index=['Statistics']).transpose()

    return df_merged, stats_df, stats_dict, view_stats_df


def correlation_heat_map(df_merged):
    df_corr = df_merged.corr()
    plot = sns.heatmap(df_corr, cmap='coolwarm')
    plt.title('Correlation Heatmap')
    plt.tight_layout()


def plot_200ma(ticker, start_date, end_date, window):
    df_dict = stock_data_grab([ticker], '2000-01-01', end_date)
    df = df_dict[ticker]
    df[f'{window} SMA'] = df['Adj Close'].rolling(window=window, min_periods=0).mean()
    df[f'Below {window} SMA'] = np.where(
        df[f'{window} SMA'] > df['Adj Close'], df['Adj Close'], None)

    ax = plt.gca()

    df['Adj Close'].loc[start_date:end_date].plot(
        kind='line', ax=ax, style='-xk')
    df[f'{window} SMA'].loc[start_date:end_date].plot(kind='line', ax=ax, style='-b')
    df[f'Below {window} SMA'].loc[start_date:end_date].plot(kind='line', ax=ax, style='-xr')
    plt.xlabel('Date', fontsize=16)
    plt.ylabel('Value (USD)', fontsize=16)
    plt.legend(
        ['Adj Close', f'{window} SMA', f'Below {window} SMA']
    )
    plt.tight_layout()

    return df


def allocation_pie_chart(stats_dict, tickers):
    pct_allocation = []
    for key in stats_dict.keys():
        if 'Allocation' in key:
            pct_allocation.append(stats_dict[key])

    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = tickers
    sizes = pct_allocation
    explode = (0, 0.1)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct='%1.1f%%', shadow=True, startangle=90,
            colors=['#2D2926FF', '#E94B3CFF'], textprops=dict(color="w"))
    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.axis('equal')
    ax1.set_title('Allocation')
    ax1.legend(labels)
    plt.tight_layout()


def plot_stocks(stock_dict, tickers):

    df_etf = stock_dict[tickers[0]]
    df_bond = stock_dict[tickers[1]]
    x = df_etf.index
    yetf = df_etf['Adj Close']
    ybond = df_bond['Adj Close']

    fig = plt.figure()

    plt.plot(x, yetf, c='#2D2926FF')
    plt.plot(x, ybond, c='#E94B3CFF')
    fig.autofmt_xdate()
    plt.xlabel('Date', fontsize=16)
    plt.ylabel('Value (USD)', fontsize=16)
    plt.legend(tickers)
    plt.tight_layout()
