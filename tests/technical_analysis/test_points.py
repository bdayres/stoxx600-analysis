import pandas as pd
import matplotlib.pyplot as plt
from technical_analysis.points import *

def test_rolling_window(data : pd.DataFrame, order):
    tops, bottoms = rolling_window(data["Close"].to_numpy(), order)
    data["Close"].plot()
    idx = data.index
    for top in tops:
        plt.plot(idx[top[1]], top[2], marker='o', color='green')

    for bottom in bottoms:
        plt.plot(idx[bottom[1]], bottom[2], marker='o', color='red')

    plt.yscale('log')
    plt.show()

def test_directional_change(data : pd.DataFrame, sigma):
    tops, bottoms = directional_change(data["Close"].to_numpy(), data["High"].to_numpy(), data["Low"].to_numpy(), sigma)
    data["Close"].plot()
    idx = data.index

    for top in tops:
        plt.plot(idx[top[1]], top[2], marker='o', color='green')

    for bottom in bottoms:
        plt.plot(idx[bottom[1]], bottom[2], marker='o', color='red')

    plt.yscale('log')
    plt.show()

def test_pips(data : pd.DataFrame, nb_points, measure):
    points = pips(data["Close"].to_numpy(), nb_points, measure)
    data["Close"].plot()
    idx = data.index

    for point in points:
        plt.plot(idx[point[1]], point[2], marker='o', color='green')
    
    plt.yscale('log')
    plt.show()

def test_naive_sup_res(data : pd.DataFrame, tops, bottoms, sigma, min_challenge):
    data["Close"].plot()
    idx = data.index
    res = naive_sup_res(tops, sigma, type="tops", min_challenge=min_challenge)
    sup = naive_sup_res(bottoms, sigma, type="bottoms", min_challenge=min_challenge)

    plt.hlines(y=[line[0] for line in res], xmin=[idx[line[1]] for line in res], xmax=[idx[line[2]] for line in res], colors="red")
    plt.hlines(y=[line[0] for line in sup], xmin=[idx[line[1]] for line in sup], xmax=[idx[line[2]] for line in sup], colors="green")
    plt.show()