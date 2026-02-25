import pandas as pd
from create_table import get_engine


engine = get_engine()

class Candle:
    def __init__(self, name):
        crypto_tables = {"btc", "eth"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name
    
    def bullvsbear(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        dataframe["Candle_Type"] = dataframe.apply(
                                                        lambda row: "Bull" if row["Close"] > row["Open"] 
                                                                    else "Bear" if row["Close"] < row["Open"] 
                                                                    else "Doji",
                                                        axis=1
                                                    )
        data = dataframe["Candle_Type"].value_counts()
        
        return data
    
    def candle_stick(self):
        dataframe = pd.read_sql(f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        parts = pd.DataFrame({
        "Body": dataframe["Body"],
        "Upper_Wick": dataframe["Upper_Wick"],
        "Lower_Wick": dataframe["Lower_Wick"]
        }, index=dataframe.index)
        parts = parts.div(parts.sum(axis=1), axis=0)

        return parts
    def bull_streak(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        bull_int = (dataframe["Candle_Type"] == "Bull").astype(int)
        bull_streak = bull_int.groupby((dataframe["Candle_Type"] != "Bull").cumsum()).cumsum()

        return bull_streak
    
    def bear_streak(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        bear_int = (dataframe["Candle_Type"] == "Bear").astype(int)
        bear_streak = bear_int.groupby((dataframe["Candle_Type"] != "Bear").cumsum()).cumsum()

        return bear_streak
