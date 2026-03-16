import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Model.train_model_crypto import Models
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

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
    
    predict_days = st.selectbox("Days to Predict", ["10D" , "15D", "30D"])

    if not predict_days:
        raise ValueError("Not a day to predict")
    
    timeframe = st.selectbox("Timeframe", ["15D", "1M", "6M"])
    if not timeframe:
        raise ValueError("Not a timeframe")
    
    train_coin = st.button("⚡Train model", width="stretch")
    eval_coin  = st.button("📊 Evaluate", width="stretch")
    predict_coin = st.button("💭 Predict", width="stretch")
    update_data = st.button("✏️ Update Data", width="stretch")

with col2:
    if predict_coin:
        model = Models(number_days=predict_days, name = cryptocurrency_data[cryptocurrency] )
        time_graph = model.timeframe(timeframe) # Timeframe

        prediction = model.forecast()
        concatinate_graph = pd.concat([time_graph, prediction])



   


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
