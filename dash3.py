import pandas as pd
from create_table import get_engine


engine = get_engine()

class Candle:
    def __init__(self, name):
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
    
    def candle_stick():
    
    def bull_streak():

    def bear_streak():


"""def bull_streaks(self):
    
    df = self.get_ohlc()

    # 1 if Bull candle, 0 otherwise
    bull_int = (df["Candle_Type"] == "Bull").astype(int)

    # 2. Group by consecutive non-Bull days and compute cumulative sum per group
    bull_streak = bull_int.groupby((df["Candle_Type"] != "Bull").cumsum()).cumsum()

    return bull_streak"""

"""def bear_streaks(self):

    df = self.get_ohlc()

    # 1 if Bear candle, 0 otherwise
    bear_int = (df["Candle_Type"] == "Bear").astype(int)

    # 2. Group by consecutive non-Bear days and compute cumulative sum per group
    bear_streak = bear_int.groupby((df["Candle_Type"] != "Bear").cumsum()).cumsum()

    return bear_streak"""

"""def candle_parts_timeseries(self):
    df = self.get_ohlc()

    parts = pd.DataFrame({
        "Body": df["Body"],
        "Upper_Wick": df["Upper_Wick"],
        "Lower_Wick": df["Lower_Wick"]
    }, index=df.index)

    # Normalize so it shows proportions
    parts = parts.div(parts.sum(axis=1), axis=0)

    return parts"""