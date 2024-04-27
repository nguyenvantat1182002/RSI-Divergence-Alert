import pandas as pd
import pandas_ta as ta
import numpy as np
import scipy.stats as stats

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
        nearest_rsi_ph = df[(df['RSI_PH']) & (df['Time'] < current_rsi_ph['Time']) & (df['RSI'] > current_rsi_ph['RSI'])]

        current_rsi_pl = df[df['RSI_PL']].iloc[-1]
        nearest_rsi_pl = df[(df['RSI_PL']) & (df['Time'] < current_rsi_pl['Time']) & (df['RSI'] < current_rsi_pl['RSI'])]
        
        if not nearest_rsi_ph.empty:
            nearest_rsi_ph = nearest_rsi_ph.iloc[-1]
            if nearest_rsi_ph['RSI'] > current_rsi_ph['RSI']:
                high = self._get_highest_high_pivot(df, nearest_rsi_ph)
                higher_high = self._get_highest_high_pivot(df, current_rsi_ph)
                if high['High'] < higher_high['High']:
                    return df, DivergenceState.BEARISH, high, higher_high, nearest_rsi_ph, current_rsi_ph

        if not nearest_rsi_pl.empty:
            nearest_rsi_pl = nearest_rsi_pl.iloc[-1]
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
    
    def _vsa_indicator(self, data: pd.DataFrame, norm_lookback: int = 168):
        # Norm lookback should be fairly large

        atr = ta.atr(data['High'], data['Low'], data['Close'], norm_lookback)
        vol_med = data['Volume'].rolling(norm_lookback).median()

        data['norm_range'] = (data['High'] - data['Low']) / atr 
        data['norm_volume'] = data['Volume'] / vol_med 

        norm_vol = data['norm_volume'].to_numpy()
        norm_range = data['norm_range'].to_numpy()

        range_dev = np.zeros(len(data))
        range_dev[:] = np.nan

        for i in range(norm_lookback * 2, len(data)):
            window = data.iloc[i - norm_lookback + 1: i+ 1]
            slope, intercept, r_val,_,_ = stats.linregress(window['norm_volume'], window['norm_range'])

            if slope <= 0.0 or r_val < 0.2:
                range_dev[i] = 0.0
                continue
        
            pred_range = intercept + slope * norm_vol[i]
            range_dev[i] = norm_range[i] - pred_range
            
        return pd.Series(range_dev, index=data.index)

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
        df['DEV'] = self._vsa_indicator(df)

        df.dropna(inplace=True)

        df['RSI_PH'] = df['RSI'] == df['RSI'].rolling(2 * self._window_size + 1, center=True).max()
        df['RSI_PL'] = df['RSI'] == df['RSI'].rolling(2 * self._window_size + 1, center=True).min()
        
        return df
    