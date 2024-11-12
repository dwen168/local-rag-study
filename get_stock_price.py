import requests
import json
import pandas as pd
from datetime import datetime, timezone


# API ref https://financeapi.net/

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}


def get_stock_price(search, interval='1d', range='1y') -> json:
    """Run the main program"""
    yfinapi = f"https://query1.finance.yahoo.com/v8/finance/chart/"
    url = f"{yfinapi}{search}?metrics=high?&interval={interval}&range={range}"
    reponse = requests.get(url, headers=headers)
    return reponse.json()['chart']['result'][0]
    

def get_formatted_stock_price(data:json):
    # Step 1: Convert 'timestamp' to human-readable dates
    timestamps = data["timestamp"]
    dates = [datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d') for ts in timestamps]

    # Step 2: Flatten the 'quote' data
    quote_data = data["indicators"]["quote"][0]
    df_quotes = pd.DataFrame(quote_data)

    # Step 3: Add the 'dates' as a new column
    df_quotes.insert(0, 'date', dates)

    # Step 4: Optionally add 'adjclose' data
    adjclose_data = data["indicators"]["adjclose"][0]["adjclose"]
    df_quotes['adjclose'] = adjclose_data

    return df_quotes

print(get_formatted_stock_price(get_stock_price('aapl')))