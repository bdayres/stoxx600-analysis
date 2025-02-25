import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def rw_top(data: np.ndarray, curr_index: int, order: int) -> bool:
    if curr_index < order * 2 + 1:
        return False

    top = True
    k = curr_index - order
    v = data[k]
    for i in range(1, order + 1):
        if data[k + i] > v or data[k - i] > v:
            top = False
            break
    
    return top

def rw_bottom(data: np.ndarray, curr_index: int, order: int) -> bool:
    if curr_index < order * 2 + 1:
        return False

    bottom = True
    k = curr_index - order
    v = data[k]
    for i in range(1, order + 1):
        if data[k + i] < v or data[k - i] < v:
            bottom = False
            break
    
    return bottom

def rolling_window(data: np.ndarray, order:int):
    tops = []
    bottoms = []
    for i in range(len(data)):
        if rw_top(data, i, order):
            # top[0] = confirmation index
            # top[1] = index of top
            # top[2] = price of top
            top = [i, i - order, data[i - order]]
            tops.append(top)
        
        if rw_bottom(data, i, order):
            # bottom[0] = confirmation index
            # bottom[1] = index of bottom
            # bottom[2] = price of bottom
            bottom = [i, i - order, data[i - order]]
            bottoms.append(bottom)
    
    return tops, bottoms

def directional_change(close: np.ndarray, high: np.ndarray, low: np.ndarray, sigma: float):
    
    up_zig = True # Last extreme is a bottom. Next is a top. 
    tmp_max = high[0]
    tmp_min = low[0]
    tmp_max_i = 0
    tmp_min_i = 0

    tops = []
    bottoms = []

    for i in range(len(close)):
        if up_zig: # Last extreme is a bottom
            if high[i] > tmp_max:
                # New high, update 
                tmp_max = high[i]
                tmp_max_i = i
            elif close[i] < tmp_max - tmp_max * sigma: 
                # Price retraced by sigma %. Top confirmed, record it
                top = [i, tmp_max_i, tmp_max]
                tops.append(top)

                # Setup for next bottom
                up_zig = False
                tmp_min = low[i]
                tmp_min_i = i
        else: # Last extreme is a top
            if low[i] < tmp_min:
                # New low, update 
                tmp_min = low[i]
                tmp_min_i = i
            elif close[i] > tmp_min + tmp_min * sigma: 
                # Price retraced by sigma %. Bottom confirmed, record it
                bottom = [i, tmp_min_i, tmp_min]
                bottoms.append(bottom)

                # Setup for next top
                up_zig = True
                tmp_max = high[i]
                tmp_max_i = i

    return tops, bottoms

def pips(data: np.ndarray, n_pips: int, dist_measure: int):
    # dist_measure
    # 1 = Euclidean Distance
    # 2 = Perpendicular Distance
    # 3 = Vertical Distance

    pips_x = [0, len(data) - 1]  # Index
    pips_y = [data[0], data[-1]] # Price

    for curr_point in range(2, n_pips):

        md = 0.0 # Max distance
        md_i = -1 # Max distance index
        insert_index = -1

        for k in range(0, curr_point - 1):

            # Left adjacent, right adjacent indices
            left_adj = k
            right_adj = k + 1

            time_diff = pips_x[right_adj] - pips_x[left_adj]
            price_diff = pips_y[right_adj] - pips_y[left_adj]
            slope = price_diff / time_diff
            intercept = pips_y[left_adj] - pips_x[left_adj] * slope;

            for i in range(pips_x[left_adj] + 1, pips_x[right_adj]):
                
                d = 0.0 # Distance
                if dist_measure == 1: # Euclidean distance
                    d =  ( (pips_x[left_adj] - i) ** 2 + (pips_y[left_adj] - data[i]) ** 2 ) ** 0.5
                    d += ( (pips_x[right_adj] - i) ** 2 + (pips_y[right_adj] - data[i]) ** 2 ) ** 0.5
                elif dist_measure == 2: # Perpindicular distance
                    d = abs( (slope * i + intercept) - data[i] ) / (slope ** 2 + 1) ** 0.5
                else: # Vertical distance    
                    d = abs( (slope * i + intercept) - data[i] )

                if d > md:
                    md = d
                    md_i = i
                    insert_index = right_adj

        pips_x.insert(insert_index, md_i)
        pips_y.insert(insert_index, data[md_i])

    return pips_x, pips_y

