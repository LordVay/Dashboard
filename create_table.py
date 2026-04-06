import os
import pandas as pd
import mysql.connector as mc
from sqlalchemy import create_engine

analog = 'mysql+mysqlconnector://root:Ballesteros14*@localhost:3306/Dashboard'
my_comp = 'mysql+mysqlconnector://dashboard_user:Ballesteros14@localhost:3306/Dashboard'

engine = create_engine(analog)
folder_path = r"C:\Users\VBallest\OneDrive - Analog Devices, Inc\Desktop\Dashboard\Cryptodataset"

import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

def get_engine():

    host     = st.secrets["DB_HOST"]
    port     = st.secrets["DB_PORT"]
    user     = st.secrets["DB_USER"]
    password = st.secrets["DB_PASSWORD"]
    database = st.secrets["DB_NAME"]

    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}?ssl_ca=ca.pem"
    return create_engine(url)

def create_tables(engine, folder_path):
        for csv in os.listdir(folder_path):
                csv_path = os.path.join(folder_path,csv)
                dataframe = pd.read_csv(csv_path)
                
                name = csv.replace(".csv", "").lower()
                dataframe.to_sql(name = name, 
                                con=engine,
                                if_exists='replace', 
                                index=False)



