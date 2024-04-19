from binance.um_futures import UMFutures
from rsi_divergence_finder import RSIDivergenceFinder


client = UMFutures()
finder = RSIDivergenceFinder(client, 'ETHWUSDT', '15m')

state, point_1, point_2 = finder.find()
print(point_1)
print(point_2)
print(state)
