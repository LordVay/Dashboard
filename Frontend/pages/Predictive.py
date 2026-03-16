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

    if train_coin:
        st.status("Training on process...⏳")
        model = Models(number_days=predict_days, name = cryptocurrency_data[cryptocurrency] )
        model.train_model()
        st.status("Tuning HyperParameters...⏳")
        st.status("Updated Model")

with col2:
    if predict_coin:
        time_graph = model.timeframe(timeframe) # Timeframe

        prediction = model.forecast()
        concatinate_graph = pd.concat([time_graph, prediction])

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.plot(time_graph.index, time_graph.values, color='steelblue', label='Historical', linewidth=2)
        ax.plot(prediction.index, prediction.values, color='tomato', label='Predicted', linewidth=2, linestyle='--')

        ax.set_title(f"{cryptocurrency_data[cryptocurrency]} Price Forecast", fontsize=14)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)



