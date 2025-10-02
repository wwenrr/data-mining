import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
from decorator.singleton import singleton
from service.kline_service import KlineService


@singleton
class TrainingService:
    def __init__(self):
        self.kline_service = KlineService()
        self.logger = logging.getLogger(__name__)
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def prepare_features(self, klines: List[List[Any]], lookback: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and target for training.
        Uses lookback period to predict next closing price.

        Features: open, high, low, close, volume for lookback periods
        Target: next close price
        """
        features = []
        targets = []

        for i in range(lookback, len(klines)):
            # Extract features from lookback periods
            feature_row = []
            for j in range(i - lookback, i):
                kline = klines[j]
                feature_row.extend(
                    [
                        float(kline[1]),  # open
                        float(kline[2]),  # high
                        float(kline[3]),  # low
                        float(kline[4]),  # close
                        float(kline[5]),  # volume
                    ]
                )
            features.append(feature_row)

            # Target is the next close price
            targets.append(float(klines[i][4]))

        return np.array(features), np.array(targets)

    def train_model(
        self,
        crypto: str,
        model_type: str = "linear",
        lookback: int = 5,
        test_size: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Train a model on the kline data.

        Args:
            crypto: Crypto name (e.g., BTC, ETH)
            model_type: Type of model ('linear' or 'random_forest')
            lookback: Number of periods to look back for features
            test_size: Proportion of data to use for testing

        Returns:
            Dictionary with training results and metrics
        """
        self.logger.info(f"Loading data for {crypto}...")
        klines = self.kline_service.get_klines(crypto)

        if len(klines) < lookback + 10:
            raise ValueError(f"Not enough data points. Need at least {lookback + 10}, got {len(klines)}")

        self.logger.info(f"Preparing features with lookback={lookback}...")
        X, y = self.prepare_features(klines, lookback)

        self.logger.info(f"Feature shape: {X.shape}, Target shape: {y.shape}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, shuffle=False)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Select and train model
        self.logger.info(f"Training {model_type} model...")
        if model_type == "linear":
            model = LinearRegression()
        elif model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        model.fit(X_train_scaled, y_train)

        # Evaluate
        self.logger.info("Evaluating model...")
        y_train_pred = model.predict(X_train_scaled)
        y_test_pred = model.predict(X_test_scaled)

        train_metrics = {
            "mse": float(mean_squared_error(y_train, y_train_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_train, y_train_pred))),
            "mae": float(mean_absolute_error(y_train, y_train_pred)),
            "r2": float(r2_score(y_train, y_train_pred)),
        }

        test_metrics = {
            "mse": float(mean_squared_error(y_test, y_test_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_test_pred))),
            "mae": float(mean_absolute_error(y_test, y_test_pred)),
            "r2": float(r2_score(y_test, y_test_pred)),
        }

        # Save model and scaler
        model_filename = f"{crypto.lower()}_{model_type}_model.joblib"
        scaler_filename = f"{crypto.lower()}_{model_type}_scaler.joblib"
        model_path = self.models_dir / model_filename
        scaler_path = self.models_dir / scaler_filename

        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        self.logger.info(f"Model saved to: {model_path}")
        self.logger.info(f"Scaler saved to: {scaler_path}")

        # Save metadata
        metadata = {
            "crypto": crypto.upper(),
            "model_type": model_type,
            "lookback": lookback,
            "test_size": test_size,
            "train_size": len(X_train),
            "test_size_samples": len(X_test),
            "feature_dim": X.shape[1],
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
        }

        metadata_filename = f"{crypto.lower()}_{model_type}_metadata.json"
        metadata_path = self.models_dir / metadata_filename
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self.logger.info(f"Metadata saved to: {metadata_path}")

        return metadata
