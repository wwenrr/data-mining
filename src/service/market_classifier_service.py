import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .market_state_service import (
    MarketStateService,
    MarketModelNotFoundError,
    ModelTrainingError,
)


class ClassifierTrainingError(Exception):
    """Raised when the supervised classifier cannot be trained."""


class ClassifierModelNotFoundError(Exception):
    """Raised when a trained classifier model is missing."""


class MarketClassifierService:
    """Train a supervised model to forecast the next market state."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state_service = MarketStateService()
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def _model_path(self, symbol: str, interval: str) -> Path:
        return self.models_dir / f"{symbol.lower()}_{interval}_classifier.joblib"

    def train_classifier(
        self,
        crypto_name: str,
        test_size: float = 0.2,
        random_state: int = 42,
        n_estimators: int = 200,
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        labeled_dataset = self.state_service.get_labeled_feature_dataset(crypto_name)
        frame = labeled_dataset["frame"].copy()
        feature_cols = labeled_dataset["feature_columns"]
        meta = labeled_dataset["meta"]

        if frame["state"].isna().all():
            raise ModelTrainingError("No market-state labels available. Train the clustering model first.")

        frame["next_state"] = frame["state"].shift(-1)
        frame = frame.dropna(subset=["next_state"])
        if frame.empty:
            raise ClassifierTrainingError("Not enough labeled samples to train the classifier.")

        X = frame[feature_cols].values
        y = frame["next_state"].astype(str).values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        stratify = y if len(np.unique(y)) > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state, stratify=stratify
        )

        classifier = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=random_state
        )
        classifier.fit(X_train, y_train)

        train_accuracy = classifier.score(X_train, y_train)
        test_accuracy = classifier.score(X_test, y_test)
        y_pred = classifier.predict(X_test)

        report = classification_report(y_test, y_pred, zero_division=0)
        matrix = confusion_matrix(y_test, y_pred).tolist()

        payload = {
            "symbol": meta["symbol"],
            "interval": meta["interval"],
            "trained_at": datetime.utcnow().isoformat(),
            "feature_columns": feature_cols,
            "scaler": scaler,
            "classifier": classifier,
            "classes": list(classifier.classes_),
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "classification_report": report,
            "confusion_matrix": matrix,
            "samples": len(frame),
        }

        path = self._model_path(meta["symbol"], meta["interval"])
        dump(payload, path)

        return {
            "symbol": meta["symbol"],
            "interval": meta["interval"],
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "classification_report": report,
            "confusion_matrix": matrix,
            "model_path": str(path),
            "samples": len(frame),
        }

    def forecast_next_state(self, crypto_name: str) -> Dict[str, Any]:
        labeled_dataset = self.state_service.get_labeled_feature_dataset(crypto_name)
        feature_cols = labeled_dataset["feature_columns"]
        frame = labeled_dataset["frame"]
        meta = labeled_dataset["meta"]

        path = self._model_path(meta["symbol"], meta["interval"])
        if not path.exists():
            raise ClassifierModelNotFoundError(
                f"No trained classifier model found for {meta['symbol']} ({meta['interval']})."
            )

        if frame.empty:
            raise ClassifierTrainingError("No feature data available for forecasting.")

        payload = load(path)
        scaler: StandardScaler = payload["scaler"]
        classifier: RandomForestClassifier = payload["classifier"]

        latest = frame.iloc[-1]
        latest_features = latest[feature_cols].values.reshape(1, -1)
        latest_scaled = scaler.transform(latest_features)

        prediction = classifier.predict(latest_scaled)[0]

        proba = {}
        if hasattr(classifier, "predict_proba"):
            probabilities = classifier.predict_proba(latest_scaled)[0]
            proba = {label: float(prob) for label, prob in zip(payload["classes"], probabilities)}

        return {
            "symbol": meta["symbol"],
            "interval": meta["interval"],
            "prediction_timestamp": latest["open_time"].isoformat(),
            "predicted_state": prediction,
            "state_probabilities": proba,
            "model_path": str(path),
            "latest_features": {col: float(latest[col]) for col in feature_cols},
        }
