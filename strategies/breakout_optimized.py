from strategies.strategy import Strategy
import pandas as pd

class BreakoutOptimized(Strategy):
    def __init__(self, data : pd.DataFrame, sup : list, res : list, sigma : float):
        super().__init__(data)
        self._sup = sup
        self._res = res
        self._max_high = 0
        self._sigma = sigma
    
    def make_choice(self, row):
        super().make_choice(row)
        current_index = row.name
        idx = self._data.index
        if self.position == 0:
            for line in self._res:
                if len(self._data) > line[2] and idx[line[2]] == current_index:
                    self._switch_position(row)
                    self._max_high = row["High"]
                    return
        elif self.position == 1:
            if row["Close"] < self._max_high - self._max_high * self._sigma:
                self._switch_position(row)
                return
            self._max_high = max(self._max_high, row["High"])