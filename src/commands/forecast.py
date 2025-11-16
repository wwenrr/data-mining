import json
import logging
import typer

from service.market_classifier_service import (
    MarketClassifierService,
    ClassifierModelNotFoundError,
    ClassifierTrainingError,
)
from service.market_state_service import MarketModelNotFoundError, ModelTrainingError
from service.kline_service import KlineNotFoundError


def forecast_command(crypto: str = typer.Option(..., "--crypto", "-c", help="Crypto symbol to forecast (e.g., BTC)")):
    logger = logging.getLogger(__name__)

    try:
        service = MarketClassifierService()
        result = service.forecast_next_state(crypto)

        logger.info("Forecast for %s (%s)", result["symbol"], result["interval"])
        logger.info("=" * 50)
        logger.info("Prediction timestamp: %s", result["prediction_timestamp"])
        logger.info("Predicted next state: %s", result["predicted_state"])
        if result["state_probabilities"]:
            logger.info("Probabilities:\n%s", json.dumps(result["state_probabilities"], indent=2))
        logger.info("Model: %s", result["model_path"])

    except (
        ClassifierModelNotFoundError,
        ClassifierTrainingError,
        MarketModelNotFoundError,
        ModelTrainingError,
        KlineNotFoundError,
        ValueError,
    ) as exc:
        logger.error(f"Forecast failed: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
