import pandas as pd

# Function to get the list of S&P 500 tickers
def get_sp500_tickers(names=False):
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)  # Read all tables from the page
    sp500 = tables[0]  # The first table contains the S&P 500 companies
    tickers = sp500['Symbol'].tolist()  # Extract stock symbols from the table
    if names:
        names_tickers = sp500['Security'].tolist()
        return tickers, names_tickers
    return tickers