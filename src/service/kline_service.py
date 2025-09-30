import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from decorator.singleton import singleton


class KlineNotFoundError(Exception):
    pass


@singleton
class KlineService:
    def __init__(self):
        self.data_dir = Path("data/kline")
        self.logger = logging.getLogger(__name__)

    def get_kline_data(self, crypto_name: str) -> Dict[str, Any]:
        crypto_name = crypto_name.lower()
        file_path = self.data_dir / f"{crypto_name}.json"

        if not file_path.exists():
            raise KlineNotFoundError(f"Kline data not found for {crypto_name.upper()}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.info(f"Loaded kline data for {crypto_name.upper()}")
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON for {crypto_name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading kline data for {crypto_name}: {e}")
            raise

    def get_symbol(self, crypto_name: str) -> str:
        data = self.get_kline_data(crypto_name)
        return data["symbol"]

    def get_interval(self, crypto_name: str) -> str:
        data = self.get_kline_data(crypto_name)
        return data["interval"]

    def get_limit(self, crypto_name: str) -> int:
        data = self.get_kline_data(crypto_name)
        return data["limit"]

    def get_days_ago(self, crypto_name: str) -> Optional[int]:
        data = self.get_kline_data(crypto_name)
        return data.get("days_ago")

    def get_timestamp(self, crypto_name: str) -> str:
        data = self.get_kline_data(crypto_name)
        return data["timestamp"]

    def get_klines(self, crypto_name: str) -> List[List[Any]]:
        data = self.get_kline_data(crypto_name)
        return data["klines"]

    def get_kline_count(self, crypto_name: str) -> int:
        klines = self.get_klines(crypto_name)
        return len(klines)

    def get_price_range(self, crypto_name: str) -> Dict[str, float]:
        klines = self.get_klines(crypto_name)
        if not klines:
            return {"high": 0.0, "low": 0.0}

        highs = [float(kline[2]) for kline in klines]
        lows = [float(kline[3]) for kline in klines]

        return {"high": max(highs), "low": min(lows)}

    def get_volume_info(self, crypto_name: str) -> Dict[str, float]:
        klines = self.get_klines(crypto_name)
        if not klines:
            return {"total": 0.0, "average": 0.0}

        volumes = [float(kline[5]) for kline in klines]
        total_volume = sum(volumes)
        avg_volume = total_volume / len(volumes) if volumes else 0.0

        return {"total": total_volume, "average": avg_volume}

    def get_latest_price(self, crypto_name: str) -> Dict[str, float]:
        klines = self.get_klines(crypto_name)
        if not klines:
            return {"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0}

        latest_kline = klines[-1]
        return {
            "open": float(latest_kline[1]),
            "high": float(latest_kline[2]),
            "low": float(latest_kline[3]),
            "close": float(latest_kline[4]),
        }

    def get_first_price(self, crypto_name: str) -> Dict[str, float]:
        klines = self.get_klines(crypto_name)
        if not klines:
            return {"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0}

        first_kline = klines[0]
        return {
            "open": float(first_kline[1]),
            "high": float(first_kline[2]),
            "low": float(first_kline[3]),
            "close": float(first_kline[4]),
        }

    def get_price_change(self, crypto_name: str) -> Dict[str, float]:
        first_price = self.get_first_price(crypto_name)
        latest_price = self.get_latest_price(crypto_name)

        if first_price["close"] == 0:
            return {"absolute": 0.0, "percentage": 0.0}

        absolute_change = latest_price["close"] - first_price["close"]
        percentage_change = (absolute_change / first_price["close"]) * 100

        return {"absolute": absolute_change, "percentage": percentage_change}

    def get_time_range(self, crypto_name: str) -> Dict[str, datetime]:
        klines = self.get_klines(crypto_name)
        if not klines:
            now = datetime.now()
            return {"start": now, "end": now}

        start_timestamp = int(klines[0][0]) / 1000
        end_timestamp = int(klines[-1][6]) / 1000

        return {
            "start": datetime.fromtimestamp(start_timestamp),
            "end": datetime.fromtimestamp(end_timestamp),
        }

    def get_summary(self, crypto_name: str) -> Dict[str, Any]:
        data = self.get_kline_data(crypto_name)
        price_range = self.get_price_range(crypto_name)
        volume_info = self.get_volume_info(crypto_name)
        latest_price = self.get_latest_price(crypto_name)
        price_change = self.get_price_change(crypto_name)
        time_range = self.get_time_range(crypto_name)

        return {
            "symbol": data["symbol"],
            "interval": data["interval"],
            "kline_count": self.get_kline_count(crypto_name),
            "time_range": {
                "start": time_range["start"].isoformat(),
                "end": time_range["end"].isoformat(),
            },
            "price": {
                "current": latest_price["close"],
                "change": price_change,
                "range": price_range,
            },
            "volume": volume_info,
            "data_timestamp": data["timestamp"],
        }

    def list_available_cryptos(self) -> List[str]:
        if not self.data_dir.exists():
            return []

        crypto_files = list(self.data_dir.glob("*.json"))
        return [f.stem.upper() for f in crypto_files]
