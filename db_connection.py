import os
import pandas as pd
import mysql.connector as mc
from create_table import get_engine


engine = get_engine()

data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
date15D = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(15)
date15D["Dailyrange"] = date15D["High"] - date15D["Low"]
date15D = date15D["Dailyrange"]

print(date15D)