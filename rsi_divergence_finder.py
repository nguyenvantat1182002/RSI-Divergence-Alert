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
    _length: int

    def __init__(self, client: UMFutures, pair: str, timeframe: str, length: int = 14):
        self._client = client
        self._pair = pair
        self._timeframe = timeframe
        self._length = length

    def find(self) -> Tuple[DivergenceState, Optional[Tuple[pd.Series, pd.Series]]]:
        df = self._get_df()
        
        # Find RSI_PH greater than the current RSI_PH and get the nearest RSI_PH
        current_rsi_ph = df[df['RSI_PH']].iloc[-1]
        nearest_rsi_ph = df[(df['RSI_PH']) & (df['Time'] < current_rsi_ph['Time']) & (df['RSI'] > current_rsi_ph['RSI'])].iloc[-1]

        current_rsi_pl = df[df['RSI_PL']].iloc[-1]
        nearest_rsi_pl = df[(df['RSI_PL']) & (df['Time'] < current_rsi_pl['Time']) & (df['RSI'] < current_rsi_pl['RSI'])].iloc[-1]

        if nearest_rsi_ph['RSI'] > current_rsi_ph['RSI']:
            # Kiểm tra trong khoảng thời gian nearest_rsi_ph đến current_rsi_ph
            # xem có PH hay không và điều điện là không empty & > 1 & có PH
            selected_data = df[(df['Time'] >= nearest_rsi_ph['Time']) & (df['Time'] <= current_rsi_ph['Time']) & (df['PH'])]
            if not selected_data.empty and len(selected_data) > 1:
                res = self._is_higher_high(selected_data)
                if not res is None: 
                    return DivergenceState.BEARISH, res

        if nearest_rsi_pl['RSI'] < current_rsi_pl['RSI']:
            selected_data = df[(df['Time'] >= nearest_rsi_pl['Time']) & (df['Time'] <= current_rsi_pl['Time']) & (df['PL'])]
            if not selected_data.empty and len(selected_data) > 1:
                res = self._is_lower_low(selected_data)
                if not res is None:
                    return DivergenceState.BULLISH, res
            
        return DivergenceState.UNKNOW, None
    
    def _is_lower_low(self, df: pd.DataFrame) -> Optional[Tuple[pd.Series, pd.Series]]:
        highest_low = df.head(1).iloc[-1]
        lowest_low = None

        for _, row in df.iterrows():
            if not row['Time'] == highest_low['Time'] and row['Low'] < highest_low['Low']:
                lowest_low = row

        if lowest_low is None:
            return lowest_low
        
        return highest_low, lowest_low
    
    def _is_higher_high(self, df: pd.DataFrame) -> Optional[Tuple[pd.Series, pd.Series]]:
        lowest_high = df.head(1).iloc[-1]
        highest_high = None

        for _, row in df.iterrows():
            if not row['Time'] == lowest_high['Time'] and row['High'] > lowest_high['High']:
                highest_high = row

        if highest_high is None:
            return highest_high
        
        return lowest_high, highest_high

    def _get_df(self) -> pd.DataFrame:
        klines = self._client.continuous_klines(
            pair=self._pair,
            contractType='PERPETUAL',
            interval=self._timeframe,
            limit=1500
        )
        df = pd.DataFrame(klines)
        df = df.iloc[:,:5]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close']

        for col in df.columns[1:]:
            df[col] = df[col].astype(float)

        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df['RSI'] = ta.rsi(df['Close'], self._length)

        df.dropna(inplace=True)

        window_size = 5
        df['PH'] = df['High'] == df['High'].rolling(2 * window_size + 1, center=True).max()
        df['PL'] = df['Low'] == df['Low'].rolling(2 * window_size + 1, center=True).min()
        df['RSI_PH'] = df['RSI'] == df['RSI'].rolling(2 * window_size + 1, center=True).max()
        df['RSI_PL'] = df['RSI'] == df['RSI'].rolling(2 * window_size + 1, center=True).min()
        
        return df
    