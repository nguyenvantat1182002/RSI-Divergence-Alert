# import mplfinance as mpf
# import matplotlib.pyplot as plt

# from binance.um_futures import UMFutures
# from rsi_divergence_finder import RSIDivergenceFinder, DivergenceState


# client = UMFutures()
# finder = RSIDivergenceFinder(client, 'BTCUSDT', '4h')

# df, state, point_1, point_2, rsi_point_1, rsi_point_2 = finder.find()
# df = df.set_index('Time')

# # print(point_1)
# # print(point_2)
# print(state)

# if not state == DivergenceState.UNKNOW:
#     alines_price = [(point_1['Time'], point_1['Low']), (point_2['Time'], point_2['Low'])]
#     alines_rsi = [(rsi_point_1['Time'], rsi_point_1['RSI']), (rsi_point_2['Time'], rsi_point_2['RSI'])]
#     plots = [
#         mpf.make_addplot(df['RSI'], panel=2, color='black', ylabel='RSI', fill_between=dict(y1=30, y2=30, color="gray")),
#         mpf.make_addplot(df['RSI'], panel=2, color='black', ylabel='RSI', fill_between=dict(y1=70, y2=70, color="gray")),
#     ]
#     s = mpf.make_mpf_style(base_mpf_style='yahoo',rc={'grid.alpha':0})
#     fig, axs = mpf.plot(df, type='candle', style=s, volume=True, addplot=plots, alines=dict(alines=alines_price, colors=['r', 'r']), returnfig=True)
#     alines_rsi = mpf._utils._construct_aline_collections(dict(alines=alines_rsi, colors=['r', 'r']), df.index)
#     axs[4].add_collection(alines_rsi)
#     plt.savefig('btc.png', bbox_inches='tight')

import os

print(os.path.basename('C:\\Users\\NCPC\\python-sources\\RSI-Divergence-Alert\\btc.png'))