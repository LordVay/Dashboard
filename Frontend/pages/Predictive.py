import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Model.train_model_crypto import Models
from Database.OHLC_fetch import Fetch
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
    
    model = Models(number_days=convert_days[predict_days], name=cryptocurrency_data[cryptocurrency])
    update = Fetch(name=cryptocurrency_data[cryptocurrency])

    update_button = update.check_updated()

    train_coin = st.button("Train model", width="stretch")
    eval_coin  = st.button("Evaluate", width="stretch")
    predict_coin = st.button("Predict", width="stretch")
    update_data = st.button("Update Data", width="stretch", disabled= update_button)
    
    if update_data:
        with st.status("Updating OHLC Data...", expanded=True) as status:
            update.append_table()
            status.update(label="Data Updated!", state="complete", expanded=False)
    
    if train_coin:
        with st.status("Training on process... ", expanded=True) as status:
            st.write("Tuning HyperParameters...")
            model.train_model()
            status.update(label="Model Updated!", state="complete", expanded=False)
    

with col2:
    if predict_coin:
        time_graph = model.timeframe(timeframe)
        time_graph.index = pd.to_datetime(time_graph.index)

        prediction = model.forecast()
        prediction = prediction.tail(convert_days[predict_days]) 
        prediction.index = pd.to_datetime(prediction.index)

        print(time_graph)
        print(prediction)

        connect_point = pd.Series([time_graph.iloc[-1]], index=[time_graph.index[-1]])
        prediction_connected = pd.concat([connect_point, prediction])

        st.session_state["time_graph"] = time_graph
        st.session_state["prediction_connected"] = prediction_connected
        st.session_state["crypto_name"] = cryptocurrency_data[cryptocurrency]

    if "time_graph" in st.session_state:
        time_graph = st.session_state["time_graph"]
        prediction_connected = st.session_state["prediction_connected"]
        crypto_name = st.session_state["crypto_name"]

        fig2, ax2 = plt.subplots(figsize = (12, 5))
        fig2.patch.set_facecolor("none") 
        ax2.set_facecolor("none")
        ax2.plot(time_graph.index, time_graph.values, color='steelblue', label='Historical', linewidth=2)
        ax2.set_title(f"{(cryptocurrency_data[cryptocurrency]).upper()} Price History", fontsize=14, color = "white")
        ax2.set_xlabel("Date", color = "white")
        ax2.set_ylabel("Price", color = "white")
        ax2.tick_params(axis='x', rotation=90, color = "white", labelcolor = "white")
        ax2.tick_params(axis='y', color = "white", labelcolor = "white")
        ax2.legend(labelcolor='white', facecolor='none', edgecolor='white')
        for spine in ax2.spines.values():
            spine.set_edgecolor('white')
        st.pyplot(fig2)

        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor("none") 
        ax.set_facecolor("none")
        ax.plot(time_graph.index, time_graph.values, color='steelblue', label='Historical', linewidth=2)
        ax.plot(prediction_connected.index, prediction_connected.values, color='tomato', label='Predicted', linewidth=2, linestyle='--')
        ax.set_title(f"{crypto_name.upper()} Price Forecast", fontsize=14, color = "white")
        ax.set_xlabel("Date", color = "white")
        ax.set_ylabel("Price", color = "white")
        ax.tick_params(axis='x', rotation=90, color = "white", labelcolor = "white")
        ax.tick_params(axis='y', color = "white", labelcolor = "white")
        ax.legend(labelcolor='white', facecolor='none', edgecolor='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        st.pyplot(fig)

if eval_coin:
    rmse_data = model.eval_rmse()
    mape_data = model.eval_mape()
    r2_data = model.eval_r_squared()
    da_data = model.directional_accuracy()

    st.session_state["rmse_data"] = rmse_data
    st.session_state["mape_data"] = mape_data
    st.session_state["r2_data"] = r2_data
    st.session_state["da_data"] = da_data

if "rmse_data" in st.session_state:
    rmse_data = st.session_state["rmse_data"] 
    mape_data = st.session_state["mape_data"]
    r2_data = st.session_state["r2_data"]
    da_data = st.session_state["da_data"] 

    colw , colx = st.columns([0.5 ,0.5], border=True, gap = "small")
    with colw:
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>RMSE</p>", unsafe_allow_html=True )
        st.line_chart(data = rmse_data, x_label= "Day", y_label= "MAE", width="stretch")

    with colx:
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>MAPE</p>", unsafe_allow_html=True )
        st.line_chart(data = mape_data, x_label= "Day", y_label= "MAPE", width="stretch")

    coly , colz = st.columns([0.5 ,0.5], border=True, gap = "small")
    with coly:
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>R-Squared</p>", unsafe_allow_html=True )
        st.line_chart(data = r2_data, x_label= "Day", y_label= "R-Squared", width="stretch")

    with colz:
        st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Directional Accuracy</p>", unsafe_allow_html=True )
        st.line_chart(data = da_data, x_label= "Day", y_label= "Directional Accuracy", width="stretch")


