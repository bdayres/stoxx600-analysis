import pandas as pd
import numpy as np
import scipy
import math

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

def fourier(df : pd.DataFrame) -> pd.DataFrame:
    # df['F_Value'] = np.fft.fft(df['Close']).astype(float)
    df['F_Freq'] = np.fft.fftfreq(len(df['Close'])).astype(float)
    return df

def ptsr(data : pd.DataFrame, lookback: int, start_index = 0):
    arr = data["Close"].iloc[start_index:].to_numpy()
    rev = np.zeros(len(arr))
    rev[:] = np.nan
    
    lookback_ = lookback + 2
    for i in range(lookback_, len(arr)):
        dat = arr[i - lookback_ + 1: i+1]
        rev_w = _perm_ts_reversibility(dat) 

        if np.isnan(rev_w):
            rev[i] = rev[i - 1]
        else:
            rev[i] = rev_w
    if start_index == 0:
        data['PTSR'] = rev
    else:
        data.iloc[start_index:, data.columns.get_loc('PTSR')] = rev
    return data

def _ordinal_patterns(arr: np.ndarray, d: int) -> np.ndarray:
    assert(d >= 2)
    fac = math.factorial(d)
    d1 = d - 1
    mults = []
    for i in range(1, d):
        mult = fac / math.factorial(i + 1)
        mults.append(mult)

    ordinals = np.empty(len(arr))
    ordinals[:] = np.nan

    for i in range(d1, len(arr)):
        dat = arr[i - d1:  i+1]
        pattern_ordinal = 0
        for l in range(1, d):
            count = 0
            for r in range(l):
                if dat[d1 - l] >= dat[d1 - r]:
                   count += 1

            pattern_ordinal += count * mults[l - 1]
        ordinals[i] = int(pattern_ordinal)

    return ordinals

def _perm_ts_reversibility(arr: np.ndarray):
    # Zanin, M.; Rodríguez-González, A.; Menasalvas Ruiz, E.; Papo, D. Assessing time series reversibility through permutation
    
    # Should be fairly large array, very least ~60
    assert(len(arr) >= 10)
    rev_arr = np.flip(arr)
   
    # [2:] drops 2 nan values off start of val
    pats = _ordinal_patterns(arr, 3)[2:].astype(int)
    r_pats = _ordinal_patterns(rev_arr, 3)[2:].astype(int)
   
    # pdf of patterns, forward and reverse time
    n = len(arr) - 2
    p_f = np.bincount(pats, minlength=6) / n 
    p_r = np.bincount(r_pats, minlength=6) / n

    if min(np.min(p_f), np.min(p_r)) > 0.0:
        rev = scipy.special.rel_entr(p_f, p_r).sum()
    else:
        rev = np.nan
        
    return rev