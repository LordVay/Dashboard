import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

st.title("Top 10 Crytpocurrency Dashboard and Predictive Model")
st.caption("Live Prices, Price History, Market Insights and Latest Crypto Headlines !")


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
    "currencies": "BTC",   # filter by coin
    "public" : "true"        # optional filter
    
    }
    response = requests.get(url, params=params)

    data = response.json()

    data_array = data["results"]

    return data_array


df = get_data()
df = df.rename(columns= {"name" : "Coin", "symbol" : "Symbol", "current_price" : "Price (USD)", "market_cap" : "Market Cap", "price_change_percentage_24h" : "24 Hours % Change" } )
st.dataframe(df.style.format({ "Price (USD)": "${:,.2f}", "Market Cap": "${:,.0f}", "24 Hours % Change": "{:.2f}%" }), hide_index= True)


st.subheader("🌍 World's Top 3 CryptoNews as of Today !")
articles = get_news()


for article in articles[0:3]:
    
        st.write(article["title"])

        raw_date = article["published_at"].replace("Z", "+00:00")
        pub_date = datetime.fromisoformat(raw_date)
        formatted_date = pub_date.strftime("%B %d, %Y %I:%M %p")

        st.caption(formatted_date)
        st.write(article["description"])
        button_label = f"Read More: {article['title'][:15]}..."
        
        if st.button(button_label, key=article["title"]):
            st.info(f"Full article: {article['description']}")
        
