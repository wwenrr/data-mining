import logging
import typer
from service.kline_service import KlineService, KlineNotFoundError


def analyze_command(crypto: str = typer.Option(..., "--crypto", "-c", help="Crypto name to analyze (e.g., BTC, ETH)")):
    logger = logging.getLogger(__name__)

    try:
        kline_service = KlineService()
        summary = kline_service.get_summary(crypto)

        logger.info(f"Analysis for {summary['symbol']}")
        logger.info("=" * 50)
        logger.info(f"Interval: {summary['interval']}")
        logger.info(f"Data points: {summary['kline_count']} klines")
        logger.info(f"Time range: {summary['time_range']['start'][:19]} -> {summary['time_range']['end'][:19]}")
        logger.info("")

        logger.info("Price Information:")
        logger.info(f"  Current price: ${summary['price']['current']:,.2f}")
        logger.info(f"  Price change: ${summary['price']['change']['absolute']:,.2f} ({summary['price']['change']['percentage']:+.2f}%)")
        logger.info(f"  High: ${summary['price']['range']['high']:,.2f}")
        logger.info(f"  Low: ${summary['price']['range']['low']:,.2f}")
        logger.info("")

        logger.info("Volume Information:")
        logger.info(f"  Total volume: {summary['volume']['total']:,.2f}")
        logger.info(f"  Average volume: {summary['volume']['average']:,.2f}")
        logger.info("")

        logger.info(f"Data fetched: {summary['data_timestamp'][:19]}")

    except KlineNotFoundError as e:
        available = kline_service.list_available_cryptos()
        logger.error(f"{e}")
        if available:
            logger.info(f"Available cryptos: {', '.join(available)}")
        else:
            logger.warning("No kline data available. Fetch some data first using the dataset command.")
    except Exception as e:
        logger.error(f"Error: {e}")
