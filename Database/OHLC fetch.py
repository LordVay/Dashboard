import requests
import pandas as pd
from dotenv import load_dotenv
import sys ,os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from create_table import get_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Backend.dash4 import get_updated_data

engine = get_engine()

class Fetch:
    def __init__(self, name):
        crypto_tables = {"btc", "eth", "ada", "bnb", "doge", "sol", "trx", "usdc", "usdt", "xrp"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name
    
    def fetch_update(self):
        
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        data_range["date"] = pd.to_datetime(data_range["date"])
        dataframe =data_range.set_index("date").sort_index()

        currency_id = {
            "btc":"bitcoin",
            "eth":"ethereum",
            "ada":"cardano",
            "bnb":"binancecoin",
            "doge":"dogecoin",
            "sol":"solana",
            "trx":"tron",
            "usdc":"usd-coin",
            "usdt":"tether",
            "xrp":"ripple"

        }
        current_time = datetime.today().date()
        last_time = dataframe.index[-1]
        days_interval = (current_time - (last_time.date())).days

        fetched_data = get_updated_data(currency=currency_id[self.name], days=days_interval)


        date_array = [last_time.date() + timedelta(days = i) for i in range((days_interval) + 1)]

        ohlc_array = []
        for i in date_array:

            specific_date_data = fetched_data[fetched_data["date"] == i]

            ohlc = {
            "ticker": (self.name).upper(),
            "date": i,
            "open": round(specific_date_data["price"].iloc[0], 2),
            "high": round(specific_date_data["price"].max(), 2),
            "low": round(specific_date_data["price"].min(), 2),
            "close": round(specific_date_data["price"].iloc[-1], 2)
            }
            
            ohlc_array.append(ohlc)
        ohlc_dataframe = pd.DataFrame(ohlc_array)
        ohlc_dataframe = ohlc_dataframe.iloc[1:]
        
        return ohlc_dataframe
        
    def append_table(self):
        data = self.fetch_update()
        data.to_sql(
            name = self.name,
            con=engine,
            if_exists="append",
            index=False
        )
    
    def check_updated(self):
        dataframe = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe =dataframe.set_index("date").sort_index()

        last_time = dataframe.index[-1]
        last_date = last_time.date()
        current_date = datetime.today().date()

        if current_date == last_date:
            return True
        else:
            return False

