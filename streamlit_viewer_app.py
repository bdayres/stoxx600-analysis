import streamlit as st
from snowflake.snowpark.functions import col

import pandas as pd
import plotly.graph_objects as go

from plotter import plot_tops_and_bottom
import technical_analysis as ta

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

        tops, bottoms = ta.rolling_window(stock_values_df["Close"].to_numpy(), 10)

        style = st.selectbox("Plot style", ("close", "candle"), index=0)
        scale = st.selectbox("Scale", ("lin", "log"), index=0)

        fig = plot_tops_and_bottom(stock_values_df, tops, bottoms, style)
        if scale == "log":
            fig.update_yaxes(type="log")
        st.plotly_chart(fig)

main()