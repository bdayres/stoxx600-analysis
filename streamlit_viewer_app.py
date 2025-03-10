import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.session import Session

import pandas as pd
import plotly.graph_objects as go

import plotter as pt
import technical_analysis.points as ta

from simulator import simulate, compute_profit_factor

from strategies.breakout_simple import BreakoutSimple
from strategies.monkey_trading import MonkeyTrading
from strategies.laplace_demon import LaplaceTrading
from strategies.breakout_optimized import BreakoutOptimized
from strategies.bull_trading import BullTrading
from strategies.forest_signal import ForestSignal

DIST_MAP = {
    1: "Euclidian Distance",
    2: "Manhattan Distance",
    3: "Vertical Distance"
}

SCALE_MAP = {
    "linear": "Linear",
    "log": "Logarithmic"
}

STYLE_MAP = {
    "close": "Closing Prices",
    "candle": "Candle Lights"
}

POINT_MAP = {
    "rw": "Rolling Window",
    "dc": "Directional Change",
    "pips": "Perceptually Important Points"
}

PRICE_MAP = {
    "close": "Closing",
    "hl": "High and Low"
}

STRATEGY_MAP = {
    "monkey": "Monkey Trading",
    "breakout": "Breakout Oracle",
    "breakoutopt": "Sigma Breakout",
    "laplace": "Laplace's Demon Trading",
    "bull": "Bull Trading",
    "forest": "Signal Forest"
}

def render_sup_res(fig, data, tops, bottoms, plot_type):
    if st.toggle("Show tops and bottoms"):
        fig = pt.plot_tops_and_bottom(fig, data, tops, bottoms)
    
    if not st.toggle("Show support and resistances", False, disabled=plot_type == "pips") or plot_type == "pips":
        return fig

    
    min_challenge = st.number_input("Minimum Challenge", 1, None, 2, 1)
    sigma = st.number_input("Margin", 0., None, 0.02, 0.01)
    fuse_tolerance = st.number_input("Fuse Tolerance", 0., None, 0.02, 0.01)

    sup = ta.naive_sup_res(bottoms, sigma, "bottoms", min_challenge, fuse_tolerance)
    res = ta.naive_sup_res(tops, sigma, "tops", min_challenge, fuse_tolerance)
    fig = pt.plot_sup_and_res(fig, data, sup, res)

    return fig

def render_indicator(fig : go.Figure, data : pd.DataFrame):
    if st.toggle("Show MACD"):
        fig = pt.plot_macd(fig, data)
    return fig

def render_strategies(fig : go.Figure, data : pd.DataFrame, tops, bottoms):
    strategy_choice = st.selectbox("Trading strategy", options=STRATEGY_MAP.keys(), format_func=lambda option: STRATEGY_MAP[option])
    strategy = None
    lookback = 0
    if strategy_choice == "monkey":
        probability = st.number_input("Monkey trade probabilty in %", 0., 100., 1., 0.1)
        strategy = MonkeyTrading(pd.DataFrame().reindex_like(data), probability)
    elif strategy_choice == "breakout":
        sup = ta.naive_sup_res(bottoms, 0.02, "bottoms", 2, 0)
        res = ta.naive_sup_res(tops, 0.02, "tops", 2, 0)
        strategy = BreakoutSimple(pd.DataFrame().reindex_like(data), sup, res)
    elif strategy_choice == "laplace":
        strategy = LaplaceTrading(pd.DataFrame().reindex_like(data), tops, bottoms)
    elif strategy_choice == "breakoutopt":
        sup = ta.naive_sup_res(bottoms, 0.02, "bottoms", 2, 0)
        res = ta.naive_sup_res(tops, 0.02, "tops", 2, 0)
        sigma = st.number_input("Sigma", 0., None, 0.02)
        strategy = BreakoutOptimized(pd.DataFrame().reindex_like(data), sup, res, sigma)
    elif strategy_choice == "bull":
        order_col, macd_col = st.columns(2)
        order, max_macd = 0, 0
        with order_col:
            order = st.number_input("Order", 3, None)
        with macd_col:
            max_macd = st.number_input("Max MACD", 3, None)
        strategy = BullTrading(pd.DataFrame().reindex_like(data), data, order, max_macd)
    elif strategy_choice == "forest":
        train_years = st.number_input("Training Years", value=5)
        lookback = 365 * train_years
        strategy = ForestSignal(data.head(lookback).copy())
    gain, decisions = simulate(data, strategy, lookback)
    st.write(f"You multiplied your money by {gain:,.2f}, buy and hold would have yielded {data.iloc[-1]['Close'] / data.iloc[0]['Close']:,.2f}")
    st.write(f"The profit factor is {compute_profit_factor(strategy)}")
    if st.toggle("Show trades"):
        fig = pt.plot_strategy(fig, decisions)
    if st.toggle("Show returns histogram"):
        st.plotly_chart(pt.plot_strategy_returns(strategy.returns))
    return fig

