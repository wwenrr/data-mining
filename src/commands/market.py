import json
import logging
import typer

from service.kline_service import KlineNotFoundError
from service.market_state_service import MarketStateService, MarketModelNotFoundError, ModelTrainingError


def market_command(
    crypto: str = typer.Option(..., "--crypto", "-c", help="Crypto symbol to analyze (e.g., BTC)"),
    show_history: bool = typer.Option(
        False, "--show-history", help="Print cluster distribution in JSON for deeper analysis"
    ),
):
    logger = logging.getLogger(__name__)

    try:
        service = MarketStateService()
        summary = service.predict_market_state(crypto)

        logger.info("Market state for %s (%s)", summary["symbol"], summary["interval"])
        logger.info("=" * 50)
        latest = summary["latest_state"]
        logger.info("Latest timestamp: %s", latest["timestamp"])
        logger.info("Closing price: $%s", f"{latest['close']:,.2f}")
        logger.info("Cluster %d → %s", latest["cluster"], latest["state"])

        logger.info("Feature snapshot:")
        for name, value in latest["features"].items():
            logger.info("  %s: %.6f", name, value)

        logger.info("State distribution:")
        for state, count in summary["state_distribution"].items():
            logger.info("  %s: %d", state, count)

        if show_history:
            logger.info("Full distribution JSON:\n%s", json.dumps(summary["state_distribution"], indent=2))

    except (MarketModelNotFoundError, ModelTrainingError, KlineNotFoundError, ValueError) as exc:
        logger.error(f"Market analysis failed: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
