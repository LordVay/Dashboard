import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Backend.dash2 import Volatile
import streamlit as st

cryptocurrency_data = {
            "Bitcoin (BTC)" : "btc", 
            "Cardona (ADA)" : "ada", 
            "Binance (BNB)" : "bnb", 
            "Dogecoin (DOGE)" : "doge", 
            "Ethereum (ETH)" : "eth",
            "Solana (SOL)" : "sol", 
            "TRON (TRX)" : "trx", 
            "USDC (USDC)" : "usdc", 
            "Tether (USDT)" : "usdt", 
            "XRP (XRP)" : "xrp"
            }

col1 , col2 = st.columns([0.3 ,0.7], border=True, gap = "small")
with col1:
    cryptocurrency = st.selectbox("Currency", ["Bitcoin (BTC)", "Cardona (ADA)", "Binance (BNB)", "Dogecoin (DOGE)", "Ethereum (ETH)",
                                            "Solana (SOL)", "TRON (TRX)", "USDC (USDC)", "Tether (USDT)", "XRP (XRP)"])

    timeframe = st.selectbox("Timeframe", ["15D", "1M", "6M", "1Y", "5Y", "Max"])
    if not timeframe:
        raise ValueError("Not a timeframe")
    
    volatility = st.selectbox("Volatility", ["30D", "60D", "90D"])

    volatility_number = {
        "30D": 30,
        "60D": 60,
        "90D": 90
    }
    volatile = Volatile(cryptocurrency_data[cryptocurrency])
    latest_volatility, change_in_volatility = volatile.volatility_graph(volatility_number[volatility])
    st.metric(label="Annualized Volatility", value = f"{latest_volatility*100:.2f}%", delta=f"{(change_in_volatility)*100:.2f}%")
    
with col2:
    high_low = volatile.high_low_range(timeframe)
    st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Timeframe: {timeframe}</p>", unsafe_allow_html=True )
    st.line_chart(data = high_low, x_label= "Date", y_label= "Daily range", width="stretch")

col1m , col2m, col3m = st.columns([0.33 ,0.33, 0.33], border=True, gap = "small")
with col1m:
    avg = volatile.avg_percentage()
    st.metric(label= f"Average Percentage", value = f"{avg:.2f}%")
    

with col2m:
    max_value, max_date= volatile.max_1D_percent()
    st.metric(label=f"Max 1-Day % : {max_date}",value = f"{max_value:.2f}%")
    

with col3m:
    min_value, min_date = volatile.min_1D_percent()
    st.metric(label=f"Min 1-Day % : {min_date}", value = f"{min_value:.2f}%")
