import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()

api_key = st.secrets["API_KEY"]
news_key = st.secrets["NEWS_API"]

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

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    data_price = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    data_price["datetime"] = pd.to_datetime(data_price["timestamp"], unit="ms")
    data_price["date"] = data_price["datetime"].dt.date

    return data_price
