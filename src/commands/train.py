import logging
import typer
from service.training_service import TrainingService
from service.kline_service import KlineNotFoundError


def train_command(
    crypto: str = typer.Option(..., "--crypto", "-c", help="Crypto name to train on (e.g., BTC, ETH)"),
    model_type: str = typer.Option(
        "linear",
        "--model",
        "-m",
        help="Model type: 'linear' or 'random_forest'",
    ),
    lookback: int = typer.Option(5, "--lookback", "-lb", help="Number of periods to look back for features"),
    test_size: float = typer.Option(0.2, "--test-size", "-ts", help="Proportion of data for testing (0.0-1.0)"),
):
    logger = logging.getLogger(__name__)

    try:
        training_service = TrainingService()

        logger.info(f"Starting model training for {crypto.upper()}...")
        logger.info("=" * 50)

        result = training_service.train_model(
            crypto=crypto,
            model_type=model_type,
            lookback=lookback,
            test_size=test_size,
        )

        logger.info("")
        logger.info("Training completed successfully!")
        logger.info("=" * 50)
        logger.info(f"Model: {result['model_type']}")
        logger.info(f"Crypto: {result['crypto']}")
        logger.info(f"Lookback: {result['lookback']} periods")
        logger.info(f"Feature dimensions: {result['feature_dim']}")
        logger.info("")

        logger.info("Training Set Metrics:")
        logger.info(f"  Samples: {result['train_size']}")
        logger.info(f"  RMSE: ${result['train_metrics']['rmse']:,.4f}")
        logger.info(f"  MAE: ${result['train_metrics']['mae']:,.4f}")
        logger.info(f"  R² Score: {result['train_metrics']['r2']:.4f}")
        logger.info("")

        logger.info("Test Set Metrics:")
        logger.info(f"  Samples: {result['test_size_samples']}")
        logger.info(f"  RMSE: ${result['test_metrics']['rmse']:,.4f}")
        logger.info(f"  MAE: ${result['test_metrics']['mae']:,.4f}")
        logger.info(f"  R² Score: {result['test_metrics']['r2']:.4f}")
        logger.info("")

        logger.info(f"Model saved to: {result['model_path']}")
        logger.info(f"Scaler saved to: {result['scaler_path']}")

    except KlineNotFoundError as e:
        kline_service = training_service.kline_service
        available = kline_service.list_available_cryptos()
        logger.error(f"{e}")
        if available:
            logger.info(f"Available cryptos: {', '.join(available)}")
        else:
            logger.warning("No kline data available. Fetch some data first using the dataset command.")
    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
