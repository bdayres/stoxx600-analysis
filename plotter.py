import pandas as pd
import plotly.graph_objects as go

def plot_prices(df : pd.DataFrame, mode="close"):
    idx = df.index
    if mode not in ["close", "candle"]:
        raise AttributeError("mode must be in list ['close', 'candle']")
    if mode == "close":
        fig = go.Figure(data=[go.Scatter(
            x=idx,
            y=df["Close"],
            mode="lines",
            name="Closing prices",
            showlegend=True
        )])
        fig.update_layout(title="Closing prices")
    elif mode == "candle":
        fig = go.Figure(data=[go.Candlestick(
            x=idx,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Prices",
            showlegend=True
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, title="Candle prices")
    fig.update_yaxes(rangebreaks=[
        { 'pattern': 'day of week', 'bounds': [6, 1]}
    ])
    return fig

def plot_tops_and_bottom(fig : go.Figure, df : pd.DataFrame, tops=None, bottoms=None):
    idx = df.index

    if tops:
        fig.add_trace(go.Scatter(
            x=[idx[top[1]] for top in tops],
            y=[top[2] for top in tops], mode="markers", 
            marker=dict(color='green', size=10), 
            name='Tops'
        ))

    if bottoms:
        fig.add_trace(go.Scatter(
            x=[idx[bottom[1]] for bottom in bottoms],
            y=[bottom[2] for bottom in bottoms],
            mode="markers",
            marker=dict(color='red', size=10),
            name='Bottoms'
        ))
    return fig

def plot_sup_and_res(fig : go.Figure, df : pd.DataFrame, sup, res):
    idx = df.index
    for line in sup:
        fig.add_trace(go.Scatter(x=[idx[line[1]], idx[line[2]]], y=[line[0]]*2, mode="lines", showlegend=False, line=dict(color='green')))
    for line in res:
        fig.add_trace(go.Scatter(x=[idx[line[1]], idx[line[2]]], y=[line[0]]*2, mode="lines", showlegend=False, line=dict(color='red')))
    return fig

def plot_strategy(fig : go.Figure, decisions):
    for i, decision in enumerate(decisions):
        fig.add_vline(decision, line_color="green" if i % 2 == 0 else "red")
    return fig

def plot_sma(fig : go.Figure, data : pd.DataFrame, window : int):
    sma = data["Close"].rolling(window).mean()
    fig.add_trace(go.Scatter(x=sma.index, y=sma, mode="lines", line=dict(color="yellow"), name="SMA"))
    return fig

def plot_ema(fig : go.Figure, data : pd.DataFrame, window : int):
    ema = data["Close"].ewm(span=window, adjust=True).mean()
    fig.add_trace(go.Scatter(x=ema.index, y=ema, mode="lines", line=dict(color="pink"), name="EMA"))
    return fig