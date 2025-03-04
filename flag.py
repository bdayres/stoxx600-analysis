from dataclasses import dataclass
import numpy as np
from trendline import fit_trendlines_single
from technical_analysis import rw_top, rw_bottom
import pandas as pd
import matplotlib.pyplot as plt

@dataclass
class FlagPattern:
    base_x: int
    base_y: int

    tip_x: int = -1
    tip_y: int = -1

    conf_x: int = -1
    conf_y: float = -1.

    pennant: bool = False

    flag_width: int = -1
    flag_height: int = -1.

    pole_width: int = -1
    pole_height: float = -1.

    support_intercept: float = -1.
    support_slope: float = -1.
    resist_intercept: float = -1.
    resist_slope: float = -1.

def check_bull_pattern_trendline(pending: FlagPattern, data: np.ndarray, i:int, order:int):
    
    # Check if data max less than pole tip 
    if data[pending.tip_x + 1 : i].max() > pending.tip_y:
        return False

    flag_min = data[pending.tip_x:i].min()

    # Find flag/pole height and width
    pole_height = pending.tip_y - pending.base_y
    pole_width = pending.tip_x - pending.base_x
    
    flag_height = pending.tip_y - flag_min
    flag_width = i - pending.tip_x

    if flag_width > pole_width * 0.5: # Flag should be less than half the width of pole
        return False

    if flag_height > pole_height * 0.75: # Flag should smaller vertically than preceding trend
        return False

    # Find trendlines going from flag tip to the previous bar (not including current bar)
    support_coefs, resist_coefs = fit_trendlines_single(data[pending.tip_x:i])
    support_slope, support_intercept = support_coefs[0], support_coefs[1]
    resist_slope, resist_intercept = resist_coefs[0], resist_coefs[1]

    # Check for breakout of upper trendline to confirm pattern
    current_resist = resist_intercept + resist_slope * (flag_width + 1)
    if data[i] <= current_resist:
        return False

    # Pattern is confiremd, fill out pattern details in pending
    if support_slope > 0:
        pending.pennant = True
    else:
        pending.pennant = False

    pending.conf_x = i
    pending.conf_y = data[i]
    pending.flag_width = flag_width
    pending.flag_height = flag_height
    pending.pole_width = pole_width
    pending.pole_height = pole_height
    
    pending.support_slope = support_slope
    pending.support_intercept = support_intercept
    pending.resist_slope = resist_slope
    pending.resist_intercept = resist_intercept

    return True

def check_bear_pattern_trendline(pending: FlagPattern, data: np.ndarray, i:int, order:int):
    # Check if data max less than pole tip 
    if data[pending.tip_x + 1 : i].min() < pending.tip_y:
        return False

    flag_max = data[pending.tip_x:i].max()

    # Find flag/pole height and width
    pole_height = pending.base_y - pending.tip_y
    pole_width = pending.tip_x - pending.base_x
    
    flag_height = flag_max - pending.tip_y
    flag_width = i - pending.tip_x

    if flag_width > pole_width * 0.5: # Flag should be less than half the width of pole
        return False

    if flag_height > pole_height * 0.75: # Flag should smaller vertically than preceding trend
        return False

    # Find trendlines going from flag tip to the previous bar (not including current bar)
    support_coefs, resist_coefs = fit_trendlines_single(data[pending.tip_x:i])
    support_slope, support_intercept = support_coefs[0], support_coefs[1]
    resist_slope, resist_intercept = resist_coefs[0], resist_coefs[1]

    # Check for breakout of lower trendline to confirm pattern
    current_support = support_intercept + support_slope * (flag_width + 1)
    if data[i] >= current_support:
        return False

    # Pattern is confiremd, fill out pattern details in pending
    if resist_slope < 0:
        pending.pennant = True
    else:
        pending.pennant = False

    pending.conf_x = i
    pending.conf_y = data[i]
    pending.flag_width = flag_width
    pending.flag_height = flag_height
    pending.pole_width = pole_width
    pending.pole_height = pole_height
    
    pending.support_slope = support_slope
    pending.support_intercept = support_intercept
    pending.resist_slope = resist_slope
    pending.resist_intercept = resist_intercept

    return True

def find_flags_pennants_trendline(data: np.ndarray, order:int) -> tuple[list[FlagPattern]]:
    assert(order >= 3)
    pending_bull = None # Pending pattern
    pending_bear = None  # Pending pattern

    last_bottom = -1
    last_top = -1

    bull_pennants = []
    bear_pennants = []
    bull_flags = []
    bear_flags = []
    for i in range(len(data)):

        # Pattern data is organized like so:
        if rw_top(data, i, order):
            last_top = i - order
            if last_bottom != -1:
                pending = FlagPattern(last_bottom, data[last_bottom])
                pending.tip_x = last_top
                pending.tip_y = data[last_top]
                pending_bull = pending
        
        if rw_bottom(data, i, order):
            last_bottom = i - order
            if last_top != -1:
                pending = FlagPattern(last_top, data[last_top])
                pending.tip_x = last_bottom
                pending.tip_y = data[last_bottom]
                pending_bear = pending

        if pending_bear is not None:
            if check_bear_pattern_trendline(pending_bear, data, i, order):
                if pending_bear.pennant:
                    bear_pennants.append(pending_bear)
                else:
                    bear_flags.append(pending_bear)
                pending_bear = None
        
        if pending_bull is not None:
            if check_bull_pattern_trendline(pending_bull, data, i, order):
                if pending_bull.pennant:
                    bull_pennants.append(pending_bull)
                else:
                    bull_flags.append(pending_bull)
                pending_bull = None

    return bull_flags, bear_flags, bull_pennants, bear_pennants

if __name__ == "__main__":
    data = pd.read_csv('hsbc_daily.csv')
    data['Date'] = data['Date'].astype('datetime64[s]')
    data = data.set_index('Date')
    idx = data.index

    bull_flags, bear_flags, bull_pennants, bear_pennants = find_flags_pennants_trendline(data["Close"].to_numpy(), 20)

    data["Close"].plot()
    for flag in bull_flags:
        end_x = flag.tip_x + flag.flag_width
        end_y = flag.tip_y - flag.flag_height
        plt.plot([idx[flag.tip_x], idx[end_x]], [flag.tip_y, end_y], color="green")
    plt.yscale("log")
    plt.show()
    