import pandas as pd
from create_table import get_engine

engine = get_engine()
class LTOverview:
    def __init__(self, name):
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
    

    """
    engine = get_engine()

class LTOverview:
    def __init__(self, name):
        self.name = name

    # ---------- SINGLE DATA LOADER (BEST PRACTICE) ----------
    def _load_clean_data(self):
        df = pd.read_sql(f"SELECT * FROM {self.name}", con=engine)

        if df.empty:
            return None

        df = (
            df.rename(columns={"close": "USDollars", "date": "Date"})
              .assign(Date=lambda x: pd.to_datetime(x["Date"]))
              .set_index("Date")
              .sort_index()
        )
        return df

    # ---------- YOUR TIMEFRAME METHOD (IMPROVED) ----------
    def timeframe(self, time):
        df = self._load_clean_data()
        if df is None:
            return None

        windows = {
            "15D": 15,
            "1M": 30,
            "6M": 180,
            "1Y": 365,
            "5Y": 365 * 5,
            "Max": len(df)
        }

        if time not in windows:
            raise ValueError(f"Invalid time: {time}")

        return df["USDollars"].tail(windows[time])

    # ---------- SPECIFIC YEAR (IMPROVED, NO LIKE) ----------
    def check_graph_specyear(self, year):
        df = self._load_clean_data()
        if df is None:
            return None

        result = df.loc[df.index.year == int(year), "USDollars"]

        return result if not result.empty else None

    # ---------- SPECIFIC MONTH + YEAR (IMPROVED) ----------
    def check_graph_specmonthyear(self, month, year):
        df = self._load_clean_data()
        if df is None:
            return None

        result = df.loc[
            (df.index.year == int(year)) &
            (df.index.month == int(month)),
            "USDollars"
        ]

        return result if not result.empty else None

    # ---------- ALL-TIME HIGH (IMPROVED) ----------
    def check_all_time_high(self):
        df = self._load_clean_data()
        if df is None:
            return None

        max_value = df["USDollars"].max()
        max_date = df["USDollars"].idxmax()

        return float(max_value), max_date

    # ---------- BEST YEAR (IMPROVED + FASTER) ----------
    def check_best_year(self):
        df = self._load_clean_data()
        if df is None:
            return None

        yearly = (
            df["USDollars"]
            .groupby(df.index.year)
            .agg(["first", "last"])
        )

        yearly["pct_change"] = (
            (yearly["last"] - yearly["first"]) / yearly["first"] * 100
        )

        best_year = yearly["pct_change"].idxmax()
        best_value = yearly["pct_change"].max()

        return best_year, float(best_value)

    # ---------- WORST YEAR (FIXED BUG) ----------
    def worst_year(self):
        df = self._load_clean_data()
        if df is None:
            return None

        yearly = (
            df["USDollars"]
            .groupby(df.index.year)
            .agg(["first", "last"])
        )

        yearly["pct_change"] = (
            (yearly["last"] - yearly["first"]) / yearly["first"] * 100
        )

        worst_year = yearly["pct_change"].idxmin()
        worst_value = yearly["pct_change"].min()

        return worst_year, float(worst_value)
    
    """