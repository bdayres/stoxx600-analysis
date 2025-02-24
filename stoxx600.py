from time import sleep
import yfinance as yf
from bs4 import BeautifulSoup
import requests as rq
from snowflake.snowpark import Session
import pandas as pd


def load_data_to_snowflake(df : pd.DataFrame, table_name, session : Session):
    df.columns = [col[0] for col in df.columns]
    df['Date'] = df.index.astype(str)
    df = df.reset_index(drop=True)
    session.write_pandas(df=df, table_name=table_name, auto_create_table=True)

def get_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = rq.get(url=yfinance, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    try:
        company_code = data['quotes'][0]['symbol']
    except:
        company_code = "N/A"
    return company_code


def get_stoxx600_symbols():
    response = rq.get("https://fr.investing.com/indices/stoxx-600-components")

    if not response.ok:
        print("Error :", response.status_code)
        exit()

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('tbody', class_="datatable-v2_body__8TXQk")

    companies = []

    for entry in table.find_all("tr"):
        companies.append(entry.find('h4').find('span', attrs={'dir': 'ltr'}).text)

    symbols = []

    for company in companies:
        ticker_name = get_ticker(company)
        print(f'Ticker for {company}')
        if ticker_name != "N/A":
            symbols.append(ticker_name)

    return symbols 

def create_name_to_symbol_db(session : Session, symbols):
    tickers = yf.Tickers(symbols)
    infos = {"NAME":[], "SYMBOL":[]}
    for _, ticker in tickers.tickers.items():
        sleep(1)
        if "shortName" in ticker.info and "symbol" in ticker.info:
            infos["NAME"].append(ticker.info["shortName"])
            infos["SYMBOL"].append(ticker.info["symbol"])
            print(f'{ticker.info["shortName"]} is {ticker.info["symbol"]}')
    df = pd.DataFrame(infos)
    session.write_pandas(df=df, table_name="NAME_SYMBOL", auto_create_table=True)


def send_stoxx600_to_snoflake(session):

    symbols = get_stoxx600_symbols()
    print(f"Found {len(symbols)} symbols")


    for symbol in symbols:
        data = yf.download(symbol)
        table_name = f'stock_{symbol}'.upper()
        load_data_to_snowflake(data, table_name, session)



def main():
    session = Session.builder.config("connection_name", "connection").create()
    # session = None

    # send_stoxx600_to_snoflake(session)
    symbols = get_stoxx600_symbols()
    create_name_to_symbol_db(session, symbols)

    session.close()

if __name__ == '__main__':
    main()
