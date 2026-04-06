import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from create_table import get_engine
from datetime import timedelta

engine = get_engine()

CRYPTO_TABLES      = {"btc", "eth", "ada", "bnb", "doge", "sol", "trx", "usdc", "usdt", "xrp"}
MODEL_DIR          = os.path.join(os.path.dirname(__file__), "Trained_Model")

class Models:

    def __init__(self, number_days: int, name: str):
        if name not in CRYPTO_TABLES:
            raise ValueError(f"'{name}' is not valid. Choose from: {CRYPTO_TABLES}")
        self.number_days        = number_days
        self.name               = name
        self._cache             = None
        self._scaler            = None
        self._last_close_train  = None
        self._last_close_all    = None  

    def clean_dataset(self):
        if self._cache is not None:
            return self._cache

        df = pd.read_sql(f"SELECT * FROM {self.name}", con=engine)
        if df.empty:
            raise ValueError(f"Table '{self.name}' returned no data.")

        df = (df.rename(columns={
                "low": "Low", "high": "High",
                "date": "Date", "close": "Close", "open": "Open",
            })
            .set_index("Date")
            .sort_index())

        c   = df["Close"]
        c1  = c.shift(1)
        ret = c1.pct_change()

        df["ma7"]  = c1.rolling(7).mean()
        df["ma21"] = c1.rolling(21).mean()
        df["ma50"] = c1.rolling(50).mean()

        df["close_ma7_ratio"]  = c1 / (df["ma7"]  + 1e-9)
        df["close_ma21_ratio"] = c1 / (df["ma21"] + 1e-9)

        df["vol14"] = ret.rolling(14).std()

        delta        = c.diff().shift(1)
        gain         = delta.clip(lower=0).rolling(14).mean()
        loss         = (-delta.clip(upper=0)).rolling(14).mean()
        df["rsi14"]  = 100 - (100 / (1 + gain / (loss + 1e-9)))

        bb_mid       = c1.rolling(20).mean()
        bb_std       = c1.rolling(20).std()
        df["bb_pct"] = (c1 - (bb_mid - 2 * bb_std)) / (4 * bb_std + 1e-9)

        df["log_return"] = np.log(c1 / (c1.shift(1) + 1e-9))

        for i in range(1, self.number_days + 1):
            df[f"Target_{i}"] = np.log(c.shift(-i) / (c + 1e-9))

        df["_raw_close"] = c

        df.drop(columns=[col for col in ["Close", "High", "Low", "Open", "ticker"]
                        if col in df.columns], inplace=True)

        target_cols  = [f"Target_{i}" for i in range(1, self.number_days + 1)]
        feature_cols = [col for col in df.columns
                        if col not in target_cols and col != "_raw_close"]

        df_features_clean = df.dropna(subset=feature_cols)

        self._last_close_all = float(df_features_clean["_raw_close"].iloc[-1])

        # Split
        split = max(int(len(df_features_clean) * 0.8), len(df_features_clean) - 365)
        train = df_features_clean.iloc[:split]
        test  = df_features_clean.iloc[split:]


        train_clean = train.dropna(subset=target_cols)
        test_clean  = test.dropna(subset=target_cols)

        self._last_close_train = float(train_clean["_raw_close"].iloc[-1])
        self._raw_close_y_test = test_clean["_raw_close"].copy()

        self._X_all_for_forecast = df_features_clean[feature_cols].copy()

        X_train = train_clean[feature_cols]
        y_train = train_clean[target_cols]
        X_test  = test_clean[feature_cols]
        y_test  = test_clean[target_cols]

        scaler     = RobustScaler()
        X_train_sc = pd.DataFrame(scaler.fit_transform(X_train),
                                index=X_train.index, columns=feature_cols)
        X_test_sc  = pd.DataFrame(scaler.transform(X_test),
                                index=X_test.index,  columns=feature_cols)
        self._scaler = scaler

        target_scaler = MinMaxScaler()
        y_train_sc    = pd.DataFrame(target_scaler.fit_transform(y_train),
                                    index=y_train.index, columns=target_cols)
        y_test_sc     = pd.DataFrame(target_scaler.transform(y_test),
                                    index=y_test.index,  columns=target_cols)
        self._target_scaler = target_scaler

        self._cache = X_train_sc, y_train_sc, X_test_sc, y_test_sc

        print(f"[{self.name.upper()}] Dataset ready — "
            f"train: {len(X_train_sc)}, test: {len(X_test_sc)}, "
            f"features: {len(feature_cols)}")
        return self._cache


    def _build_sequences(self, X: pd.DataFrame, y: pd.DataFrame = None):
        seq_len = self.number_days
        X_vals  = X.values
        seqs, indices = [], []

        for i in range(seq_len, len(X_vals) + 1):
            seqs.append(X_vals[i - seq_len: i])
            indices.append(X.index[i - 1])

        X_seq = np.array(seqs)

        if y is not None:
            valid_idx = [idx for idx in indices if idx in y.index]
            y_seq     = y.loc[valid_idx]
            return X_seq[:len(valid_idx)], y_seq, valid_idx

        return X_seq, indices


    def _build_lstm(self, input_shape):
        model = Sequential([
            Input(shape=input_shape),
            Bidirectional(LSTM(64, return_sequences=True)),
            Dropout(0.3),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dense(self.number_days),
        ])
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])
        model.summary()
        return model


    def train_model(self):
        X_train, y_train, X_test, y_test = self.clean_dataset()

        X_train_seq, y_train_seq, _ = self._build_sequences(X_train, y_train)

        val_cut     = int(len(X_train_seq) * 0.85)
        X_tr, X_val = X_train_seq[:val_cut], X_train_seq[val_cut:]
        y_tr        = y_train_seq.values[:val_cut]
        y_val       = y_train_seq.values[val_cut:]

        print(f"[{self.name.upper()}] Training — "
              f"sequences: {X_tr.shape}, val: {X_val.shape}")

        lstm_model = self._build_lstm((self.number_days, X_train.shape[1]))

        callbacks = [
            EarlyStopping(monitor="val_loss", patience=15,
                          restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                              patience=7, min_lr=1e-6, verbose=1),
        ]

        lstm_model.fit(
            X_tr, y_tr,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=32,
            callbacks=callbacks,
            verbose=1,
        )

        os.makedirs(MODEL_DIR, exist_ok=True)
        model_path = os.path.join(MODEL_DIR, f"LSTM_{self.name}_model_{self.number_days}.keras") 
        lstm_model.save(model_path)
        print(f"[{self.name.upper()}] Model saved → {model_path}")
        return lstm_model


    def test_model(self) -> pd.DataFrame:
        self.clean_dataset()
        _, _, X_test, _ = self._cache

        model_path           = os.path.join(MODEL_DIR, f"LSTM_{self.name}_model_{self.number_days}.keras")
        lstm_model           = load_model(model_path)
        X_test_seq, test_idx = self._build_sequences(X_test)
        preds_scaled         = lstm_model.predict(X_test_seq)

        log_returns = self._target_scaler.inverse_transform(preds_scaled)

        # Reconstruct: predicted_price[t+i] = close[t] * exp(log_return[t,i])
        prices = np.zeros_like(log_returns)
        for j, idx in enumerate(test_idx):
            base = (float(self._raw_close_y_test.loc[idx])
                    if idx in self._raw_close_y_test.index
                    else self._last_close_train)
            prices[j] = base * np.exp(log_returns[j])

        return pd.DataFrame(prices, index=test_idx,
                            columns=[f"Target_{i}" for i in range(1, self.number_days + 1)])


    def _get_test_and_preds(self):
        _, _, _, y_test_sc = self.clean_dataset()

        log_returns_actual = self._target_scaler.inverse_transform(y_test_sc.values)

        prices_actual = np.zeros_like(log_returns_actual)
        for j, idx in enumerate(y_test_sc.index):
            base = (float(self._raw_close_y_test.loc[idx])
                    if idx in self._raw_close_y_test.index
                    else self._last_close_train)
            prices_actual[j] = base * np.exp(log_returns_actual[j])

        y_test = pd.DataFrame(prices_actual,
                              index=y_test_sc.index,
                              columns=y_test_sc.columns)
        preds  = self.test_model()
        common = y_test.index.intersection(preds.index)
        return y_test.loc[common], preds.loc[common]

    def eval_rmse(self) -> pd.Series:
        y, p = self._get_test_and_preds()
        return pd.Series(
            [np.sqrt(mean_squared_error(y[f"Target_{i}"], p[f"Target_{i}"]))
             for i in range(1, self.number_days + 1)],
            index=range(1, self.number_days + 1), name="RMSE")

    def eval_mae(self) -> pd.Series:
        y, p = self._get_test_and_preds()
        return pd.Series(
            [mean_absolute_error(y[f"Target_{i}"], p[f"Target_{i}"])
             for i in range(1, self.number_days + 1)],
            index=range(1, self.number_days + 1), name="MAE")

    def eval_r_squared(self) -> pd.Series:
        y, p = self._get_test_and_preds()
        return pd.Series(
            [r2_score(y[f"Target_{i}"], p[f"Target_{i}"])
             for i in range(1, self.number_days + 1)],
            index=range(1, self.number_days + 1), name="R²")

    def eval_mape(self) -> pd.Series:
        y, p = self._get_test_and_preds()
        return pd.Series(
            [np.mean(np.abs((y[f"Target_{i}"].values - p[f"Target_{i}"].values)
                            / (y[f"Target_{i}"].values + 1e-9))) * 100
             for i in range(1, self.number_days + 1)],
            index=range(1, self.number_days + 1), name="MAPE%")

    def directional_accuracy(self) -> pd.Series:
        y, p = self._get_test_and_preds()
        scores = []
        for i in range(1, self.number_days + 1):
            ad  = np.sign(np.diff(y[f"Target_{i}"].values))
            pd_ = np.sign(np.diff(p[f"Target_{i}"].values))
            scores.append(np.mean(ad == pd_) * 100)
        return pd.Series(scores, index=range(1, self.number_days + 1), name="DA%")

    def eval_summary(self) -> pd.DataFrame:
        summary = pd.concat([
            self.eval_r_squared(), self.eval_mae(),
            self.eval_rmse(),      self.eval_mape(),
            self.directional_accuracy(),
        ], axis=1)
        print(f"\n{'='*65}")
        print(f"  Evaluation — {self.name.upper()}  (horizon={self.number_days}d)")
        print(f"{'='*65}")
        print(summary.round(4).to_string())
        print(f"{'='*65}\n")
        return summary

    def forecast(self) -> pd.DataFrame:
        self.clean_dataset()
        X_all = self._X_all_for_forecast

        scaler_input = pd.DataFrame(
            self._scaler.transform(X_all),
            index=X_all.index,
            columns=X_all.columns
        )

        model_path   = os.path.join(MODEL_DIR, f"LSTM_{self.name}_model_{self.number_days}.keras")  # ✅
        lstm_model   = load_model(model_path)
        last_seq     = scaler_input.values[-self.number_days:].reshape(1, self.number_days, -1)
        last_date    = pd.Timestamp(X_all.index[-1])

        preds_scaled = lstm_model.predict(last_seq)
        log_returns  = self._target_scaler.inverse_transform(preds_scaled)[0]

        # Anchor to true last close
        prices = self._last_close_all * np.exp(log_returns)

        future_dates = [last_date + timedelta(days=i) for i in range(1, self.number_days + 1)]
        result = pd.DataFrame(
            {"USDollars": [round(float(p), 4) for p in prices]},
            index=pd.DatetimeIndex(future_dates, name="Date")
        )
        return result

    def reset_cache(self):
        self._cache                 = None
        self._scaler                = None
        self._target_scaler         = None
        self._last_close_train      = None
        self._last_close_all        = None
        self._raw_close_y_test      = None
        self._X_all_for_forecast    = None 
        print(f"[{self.name.upper()}] Cache cleared.")

    def timeframe(self, time):
        dataframe = pd.read_sql(sql=f"SELECT * FROM {self.name}", con=engine)
        if dataframe.empty:
            return None
        timeframe = {"15D": 15, "1M": 30, "6M": 180}
        if time not in timeframe:
            raise ValueError(f"Invalid time: {time}")
        dataframe["date"] = pd.to_datetime(dataframe["date"]).dt.strftime("%Y-%m-%d")
        dataframe = (dataframe
                     .rename(columns={"close": "USDollars", "date": "Date"})
                     .set_index("Date")
                     .tail(timeframe[time])["USDollars"])
        return dataframe

