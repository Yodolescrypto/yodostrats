# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from datetime import datetime, timedelta, timezone
from freqtrade.exchange import timeframe_to_minutes
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, merge_informative_pair)

from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal, Real  # noqa
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.pivots_points import pivots_points
from typing import Any, Dict, List

# 13% APR 1 year backtest
class degen(IStrategy):
    custom_info = {}
    
    class HyperOpt:
        # Define a custom stoploss space.
        def stoploss_space():
            return [SKDecimal(-0.2, -0.1, decimals=3, name='stoploss')]

        # Define custom ROI space
        
        def roi_space() -> List['Dimension']:
            return [
                Integer(0, 0.01, name='roi_t1'),
                Integer(0, 30, name='roi_t2'),
                Integer(30, 60 , name='roi_t3'),
                Integer(60, 100 , name='roi_t4'),
                SKDecimal(0.1, 1, decimals=3, name='roi_p1'),
                SKDecimal(0.1, 0.5, decimals=3, name='roi_p2'),
                SKDecimal(0.05, 0.1, decimals=3, name='roi_p3'),
                SKDecimal(0.0, 0.03, decimals=3, name='roi_p4'),
            ]
           
        def trailing_space() -> List['Dimension']:
            return [
                Categorical([True, False], name='trailing_stop'),
                SKDecimal(0.02, 0.09, decimals=3, name='trailing_stop_positive'),
                SKDecimal(0.02, 0.1, decimals=3, name='trailing_stop_positive_offset_p1'),
                Categorical([True, False] , name='trailing_only_offset_is_reached'),

            ]
    
    custom_info = 0

    INTERFACE_VERSION = 3

    timeframe = '1m'
    informative_timeframe = '1m'

    can_short: bool = True

    minimal_roi = {
        "0": 0.28,
        "88": 0.264,
        "163": 0,
    }

    # Real values in JSON, you'll have to hyperopt it, would be too easy :)
    stoploss = -0.338

    trailing_stop= False
    trailing_stop_positive=0.02
    trailing_stop_positive_offset= 0.03
    trailing_only_offset_is_reached= False

    process_only_new_candles = True

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
    startup_candle_count: int = 50

    order_types = {
        'entry': 'market',
        'exit': 'market',
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

            'main_plot': {

            }
            },
            'subplots': {

            }
        }
    
    @property
    def protections(self):
        return  [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 1
            }
        ]    
    
    def leverage(self, pair: str, current_time: 'datetime', current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:

        return self.custom_info

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            entry_tag: str, **kwargs) -> float:

        if entry_tag == "1_short":
            self.custom_info = 20
            return (self.wallets.get_total_stake_amount() / 4 )
        if entry_tag == "1_long":
            self.custom_info = 20
            return (self.wallets.get_total_stake_amount() / 4 )


    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        pp = pivots_points(dataframe)
        dataframe['pivot'] = pp["r1"]


        # Stochastic Fast
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']

        return dataframe


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe.loc[
            (
                # SHORT 
                (dataframe["close"] < 31000) &
                (dataframe["close"] > 29600) &
                (dataframe["fastd"] > 80) &
                (dataframe["fastk"] > 80) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_short', 'enter_tag']] = (1, "1_short")
        
        dataframe.loc[
            (
                # LONG 
                (dataframe["close"] > 28000) &
                (dataframe["close"] < 29600) &
                (dataframe["fastd"] < 20) &
                (dataframe["fastk"] < 20) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_long', 'enter_tag']] = (1, "1_long") 

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                (dataframe['volume'] == 0)  # Make sure Volume is not 0
            ),
            'exit_long'] = 0

        return dataframe
