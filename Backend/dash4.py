import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

api_key = os.getenv("API_KEY")
news_key = os.getenv("NEWS_API")

if not news_key or not api_key:
    raise ValueError("API key not found in environment variables.")

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": api_key  
}

@st.cache_data
def get_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd", 
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    dataframe = pd.DataFrame(data = data, columns= ["name", "symbol", "current_price", "market_cap", "price_change_percentage_24h"])

    return dataframe

@st.cache_data
def get_news():
    url = "https://cryptopanic.com/api/developer/v2/posts/"

    params = {
    "auth_token": news_key,
    "currencies": "BTC",  
    "public" : "true"        
    
    }
    response = requests.get(url, params=params)

    data = response.json()

    data_array = data["results"]

    return data_array

@st.cache_data
def get_updated_data(currency, days):
    url = f"https://api.coingecko.com/api/v3/coins/{currency}/market_chart"

    params = {
        "vs_currency" : "usd",
        "days": days,
        "interval" : "hourly"
    }

    response = requests.get(url, params=params)
    data = response.json()
    data_price = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    data_price["datetime"] = pd.to_datetime(data_price["timestamp"], unit="ms")
    data_price["date"] = data_price["datetime"].dt.date

    return data_price



currency_id = []
current_time = datetime.today().date()

data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
if data_range.empty:
    return None
        
data_range["date"] = pd.to_datetime(data_range["date"])
dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date"}).set_index("Date").sort_index())

last_time = dataframe.index[-1]
days_interval = (current_time - last_time).days

fetched_data = get_updated_data(currency=currency_id, days=days_interval)


date_array = [last_time + timedelta(days = i) for i in range((days_interval) + 1)]

ohlc_array = []
for i in date_array:

    specific_date_data = fetched_data[fetched_data["date" == i]]

    ohlc = {
    "ticker": cryptocurremcy,
    "date": i,
    "open": specific_date_data["price"].iloc[0],
    "high": specific_date_data["price"].max(),
    "low": specific_date_data["price"].min(),
    "close": specific_date_data["price"].iloc[-1]
    }
    
    ohlc_array.append(ohlc)
ohlc_dataframe = pd.DataFrame(ohlc_array)
ohlc_dataframe =(ohlc_dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "open":"Open", "close":"Close"}))

