import os
import pandas as pd
import mysql.connector as mc
from create_table import get_engine
from model import Train


engine = get_engine()

model = Train("btc")
data = model.train_model()
print(data)
