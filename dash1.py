import pandas as pd
from create_table import get_engine

engine = get_engine()
class LTOverview:
    def __init__(self, name):
        self.name = name

    def timeframe(self, time): # 15d 1M 6M 1Y 5Y Max
        date = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if not date.empty:
            if time == "15D":
                date15D = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(15)["USDollars"]
                return date15D
            if time == "1M":
                date1M = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(30)["USDollars"]
                return date1M
            if time == "6M":
                date6M = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(180)["USDollars"]
                return date6M
            if time == "1Y":
                date1Y = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(365)["USDollars"]
                return date1Y
            if time == "5Y":
                date5Y = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(1825)["USDollars"]
                return date5Y
            if time == "Max":
                Max = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(date["USDollars"].count())["USDollars"]
                return Max
        else:
            return None

    def check_graph_specyear(self, year):
        spec_yeardata = pd.read_sql(sql = f"""SELECT * FROM {self.name} WHERE date LIKE '%{year}%'""", con = engine)

        if not spec_yeardata.empty:
            spec_yeardata = spec_yeardata.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date")["USDollars"]
            return spec_yeardata
        else:
            return None
    
    def check_graph_specmonthyear(self,month,year):
        spec_monthyeardata = pd.read_sql(sql = f"""SELECT * FROM {self.name} WHERE date LIKE '%{year}-__-{month}%'""", con = engine)
        if not spec_monthyeardata.empty:
            spec_monthyeardata = spec_monthyeardata.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date")["USDollars"]
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
        max_value = 0
        distinct_year = pd.read_sql(sql = f"""SELECT DISTINCT YEAR(date) AS date FROM {self.name}""", con = engine)
        array_year = distinct_year["date"].to_numpy()
       
        for year in array_year:
            check_best = pd.read_sql(sql = f"""SELECT close FROM {self.name} WHERE date LIKE '%{year}%' """, con=engine)
            first_value = check_best.iloc[0]
            last_value = check_best.iloc[-1]
            percent_increase = ((last_value - first_value)/first_value)*100

            if percent_increase > max_value:
                max_value = percent_increase
        
        return max_value

    def worst_year(self):
        min_value = float('inf')
        distinct_year = pd.read_sql(sql = f"""SELECT DISTINCT YEAR(date) AS date FROM {self.name}""", con = engine)
        array_year = distinct_year["date"].to_numpy()
       
        for year in array_year:
            check_best = pd.read_sql(sql = f"""SELECT close FROM {self.name} WHERE date LIKE '%{year}%' """, con=engine)
            first_value = check_best.iloc[0]
            last_value = check_best.iloc[-1]
            percent_increase = ((last_value - first_value)/first_value)*100

            if percent_increase > min_value:
                max_value = percent_increase
        
        return min_value