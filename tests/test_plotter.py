import plotter as pt
import pandas as pd
from technical_analysis.indicators import atr

def test_indicators(data : pd.DataFrame):
    data = atr(data, 10)
    fig = pt.plot_prices(data)
    fig = pt.plot_indicators(fig, data, ["ATR"])
    fig.show()