import pandas as pd
import numpy as np

def tr(df : pd.DataFrame) -> pd.DataFrame:
    df["TR"] = np.maximum(df['High'] - df['Low'], np.abs(df['High'] - df['Close'].shift(1)), np.abs(df['Low'] - df['Close'].shift(1)))
    return df

def atr(df : pd.DataFrame, window : int) -> pd.DataFrame:
    if not ("TR" in df.columns):
        df = tr(df)
    df["ATR"] = df["TR"].rolling(window).mean()
    return df

def macd(df : pd.DataFrame):
    long_ema = df["Close"].ewm(span=26).mean()
    short_ema = df["Close"].ewm(span=12).mean()
    df["MACD"] = long_ema - short_ema
    return df

def rsi(df : pd.DataFrame, window : int):
    df['Change'] = df['Close'].diff()

    df['Gain'] = np.where(df['Change'] > 0, df['Change'], 0)
    df['Loss'] = np.where(df['Change'] < 0, -df['Change'], 0)

    df['Avg_Gain'] = df['Gain'].rolling(window=window).mean()
    df['Avg_Loss'] = df['Loss'].rolling(window=window).mean()

    df['RS'] = df['Avg_Gain'] / df['Avg_Loss']
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    return df

def bollinger_band(df : pd.DataFrame, window=20) -> pd.DataFrame:
    df['SMA'] = df['Close'].rolling(window=window).mean()

    df['STD'] = df['Close'].rolling(window=window).std()

    df['Upper Band'] = df['SMA'] + (df['STD'] * 2)
    df['Lower Band'] = df['SMA'] - (df['STD'] * 2)
    return df