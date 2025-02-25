import technical_analysis as ta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_tops_and_bottom(df : pd.DataFrame, tops=None, bottoms=None, mode="close"):
    if mode not in ["close", "candle"]:
        raise AttributeError("mode must be in list ['close', 'candle']")

    fig = None
    idx = df.index

    points = [
        go.Scatter(
            x=[idx[top[1]] for top in tops],
            y=[top[2] for top in tops], mode="markers", 
            marker=dict(color='green', size=10), 
            name='Tops'
        ), go.Scatter(
            x=[idx[bottom[1]] for bottom in bottoms],
            y=[bottom[2] for bottom in bottoms],
            mode="markers",
            marker=dict(color='red', size=10),
            name='Bottoms'
        )
    ]
    
    if mode == "close":
        fig = go.Figure(data=[go.Scatter(
            x=idx,
            y=df["Close"],
            mode="lines",
            name="Closing prices"
        )] + points)
        fig.update_layout(title="Closing prices")
    elif mode == "candle":
        fig = go.Figure(data=[go.Candlestick(
            x=idx,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Prices"
        )] + points)
        fig.update_layout(xaxis_rangeslider_visible=False, title="Candle prices")
    fig.update_yaxes(rangebreaks=[
        { 'pattern': 'day of week', 'bounds': [6, 1]}
    ])

    return fig


def main():
    data = pd.read_csv("hsbc_daily.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")

    tops, bottoms = ta.rolling_window(data["Close"].to_numpy(), 100)

    # tops, bottoms = ta.directional_change(data["Close"].to_numpy(), data["High"].to_numpy(), data["Low"].to_numpy(), 0.2)

    fig = plot_tops_and_bottom(data, tops, bottoms, mode="close")

    fig.show()


if __name__ == '__main__':
    main()