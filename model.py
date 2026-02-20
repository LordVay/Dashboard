import pandas as pd
from create_table import get_engine


engine = get_engine()
class Train:
    def __init__(self, name):
        self.name = name

    def train_model(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}))
        dataframe["Date"] = pd.to_datetime(dataframe["Date"]).sort_values("Date")
        dataframe.set_index("Date", inplace=True)

        return dataframe

    


