# yodostrats
## Introduction
This guide will help you to install and backtest Freqtrade strategies on your system. Freqtrade is a open source algorithmic trading software for cryptocurrencies.    

## Prerequisites
- Docker Compose

## Steps
1. Clone the repository from the develop branch: https://github.com/freqtrade/freqtrade
2. Copy the strategies you want to use to your user_data/strategies/ folder.

## Backtesting
You can backtest the selected strategies with the pairs of your choice. For example, to backtest the strategy **<strat_name>** for the pair **BTC/USDT**, run the following command in your terminal:
``docker-compose run --rm freqtrade backtesting --strategy <strat_name> --timerange <start>- --dry-run-wallet 1000 --breakdown month --enable-protections --cache none -c user_data/config.json --fee <exchange_fee> -p "BTC/USDT"``

It is recommended to perform a dry-run for a few weeks before going live to ensure the safety of your wallet. Note that some strategies may be tested with compounding, which increases the risk and gives a bigger delta between backtest and live-runs.

## Hyperoptimization
You can hyperopt on custom buy parameters using the following command:

``docker-compose run --rm freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy --strategy hyperopt_strat --timerange 20221101- --dry-run-wallet 1000  --enable-protections  -c user_data/confi.json  --fee 0.0002 -p "BTC/USDT"``

## Donations 
Donations are welcome but not necessary. You can donate to the address **cabyodo.eth**.

## Conclusion
Have fun trading !