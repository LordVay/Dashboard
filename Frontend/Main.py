import streamlit as st
from datetime import datetime
import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Backend.dash4 import get_news, get_data
import streamlit as st

st.title("Top 10 Crytpocurrency Dashboard and Predictive Model")
st.caption("Live Prices, Price History, Market Insights and Latest Crypto Headlines !")

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
        
