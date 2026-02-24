import pandas as pd
from create_table import get_engine


engine = get_engine()

class Heat_Map:
    def __init__(self, name):
        crypto_tables = {"btc", "eth"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name

    def month_heatmap(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())

        dataframe['Date'] = pd.to_datetime(dataframe['Date'])
        dataframe = dataframe.sort_values('date')

        dataframe['year'] = dataframe['date'].dataframe.year
        dataframe['month'] = dataframe['date'].dataframe.month

        monthly_return = (
            dataframe.groupby(['year', 'month'])
            .apply(lambda x: (x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0])
            .reset_index(name='monthly_return')
        )

        # Pivot for heatmap
        heatmap_data = monthly_return.pivot(index='year',
                                            columns='month',
                                            values='monthly_return')

        # Rename month numbers
        heatmap_data.columns = ['Jan','Feb','Mar','Apr','May','Jun',
                                'Jul','Aug','Sep','Oct','Nov','Dec']
        
        return heatmap_data
            
