import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": api_key  
}
def get_ohlc(name):
    url = f"https://api.coingecko.com/api/v3/coins/{name}/ohlc"

    params = {
        "vs_currency": "usd", 
        "days": "1"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["timestamp_ms", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["timestamp_ms"], unit="ms").dt.date
    df =(df.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
    df = df.drop("timestamp_ms", axis = 1)
    df = df.iloc[-1]
    print(df)

get_ohlc("bitcoin")