from strategies.strategy import Strategy
import pandas as pd
from technical_analysis.indicators import macd, rsi, atr, bollinger_band
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score

class ForestSignal(Strategy):
    def __init__(self, data : pd.DataFrame):
        super().__init__(data)

        self._compute_indicator()
        self._compute_signal()

        self._data.dropna(inplace=True)

        X = self._data[['RSI', 'MACD', 'Upper Band', 'ATR']]
        y = self._data['Target']

        # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=True)

        # self._model = RandomForestClassifier(n_estimators=100)
        # self._model.fit(X_train, y_train)
        # y_pred = self._model.predict(X_test)

        # accuracy = accuracy_score(y_test, y_pred)
        # print(f'Accuracy: {accuracy}')

        # tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

        # print(f"True positive : {tp}\nTrue negative : {tn}\nFalse positive {fp}\nFalse negative {fn}")
        # print(f"TP ratio {tp / (tp + fn)}\nTN ratio {tn / (tn + fp)}")

        self._model = RandomForestClassifier(n_estimators=100)
        self._model.fit(X, y)
        self._cons = 0


    def _compute_indicator(self):

        self._data = atr(self._data, 10)
        self._data = rsi(self._data, 10)
        self._data = macd(self._data)
        self._data = bollinger_band(self._data, 20)
        

    def _compute_signal(self):
        self._data["Diff"] = self._data["Close"].diff(20).shift(-20)
        self._data["Target"] = self._data["Diff"] > self._data["Close"] * 0.05


    def make_choice(self, row):
        super().make_choice(row)
        self._compute_indicator()
        print(row.name)
        y_pred = self._model.predict(self._data[['RSI', 'MACD', 'Upper Band', 'ATR']])
        choice = y_pred[-1]
        if self.position == 0 and choice:
            self._switch_position(row)
            self._cons = 10
            return
        elif self.position == 1:
            if choice:
                self._cons = 10
            else:
                self._cons -= 1
            if self._cons <= 0:
                self._switch_position(row)
                return
