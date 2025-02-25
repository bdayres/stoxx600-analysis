import streamlit as st
from snowflake.snowpark.functions import col

import pandas as pd
import plotly.graph_objects as go

import plotter as pt
import technical_analysis as ta

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


def main():
    st.title("Stoxx600 Viewer App 💸")

    cnx = st.connection('snowflake')
    session = cnx.session()

    stock_df = session.sql("SELECT * FROM TRADING.STOXX600.NAME_SYMBOL")
    names = st.multiselect("Stock list", stock_df.select(col("name")), max_selections=1)

    if names:
        symbol_df = session.sql(f"SELECT SYMBOL FROM TRADING.STOXX600.NAME_SYMBOL WHERE NAME='{names[0]}'").to_pandas()
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

        plot_type = st.selectbox("Plot type", ("Rolling Window", "Directional Change", "Perceptually Important Points"))

        if style and scale:
            tops, bottoms = None, None

            if plot_type == "Rolling Window":
                order = st.number_input("Order", min_value=1, step=1, value=10)
                tops, bottoms = ta.rolling_window(stock_values_df["Close"].to_numpy(), order)
            elif plot_type == "Directional Change":
                sigma = st.number_input("Sigma", min_value=0., step=0.005, value=0.02)
                tops, bottoms = ta.directional_change(stock_values_df["Close"].to_numpy(), stock_values_df["High"].to_numpy(), stock_values_df["Low"].to_numpy(), sigma)
            elif plot_type == "Perceptually Important Points":
                npoint_col, dist_col = st.columns(2)
                nb_points = None
                distance_type = None
                with npoint_col:
                    nb_points = st.number_input("Number of Points", min_value=5, step=1, value=5)
                with dist_col:
                    distance_type = st.segmented_control("Distance Measured", options=DIST_MAP.keys(), format_func=lambda option: DIST_MAP[option], selection_mode="single")
                
                tops, bottoms = ta.pips(stock_values_df["Close"].to_numpy(), nb_points, distance_type)
            
            fig = pt.plot_prices(stock_values_df, style)

            tb_col, sr_col = st.columns(2)

            with tb_col:
                if st.toggle("Show tops and bottoms", True):
                    fig = pt.plot_tops_and_bottom(fig, stock_values_df, tops, bottoms)

            with sr_col:
                if st.toggle("Show support and resistances"):
                    sup = ta.naive_sup_res(bottoms, 0.02, "bottoms", 2)
                    res = ta.naive_sup_res(tops, 0.02, "tops", 2)
                    fig = pt.plot_sup_and_res(fig, stock_values_df, sup, res)

            fig.update_yaxes(type=scale)
            st.plotly_chart(fig)

        
main()