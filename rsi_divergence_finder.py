import pandas as pd
import pandas_ta as ta

from typing import Optional, Tuple
from enum import Enum
from binance.um_futures import UMFutures


class DivergenceState(Enum):
    UNKNOW = 0
    BEARISH = 1
    BULLISH = 2


class RSIDivergenceFinder:
    _client: UMFutures
    _pair: str
    _timeframe: str
    _rsi_length: int
    _window_size: int

    def __init__(self, client: UMFutures, pair: str, timeframe: str, rsi_length: int = 14, window_size: int = 5):
        self._client = client
        self._pair = pair
        self._timeframe = timeframe
        self._rsi_length = rsi_length
        self._window_size = window_size

    def find(self) -> Tuple[DivergenceState, Optional[Tuple[pd.Series, pd.Series]]]:
        df = self._get_df().tail(100)
        
        # Find RSI_PH greater than the current RSI_PH and get the nearest RSI_PH
        current_rsi_ph = df[df['RSI_PH']].iloc[-1]
        nearest_rsi_ph = df[(df['RSI_PH']) & (df['Time'] < current_rsi_ph['Time']) & (df['RSI'] > current_rsi_ph['RSI'])].iloc[-1]

        current_rsi_pl = df[df['RSI_PL']].iloc[-1]
        nearest_rsi_pl = df[(df['RSI_PL']) & (df['Time'] < current_rsi_pl['Time']) & (df['RSI'] < current_rsi_pl['RSI'])].iloc[-1]

        if nearest_rsi_ph['RSI'] > current_rsi_ph['RSI']:
            high = self._get_highest_high_pivot(df, nearest_rsi_ph)
            higher_high = self._get_highest_high_pivot(df, current_rsi_ph)
            if high['High'] < higher_high['High']:
                return df, DivergenceState.BEARISH, high, higher_high, nearest_rsi_ph, current_rsi_ph

        if nearest_rsi_pl['RSI'] < current_rsi_pl['RSI']:
            low = self._get_lowest_low_pivot(df, nearest_rsi_pl)
            lower_low = self._get_lowest_low_pivot(df, current_rsi_pl)
            if low['Low'] > lower_low['Low']:
                return df, DivergenceState.BULLISH, low, lower_low, nearest_rsi_pl, current_rsi_pl
            
        return df, DivergenceState.UNKNOW, None, None, None, None
    
    def _get_lowest_low_pivot(self, df: pd.DataFrame, pivot: pd.Series) -> pd.Series:
        left_bars = df[df['Time'] < pivot['Time']].tail(self._window_size)
        right_bars = df[df['Time'] > pivot['Time']].head(3)
        merged_df = pd.concat([left_bars, right_bars])
        lowest = merged_df.nsmallest(1, 'Low').iloc[0]
        if lowest['Low'] > pivot['Low']:
            lowest = pivot
        return lowest
    
    def _get_highest_high_pivot(self, df: pd.DataFrame, pivot: pd.Series) -> pd.Series:
        left_bars = df[df['Time'] < pivot['Time']].tail(self._window_size)
        right_bars = df[df['Time'] > pivot['Time']].head(3)
        merged_df = pd.concat([left_bars, right_bars])
        highest = merged_df.nlargest(1, 'High').iloc[0]
        if highest['High'] < pivot['High']:
            highest = pivot
        return highest
    
    def _get_df(self) -> pd.DataFrame:
        klines = self._client.continuous_klines(
            pair=self._pair,
            contractType='PERPETUAL',
            interval=self._timeframe,
            limit=1000
        )
        df = pd.DataFrame(klines)
        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']

        for col in df.columns[1:]:
            df[col] = df[col].astype(float)

        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df['RSI'] = ta.rsi(df['Close'], self._rsi_length)

        df.dropna(inplace=True)

        df['RSI_PH'] = df['RSI'] == df['RSI'].rolling(2 * self._window_size + 1, center=True).max()
        df['RSI_PL'] = df['RSI'] == df['RSI'].rolling(2 * self._window_size + 1, center=True).min()
        
        return df
    