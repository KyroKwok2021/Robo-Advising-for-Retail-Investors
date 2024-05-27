import numpy as np
import pandas as pd
import get_vix_cobe
from scipy.signal import argrelextrema


class Signal_Generator:

    def __init__(self, df_raw, para_dict):
        self.df_raw = df_raw
        
        self.window_sma_reverse = para_dict.get('window_sma_reverse')
        self.window_z_reverse = para_dict.get('window_z_reverse')
        self.upper_threshold_reverse = para_dict.get('upper_threshold_reverse')
        self.lower_threshold_reverse = para_dict.get('lower_threshold_reverse')
        self.holding_n_reverse = para_dict.get('holding_n_reverse')

        self.window_sma_minima = para_dict.get('window_sma_minima')
        self.window_z_minima = para_dict.get('window_z_minima')
        self.order_minima = para_dict.get('order_minima')
        self.holding_n_minima =  para_dict.get('holding_n_minima')
    
        self.spread = (self.df_raw['VIXF'] - self.df_raw['VIX']).rename('Spread')
        self.rolling_z_reverse = (self.__smoothed_rolling_z(self.spread, self.window_sma_reverse, self.window_z_reverse)).rename('Rolling Z Reverse')
        self.rolling_z_minima = (self.__smoothed_rolling_z(self.spread, self.window_sma_minima, self.window_z_minima)).rename('Rolling Z Minima')

        self.get_signals()
        self.df_info = pd.concat([
            self.df_raw['SPX'], self.df_raw['VIXF'], self.df_raw['VIX'], self.spread, 
            self.rolling_z_reverse, self.signals_reverse,
            self.rolling_z_minima, self.signals_minima,
        ], axis=1)

    def __smoothed_rolling_z(self, raw, window_sma: int, window_z: int):
        smoothed = raw.rolling(window_sma).mean()
        rolling_z = (smoothed - smoothed.rolling(window_z).mean()) / smoothed.rolling(window_z).std()
        return rolling_z


    def __get_extrema(self, ds:pd.Series, order: int = 5) -> pd.Series:
        is_maxima_num_index = argrelextrema(ds.to_numpy(), np.greater, axis=0, order=order)[0]
        is_minima_num_index = argrelextrema(ds.to_numpy(), np.less, axis=0, order=order)[0]
        local_max_index_ls = []
        local_min_index_ls = []
        for i in is_maxima_num_index:
            if i > order and i < len(ds) - order:
                local_max_index_ls.append(ds.iloc[i : i + 1].index)
        for i in is_minima_num_index:
            if i > order and i < len(ds) - order:
                local_min_index_ls.append(ds.iloc[i : i + 1].index)
        local_max_index_arr = np.array(local_max_index_ls).reshape(-1)
        local_min_index_arr = np.array(local_min_index_ls).reshape(-1)

        ds_zero = pd.Series(0, index=ds.index).rename(f"{ds.name} extrema (order{order})")
        ds_zero.loc[local_max_index_arr] = -1
        ds_zero.loc[local_min_index_arr] = 1
        return ds_zero


    def __getSignals_Extrema(self, ds, order: int = 1) -> pd.Series:
        extrema = self.__get_extrema(ds, order)
        return extrema.shift(order).rename(f'Signal Extrema')
    

    def __lambda_reverse_threshold(self, x, long_reverse_threshold: float = 0, short__reverse_threshold: float = 0) -> int:
        if x < long_reverse_threshold:
            return 1
        elif x > short__reverse_threshold:
            return -1
        else:
            return 0
        

    def __getSignals_ReverseThreshold(self, ds, long_reverse_threshold: float = 0, short_reverse_threshold: float = 0
    ) -> pd.Series:
        """
        指標觸及Threshold, 看回調, vice versa
        eg: RSI突破90, 看空
        """
        ds = pd.Series(ds, index=self.df_raw.index)
        signal = ds.apply(
            lambda x: self.__lambda_reverse_threshold(
                x, long_reverse_threshold, short_reverse_threshold
            )
        )
        return signal.rename('Signal Reverse Threshold')
    

    def __extend_signals_holding(self, signals, n):
      signals = list(signals)
      length = len(signals)
      signals_extend_n = signals[:]  # Create a copy of the original signal to manipulate
      i = 0
      while i < length:
          if signals[i] != 0:
              # Initialize a counter to keep track of how many extensions we've done
              extend_count = 0
              while extend_count < n-1:
                  # Check if we are still within bounds and the next element is zero
                  if i + extend_count + 1 < length and signals[i + extend_count + 1] == 0:
                      signals_extend_n[i + extend_count + 1] = signals[i]
                      extend_count += 1
                  else:
                      break
          i += 1
      return pd.Series(signals_extend_n, index=self.df_raw.index)


    def get_signals(self):
        signals_reverse = self.__getSignals_ReverseThreshold(self.rolling_z_reverse, self.lower_threshold_reverse, self.upper_threshold_reverse)
        signals_reverse = self.__extend_signals_holding(signals_reverse, self.holding_n_reverse)
        self.signals_reverse = signals_reverse.rename('Signal Reverse')
        
        signals_minima = self.__getSignals_Extrema(self.rolling_z_minima, self.order_minima)
        signals_minima = self.__extend_signals_holding(signals_minima, self.holding_n_minima)
        self.signals_minima = signals_minima.rename('Signal Minima')


def run():
    df_raw = get_vix_cobe.run()
    para_dict = {
        'window_sma_reverse': 26,
        'window_z_reverse': 45,
        'upper_threshold_reverse': 2.3,
        'lower_threshold_reverse': -1.9,
        'holding_n_reverse': 25,

        'window_sma_minima': 16,
        'window_z_minima': 20,
        'order_minima': 4,
        'holding_n_minima': 28 
    }

    singal_generator = Signal_Generator(df_raw, para_dict)
    return singal_generator

if __name__ == '__main__':
    Signal_Generator = run()