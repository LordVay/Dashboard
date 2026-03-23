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

    convert_days = {
        "10D":10,
        "15D":15,
        "30D":30
    }

    if not predict_days:
        raise ValueError("Not a day to predict")
    
    timeframe = st.selectbox("Timeframe", ["15D", "1M", "6M"])
    if not timeframe:
        raise ValueError("Not a timeframe")
    
    train_coin = st.button("⚡Train model", width="stretch")
    eval_coin  = st.button("📊 Evaluate", width="stretch")
    predict_coin = st.button("💭 Predict", width="stretch")
    update_data = st.button("✏️ Update Data", width="stretch")
    model = Models(number_days=convert_days[predict_days], name=cryptocurrency_data[cryptocurrency])

    if train_coin:
        with st.status("Training on process... ⏳", expanded=True) as status:
            st.write("Tuning HyperParameters...")
            model.train_model()
            
            status.update(label="✅ Model Updated!", state="complete", expanded=False)

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
if eval_coin:
    colw , colx = st.columns([0.5 ,0.5], border=True, gap = "small")

    with colw:
        mae_data = model.eval_mae()
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>MAE</p>", unsafe_allow_html=True )
        st.area_chart(data = mae_data, x_label= "Day", y_label= "MAE", width="stretch")

    with colx:
        mape_data = model.eval_mape()
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>MAPE</p>", unsafe_allow_html=True )
        st.line_chart(data = mape_data, x_label= "Day", y_label= "MAPE", width="stretch")

    coly , colz = st.columns([0.5 ,0.5], border=True, gap = "small")

    with coly:
        r2_data = model.eval_r_squared()
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>R-Squared</p>", unsafe_allow_html=True )
        st.line_chart(data = r2_data, x_label= "Day", y_label= "R-Squared", width="stretch")

    with colz:
        da_data = model.directional_accuracy()
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Directional Accuracy</p>", unsafe_allow_html=True )
        st.line_chart(data = da_data, x_label= "Day", y_label= "Directional Accuracy", width="stretch")


