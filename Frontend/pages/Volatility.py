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
    
with col2:
    volatile = Volatile(cryptocurrency_data[cryptocurrency])
    high_low = volatile.high_low_range(timeframe)
    st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Timeframe: {timeframe}</p>", unsafe_allow_html=True )
    st.line_chart(data = high_low, x_label= "Date", y_label= "Daily range", width="stretch")
