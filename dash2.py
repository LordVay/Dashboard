import pandas as pd
from create_table import get_engine


engine = get_engine()

class Volatile:
    def __init__(self, name):
        self.name = name

    def high_low_range (self, time): # 15d 1M 6M 1Y 5Y Max
        data_range = pd.read_sql(sql = f"""SELECT * from {self.name}""", con = engine)
        if not data_range.empty:
            if time == "15D":
                data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
                date15D = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(15)
                date15D["Dailyrange"] = date15D["High"] - date15D["Low"]
                date15D = date15D["Dailyrange"]
                return date15D
            
            if time == "1M":
                data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
                date1M = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(30)
                date1M["Dailyrange"] = date1M["High"] - date1M["Low"]
                date1M = date1M["Dailyrange"]
                return date1M
            
            if time == "6M":
                data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
                date6M = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(180)
                date6M["Dailyrange"] = date6M["High"] - date6M["Low"]
                date6M = date6M["Dailyrange"]
                return date6M
            
            if time == "1Y":
                data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
                date1Y = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(180)
                date1Y["Dailyrange"] = date1Y["High"] - date1Y["Low"]
                date1Y = date1Y["Dailyrange"]
                return date1Y
            
            if time == "5Y":
                data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
                date5Y = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(180)
                date5Y["Dailyrange"] = date5Y["High"] - date5Y["Low"]
                date5Y = date5Y["Dailyrange"]
                return date5Y
            
            if time == "Max":
                data_range = pd.read_sql(sql = f"""SELECT * from btc""", con = engine) 
                Max = data_range.rename(columns={'low': 'Low' , 'date': 'Date', 'high': 'High'}).set_index("Date").tail(180)
                Max["Dailyrange"] = Max["High"] - Max["Low"]
                Max = Max["Dailyrange"]
                return Max

    def volatily_graph(self, volatile_time):
        
    def avg_percentage(self):
        
    def max_1D_percent(self):

    def min_1D_percent(self):