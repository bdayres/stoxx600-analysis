import pandas as pd
from typing import Callable
import random
import technical_analysis as ta


def simulate(data : pd.DataFrame, strategy : Callable[[pd.DataFrame, int], int], lookback):
# 0 : Rien
# 1 : Acheter
    position = 0
    position_price = 0
    total_gain = 1
    decisions = []
    idx = data.index
    for i in range(lookback, len(data)):
        change = strategy(data[:i], position)
        if position == 0 and change:
            position = 1
            position_price = data.iloc[i]["Close"]
            decisions.append(idx[i])
        elif position == 1 and change:
            position = 0
            total_gain *= data.iloc[i]["Close"] / position_price
            decisions.append(idx[i])
    return total_gain, decisions

def make_monkey(probability):
    def monkey_strat(data : pd.DataFrame, current_position : int) -> int:
        return random.randint(0, 100) > probability
    return monkey_strat

def make_breakout_oracle(sup, res):
    def breakout_oracle(data : pd.DataFrame, current_position : int) -> int:
        current_index = data.index[-1]
        if current_position == 0:
            for line in res:
                if len(data) > line[2] and data.index[line[2]] == current_index:
                    return True
        elif current_position == 1:
            for line in sup:
                if len(data) > line[2] and data.index[line[2]] == current_index:
                    return True
        return False
    return breakout_oracle

def test_monkey(data : pd.DataFrame):
    gain, decisions = simulate(data, make_monkey(99), 0)
    buy_and_hold = data.iloc[-1]["Close"] / data.iloc[0]["Close"]
    print(gain, buy_and_hold)

def test_breakout_oracle(data : pd.DataFrame):
    tops, bottoms = ta.rolling_window(data["Close"].to_numpy(), 10)
    sup = ta.naive_sup_res(bottoms, 0.02, "bottoms", 2, 0)
    res = ta.naive_sup_res(tops, 0.02, "tops", 2, 0)
    gain, decisions = simulate(data, make_breakout_oracle(sup, res), 1)
    print(gain)

if __name__ == '__main__':
    data = pd.read_csv("hsbc_daily.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")
    # test_monkey(data)
    test_breakout_oracle(data)