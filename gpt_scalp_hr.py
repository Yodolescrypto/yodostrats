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
from technical.util import resample_to_interval, resampled_merge

from freqtrade.persistence import Trade
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal, Real  # noqa
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.pivots_points import pivots_points
from typing import Any, Dict, List, Optional

# 13% APR 1 year backtest
class gpt_scalp_hr(IStrategy):
    custom_info = {}
    """
    This is a strategy template to get you started.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy.
    timeframe = '1m'

    # Can this strategy go short?
    can_short: bool = True

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 1

    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.2

    # Trailing stoploss
    trailing_stop= True
    trailing_stop_positive=0.01
    trailing_stop_positive_offset= 0.2
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
        'entry': 'market',
        'exit': 'market',
        'stoploss': 'market',
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
            # Main plot indicators (Moving averages, ...)
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
                "stop_duration_candles": 1
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
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """

        return [("ETH/USDT:USDT", "5m")]
    
    @informative('5m')
    @informative('15m')
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        # Add the bullish engulfing pattern indicator
        dataframe['bullish_engulfing'] = ta.CDLENGULFING(dataframe)
        # Add the bearish engulfing pattern indicator
        dataframe['bearish_engulfing'] = ta.CDLENGULFING(dataframe)
        
        dataframe['rsi'] = ta.RSI(dataframe)

        return dataframe



    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 5m #
        dataframe.loc[
            (
                (dataframe['bullish_engulfing_5m'] == 100) &
                (dataframe['rsi_5m'] > 30) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_long', 'enter_tag']] = (1, 'openai_told_me_to_enter')

        dataframe.loc[
            (            
                (dataframe['bearish_engulfing_5m'] == -100) &
                (dataframe['rsi_5m'] < 70) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_short', 'enter_tag']] = (1, "yodo_knows_better_en")
        #15m
        dataframe.loc[
            (
                (dataframe['bullish_engulfing_15m'] == 100) &
                (dataframe['rsi_15m'] > 30) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_long', 'enter_tag']] = (1, 'openai_told_me_to_enter_15m')

        dataframe.loc[
            (            
                (dataframe['bearish_engulfing_15m'] == -100) &
                (dataframe['rsi_15m'] < 70) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_short', 'enter_tag']] = (1, "yodo_knows_better_en_15m")
        return dataframe


    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (            

                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['exit_long', 'exit_tag']] = (0, "open_ai_told_me_to_exit")
        
        dataframe.loc[
            (

                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['exit_short', 'exit_tag']] = (0, 'yodo_knows_better_ex')
        return dataframe
