import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Backend.dash3 import Candle
import streamlit as st
import matplotlib.pyplot as plt

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
    
    if not cryptocurrency:
        raise ValueError("Not a Cryptocurrency")
    
    timeframe = st.selectbox("Timeframe", ["15D", "1M", "6M", "1Y", "5Y", "Max"])

    if not timeframe:
        raise ValueError("Not a timeframe")
    
    
with col2:
    candle = Candle(cryptocurrency_data[cryptocurrency])
    data_array = candle.bullvsbear(timeframe)
    labels = "Bull", "Bear", "Doji"
    sizes = [data_array[0] , data_array[1], data_array[2]]
    explode = (0, 0, 0)

    fig1,ax1 = plt.subplots()
    fig1.patch.set_facecolor("#0E1117") 
    ax1.set_facecolor("black")
    colors = ["gray", "blue", "red"] 
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90, colors= colors, textprops={'color' : "white"})
    ax1.axis('equal')
    ax1.set_title("Bull vs Bear vs Doji", color="white", fontsize=14)

    st.pyplot(fig1)

colm1, colm2 = st.columns([0.5 ,0.5], border=True, gap = "small")

with colm1:
    st.markdown("Maximum Bear Streak", unsafe_allow_html=True)
    max_streak_bear, max_date_bear, min_date_bear = candle.bear_streak()
    st.metric(label=f"{min_date_bear} - {max_date_bear}", value = f"{max_streak_bear} Days")

with colm2:
    st.markdown("Maximum Bull Streak", unsafe_allow_html=True)
    max_streak_bull, max_date_bull, min_date_bull = candle.bull_streak()
    st.metric(label=f"{min_date_bull} - {max_date_bull}", value = f"{max_streak_bull} Days")


    