# Mind Strategy V1

### The following are the indicators used in the strategy:

 * Bollinger Bands (BB): Bollinger Bands are a volatility indicator that consists of three lines: a middle band, which is a simple moving average (SMA), and an upper and lower band that are drawn above and below the middle band, respectively, by a certain number of standard deviations. In this strategy, the middle band and upper and lower bands are used to identify potential entry points for long and short positions.
 * Moving Average Convergence Divergence (MACD): The MACD indicator is a trend-following momentum indicator that shows the relationship between two exponential moving averages (EMAs) of a security's price. In this strategy, the MACD histogram and signal line are used to confirm potential entry points for long and short positions.
 * Stochastic Fast (STOCHF): The Stochastic Fast indicator is a momentum indicator that compares a security's closing price to its price range over a given time period. In this strategy, the fast stochastic %K and %D lines are used to confirm potential entry points for long and short positions.
 * Relative Strength Index (RSI): The RSI is a momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions. In this strategy, the RSI is used to confirm potential entry points for long and short positions.
 * Average Directional Index (ADX): The ADX is a trend strength indicator that measures the strength of a trend, regardless of its direction. In this strategy, the ADX is used to confirm potential entry points for long and short positions.

### Based on the above indicators and parameters, the strategy identifies potential entry points for long and short positions when the following conditions are met:

 * Reversal incoming trigger based on Bollinger Bands: The price crosses above or below the lower, middle, or upper Bollinger Band, and the Bollinger Bands' rolling averages confirm the reversal.
 * Momentum Analysis: The RSI is above 30 and has crossed above 30 in the previous period, and the fast stochastic %K and %D lines are moving in the same direction. The MACD histogram is declining over a period of 10 days.
 * Volume: The volume is above zero.

The TP/SL zone is to be determined with the traded pair, alongside with the leverage tier. 

Below a backtest on BTCUSDT for 400days:
```
| Metric                      | Value                 |
|-----------------------------+-----------------------|
| Backtesting from            | 2022-02-20 00:00:00   |
| Backtesting to              | 2023-03-05 00:00:00   |
| Max open trades             | 1                     |
| Total/Daily Avg Trades      | 19 / 0.05             |
| Starting balance            | 1000 USDT             |
| Final balance               | 1379.575 USDT         |
| Absolute profit             | 379.575 USDT          |
| Total profit %              | 37.96%                |
| CAGR %                      | 36.44%                |
| Sortino                     | 18.74                 |
| Sharpe                      | 0.20                  |
| Calmar                      | 26.03                 |
| Profit factor               | 1.97                  |
| Expectancy                  | 0.67                  |
| Trades per day              | 0.05                  |
| Avg. daily profit %         | 0.10%                 |
| Avg. stake amount           | 98.567 USDT           |
| Total trade volume          | 1872.771 USDT         |
| Long / Short                | 5 / 14                |
| Total profit Long %         | 16.08%                |
| Total profit Short %        | 21.88%                |
| Absolute profit Long        | 160.788 USDT          |
| Absolute profit Short       | 218.786 USDT          |
| Best Pair                   | BTC/USDT:USDT 381.44% |
| Worst Pair                  | BTC/USDT:USDT 381.44% |
| Best trade                  | BTC/USDT:USDT 286.97% |
| Worst trade                 | BTC/USDT:USDT -32.58% |
| Best day                    | 284.903 USDT          |
| Worst day                   | -32.202 USDT          |
| Days win/draw/lose          | 6 / 343 / 13          |
| Avg. Duration Winners       | 13 days, 8:47:00      |
| Avg. Duration Loser         | 5 days, 3:30:00       |
| Rejected Entry signals      | 0                     |
| Entry/Exit Timeouts         | 0 / 0                 |
| Min balance                 | 900.682 USDT          |
| Max balance                 | 1441.977 USDT         |
| Max % of account underwater | 7.68%                 |
| Absolute Drawdown (Account) | 7.37%                 |
| Absolute Drawdown           | 88.317 USDT           |
| Drawdown high               | 198.408 USDT          |
| Drawdown low                | 110.092 USDT          |
| Drawdown Start              | 2022-09-09 04:02:00   |
| Drawdown End                | 2022-10-23 21:23:00   |
| Market change               | -53.00%               |
```