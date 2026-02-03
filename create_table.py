import os
import pandas as pd
import mysql.connector as mc
from sqlalchemy import create_engine


engine = create_engine('mysql+mysqlconnector://root:Ballesteros14*@localhost:3306/Dashboard')
folder_path = r"C:\Users\VBallest\OneDrive - Analog Devices, Inc\Desktop\Dashboard\Cryptodataset"

def get_engine():
        return engine

def create_tables(engine, folder_path):
        for csv in os.listdir(folder_path):
                csv_path = os.path.join(folder_path,csv)
                dataframe = pd.read_csv(csv_path)
                name = csv.replace(".csv", "").lower()

                dataframe.to_sql(name = name, 
                                con=engine,
                                if_exists='replace', 
                                index=False)



