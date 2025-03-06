import pandas as pd

import tests.strategies.test_strategies as ts

def main():
    data = pd.read_csv("hsbc_daily.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")

    ts.test_forest(data)

if __name__ == "__main__":
    main()