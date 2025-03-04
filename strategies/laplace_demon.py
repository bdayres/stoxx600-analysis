from strategies.strategy import Strategy
import pandas as pd

class LaplaceTrading(Strategy):
    def __init__(self, data : pd.DataFrame, tops : list, bottoms : list):
        super().__init__(data)
        self._tops = tops
        self._bottoms = bottoms
        self._top_idx = 0
        self._bottom_idx = 0

    def make_choice(self, row):
        super().make_choice(row)
        idx = self._data.index
        current_index = row.name
        if self.position == 0:
            for i in range(self._bottom_idx, len(self._bottoms)):
                bottom = self._bottoms[i]
                if len(self._data) > bottom[1] and idx[bottom[1]] == current_index:
                    self._switch_position(row)
                    self._bottom_idx = i
                    return
        elif self.position == 1:
            for i in range(self._top_idx, len(self._tops)):
                top = self._tops[i]
                if len(self._data) > top[1] and idx[top[1]] == current_index:
                    self._switch_position(row)
                    self._top_idx = i
                    return