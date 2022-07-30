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
class limit(IStrategy):
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
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 10

    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -1

    # Trailing stoploss
    trailing_stop= False
    trailing_stop_positive=0.02
    trailing_stop_positive_offset= 0.1
    trailing_only_offset_is_reached= False
    
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
    
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            entry_tag: str, **kwargs) -> float:


        return 50 #- (self.wallets.get_total_stake_amount() / 20) 
    


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
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.informative_timeframe) for pair in pairs]
        return informative_pairs
    
    @informative('30m')
    @informative('1h')
    @informative('4h')
    @informative('1d')
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        period = 14
        smoothD = 3
        SmoothK = 3
        
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        # values [0, 100]

        dataframe['doji_short'] = ta.CDLEVENINGDOJISTAR(dataframe)  
        dataframe['doji_long'] = ta.CDLMORNINGSTAR(dataframe) 
        dataframe['gravestone'] = ta.CDLGRAVESTONEDOJI(dataframe)
        dataframe['dragonfly'] = ta.CDLDRAGONFLYDOJI(dataframe)

        macd, macdsignal, macdhist = ta.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        dataframe['macd'] = macd
        dataframe['macds'] = macdsignal
        dataframe['macdh'] = macdhist
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['cci'] = ta.CCI(dataframe)

        stochrsi  = (dataframe['rsi'] - dataframe['rsi'].rolling(period).min()) / (dataframe['rsi'].rolling(period).max() - dataframe['rsi'].rolling(period).min())
        dataframe['srsi_k'] = stochrsi.rolling(SmoothK).mean() * 100
        dataframe['srsi_d'] = dataframe['srsi_k'].rolling(smoothD).mean()
        self.custom_info['lclose'] = dataframe['close']
        self.custom_info['lopen'] = dataframe['open']
        
        return dataframe



    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        
        dataframe.loc[
            (
                # LONG 
                (dataframe['macds_1d'] < dataframe['macd_1d']) &
                (dataframe['macds_4h'] > dataframe['macd_4h']) & 
                (dataframe['macds_1h'] > dataframe['macd_1h']) &     
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_long', 'enter_tag']] = (1, 'macd')
        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (            
                (dataframe['macds_1d'] > dataframe['macd_1d']) &  
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'exit_long'] = 1
        
        return dataframe