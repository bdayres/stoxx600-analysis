import pandas as pd
from typing import Callable
import random


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

def monkey_strat(data : pd.DataFrame, current_position : int) -> int:
    return random.randint(0, 100) > 99

def test_monkey(data : pd.DataFrame):
    gain, decisions = simulate(data, monkey_strat, 0)
    buy_and_hold = data.iloc[-1]["Close"] / data.iloc[0]["Close"]
    print(gain, buy_and_hold)

if __name__ == '__main__':
    data = pd.read_csv("hsbc_daily.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")
    test_monkey(data)