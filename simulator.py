import pandas as pd

import technical_analysis as ta
import strategy as stg
from strategies.monkey_trading import MonkeyTrading
from strategies.breakout_simple import BreakoutSimple
from strategies.laplace_demon import LaplaceTrading
from strategies.bull_trading import BullTrading
import plotter as pt

def simulate(data : pd.DataFrame, strategy : stg.Strategy, lookback : int):
    for i in range(lookback, len(data)):
        strategy.make_choice(data.iloc[i])
    return strategy.gain, strategy.decisions

def test_monkey(data : pd.DataFrame):
    strategy = MonkeyTrading(pd.DataFrame().reindex_like(data), 1.)
    gain, decisions = simulate(data, strategy, 0)
    buy_and_hold = data.iloc[-1]["Close"] / data.iloc[0]["Close"]
    print(gain, buy_and_hold)

def test_breakout_oracle(data : pd.DataFrame):
    tops, bottoms = ta.rolling_window(data["Close"].to_numpy(), 10)
    sup = ta.naive_sup_res(bottoms, 0.02, "bottoms", 2, 0)
    res = ta.naive_sup_res(tops, 0.02, "tops", 2, 0)
    strategy = BreakoutSimple(pd.DataFrame().reindex_like(data), sup, res)
    gain, decisions = simulate(data, strategy, 1)
    print(gain)

def test_god_trading(data : pd.DataFrame):
    # gain, decisions = simulate(data, make_god_trading(data), 1)
    tops, bottoms = ta.rolling_window(data["Close"].to_numpy(), 1)
    strat = LaplaceTrading(pd.DataFrame().reindex_like(data), tops, bottoms)
    gain, _ = simulate(data, strat, 0)
    print(gain)

def test_bull_trading(data : pd.DataFrame):
    strat = BullTrading(pd.DataFrame().reindex_like(data), data, 20)
    gain, decisions = simulate(data, strat, 0)
    fig = pt.plot_prices(data)
    fig = pt.plot_strategy(fig, decisions)
    print(gain)
    fig.show()

if __name__ == '__main__':
    data = pd.read_csv("hsbc_daily.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")
    # test_monkey(data)
    # test_breakout_oracle(data)
    # test_god_trading(data)
    test_bull_trading(data)