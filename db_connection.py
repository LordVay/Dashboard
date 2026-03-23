import pandas as pd
import requests
from Model.train_model_crypto import Models
from create_table import get_engine


model = Models(15, "btc")
data = model.eval_r_squared()
print(data)

