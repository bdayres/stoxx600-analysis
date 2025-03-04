import pandas as pd

import strategies.strategy as stg

def simulate(data : pd.DataFrame, strategy : stg.Strategy, lookback : int):
    for i in range(lookback, len(data)):
        strategy.make_choice(data.iloc[i])
    return strategy.gain, strategy.decisions