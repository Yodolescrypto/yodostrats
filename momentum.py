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
from technical.util import resample_to_interval, resampled_merge

from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal, Real  # noqa
# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.pivots_points import pivots_points
from typing import Any, Dict, List

# 13% APR 1 year backtest
class momentum(IStrategy):
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
    informative_timeframe = '15m'

    # Can this strategy go short?
    can_short: bool = True

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 0.156,
        "311": 0.109,
        "708": 0.075,
        "1454": 0
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.167

    # Trailing stoploss
    trailing_stop= True
    trailing_stop_positive=0.01
    trailing_stop_positive_offset= 0.012
    trailing_only_offset_is_reached= True

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
                "stop_duration_candles": 1
            }
        ]    

    def leverage(self, pair: str, current_time: 'datetime', current_rate: float,
                 proposed_leverage: float, max_leverage: float, side: str,
                 **kwargs) -> float:
        """
        Customize leverage for each new trade.

        :param pair: Pair that's currently analyzed
        :param current_time: datetime object, containing the current datetime
        :param current_rate: Rate, calculated based on pricing settings in exit_pricing.
        :param proposed_leverage: A leverage proposed by the bot.
        :param max_leverage: Max leverage allowed on this pair
        :param side: 'long' or 'short' - indicating the direction of the proposed trade
        :return: A leverage amount, which is between 1.0 and max_leverage.
        """
        return 20.0
    
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            entry_tag: str, **kwargs) -> float:


        return 100 #- (self.wallets.get_total_stake_amount() / 20) 
    


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
    

    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        period = 14
        smoothD = 3
        SmoothK = 3
        
        #1h DF
        dataframe1h = resample_to_interval(dataframe, 60)
        
        macd, macdsignal, macdhist = ta.MACD(dataframe1h['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        dataframe1h['macdf'] = macd
        dataframe1h['macdd'] = macdsignal
        dataframe1h['macdh'] = macdhist
        stoch_fast = ta.STOCHF(dataframe1h)
        dataframe1h['fastd'] = stoch_fast['fastd']
        dataframe1h['fastk'] = stoch_fast['fastk']
        dataframe1h['rsi'] = ta.RSI(dataframe1h, timeperiod=14)

        dataframe1h['cci'] = ta.CCI(dataframe1h)

        stochrsi  = (dataframe1h['rsi'] - dataframe1h['rsi'].rolling(period).min()) / (dataframe1h['rsi'].rolling(period).max() - dataframe1h['rsi'].rolling(period).min())
        dataframe1h['srsi_k'] = stochrsi.rolling(SmoothK).mean() * 100
        dataframe1h['srsi_d'] = dataframe1h['srsi_k'].rolling(smoothD).mean()
        
        #1m DF
        dataframe15m = resample_to_interval(dataframe, 15)
        macd, macdsignal, macdhist = ta.MACD(dataframe15m['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        dataframe15m['macdf'] = macd
        dataframe15m['macdd'] = macdsignal
        dataframe15m['macdh'] = macdhist
        stoch_fast = ta.STOCHF(dataframe15m)
        dataframe15m['fastd'] = stoch_fast['fastd']
        dataframe15m['fastk'] = stoch_fast['fastk']
        dataframe15m['rsi'] = ta.RSI(dataframe15m, timeperiod=14)
        dataframe15m['cci'] = ta.CCI(dataframe15m)

        stochrsi  = (dataframe15m['rsi'] - dataframe15m['rsi'].rolling(period).min()) / (dataframe15m['rsi'].rolling(period).max() - dataframe15m['rsi'].rolling(period).min())
        dataframe15m['srsi_k'] = stochrsi.rolling(SmoothK).mean() * 100
        dataframe15m['srsi_d'] = dataframe15m['srsi_k'].rolling(smoothD).mean()

        #1m DF
        
        macd, macdsignal, macdhist = ta.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        dataframe['macdf'] = macd
        dataframe['macdd'] = macdsignal
        dataframe['macdh'] = macdhist
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['cci'] = ta.CCI(dataframe)

        stochrsi  = (dataframe['rsi'] - dataframe['rsi'].rolling(period).min()) / (dataframe['rsi'].rolling(period).max() - dataframe['rsi'].rolling(period).min())
        dataframe['srsi_k'] = stochrsi.rolling(SmoothK).mean() * 100
        dataframe['srsi_d'] = dataframe['srsi_k'].rolling(smoothD).mean()
        
        #Resampling
        dataframe = resampled_merge(dataframe, dataframe15m, fill_na=True)
        dataframe = resampled_merge(dataframe, dataframe1h, fill_na=True)

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
                (dataframe["resample_15_macdh"] < 0) &
                (dataframe["resample_15_cci"] > 100) &
                (dataframe["cci"] > 100) &
                (dataframe["macdh"].rolling(15).sum() > 0) & # Checking 15 last exercices before entering position to verify signal
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_long'] = 0
        
        dataframe.loc[
            (
                (dataframe["resample_15_macdh"] > -100) &
                (dataframe["resample_15_cci"] < -100) &
                (dataframe["cci"] > -100) &
                (dataframe["macdh"].rolling(15).sum() < 0) & # Checking 15 last exercices before entering position to verify signal
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (                   
                (dataframe['volume'] == 0)  # Make sure Volume is not 0
            ),
            'exit_long'] = 0
        # Uncomment to use shorts (Only used in futures/margin mode. Check the documentation for more info)
        
        dataframe.loc[
            (
                (dataframe['volume'] == 0)  # Make sure Volume is not 0
            ),
            'exit_short'] = 1
        
        return dataframe