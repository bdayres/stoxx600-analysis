# Import python packages
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

def show_candles(df : pd.DataFrame, start, end):
    interval_df = df.loc[start:end]
    fig = go.Figure(data=[go.Candlestick(
        x=interval_df.index,
        open=interval_df['Open'],
        high=interval_df['High'],
        low=interval_df['Low'],
        close=interval_df['Close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_xaxes(rangebreaks=[
        { 'pattern': 'day of week', 'bounds': [6, 1]}
    ])
    st.plotly_chart(fig)

# Write directly to the app
st.title("Stoxx600 Viewer App 💸")

# Get the current credentials
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
    start = st.date_input("Start")
    end = st.date_input("End", value='today')
    show_candles(stock_values_df, start, end)