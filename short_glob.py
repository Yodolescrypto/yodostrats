# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from datetime import datetime, timedelta, timezone
from freqtrade.exchange import timeframe_to_minutes
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, merge_informative_pair, informative)

from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal, Real  # noqa
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.pivots_points import pivots_points
from typing import Any, Dict, List


class shortglob(IStrategy):

    INTERFACE_VERSION = 3


    timeframe = '1m'
    informative_timeframe = '1h'
    can_short: bool = True

    minimal_roi = {
        "0": 0
    }


    stoploss = -1

    # Trailing stoploss
    trailing_stop= False
    trailing_stop_positive=0.01
    trailing_stop_positive_offset= 0.012
    trailing_only_offset_is_reached= False

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
    startup_candle_count: int = 50


    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }
    
    @property
    def plot_config(self):
        return {
            # Main plot indicators (Moving averages, ...)
            'main_plot': {
                "MACD": {
                    'fastd': {'color': 'blue'},
                    'fastk': {'color': 'orange'},
                },
                "RSI": {
                    'rsi': {'color': 'red'},
                },
                "Pivot": {
                    'pivot': {'color': 'black'},
                },
                'SMA': {
                    'sma15': {'color': 'white'},
                    'sma50': {'color': 'yellow'},
                },
            },
            'subplots': {

            }
        }
    @property
    def protections(self):
        return  [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 60
            }
        ]    

    def leverage(self, pair: str, current_time: 'datetime', current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:

        return 20.0
    
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            entry_tag: str, **kwargs) -> float:


        return self.wallets.get_total_stake_amount() / 10
    


    def informative_pairs(self):

        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.informative_timeframe) for pair in pairs]
        return informative_pairs
    

    
    @informative('1h')
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        pp = pivots_points(dataframe)
        dataframe['pivot'] = pp["r1"]

        dataframe['doji_short'] = ta.CDLEVENINGDOJISTAR(dataframe)  
        dataframe['doji_long'] = ta.CDLMORNINGSTAR(dataframe) 

        # Stochastic Fast
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']

       
        # # SMA - Simple Moving Average
        dataframe['sma15'] = ta.SMA(dataframe, timeperiod=15)
        dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)

        return dataframe



    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe.loc[
            (
                # LONG 
                (dataframe["fastk_1h"] > 80) &
                (dataframe["fastd_1h"] > 80) &
                (qtpylib.crossed_below(dataframe['fastk_1h'], dataframe['fastd_1h'])) &
                (dataframe['close'] > dataframe['sma15_1h']) &  # MA above close
                (dataframe['close'] > dataframe['sma50_1h']) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_long'] = 0

        dataframe.loc[
            (
                # SHORT
                # GUARDS  
                (dataframe["fastk_1h"] < 20) &
                (dataframe["fastd_1h"] < 20) &
                (dataframe['close'] < dataframe['sma15_1h']) &  
                (dataframe['close'] < dataframe['sma50_1h']) &

                # KICK
                (qtpylib.crossed_below(dataframe['fastk_1h'], dataframe['fastd_1h'])) &

                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['fastk_1h'], dataframe['fastd_1h']))
            ),
            'exit_short'] = 1

        return dataframe