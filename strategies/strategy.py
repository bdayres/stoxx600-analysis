import pandas as pd

class Strategy:
    def __init__(self, data : pd.DataFrame):
        self._data = data
        self._current_price = 0
        self.decisions = []
        self.position = 0
        self.gain = 1
        self.returns = []
    
    def _switch_position(self, row : pd.Series):
        if self.position == 0:
            self.position = 1
            self._current_price = row["Close"]
        else:
            self.position = 0
            self.gain *= row["Close"] / self._current_price
            self.returns.append((row["Close"] / self._current_price) - 1)
        self.decisions.append(row.name)

    def make_choice(self, row : pd.Series) -> int:
        self._data.loc[row.name] = row