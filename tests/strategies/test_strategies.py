from simulator import simulate, compute_profit_factor
import technical_analysis.points as ta
import pandas as pd

from strategies.monkey_trading import MonkeyTrading
from strategies.breakout_simple import BreakoutSimple
from strategies.laplace_demon import LaplaceTrading
from strategies.bull_trading import BullTrading
from strategies.forest_signal import ForestSignal
import plotter as pt

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
    pt.plot_strategy_returns(strategy.returns).show()

    print(gain)

def test_god_trading(data : pd.DataFrame):
    # gain, decisions = simulate(data, make_god_trading(data), 1)
    tops, bottoms = ta.rolling_window(data["Close"].to_numpy(), 1)
    strat = LaplaceTrading(pd.DataFrame().reindex_like(data), tops, bottoms)
    gain, _ = simulate(data, strat, 0)
    print(compute_profit_factor(strat))
    print(gain)

def test_bull_trading(data : pd.DataFrame):
    strat = BullTrading(pd.DataFrame().reindex_like(data), data, 20, 20)
    gain, decisions = simulate(data, strat, 0)
    fig = pt.plot_prices(data)
    fig = pt.plot_strategy(fig, decisions)
    print(gain)
    fig.show()

def test_forest(data : pd.DataFrame):
    strat = ForestSignal(data.head(365 * 15).copy())
    gain, decisions = simulate(data, strat, 365 * 15)
    fig = pt.plot_prices(data)
    fig = pt.plot_strategy(fig, decisions)
    print(gain)
    fig.show()