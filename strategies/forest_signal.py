from strategies.strategy import Strategy
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

class ForestSignal(Strategy):
    def __init__(self, data : pd.DataFrame):
        super().__init__(data)

        self._compute_indicator()

        X = self._data[['RSI', 'MACD', 'BB_Low', 'BB_High', 'SMA_50', 'SMA_200']]
        y = self._data['Buy_Signal']
        y.cumsum().plot()
        plt.show()
        

        # Diviser en ensemble d'entraînement et de test
        # self._model = RandomForestRegressor(n_estimators=100, random_state=42)
        # self._model.fit(X, y)

    def _compute_indicator(self):

        # RSI (Relative Strength Index)
        self._data["RSI"] = RSIIndicator(self._data["Close"]).rsi()

        # MACD (Moving Average Convergence Divergence)
        self._data["MACD"] = MACD(self._data["Close"]).macd()

        # Bandes de Bollinger
        bb = BollingerBands(self._data["Close"])
        self._data["BB_High"] = bb.bollinger_hband()
        self._data["BB_Low"] = bb.bollinger_lband()

        # Moyennes mobiles
        self._data["SMA_50"] = self._data["Close"].rolling(window=50).mean()
        self._data["SMA_200"] = self._data["Close"].rolling(window=200).mean()
        
        self._data["Buy_Signal"] = (
                     (self._data["MACD"] > 0)
                     ).astype(int)
        self._data.dropna(inplace=True)

    def make_choice(self, row):
        super().make_choice(row)
        
        # self._compute_indicator()
        
        # prediction = self._model.predict(self._data[row.name])

        # print(f"Prédiction pour la nouvelle entrée : {prediction[0]}")
    
