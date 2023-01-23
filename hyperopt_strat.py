import numpy as np  
import pandas as pd  
from pandas import DataFrame
from datetime import datetime, timedelta, timezone
from freqtrade.exchange import timeframe_to_minutes
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, merge_informative_pair, informative)
from technical.util import resample_to_interval, resampled_merge
from freqtrade.persistence import Trade
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal, Real  # noqa
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.pivots_points import pivots_points
from typing import Any, Dict, List, Optional


class hyperopt_strat(IStrategy):
    custom_info = {}
    INTERFACE_VERSION = 3

    timeframe = '1m'

    can_short: bool = True

    minimal_roi = {
        "0": 1

    }
    
    # HO parameters
    buy_rsi5 = IntParameter(20, 40, default=30, space="buy")
    buy_rsi15 = IntParameter(20, 40, default=30, space="buy")

    buy_rsi5_short = IntParameter(60, 80, default=70, space="buy")
    buy_rsi15_short = IntParameter(60, 80, default=70, space="buy")

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.15

    # Trailing stoploss
    trailing_stop= True
    trailing_stop_positive=0.02
    trailing_stop_positive_offset= 0.10
    trailing_only_offset_is_reached= True
    
    custom_price_max_distance_ratio = 1

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
        
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 50


    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'limit',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }
    
    @property
    def plot_config(self):
        return {
            'main_plot': {

            },
            'subplots': {
                "MACD": {
                    'macdh': {'color': 'blue'},
                    'macdd': {'color': 'cyan'},
                    'macdf': {'color': 'purple'},
                },
                "CCI": {
                    'cci': {'color': 'red'},

                },
            }
        } 

    @property
    def protections(self):
        return  [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 5
            }
        ]       
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            entry_tag: str, **kwargs) -> float:


        return (100)
    
    def leverage(self, pair: str, current_time: 'datetime', current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:

        return 10

    def informative_pairs(self):

        return [("ETH/USDT:USDT", "5m")]
    
    @informative('5m')
    @informative('15m')
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe



    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 5m #
        dataframe.loc[
            (
                (dataframe['rsi_5m'] < self.buy_rsi5.value) &
                (dataframe['rsi_15m'] < self.buy_rsi15.value) &
                (dataframe['volume'] > 0) 
            ),
            ['enter_long', 'enter_tag']] = (1, 'bullish_5m')

        dataframe.loc[
            (
                (dataframe['rsi_5m'] > self.buy_rsi5_short.value) &
                (dataframe['rsi_15m'] > self.buy_rsi15_short.value) &
                (dataframe['volume'] > 0) 
            ),
            ['enter_short', 'enter_tag']] = (1, "bearish_5m")
        
        return dataframe


    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (            

                (dataframe['volume'] > 0)  
            ),
            ['exit_long', 'exit_tag']] = (0, "open_ai_told_me_to_exit")
        
        dataframe.loc[
            (

                (dataframe['volume'] > 0) 
            ),
            ['exit_short', 'exit_tag']] = (0, 'yodo_knows_better_ex')
        return dataframe