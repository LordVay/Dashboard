import os
import pandas as pd
import mysql.connector as mc
from create_table import get_engine
import numpy as np


engine = get_engine()

data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine)
dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
dataframe['log_return'] = np.log(dataframe['Close'] / dataframe['Close'].shift(1))
dataframe['vol_30d'] = dataframe['log_return'].rolling(window=30).std() * np.sqrt(365)

latest_vol = dataframe['vol_30d'].iloc[-1]
print("Latest 30-day Volatility:", latest_vol)