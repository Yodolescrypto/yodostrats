# yodostrats
1. Installation
    
    Follow the steps from this repository, develop branch:
    https://github.com/freqtrade/freqtrade 

2. Move these strategies to your user_data/strategies/ folder

3. Backtest with the pairs of your choice (i.e BTC/USDT):

    ``bash
    docker-compose run --rm freqtrade backtesting --strategy <strat_name> --timerange <start>- --dry-run-wallet 1000 --breakdown month --enable-protections --cache none -c user_data/config.json --fee <exchange_fee> -p "BTC/USDT"
    ``

4. Dry-run for a few weeks before going live, for your wallet's sake

5. Some strategies are tested with coumpounding, this is not recommended as it increases a lot the risk and give a bigger delta between backtest - live-runs

6. Please have fun trading


Hyperopting:
To Hyperopt on custom buy parameters (as provided on hyperopt_strat.py):
  ``bash
    docker-compose run --rm freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --spaces buy --strategy hyperopt_strat --timerange 20221101- --dry-run-wallet 1000  --enable-protections  -c user_data/confi.json  --fee 0.0002 -p "BTC/USDT"
    ``


Donations welcome but in no circumstances necessary : cabyodo.eth
