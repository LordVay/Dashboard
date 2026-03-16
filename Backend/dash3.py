import pandas as pd
from create_table import get_engine


engine = get_engine()

class Candle:
    def __init__(self, name):
        crypto_tables = {"btc", "eth", "ada", "bnb", "doge", "sol", "trx", "usdc", "usdt", "xrp"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name
    
    def bullvsbear(self, time): # Verified
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
        timeframe = {
        "15D": 15,
        "1M": 30,
        "6M": 180,
        "1Y": 365,
        "5Y": 365 * 5,
        "Max": len(dataframe)
        }

        data = dataframe["Candle_Type"].tail(timeframe[time]).value_counts()

        size_bull = data.get("Bull", 0)
        size_bear = data.get("Bear", 0)
        size_doji = data.get("Doji", 0)

        size = [size_bull, size_bear, size_doji]
        return  size
    
    def candle_stick(self, time): # Verified but needs to simplify
        dataframe = pd.read_sql(f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        
        dataframe["Body"] = (dataframe["Close"] - dataframe["Open"]).abs()
        dataframe["Upper_Wick"] = dataframe["High"] - dataframe[["Open","Close"]].max(axis=1)
        dataframe["Lower_Wick"] = dataframe[["Open","Close"]].min(axis=1) - dataframe["Low"]


        parts = pd.DataFrame({
        "Body": dataframe["Body"],
        "Upper_Wick": dataframe["Upper_Wick"],
        "Lower_Wick": dataframe["Lower_Wick"]
        }, index=dataframe.index)
        parts = parts.div(parts.sum(axis=1), axis=0)

        timeframe = {
        "15D": 15,
        "1M": 30,
        "6M": 180,
        "1Y": 365,
        "5Y": 365 * 5,
        "Max": len(dataframe)
        }

        parts = parts.tail(timeframe[time])
        return parts
    
    def bull_streak(self): # Verified
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        
        dataframe["Candle_Type"] = dataframe.apply(
                                                        lambda row: "Bull" if row["Close"] > row["Open"] 
                                                                    else "Bear" if row["Close"] < row["Open"] 
                                                                    else "Doji",
                                                        axis=1
                                                    )
        bull_int = (dataframe["Candle_Type"] == "Bull").astype(int)
        dataframe["bull_streak"] = bull_int.groupby((dataframe["Candle_Type"] != "Bull").cumsum()).cumsum()


        max_streak_bull = dataframe["bull_streak"].max()
        max_date_bull = dataframe["bull_streak"].idxmax().strftime("%Y-%m-%d")
        min_date_bull = dataframe.loc[:max_date_bull].iloc[-max_streak_bull].name.strftime("%Y-%m-%d")


        return max_streak_bull, max_date_bull, min_date_bull
    
    def bear_streak(self): # verified
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())
        
        dataframe["Candle_Type"] = dataframe.apply(
                                                        lambda row: "Bull" if row["Close"] > row["Open"] 
                                                                    else "Bear" if row["Close"] < row["Open"] 
                                                                    else "Doji",
                                                        axis=1
                                                    )
        
        bear_int = (dataframe["Candle_Type"] == "Bear").astype(int)
        dataframe["bear_streak"]= bear_int.groupby((dataframe["Candle_Type"] != "Bear").cumsum()).cumsum()

        max_streak_bear = dataframe["bear_streak"].max()
        max_date_bear = dataframe["bear_streak"].idxmax().strftime("%Y-%m-%d")
        min_date_bear = dataframe.loc[:max_date_bear].iloc[-max_streak_bear].name.strftime("%Y-%m-%d")


        return max_streak_bear, max_date_bear, min_date_bear
