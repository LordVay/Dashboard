import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
news_key = os.getenv("NEWS_API")

if not news_key:
    raise ValueError("API key not found in environment variables.")

def get_news():
    url = "https://cryptopanic.com/api/developer/v2/posts/"

    params = {
    "auth_token": news_key,
    "currencies": "BTC",   # filter by coin
    "public" : "true"        # optional filter
    
    }

    response = requests.get(url, params=params)

    data = response.json()
    


