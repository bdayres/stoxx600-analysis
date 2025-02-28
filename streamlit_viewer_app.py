import streamlit as st
from snowflake.snowpark.functions import col

import pandas as pd
import plotly.graph_objects as go

import plotter as pt
import technical_analysis as ta

import simulator as sim

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

def render_sup_res(fig, data, tops, bottoms):
    challenge_col, sigma_col, fuse_col = st.columns(3)
    min_challenge, sigma, fuse_tolerance = None, None, None
    
    with challenge_col:
        min_challenge = st.number_input("Minimum Challenge", 1, None, 2, 1)
    
    with sigma_col:
        sigma = st.number_input("Margin", 0., None, 0.02, 0.01)
    
    with fuse_col:
        fuse_tolerance = st.number_input("Fuse Tolerance", 0., None, 0.02, 0.01)

    sup = ta.naive_sup_res(bottoms, sigma, "bottoms", min_challenge, fuse_tolerance)
    res = ta.naive_sup_res(tops, sigma, "tops", min_challenge, fuse_tolerance)
    fig = pt.plot_sup_and_res(fig, data, sup, res)

    return fig, sup, res

def main():

    st.set_page_config(
        page_title="Stoxx600 Visual Analyser"
    )

    st.title("Stoxx600 Viewer App 💸")

    cnx = st.connection('snowflake')
    session = cnx.session()

    stock_df = session.sql("SELECT * FROM TRADING.STOXX600.NAME_SYMBOL")
    name = st.selectbox("Stock list", stock_df.select(col("name")))

    if name:
        symbol_df = session.sql(f"SELECT SYMBOL FROM TRADING.STOXX600.NAME_SYMBOL WHERE NAME='{name}'").to_pandas()
        symbol = symbol_df['SYMBOL'].iloc[0]
        
        stock_values_df = session.sql(f"SELECT * FROM TRADING.STOXX600.\"STOCK_{symbol}\"").to_pandas()
        stock_values_df['Date'] = pd.to_datetime(stock_values_df['Date'])
        stock_values_df.set_index('Date', inplace=True)
        # start = st.date_input("Start", value='2020-01-01')
        # end = st.date_input("End", value='today')

        style_col, scale_col = st.columns(2)

        style = None
        scale = None

        with style_col:
            style = st.segmented_control("Style", options=STYLE_MAP.keys(), format_func=lambda option: STYLE_MAP[option], selection_mode="single", default="close")
        with scale_col:
            scale = st.segmented_control("Scale", options=SCALE_MAP.keys(), format_func=lambda option: SCALE_MAP[option], selection_mode="single", default="linear")

        plot_type = st.selectbox("Plot type", options = POINT_MAP.keys(), format_func=lambda option: POINT_MAP[option])

        if style and scale:
            tops, bottoms = None, None

            if plot_type == "rw":
                order_col, type_col = st.columns(2)
                order, price_type = None, None
                with order_col:
                    order = st.number_input("Order", min_value=1, step=1, value=10)
                with type_col:
                    price_type = st.selectbox("Price Type", options = PRICE_MAP.keys(), format_func=lambda option: PRICE_MAP[option])
                
                if price_type == "hl":
                    tops, _ = ta.rolling_window(stock_values_df["High"].to_numpy(), order)
                    _, bottoms = ta.rolling_window(stock_values_df["Low"].to_numpy(), order)
                else:
                    tops, bottoms = ta.rolling_window(stock_values_df["Close"].to_numpy(), order)
            elif plot_type == "dc":
                sigma = st.number_input("Sigma", min_value=0., step=0.005, value=0.02)
                tops, bottoms = ta.directional_change(stock_values_df["Close"].to_numpy(), stock_values_df["High"].to_numpy(), stock_values_df["Low"].to_numpy(), sigma)
            elif plot_type == "pips":
                npoint_col, dist_col = st.columns(2)
                nb_points = None
                distance_type = None
                with npoint_col:
                    nb_points = st.number_input("Number of Points", min_value=5, step=1, value=5)
                with dist_col:
                    distance_type = st.selectbox("Distance Measured", options=DIST_MAP.keys(), format_func=lambda option: DIST_MAP[option])
                
                tops = ta.pips(stock_values_df["Close"].to_numpy(), nb_points, distance_type)
            
            fig = pt.plot_prices(stock_values_df, style)

            tb_col, sr_col = st.columns(2)
            sup, res = [], []
            show_sup_res = None

            with tb_col:
                if st.toggle("Show tops and bottoms"):
                    fig = pt.plot_tops_and_bottom(fig, stock_values_df, tops, bottoms)

            with sr_col:
                show_sup_res = st.toggle("Show support and resistances", False, disabled=plot_type == "pips")
            
            if show_sup_res and plot_type != "pips":
                fig, sup, res = render_sup_res(fig, stock_values_df, tops, bottoms)
            
            prob = st.number_input("Monkey trade probabilty", 0, 100, 95)

            if st.button("MONKEY TRADE !!!"):
                gain, decisions = sim.simulate(stock_values_df, sim.make_monkey(prob), 0)
                st.write(f"You multiplied your money by {gain}, buy and hold would have yielded {stock_values_df.iloc[-1]["Close"] / stock_values_df.iloc[0]["Close"]}")
                fig = pt.plot_strategy(fig, decisions)

            if st.button("Breakout Trading"):
                gain, decisions = sim.simulate(stock_values_df, sim.make_breakout_oracle(sup, res), 1)
                st.write(f"You multiplied your money by {gain}, buy and hold would have yielded {stock_values_df.iloc[-1]["Close"] / stock_values_df.iloc[0]["Close"]}")
                fig = pt.plot_strategy(fig, decisions)

            fig.update_yaxes(type=scale)
            st.plotly_chart(fig)

        
main()