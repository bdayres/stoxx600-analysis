from typing import Optional
import pandas as pd
import numpy as np

import strategies.strategy as stg
from streamlit.delta_generator import DeltaGenerator

def simulate(data : pd.DataFrame, strategy : stg.Strategy, lookback : int, progress_bar : Optional[DeltaGenerator] = None):
    for i in range(lookback, len(data)):
        strategy.make_choice(data.iloc[i])
        progress_bar.progress(i / len(data), "Simulating")
    progress_bar.progress(1., "Simulation Over")
    return strategy.gain, strategy.decisions

def compute_profit_factor(strategy : stg.Strategy):
    gains = 0.
    loss = 0.
    for ret in strategy.returns:
        if ret > 0:
            gains += ret
        else:
            loss -= ret
    if loss != 0:
        return gains / loss
    return 10e3