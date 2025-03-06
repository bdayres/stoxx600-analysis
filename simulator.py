import pandas as pd

import strategies.strategy as stg

def simulate(data : pd.DataFrame, strategy : stg.Strategy, lookback : int):
    for i in range(lookback, len(data)):
        strategy.make_choice(data.iloc[i])
    return strategy.gain, strategy.decisions

def compute_profit_factor(strategy : stg.Strategy):
    gains = 0.
    loss = 0.
    for ret in strategy.returns:
        if ret > 0:
            gains += ret
        else:
            loss -= ret
    print(gains, loss)
    return gains / loss