def naive_sup_res(points, sigma, type="tops", min_challenge=2):
    # On parcours tout les points
    # Pour chaque point, on parcour les point d'après
    #   - Si on dépasse, on annule
    #   - Si on reste dedans, on continue
    #   - Si on challenge, on continue et on compte

    sup_res = []
    i = 0

    while i < len(points):
        count = 0
        error_margin = points[i][2] * sigma
        j = 0
        for next_point in points[i+1:]:
            if type == "tops" and next_point[2] > points[i][2] + error_margin:
                break
            if type == "bottoms" and next_point[2] < points[i][2] - error_margin:
                break
            if next_point[2] > points[i][2] - error_margin and next_point[2] < points[i][2] + error_margin:
                count += 1
            j += 1
        if count >= min_challenge:
            sup_res.append([points[i][2], points[i][1], points[i + j][1]])
            i += j
        else:
            i += 1
    return sup_res

def test_rolling_window(close : pd.Series, idx : pd.Index, order):
    tops, bottoms = rolling_window(close.to_numpy(), order)
    close.plot()
    for top in tops:
        plt.plot(idx[top[1]], top[2], marker='o', color='green')

    for bottom in bottoms:
        plt.plot(idx[bottom[1]], bottom[2], marker='o', color='red')

    plt.yscale('log')
    plt.show()

def test_directional_change(close : pd.Series, high : pd.Series, low : pd.Series, idx : pd.Index, sigma):
    tops, bottoms = directional_change(close.to_numpy(), high.to_numpy(), low.to_numpy(), sigma)
    close.plot()

    for top in tops:
        plt.plot(idx[top[1]], top[2], marker='o', color='green')

    for bottom in bottoms:
        plt.plot(idx[bottom[1]], bottom[2], marker='o', color='red')

    plt.yscale('log')
    plt.show()

def test_pips(close : pd.Series, nb_points, measure):
    pips_x, pips_y = pips(close.to_numpy(), nb_points, measure)
    close.plot()

    for i in range(5):
        plt.plot(pips_x[i], pips_y[i], marker='o', color='red')
    
    plt.yscale('log')
    plt.show()

def test_naive_sup_res(close : pd.Series, tops, bottoms, sigma, min_challenge):
    close.plot()
    res = naive_sup_res(tops, sigma, type="tops", min_challenge=min_challenge)
    sup = naive_sup_res(bottoms, sigma, type="bottoms", min_challenge=min_challenge)

    plt.hlines(y=[line[0] for line in res], xmin=[idx[line[1]] for line in res], xmax=[idx[line[2]] for line in res], colors="red")
    plt.hlines(y=[line[0] for line in sup], xmin=[idx[line[1]] for line in sup], xmax=[idx[line[2]] for line in sup], colors="green")
    plt.show()



if __name__ == '__main__':
    hsbc = pd.read_csv("hsbc_daily.csv")
    hsbc['Date'] = pd.to_datetime(hsbc['Date'])
    hsbc.set_index('Date')
    idx = hsbc.index

    tops, bottoms = rolling_window(hsbc['Close'], 20)
    test_naive_sup_res(hsbc['Close'], tops, bottoms, 0.02, 2)

    # test_rolling_window(hsbc['Close'], idx, 100)
    # test_directional_change(hsbc['Close'], hsbc['High'], hsbc['Low'], idx, 0.2)
    # test_pips(hsbc['Close'], 5, 3)

