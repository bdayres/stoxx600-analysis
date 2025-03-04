from strategies.strategy import Strategy
import random
import pandas as pd

class MonkeyTrading(Strategy):
    def __init__(self, data : pd.DataFrame, probability : float):
        Strategy.__init__(self, data)
        self._probability = probability
    
    def make_choice(self, row):
        super().make_choice(row)
        if random.random() * 100 < self._probability:
            self._switch_position(row)