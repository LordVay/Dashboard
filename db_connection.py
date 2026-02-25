import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
news_key = os.getenv("NEWS_API")

if not news_key:
    raise ValueError("API key not found in environment variables.")

def get_news():
    url = "https://cryptopanic.com/api/developer/v2/posts/"

    params = {
    "auth_token": news_key,
    "currencies": "BTC",   # filter by coin
    "public" : "true"        # optional filter
    
    }

    response = requests.get(url, params=params)

    data = response.json()
    


<<<<<<< HEAD

engine = get_engine()

def tries(time):
    date = pd.read_sql(sql = f"""SELECT * FROM btc""", con = engine )

    if date.empty:
        return None
            
    timeframe = {
            "15D": 15,
            "1M": 30,
            "6M": 180,
            "1Y": 365,
            "5Y": 365 * 5,
            "Max": len(date)
            }

    if time not in timeframe:
        raise ValueError(f"Invalid time: {time}")  
            
    dataframe = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(timeframe[time])["USDollars"]
    return dataframe


def check_graph_specyear(year):
        spec_yeardata = pd.read_sql(sql = f"""SELECT * FROM btc WHERE date LIKE '%{year}%'""", con = engine)

        if not spec_yeardata.empty:
            spec_yeardata = spec_yeardata.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date")["USDollars"]
            return spec_yeardata
        else:
            return None

def check_graph_specmonthyear(month,year):
        double_int_month = f"{month:02}"
        spec_monthyeardata = pd.read_sql(sql = f"""SELECT * FROM btc""", con = engine)
        if not spec_monthyeardata.empty:
            spec_monthyeardata["date"] = pd.to_datetime(spec_monthyeardata["date"])
            spec_monthyeardata = spec_monthyeardata.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date")["USDollars"]
            spec_monthyeardata = spec_monthyeardata[(spec_monthyeardata.index.year == int(year))&(spec_monthyeardata.index.month == int(double_int_month))]
            return spec_monthyeardata
        else:
            return None
=======
>>>>>>> ffd199a6c81346cadaa27cb29e6a9e3f09c559ca
