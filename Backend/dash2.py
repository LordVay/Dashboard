import pandas as pd
from create_table import get_engine
import numpy as np


engine = get_engine()

class Volatile:
    def __init__(self, name):
        crypto_tables = {"btc", "eth"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name

    def high_low_range (self, time): # Verified
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        if data_range.empty:
            return None
        
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date"}).set_index("Date").sort_index())
        dataframe["DailyRange"] = dataframe["High"] - dataframe ["Low"]

        timeframe = {
        "15D": 15,
        "1M": 30,
        "6M": 180,
        "1Y": 365,
        "5Y": 365 * 5,
        "Max": len(data_range)
        }

        if time not in timeframe:
            return ValueError(f"Invalid time: {time}")   

        new_data = dataframe["Daily Range"].tail(timeframe[time])
        return new_data
    
    def volatility_graph(self, volatile_time): #Verified
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        if data_range.empty:
            return None
        dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        dataframe['log_return'] = np.log(dataframe['Close'] / dataframe['Close'].shift(1))
        dataframe[f'vol_{volatile_time}d'] = dataframe['log_return'].rolling(window=volatile_time).std() * np.sqrt(365)

        latest_vol = dataframe[f'vol_{volatile_time}d'].iloc[-1]
        return latest_vol

    def avg_percentage(self): # Verified
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)

        if data_range.empty:
            return None
        
        dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        dataframe["Percentage_change"]  = dataframe["Close"].pct_change() * 100
        avg = dataframe["Percentage_change"].mean()

        return avg
    
    def max_1D_percent(self):# Verified
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        
        if data_range.empty:
            return None
        
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        dataframe["Percentage_change"]  = dataframe["Close"].pct_change() * 100
        max_value = dataframe["Percentage_change"].max()
        max_date = dataframe["Percentage_change"].idxmax()

        return max_value, max_date
    
    def min_1D_percent(self): #Verified
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        
        if data_range.empty:
            return None
        
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe =(data_range.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        dataframe["Percentage_change"]  = dataframe["Close"].pct_change() * 100
        min_value = dataframe["Percentage_change"].min()
        min_date = dataframe["Percentage_change"].idxmin()

        return min_value, min_date