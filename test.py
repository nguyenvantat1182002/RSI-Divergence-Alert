import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas_ta as ta
import pandas as pd
import numpy as np
import scipy.stats as stats

from binance.um_futures import UMFutures
from rsi_divergence_finder import RSIDivergenceFinder, DivergenceState


client = UMFutures()
finder = RSIDivergenceFinder(client, 'BTCUSDT', '5m')


# def get_pairs(client: UMFutures):
#     info = client.exchange_info()
#     symbols = list(filter(lambda x: x['contractType'] == 'PERPETUAL', info['symbols']))
#     return [(item['pair'], item['underlyingSubType'][0].lower()) for item in symbols if item['pair'].endswith('USDT') and item['underlyingSubType']]


# print(get_pairs(client))
df, state, point_1, point_2, rsi_point_1, rsi_point_2 = finder.find()
print(df)
df = df.set_index('Time')

def highlight_deviation(df: pd.DataFrame):
    mco = []
    for _, row in df.iterrows():
        mco.append('yellow' if row['DEV'] > 0.9 else None)
    return mco



ema_50 = ta.ema(df['Close'], 50)

# # print(point_1)
# # print(point_2)
# # print(state)

if not state == DivergenceState.UNKNOW:
    alines_price = [(point_1['Time'], point_1['Low']), (point_2['Time'], point_2['Low'])]
    alines_rsi = [(rsi_point_1['Time'], rsi_point_1['RSI']), (rsi_point_2['Time'], rsi_point_2['RSI'])]
    plots = [
        mpf.make_addplot(ema_50, panel=0, color='black', width=1),
        mpf.make_addplot(df['RSI'], panel=2, color='white', fill_between=dict(y1=30, y2=30, color="gray")),
        mpf.make_addplot(df['RSI'], panel=2, color='white', fill_between=dict(y1=70, y2=70, color="gray")),
    ]

    mco = highlight_deviation(df)
    s = mpf.make_mpf_style(base_mpf_style='yahoo',rc={'grid.alpha':0}, figcolor='#fff', facecolor="#fff")
    fig, axs = mpf.plot(df, type='candle', style=s, volume=True, addplot=plots, datetime_format='', alines=dict(alines=alines_price, colors=['r', 'r']), returnfig=True, ylabel='', ylabel_lower='', marketcolor_overrides=mco, mco_faceonly=False)
    alines_rsi = mpf._utils._construct_aline_collections(dict(alines=alines_rsi, colors=['r', 'r']), df.index)
    axs[4].add_collection(alines_rsi)
    axs[0].xaxis.set_tick_params(labelbottom=False)
    plt.show()
