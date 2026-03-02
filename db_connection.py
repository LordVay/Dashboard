import requests
import pandas as pd
from dotenv import load_dotenv
import os
import pandas as pd
from create_table import get_engine
import numpy as np


load_dotenv()
api_key = os.getenv("API_KEY")
news_key = os.getenv("NEWS_API")

print(api_key)
print(news_key)

def get_news():
    url = "https://cryptopanic.com/api/developer/v2/posts/"

    params = {
    "auth_token": news_key,
    "currencies": "BTC",   # filter by coin
    "public" : "true"        # optional filter
    
    }
    response = requests.get(url, params=params)

    data = response.json()

    data_array = data["results"]

    return data_array

array = get_news()
print(array)
