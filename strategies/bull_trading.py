from strategy import Strategy
from flag import FlagPattern, find_flags_pennants_trendline
import pandas as pd
import technical_analysis as ta

class BullTrading(Strategy):
    def __init__(self, data : pd.DataFrame, full_data : pd.DataFrame, order : int):
        super().__init__(data)
        self._bull_flags = find_flags_pennants_trendline(full_data["Close"].to_numpy(), order)[0]
        self._current_flag = FlagPattern(0, 0)
        self._macd = ta.get_macd(full_data)
        self._max_macd = 1
        self._current_macd = 0
    
    def make_choice(self, row):
        super().make_choice(row)
        idx = self._data.index
        if self.position == 0:
            for flag in self._bull_flags:
                if idx[flag.tip_x + flag.flag_width] == row.name:
                    self._current_flag = flag
                    self._current_macd = 0
                    self._switch_position(row)
                    return
        else:
            if row.name > idx[self._current_flag.tip_x + self._current_flag.flag_width + self._current_flag.tip_x - self._current_flag.base_x]:
                self._switch_position(row)
                return
            # elif self._macd.loc[row.name]:
            #     self._current_macd += 1
            #     if self._current_macd > self._max_macd:
            #         self._switch_position(row)
            #         return
                