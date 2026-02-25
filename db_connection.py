import os
import pandas as pd
import mysql.connector as mc
from create_table import get_engine

import numpy as np

from model import Train



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