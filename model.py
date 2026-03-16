import pandas as pd
from create_table import get_engine


engine = get_engine()

class Models:
    def __init__ (self, number_days, name):
        self.number_days = number_days
        crypto_tables = {"btc", "eth", "ada", "bnb", "doge", "sol", "trx", "usdc", "usdt", "xrp"}
        if name not in crypto_tables:
            raise ValueError("Not Valid")
        self.name = name

    def clean_dataset(self):
        dataframe = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine)
        if dataframe.empty:
            return None
        dataframe =(dataframe.rename(columns={"low": "Low", "high": "High", "date": "Date", "close": "Close", "open": "Open"}).set_index("Date").sort_index())


        for i in range(1, self.number_days):
            dataframe[f"Log_ {i}"] = dataframe["Close"].shift(i)
        
        for i in range(1, 16):
            dataframe[f"Target_{i}"] = dataframe["Close"].shift(-i)

        dataframe["return"] = dataframe["Close"].pct_change()
        dataframe["movingav_20"] = dataframe["Close"].rolling(20).mean()
        dataframe["movingav_50"] = dataframe["Close"].rolling(50).mean()
        dataframe["movingav_100"] = dataframe["Close"].rolling(100).mean()
        dataframe["vol_10"] = dataframe["Close"].rolling(10).std()
        dataframe["vol_20"] = dataframe["Close"].rolling(20).std()

        dataframe.drop(["ticker", "Close", "High", "Open", "Low"], axis = 1, inplace = True)
        dataframe.dropna(inplace=True)

        train_size = int(len(dataframe) * 0.8)
        train = dataframe.iloc[:train_size]
        test = dataframe.iloc[train_size:]

        X_train = train.drop([f"Target_{i}" for i in range(1, 16)] , axis=1)
        y_train = train[[f"Target_{i}" for i in range(1, 16)]]
        X_test = test.drop([f"Target_{i}" for i in range(1, 16)],axis=1)
        y_test = test[[f"Target_{i}" for i in range(1, 16)]]
        
        return X_train, y_train, X_test, y_test

    def train_model(self):
        X_train, y_train, X_test, y_test = self.clean_dataset()
        model = XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8
        )
        
        model.fit(X_train, y_train)
        model.save_model(f"XGB {self.name} model {self.number_days}.json")
        
    def test_model(self):
        _, _, X_test, _ = self.clean_dataset()
        loaded_model = XGBRegressor()
        loaded_model.load_model(f"XGB {self.name} model {self.number_days}.json")

        preds = loaded_model.predict(X_test)

        return preds
    
    def eval_rmse(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        prediction = pd.DataFrame(prediction)
        rmse = np.sqrt(mean_squared_error(y_test, prediction))
        return rmse
    
    def eval_mae(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        prediction = pd.DataFrame(prediction)
        mae = mean_absolute_error(y_test, prediction)
        return mae
    
    def eval_r_squared(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        prediction = pd.DataFrame(prediction)
        r2score = r2_score(y_test, prediction)
        return r2score

    def directional_accuracy(self):
        _, _, _, y_test = self.clean_dataset()
        prediction = self.test_model()
        prediction = pd.DataFrame(prediction)
        actual_direction = np.sign(np.diff(y_test))
        predicted_direction = np.sign(np.diff(prediction))
        correct = (actual_direction == predicted_direction)
        da = np.mean(correct) * 100
        return da

    


