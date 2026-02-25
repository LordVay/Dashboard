import pandas as pd
from create_table import get_engine

engine = get_engine()
class LTOverview:
    def __init__(self, name):
        crypto_tables = {"btc", "eth"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name

    def timeframe(self, time): # 15d 1M 6M 1Y 5Y Max
        date = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )

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

    def check_graph_specyear(self, year):
        spec_yeardata = pd.read_sql(sql = f"""SELECT * FROM {self.name} WHERE date LIKE '%{year}%'""", con = engine)

        if not spec_yeardata.empty:
            spec_yeardata = spec_yeardata.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date")["USDollars"]
            return spec_yeardata
        else:
            return None
    
    def check_graph_specmonthyear(self,month,year): 
        double_int_month = f"{month:02}"
        spec_monthyeardata = pd.read_sql(sql = f"""SELECT * FROM btc""", con = engine)
        if not spec_monthyeardata.empty:
            spec_monthyeardata["date"] = pd.to_datetime(spec_monthyeardata["date"])
            spec_monthyeardata = spec_monthyeardata.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date")["USDollars"]
            spec_monthyeardata = spec_monthyeardata[(spec_monthyeardata.index.year == int(year))&(spec_monthyeardata.index.month == int(double_int_month))]
            return spec_monthyeardata
        else:
            return None
    
    def check_all_time_high(self):
        all_timehigh = pd.read_sql(sql = f"""SELECT date, close FROM {self.name} WHERE close = (SELECT MAX(close) FROM {self.name})""", con = engine)
        if not all_timehigh.empty:
            max_value = all_timehigh.loc[0, "close"]
            max_date = all_timehigh.loc[0, "date"]
            return max_value, max_date
        else:
            return None
        
        
    def check_best_year(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        yearly = (
            dataframe["USDollars"]
            .groupby(dataframe.index.year)
            .agg(["first", "last"])
        )

        yearly["pct_change"] = (
            (yearly["last"] - yearly["first"]) / yearly["first"] * 100
        )

        best_year = yearly["pct_change"].idxmax()
        best_value = yearly["pct_change"].max()

        return best_year, float(best_value)

    def worst_year(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        yearly = (
            dataframe["USDollars"]
            .groupby(dataframe.index.year)
            .agg(["first", "last"])
        )

        yearly["pct_change"] = (
            (yearly["last"] - yearly["first"]) / yearly["first"] * 100
        )

        worst_year = yearly["pct_change"].idxmin()
        worst_value = yearly["pct_change"].min()

        return worst_year, float(worst_value)

   