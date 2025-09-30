import typer
from service.binance_service import BinanceService

def dataset_command(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair symbol (e.g., BTCUSDT)"),
    interval: str = typer.Option(..., "--interval", "-i", help="Time interval (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Number of klines to retrieve (max 1000)"),
    days_ago: int = typer.Option(None, "--days", "-d", help="Number of days ago to start fetching data from")
):
    try:
        binance_service = BinanceService()
        result = binance_service.get_klines(symbol, interval, limit, days_ago)
        
        time_info = f" starting from {days_ago} days ago" if days_ago else ""
        print(f"Retrieved {len(result['klines'])} klines for {symbol} ({interval}){time_info}")
        print("Sample data (first 3 klines):")
        
        for i, kline in enumerate(result['klines'][:3]):
            print(f"Kline {i+1}:")
            print(f"  Open time: {kline[0]}")
            print(f"  Open: {kline[1]}")
            print(f"  High: {kline[2]}")
            print(f"  Low: {kline[3]}")
            print(f"  Close: {kline[4]}")
            print(f"  Volume: {kline[5]}")
            print(f"  Close time: {kline[6]}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
