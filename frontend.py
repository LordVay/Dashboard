import streamlit as st
from db_connection import get_chart

st.line_chart(get_chart(timeframe=100), x_label= "Date", y_label= "USDollars")

