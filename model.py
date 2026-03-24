import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from xgboost import XGBRegressor
from create_table import get_engine
from datetime import timedelta

engine = get_engine()

CRYPTO_TABLES = {"btc", "eth", "ada", "bnb", "doge", "sol", "trx", "usdc", "usdt", "xrp"}

PARAM_GRID = {
    "n_estimators":     [400, 600, 800, 1000],
    "max_depth":        [3, 4, 5, 6],
    "learning_rate":    [0.01, 0.03, 0.05, 0.08],
    "subsample":        [0.6, 0.7, 0.8, 0.9],
    "colsample_bytree": [0.5, 0.6, 0.7, 0.8],
    "min_child_weight": [1, 3, 5],
    "gamma":            [0, 0.05, 0.1, 0.2],
    "reg_alpha":        [0, 0.01, 0.1, 0.5],
    "reg_lambda":       [0.5, 1.0, 1.5, 2.0],
}


class Models:

    def __init__(self, number_days: int, name: str):
        if name not in CRYPTO_TABLES:
            raise ValueError(f"'{name}' is not valid. Choose from: {CRYPTO_TABLES}")
        self.number_days = number_days
        self.name        = name
        self._cache      = None          
        self._scaler     = None        

    def clean_dataset(self):
    
        if self._cache is not None:
            return self._cache

        df = pd.read_sql(f"SELECT * FROM {self.name}", con=engine)
        if df.empty:
            raise ValueError(f"Table '{self.name}' returned no data.")

        df = (df.rename(columns={
                "low": "Low", "high": "High",
                "date": "Date", "close": "Close", "open": "Open"
              })
              .set_index("Date")
              .sort_index())

        for i in range(1, int(self.number_days) + 1):
            df[f"close_lag_{i}"] = df["Close"].shift(i)

        df["return"]         = df["Close"].pct_change().shift(1)
        df["log_return"]     = np.log(df["Close"] / (df["Close"].shift(1) + 1e-9)).shift(1)

        close_s1 = df["Close"].shift(1)
        ret_s1   = df["Close"].pct_change().shift(1)

        for w in [7, 14, 20, 50, 100]:
            df[f"ma_{w}"]      = close_s1.rolling(w).mean()
            df[f"vol_{w}"]     = ret_s1.rolling(w).std()

        df["close_to_ma20"]  = (df["Close"].shift(1) / (df["ma_20"] + 1e-9))
        df["close_to_ma50"]  = (df["Close"].shift(1) / (df["ma_50"] + 1e-9))
        df["close_to_ma100"] = (df["Close"].shift(1) / (df["ma_100"] + 1e-9))

        for w in [14, 30]:
            df[f"roll_min_{w}"] = close_s1.rolling(w).min()
            df[f"roll_max_{w}"] = close_s1.rolling(w).max()

        for period in [7, 14]:
            delta  = df["Close"].diff()
            gain   = delta.clip(lower=0).rolling(period).mean()
            loss   = (-delta.clip(upper=0)).rolling(period).mean()
            df[f"rsi_{period}"] = (100 - (100 / (1 + gain / (loss + 1e-9)))).shift(1)

        ema12              = df["Close"].ewm(span=12, adjust=False).mean()
        ema26              = df["Close"].ewm(span=26, adjust=False).mean()
        macd_raw           = ema12 - ema26
        df["macd"]         = macd_raw.shift(1)
        df["macd_signal"]  = macd_raw.ewm(span=9, adjust=False).mean().shift(1)
        df["macd_hist"]    = (macd_raw - macd_raw.ewm(span=9, adjust=False).mean()).shift(1)

        bb_mid             = df["Close"].rolling(20).mean()
        bb_std             = df["Close"].rolling(20).std()
        bb_upper           = bb_mid + 2 * bb_std
        bb_lower           = bb_mid - 2 * bb_std
        df["bb_width"]     = ((bb_upper - bb_lower) / (bb_mid + 1e-9)).shift(1)
        df["bb_pct"]       = ((df["Close"] - bb_lower) /
                              (bb_upper - bb_lower + 1e-9)).shift(1)

        
        hl   = df["High"] - df["Low"]
        hpc  = (df["High"] - df["Close"].shift(1)).abs()
        lpc  = (df["Low"]  - df["Close"].shift(1)).abs()
        tr   = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)
        for w in [7, 14]:
            df[f"atr_{w}"] = tr.rolling(w).mean().shift(1)

        
        low14          = df["Low"].rolling(14).min()
        high14         = df["High"].rolling(14).max()
        stoch_k        = 100 * (df["Close"] - low14) / (high14 - low14 + 1e-9)
        df["stoch_k"]  = stoch_k.shift(1)
        df["stoch_d"]  = stoch_k.rolling(3).mean().shift(1)

        
        for span in [9, 21, 50, 200]:
            df[f"ema_{span}"] = df["Close"].ewm(span=span, adjust=False).mean().shift(1)
        df["bull_regime"] = (df["Close"].shift(1) > df["ema_200"]).astype(int)

       
        for i in range(1, 16):
            df[f"Target_{i}"] = df["Close"].shift(-i)

        
        cols_to_drop = [c for c in ["ticker", "Close", "High", "Low", "Open"]
                        if c in df.columns]
        df.drop(cols_to_drop, axis=1, inplace=True)
        df.dropna(inplace=True)

        
        split      = int(len(df) * 0.8)
        train      = df.iloc[:split]
        test       = df.iloc[split:]

        target_cols = [f"Target_{i}" for i in range(1, 16)]
        X_train    = train.drop(target_cols, axis=1)
        y_train    = train[target_cols]
        X_test     = test.drop(target_cols, axis=1)
        y_test     = test[target_cols]

        
        scaler         = RobustScaler()
        X_train_sc     = pd.DataFrame(scaler.fit_transform(X_train),
                                      index=X_train.index, columns=X_train.columns)
        X_test_sc      = pd.DataFrame(scaler.transform(X_test),
                                      index=X_test.index,  columns=X_test.columns)
        self._scaler   = scaler
        self._cache    = X_train_sc, y_train, X_test_sc, y_test
        return self._cache

    def train_model(self, tune: bool = True):
       
        X_train, y_train, X_test, y_test = self.clean_dataset()

        if tune:
            tscv = TimeSeriesSplit(n_splits=5)
            base = XGBRegressor(
                objective="reg:squarederror",
                tree_method="hist",
                random_state=42,
                n_jobs=-1,
            )
            search = RandomizedSearchCV(
                estimator=base,
                param_distributions=PARAM_GRID,
                n_iter=30,
                scoring="r2",
                cv=tscv,
                verbose=0,
                random_state=42,
                n_jobs=-1,
            )
            # Tune on Day+1 target, apply best params to all horizons
            search.fit(X_train, y_train["Target_1"])
            best_params = search.best_params_
        else:
            best_params = dict(
                n_estimators=800,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.7,
                min_child_weight=3,
                gamma=0.1,
                reg_alpha=0.1,
                reg_lambda=1.5,
            )

        model = XGBRegressor(
            **best_params,
            objective="reg:squarederror",
            tree_method="hist",
            random_state=42,
            n_jobs=-1,
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        model_path = f"XGB_{self.name}_model_{self.number_days}.json"
        model.save_model(model_path)
        print(f"[{self.name.upper()}] Model saved → {model_path}")
        return model

    def test_model(self) -> pd.DataFrame:
        _, _, X_test, _ = self.clean_dataset()

        model = XGBRegressor()
        model.load_model(f"XGB_{self.name}_model_{self.number_days}.json")

        preds = model.predict(X_test)
        return pd.DataFrame(
            preds,
            index=X_test.index,
            columns=[f"Target_{i}" for i in range(1, 16)],
        )

    def _get_test_and_preds(self):
        _, _, _, y_test = self.clean_dataset()
        preds = self.test_model()
        return y_test, preds

    def eval_rmse(self) -> pd.Series:
        y_test, preds = self._get_test_and_preds()
        return pd.Series(
            [np.sqrt(mean_squared_error(y_test[f"Target_{i}"], preds[f"Target_{i}"]))
             for i in range(1, 16)],
            index=[i for i in range(1, 16)],
            name="RMSE",
        )

    def eval_mae(self) -> pd.Series:
        y_test, preds = self._get_test_and_preds()
        return pd.Series(
            [mean_absolute_error(y_test[f"Target_{i}"], preds[f"Target_{i}"])
             for i in range(1, 16)],
            index=[i for i in range(1, 16)],
            name="MAE",
        )

    def eval_r_squared(self) -> pd.Series:
        y_test, preds = self._get_test_and_preds()
        return pd.Series(
            [r2_score(y_test[f"Target_{i}"], preds[f"Target_{i}"])
             for i in range(1, 16)],
            index=[i for i in range(1, 16)],
            name="R²",
        )

    def eval_mape(self) -> pd.Series:
        y_test, preds = self._get_test_and_preds()
        return pd.Series(
            [np.mean(np.abs((y_test[f"Target_{i}"].values -
                             preds[f"Target_{i}"].values) /
                            (y_test[f"Target_{i}"].values + 1e-9))) * 100
             for i in range(1, 16)],
            index=[i for i in range(1, 16)],
            name="MAPE%",
        )

    def directional_accuracy(self) -> pd.Series:
        y_test, preds = self._get_test_and_preds()
        da_scores = []
        for i in range(1, 16):
            actual = y_test[f"Target_{i}"].values
            pred   = preds[f"Target_{i}"].values
            actual_dir = np.sign(np.diff(actual))
            pred_dir   = np.sign(np.diff(pred))
            da_scores.append(np.mean(actual_dir == pred_dir) * 100)

        return pd.Series(
            da_scores,
            index=[i for i in range(1, 16)],
            name="DA%",
        )

    def eval_summary(self) -> pd.DataFrame:
        summary = pd.concat([
            self.eval_r_squared(),
            self.eval_mae(),
            self.eval_rmse(),
            self.eval_mape(),
            self.directional_accuracy(),
        ], axis=1)

        print(f"\n{'='*65}")
        print(f"  Evaluation Summary — {self.name.upper()}  (number_days={self.number_days})")
        print(f"{'='*65}")
        print(summary.round(4).to_string())
        print(f"{'='*65}\n")
        return summary

    def forecast(self) -> pd.DataFrame:
        X_train, _, X_test, _ = self.clean_dataset()

        last_features = X_test.iloc[[-1]]
        last_date     = X_test.index[-1]

        model = XGBRegressor()
        model.load_model(f"XGB_{self.name}_model_{self.number_days}.json")

        preds = model.predict(last_features)[0]   # shape: (15,)

        rows = []
        for i, price in enumerate(preds, start=1):
            rows.append({
                "day":             i,
                "date":            last_date + timedelta(days=i),
                "predicted_close": round(float(price), 4),
            })

        result = pd.DataFrame(rows)
        return result
    
    def reset_cache(self):
        self._cache  = None
        self._scaler = None
        print(f"[{self.name.upper()}] Cache cleared.")

    def timeframe(self, time):
        date = pd.read_sql(sql = f"""SELECT * FROM {self.name}""", con = engine )

        if date.empty:
            return None
        
        timeframe = {
        "15D": 15,
        "1M": 30,
        "6M": 180,
        }

        if time not in timeframe:
            raise ValueError(f"Invalid time: {time}")  
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe = date.rename(columns={'close': 'USDollars' , 'date': 'Date'}).set_index("Date").tail(timeframe[time])["USDollars"]
        return dataframe
    


