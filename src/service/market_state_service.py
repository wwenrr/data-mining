import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .kline_service import KlineService, KlineNotFoundError


class ModelTrainingError(Exception):
    """Raised when the KMeans model cannot be trained."""


class MarketModelNotFoundError(Exception):
    """Raised when a trained market-state model is missing."""


class MarketStateService:
    """Service responsible for training and using KMeans market-state models."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kline_service = KlineService()
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def _model_path(self, symbol: str, interval: str) -> Path:
        return self.models_dir / f"{symbol.lower()}_{interval}.joblib"

    def _load_dataframe(self, crypto_name: str) -> Dict[str, Any]:
        data = self.kline_service.get_kline_data(crypto_name)
        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "trade_count",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ]
        frame = pd.DataFrame(data["klines"], columns=columns)
        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_asset_volume",
            "taker_buy_base",
            "taker_buy_quote",
        ]
        for col in numeric_cols:
            frame[col] = frame[col].astype(float)

        frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms")
        frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms")
        frame.sort_values("open_time", inplace=True)
        frame.reset_index(drop=True, inplace=True)
        return {"data": data, "frame": frame}

    @staticmethod
    def _compute_features(frame: pd.DataFrame) -> Dict[str, Any]:
        df = frame.copy()
        df["return"] = df["close"].pct_change()
        df["volatility_7"] = df["return"].rolling(7).std()
        df["volatility_14"] = df["return"].rolling(14).std()
        df["ma_7"] = df["close"].rolling(7).mean()
        df["ma_14"] = df["close"].rolling(14).mean()
        df["ma_50"] = df["close"].rolling(50).mean()
        df["ma_slope"] = df["ma_7"] - df["ma_14"]

        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["rsi_14"] = 100 - (100 / (1 + rs))

        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        df["volume_change"] = df["volume"].pct_change()
        df["future_return_1"] = df["close"].shift(-1) / df["close"] - 1

        feature_cols = [
            "return",
            "volatility_7",
            "volatility_14",
            "ma_7",
            "ma_14",
            "ma_50",
            "ma_slope",
            "rsi_14",
            "macd",
            "macd_signal",
            "volume_change",
        ]

        feature_frame = df[["open_time", "close", "future_return_1"] + feature_cols].dropna()
        return {"frame": feature_frame, "columns": feature_cols}

    @staticmethod
    def _assign_labels(cluster_returns: Dict[int, float]) -> Dict[int, str]:
        if not cluster_returns:
            return {}

        sorted_clusters = sorted(cluster_returns.items(), key=lambda item: item[1], reverse=True)
        labels = {}

        if len(sorted_clusters) == 1:
            labels[sorted_clusters[0][0]] = "Sideway"
            return labels

        labels[sorted_clusters[0][0]] = "Bullish"
        labels[sorted_clusters[-1][0]] = "Bearish"

        for cluster_id, _ in sorted_clusters[1:-1]:
            if cluster_id not in labels:
                labels[cluster_id] = "Sideway"

        if len(sorted_clusters) == 2:
            labels.setdefault(sorted_clusters[1][0], "Bearish")

        return labels

    def _resolve_cluster_count(
        self, X: np.ndarray, forced_clusters: Optional[int], min_clusters: int, max_clusters: int
    ) -> int:
        sample_count = len(X)
        if sample_count < 2:
            raise ModelTrainingError("Need at least two samples to train KMeans.")

        if forced_clusters is not None:
            if forced_clusters < 2:
                raise ModelTrainingError("KMeans requires at least 2 clusters.")
            if sample_count <= forced_clusters:
                raise ModelTrainingError("Not enough samples for the requested number of clusters.")
            return forced_clusters

        best_k = None
        best_score = -1.0
        for k in range(min_clusters, max_clusters + 1):
            if sample_count <= k:
                break
            model = KMeans(n_clusters=k, n_init=10, random_state=42)
            labels = model.fit_predict(X)
            if len(set(labels)) == 1:
                continue
            score = silhouette_score(X, labels)
            if score > best_score:
                best_score = score
                best_k = k

        if best_k is None:
            raise ModelTrainingError("Unable to determine an appropriate number of clusters.")

        return best_k

    def train_model(
        self,
        crypto_name: str,
        n_clusters: Optional[int] = None,
        min_clusters: int = 2,
        max_clusters: int = 6,
    ) -> Dict[str, Any]:
        dataset = self._load_dataframe(crypto_name)
        feature_payload = self._compute_features(dataset["frame"])
        feature_frame = feature_payload["frame"]
        feature_cols = feature_payload["columns"]

        if feature_frame.empty:
            raise ModelTrainingError("Not enough data to compute features for training.")

        X = feature_frame[feature_cols].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        cluster_count = self._resolve_cluster_count(X_scaled, n_clusters, min_clusters, max_clusters)

        model = KMeans(n_clusters=cluster_count, n_init=10, random_state=42)
        labels = model.fit_predict(X_scaled)
        feature_frame = feature_frame.assign(cluster=labels)

        cluster_returns = feature_frame.groupby("cluster")["future_return_1"].mean().to_dict()
        cluster_labels = self._assign_labels(cluster_returns)

        model_payload = {
            "symbol": dataset["data"]["symbol"],
            "interval": dataset["data"]["interval"],
            "trained_at": datetime.utcnow().isoformat(),
            "n_clusters": cluster_count,
            "feature_columns": feature_cols,
            "scaler": scaler,
            "model": model,
            "cluster_returns": cluster_returns,
            "cluster_labels": cluster_labels,
            "samples": len(feature_frame),
        }

        path = self._model_path(dataset["data"]["symbol"], dataset["data"]["interval"])
        dump(model_payload, path)

        return {
            "symbol": dataset["data"]["symbol"],
            "interval": dataset["data"]["interval"],
            "n_clusters": cluster_count,
            "cluster_labels": cluster_labels,
            "cluster_returns": cluster_returns,
            "model_path": str(path),
            "samples": len(feature_frame),
        }

    def predict_market_state(self, crypto_name: str) -> Dict[str, Any]:
        dataset = self._load_dataframe(crypto_name)
        symbol = dataset["data"]["symbol"]
        interval = dataset["data"]["interval"]
        path = self._model_path(symbol, interval)

        if not path.exists():
            raise MarketModelNotFoundError(f"No trained model found for {symbol} ({interval}).")

        model_payload = load(path)
        feature_payload = self._compute_features(dataset["frame"])
        feature_frame = feature_payload["frame"]
        feature_cols = feature_payload["columns"]

        if feature_frame.empty:
            raise ModelTrainingError("Not enough data to compute features for prediction.")

        scaler: StandardScaler = model_payload["scaler"]
        model: KMeans = model_payload["model"]

        X_scaled = scaler.transform(feature_frame[feature_cols].values)
        predictions = model.predict(X_scaled)
        feature_frame = feature_frame.assign(cluster=predictions)

        cluster_labels = model_payload.get("cluster_labels", {})
        feature_frame["state"] = feature_frame["cluster"].map(cluster_labels)

        latest = feature_frame.iloc[-1]
        latest_state = {
            "timestamp": latest["open_time"].isoformat(),
            "close": float(latest["close"]),
            "cluster": int(latest["cluster"]),
            "state": latest["state"] or "Unknown",
            "features": {col: float(latest[col]) for col in feature_cols},
        }

        state_counts = feature_frame["state"].fillna("Unlabeled").value_counts().to_dict()

        return {
            "symbol": symbol,
            "interval": interval,
            "n_clusters": model_payload["n_clusters"],
            "cluster_labels": cluster_labels,
            "latest_state": latest_state,
            "state_distribution": state_counts,
            "model_path": str(path),
        }
