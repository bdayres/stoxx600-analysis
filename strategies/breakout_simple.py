from strategy import Strategy
import pandas as pd

class BreakoutSimple(Strategy):
    def __init__(self, data : pd.DataFrame, sup : list, res : list):
        super().__init__(data)
        self._sup = sup
        self._res = res
    
    def make_choice(self, row):
        super().make_choice(row)
        current_index = row.name
        idx = self._data.index
        if self.position == 0:
            for line in self._res:
                if len(self._data) > line[2] and idx[line[2]] == current_index:
                    self._switch_position(row)
                    return
        elif self.position == 1:
            for line in self._sup:
                if len(self._data) > line[2] and idx[line[2]] == current_index:
                    self._switch_position(row)
                    return
