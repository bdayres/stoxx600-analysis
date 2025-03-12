from strategies.strategy import Strategy
import pandas as pd
from technical_analysis.indicators import macd, rsi, atr, bollinger_band, ptsr, fourier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score
import matplotlib.pyplot as plt
import numpy as np

FEATURES = ['RSI', 'MACD', 'Upper Band', 'ATR', 'Volume_EMA']

class ForestSignal(Strategy):
    def __init__(self, data : pd.DataFrame):
        super().__init__(data)

        self._compute_indicator()
        self._compute_signal()

        self._data.dropna(inplace=True)

        X = self._data[FEATURES]
        y = self._data['Target']

        self._model = RandomForestClassifier(n_estimators=100)
        self._model.fit(X, y)

    def _mean_confusion(self):
        X = self._data[FEATURES]
        y = self._data['Target']

        mat = np.zeros((3, 3))
        accuracy = 0

        for i in range(20):
            print(i)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=True)

            self._model = RandomForestClassifier(n_estimators=100)
            self._model.fit(X_train, y_train)
            y_pred = self._model.predict(X_test)

            accuracy += accuracy_score(y_test, y_pred)
            mat += confusion_matrix(y_test, y_pred)

        print(f'Accuracy: {accuracy / 20}')

        print(mat / 20)

    def _compute_indicator(self, start_index=0):

        self._data = atr(self._data, 10)
        self._data = rsi(self._data, 10)
        self._data = macd(self._data)
        self._data = bollinger_band(self._data, 20)
        # self._data = fourier(self._data)
        self._data["Volume_EMA"] = self._data["Volume"].ewm(20).mean()
        # self._data = ptsr(self._data, 100, start_index)

    def _compute_signal(self):
        self._data["Diff"] = self._data["Close"].diff(20).shift(-20)
        self._data["Target"] = 0
        self._data.loc[self._data["Diff"] > self._data["Close"] * 0.05, "Target"] = 1
        self._data.loc[self._data["Diff"] < -self._data["Close"] * 0.05, "Target"] = -1
        # self._data["EMA"] = self._data["Close"].ewm(15).mean()
        # diff = self._data["EMA"].diff(1).shift(-1)


    def make_choice(self, row):
        super().make_choice(row)
        self._compute_indicator(self._data.index.get_loc(row.name) - 120)
        print(row.name)
        y_pred = self._model.predict(self._data[FEATURES])
        choice = y_pred[-1]
        if self.position == 0 and choice == 1:
            self._switch_position(row)
            self._cons = 10
            return
        elif self.position == 1 and choice == -1:
            self._switch_position(row)
            return
