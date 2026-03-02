import streamlit as st
from db_connection import tries, check_graph_specyear, check_graph_specmonthyear

st.line_chart(tries("1Y"), x_label= "Date", y_label= "USDollars")
st.line_chart(check_graph_specyear(2015), x_label= "Date", y_label= "USDollars")
st.line_chart(check_graph_specmonthyear(2, 2015), x_label= "Date", y_label= "USDollars")
