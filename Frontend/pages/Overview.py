import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Backend.dash1 import LTOverview
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
year_ranges = {
            "Bitcoin (BTC)" : list(range(2010, 2027)), 
            "Cardona (ADA)" : list(range(2017, 2027)), 
            "Binance (BNB)" : list(range(2017, 2027)), 
            "Dogecoin (DOGE)" : list(range(2016, 2027)), 
            "Ethereum (ETH)" : list(range(2015, 2027)),
            "Solana (SOL)" : list(range(2020, 2027)), 
            "TRON (TRX)" : list(range(2017, 2027)), 
            "USDC (USDC)" : list(range(2018, 2027)), 
            "Tether (USDT)" : list(range(2017, 2027)), 
            "XRP (XRP)" : list(range(2015, 2027))
            }


months = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

col1 , col2 = st.columns([0.3 ,0.7], border=True, gap = "small")

with col1:
    cryptocurrency = st.selectbox("Currency", ["Bitcoin (BTC)", "Cardona (ADA)", "Binance (BNB)", "Dogecoin (DOGE)", "Ethereum (ETH)",
                                           "Solana (SOL)", "TRON (TRX)", "USDC (USDC)", "Tether (USDT)", "XRP (XRP)"])
    year_array = year_ranges.get(cryptocurrency, [])
    if not cryptocurrency:
        raise ValueError("Not a Cryptocurrency")
    
    timeframe = st.selectbox("Timeframe", ["15D", "1M", "6M", "1Y", "5Y", "Max"])
    if not timeframe:
        raise ValueError("Not a timeframe")

    year = st.selectbox("Year", year_array)
    if not year:
        raise ValueError("Not a Year")

    month = st.selectbox("Month",[
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ])
    if not month:
        raise ValueError("Not a month")

with col2 :

    overview = LTOverview(cryptocurrency_data[cryptocurrency])
    data = overview.timeframe(timeframe)
    st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Timeframe: {timeframe}</p>", unsafe_allow_html=True )
    st.line_chart(data = data, x_label= "Date", y_label= "USDollars", width="stretch")

coly, colm = st.columns([2,2], border=True)
with coly:
    year_graph = overview.check_graph_specyear(year)
    st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Year</p>", unsafe_allow_html=True )
    st.line_chart(data = year_graph, x_label= "Date", y_label= "USDollars", width="stretch")
with colm:
    month_year_graph = overview.check_graph_specmonthyear(months[month], year)
    st.markdown( f"<p style='text-align: center; color: white; font-size:25x;'>Month</p>", unsafe_allow_html=True )
    st.line_chart(data = month_year_graph, x_label= "Date", y_label= "USDollars", width="stretch")   

colm1, colm2, colm3 = st.columns([0.33, 0.33, 0.33])
with colm1:
    max_value, max_date = overview.check_all_time_high()
    st.metric(label= f"{max_date}", value = f"${max_value}", border = True)
    st.markdown("<p style='text-align:center; color:gray;'>All time high</p>", unsafe_allow_html=True)

with colm2:
    best_year, best_value= overview.check_best_year()
    st.metric(label=f"{best_year}",value = f"{int(best_value)}%", border = True)
    st.markdown("<p style='text-align:center; color:gray;'>Best Year</p>", unsafe_allow_html=True)

with colm3:
    worst_year, worst_value = overview.check_worst_year()
    st.metric(label=f"{worst_year}", value = f"{int(worst_value)}%", border = True)
    st.markdown("<p style='text-align:center; color:gray;'>Worst Year</p>", unsafe_allow_html=True)


