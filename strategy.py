import pandas as pd
import random
import technical_analysis as ta

class Strategy:
    def __init__(self, data : pd.DataFrame):
        self._data = data
        self._current_price = 0
        self.decisions = []
        self.position = 0
        self.gain = 1
    
    def _switch_position(self, row : pd.Series):
        if self.position == 0:
            self.position = 1
            self._current_price = row["Close"]
        else:
            self.position = 0
            self.gain *= row["Close"] / self._current_price
        self.decisions.append(row.name)

    def make_choice(self, row : pd.Series) -> int:
        self._data.loc[row.name] = row

class MonkeyTrading(Strategy):
    def __init__(self, data : pd.DataFrame, probability : float):
        Strategy.__init__(self, data)
        self._probability = probability
    
    def make_choice(self, row):
        super().make_choice(row)
        if random.random() * 100 < self._probability:
            self._switch_position(row)

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

class LaplaceTrading(Strategy):
    def __init__(self, data : pd.DataFrame, tops : list, bottoms : list):
        super().__init__(data)
        self._tops = tops
        self._bottoms = bottoms        

    def make_choice(self, row):
        super().make_choice(row)
        idx = self._data.index
        current_index = row.name
        if self.position == 0:
            for bottom in self._bottoms:
                if len(self._data) > bottom[1] and idx[bottom[1]] == current_index:
                    self._switch_position(row)
        elif self.position == 1:
            for top in self._tops:
                if len(self._data) > top[1] and idx[top[1]] == current_index:
                    self._switch_position(row)