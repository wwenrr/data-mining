import logging
import typer

from service.market_classifier_service import (
    MarketClassifierService,
    ClassifierTrainingError,
)
from service.market_state_service import MarketModelNotFoundError, ModelTrainingError
from service.kline_service import KlineNotFoundError


def train_classifier_command(
    crypto: str = typer.Option(..., "--crypto", "-c", help="Crypto symbol to train classifier for (e.g., BTC)"),
    test_size: float = typer.Option(0.2, "--test-size", help="Test size ratio for evaluation"),
    estimators: int = typer.Option(200, "--estimators", "-n", help="Number of trees in the RandomForest"),
    max_depth: int = typer.Option(None, "--max-depth", help="Max depth for each tree"),
):
    logger = logging.getLogger(__name__)

    try:
        service = MarketClassifierService()
        result = service.train_classifier(
            crypto_name=crypto,
            test_size=test_size,
            n_estimators=estimators,
            max_depth=max_depth,
        )

        logger.info(
            "Trained classifier for %s (%s) on %d samples",
            result["symbol"],
            result["interval"],
            result["samples"],
        )
        logger.info("Model saved to: %s", result["model_path"])
        logger.info("Train accuracy: %.4f", result["train_accuracy"])
        logger.info("Test accuracy: %.4f", result["test_accuracy"])
        logger.info("Classification report:\n%s", result["classification_report"])
        logger.info("Confusion matrix: %s", result["confusion_matrix"])

    except (
        ClassifierTrainingError,
        MarketModelNotFoundError,
        ModelTrainingError,
        KlineNotFoundError,
        ValueError,
    ) as exc:
        logger.error(f"Classifier training failed: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
