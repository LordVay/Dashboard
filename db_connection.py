import os
import pandas as pd
import mysql.connector as mc
from create_table import get_engine


engine = get_engine()

dataframe = pd.read_sql(sql = "SELECT date from btc", con = engine)
print(dataframe)