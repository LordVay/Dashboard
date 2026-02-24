import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

st.title("Top 10 Crytpocurrency Dashboard and Predictive Model")
st.caption("Live Prices, Price History, Market Insights and Latest Crypto Headlines !")

@st.cache_data
def get_latest_data():
    load_dotenv()
api_key = os.getenv("API_KEY")

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


col1, col2 = st.columns([3, 1])

with col1:
    df = get_data()
    df = df.rename(columns= {"name" : "Coin", "symbol" : "Symbol", "current_price" : "Price (USD)", "market_cap" : "Market Cap", "price_change_percentage_24h" : "24 Hours % Change" } )
    st.dataframe(df.style.format({ "Price (USD)": "${:,.2f}", "Market Cap": "${:,.0f}", "24 Hours % Change": "{:.2f}%" }), hide_index= True)