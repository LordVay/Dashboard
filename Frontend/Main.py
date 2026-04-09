import streamlit as st
from datetime import datetime
import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Backend.dash4 import get_news, get_data
import streamlit as st

st.title("Top 10 Crytpocurrency Dashboard and Predictive Model")
st.caption("Live Prices, Price History, Market Insights and Latest Crypto Headlines !")

df = get_data()
df = df.rename(columns= {"name" : "Coin", "symbol" : "Symbol", "current_price" : "Price (USD)", "market_cap" : "Market Cap", "price_change_percentage_24h" : "24 Hours % Change" } )
st.dataframe(df.style.format({ "Price (USD)": "${:,.2f}", "Market Cap": "${:,.0f}", "24 Hours % Change": "{:.2f}%" }), hide_index= True)

        