def render_year_range(index : pd.DatetimeIndex):
    min_date = index[0].to_pydatetime()
    max_date = index[-1].to_pydatetime()
    return st.slider("Sample Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

def render_style():

    style = st.segmented_control("Style", options=STYLE_MAP.keys(), format_func=lambda option: STYLE_MAP[option], selection_mode="single", default="close")
    scale = st.segmented_control("Scale", options=SCALE_MAP.keys(), format_func=lambda option: SCALE_MAP[option], selection_mode="single", default="linear")
    
    return style, scale

def render_tops_bottoms(data : pd.DataFrame, plot_type : str):
    tops, bottoms = None, None

    if plot_type == "rw":
        order = st.number_input("Order", min_value=1, step=1, value=10)
        price_type = st.selectbox("Price Type", options = PRICE_MAP.keys(), format_func=lambda option: PRICE_MAP[option])
        
        if price_type == "hl":
            tops, _ = ta.rolling_window(data["High"].to_numpy(), order)
            _, bottoms = ta.rolling_window(data["Low"].to_numpy(), order)
        else:
            tops, bottoms = ta.rolling_window(data["Close"].to_numpy(), order)
    elif plot_type == "dc":
        sigma = st.number_input("Sigma", min_value=0., step=0.005, value=0.02)
        tops, bottoms = ta.directional_change(data["Close"].to_numpy(), data["High"].to_numpy(), data["Low"].to_numpy(), sigma)
    elif plot_type == "pips":
        nb_points = st.number_input("Number of Points", min_value=5, step=1, value=5)
        distance_type = st.selectbox("Distance Measured", options=DIST_MAP.keys(), format_func=lambda option: DIST_MAP[option])
        
        tops = ta.pips(data["Close"].to_numpy(), nb_points, distance_type)
    return tops, bottoms

@st.cache_data
def get_name_df(_session : Session) -> pd.DataFrame :
    return _session.sql("SELECT * FROM TRADING.STOXX600.NAME_SYMBOL").to_pandas()

@st.cache_data
def get_stock_symbol(_session : Session, name : str) -> str:
    return _session.sql(f"SELECT SYMBOL FROM TRADING.STOXX600.NAME_SYMBOL WHERE NAME='{name}'").to_pandas()["SYMBOL"].iloc[0]

@st.cache_data
def get_stock_data(_session : Session, symbol : str) -> pd.DataFrame:
    return _session.sql(f"SELECT * FROM TRADING.STOXX600.\"STOCK_{symbol}\"").to_pandas()

def main():
    st.set_page_config(page_title="Stoxx600 Visual Analyser")

    st.title("Stoxx600 Viewer App 💸")

    cnx = st.connection('snowflake')
    session = cnx.session()

    name_df = get_name_df(session)
    name = st.selectbox("Stock list", name_df["NAME"])

    if not name:
        return
    
    with st.sidebar:
        stock_values_df = get_stock_data(session, get_stock_symbol(session, name))
        stock_values_df['Date'] = pd.to_datetime(stock_values_df['Date'])
        stock_values_df.set_index('Date', inplace=True)

        start_date, end_date = render_year_range(stock_values_df.index)
        stock_values_df = stock_values_df.loc[start_date:end_date]

        style, scale = render_style()

        if not (style and scale):
            return
        
        fig = pt.plot_prices(stock_values_df, style)

        plot_type = st.selectbox("Plot type", options = POINT_MAP.keys(), format_func=lambda option: POINT_MAP[option])
        tops, bottoms = render_tops_bottoms(stock_values_df, plot_type)
        fig = render_sup_res(fig, stock_values_df, tops, bottoms, plot_type)

        render_indicator(fig, stock_values_df)
        
        render_strategies(fig, stock_values_df, tops, bottoms)

        fig.update_yaxes(type=scale)

    st.plotly_chart(fig)

        
main()