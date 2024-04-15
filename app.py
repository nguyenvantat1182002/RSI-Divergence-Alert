from rsi_divergence_finder import RSIDivergenceFinder
from binance.um_futures import UMFutures


client = UMFutures()
finder = RSIDivergenceFinder(client, 'BTCUSDT', '1h')

state, res = finder.find()
if res is not None:
    point_1, point_2 = res
    print(point_1)
    print(point_2)
print(state)
