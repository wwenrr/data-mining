import logging
import typer

from service.kline_service import KlineNotFoundError
from service.market_state_service import MarketStateService, ModelTrainingError


def train_command(
    crypto: str = typer.Option(..., "--crypto", "-c", help="Crypto symbol to train (e.g., BTC)"),
    clusters: int = typer.Option(None, "--clusters", "-k", help="Number of clusters (auto-select if omitted)"),
    min_clusters: int = typer.Option(2, "--min-clusters", help="Minimum clusters when auto-selecting"),
    max_clusters: int = typer.Option(6, "--max-clusters", help="Maximum clusters when auto-selecting"),
):
    logger = logging.getLogger(__name__)

    try:
        service = MarketStateService()
        result = service.train_model(crypto, clusters, min_clusters, max_clusters)

        logger.info(
            "Trained KMeans model for %s (%s) using %d clusters on %d samples",
            result["symbol"],
            result["interval"],
            result["n_clusters"],
            result["samples"],
        )
        logger.info("Model saved to: %s", result["model_path"])
        for cluster_id, label in result["cluster_labels"].items():
            ret = result["cluster_returns"].get(cluster_id)
            ret_value = float(ret) if ret is not None else float("nan")
            logger.info("  Cluster %d → %s (mean future return: %.4f)", cluster_id, label, ret_value)

    except (ModelTrainingError, KlineNotFoundError, ValueError) as exc:
        logger.error(f"Training failed: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
