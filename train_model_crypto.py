import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from create_table import create_engine
from xgboost import XGBRegressor

engine = create_engine()

class Model:
    def __init__ (self, number_days, name):
        self.number_days = number_days
        crypto_tables = {"btc", "eth"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name

    def clean_dataset(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine)
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date", inplace= True))


        for i in range(1, self.number_days):
            dataframe[f"Log_ {i}"] = dataframe["Close"].shift(i)
        
        dataframe["Target"] = dataframe["Close"].shift(-1)

        dataframe["return"] = dataframe["Close"].pct_change()
        dataframe["movingav_5"] = dataframe["Close"].rolling(5).mean()
        dataframe["movingav_10"] = dataframe["Close"].rolling(10).mean()
        dataframe["vol_10"] = dataframe["Close"].rolling(10).std()

        dataframe.dropna(inplace=True)

        train_size = int(len(dataframe) * 0.8)
        train = dataframe.iloc[:train_size]
        test = dataframe.iloc[train_size:]

        X_train = train.drop(["target", "Close"], axis=1)
        y_train = train["target"]

        X_test = test.drop(["target", "Close"], axis=1)
        y_test = test["target"]
        
        return X_train, y_train, X_test, y_test

    def train_model(self):
        X_train, y_train, X_test, y_test = self.clean_dataset()
        model = XGBRegressor(
            n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42
        )
        
        model.fit(X_train, y_train)
        model.save_model(f"XGB {self.name} model.json")
        
    def test_model(self):
        _, _, X_test, _ = self.clean_dataset()
        loaded_model = XGBRegressor()
        loaded_model.load_model(f"XGB {self.name} model.json")

        preds = loaded_model.predict(X_test)

        return preds
    
    def eval_rmse(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        rmse = np.sqrt(mean_squared_error(prediction, y_test))
        return rmse
    
    def eval_mae(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        mae = mean_absolute_error(prediction, y_test)
        return mae
    
    def eval_r_squared(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        r2score = r2_score(prediction, y_test)
        return r2score