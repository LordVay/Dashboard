import requests
import pandas as pd
from dotenv import load_dotenv
import os
import pandas as pd
from create_table import get_engine
import numpy as np

engine = get_engine()

def month_heatmap(year):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM btc""", con = engine )
        if dataframe.empty:
            return None
        
        dataframe['date'] = pd.to_datetime(dataframe['date'])
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())

        dataframe['year'] = dataframe.index.year
        dataframe['month'] = dataframe.index.month

        monthly_return = (
            dataframe.groupby(['year', 'month'])
            .apply(lambda x: (x['Close'].iloc[-1] - x['Close'].iloc[0]) / x['Close'].iloc[0])
            .reset_index(name='monthly_return')
        )

        # Pivot for heatmap
        heatmap_data = monthly_return.pivot(index='year',
                                            columns='month',
                                            values='monthly_return')

        # Rename month numbers
        heatmap_data.columns = ['Jan','Feb','Mar','Apr','May','Jun',
                                'Jul','Aug','Sep','Oct','Nov','Dec']
        
        year_heatmap = heatmap_data.loc[year]
        return year_heatmap

data= month_heatmap(2020)
print(data)
