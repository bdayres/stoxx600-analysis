import yfinance as yf
from bs4 import BeautifulSoup
import requests as rq

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
        if ticker_name != "N/A":
            symbols.append(ticker_name)

    return symbols

symbols = get_stoxx600_symbols()
print(f"Found {len(symbols)} symbols")

for symbol in symbols:
    ticker = yf.Ticker(symbol)
    print(f"{symbol} is {ticker.info.get('longName', 'Not found')}")