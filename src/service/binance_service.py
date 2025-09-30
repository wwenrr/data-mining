import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from decorator.singleton import singleton
from service.restful_service import RestfulService

@singleton
class BinanceService:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.restful_service = RestfulService()
        self.logger = logging.getLogger(__name__)
        
    def get_klines(self, symbol: str, interval: str, limit: int = 100, days_ago: Optional[int] = None) -> Dict[str, Any]:
        if limit > 1000:
            self.logger.warning(f"Limit {limit} exceeds maximum 1000, setting to 1000")
            limit = 1000
            
        endpoint = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        
        if days_ago is not None:
            start_date = datetime.now() - timedelta(days=days_ago)
            start_timestamp = int(start_date.timestamp() * 1000)
            params["startTime"] = start_timestamp
            self.logger.info(f"Fetching data starting from {days_ago} days ago ({start_date.strftime('%Y-%m-%d %H:%M:%S')})")
        url_params = [f"{key}={value}" for key, value in params.items()]
        url = f"{endpoint}?{'&'.join(url_params)}"
        
        try:
            self.logger.info(f"Fetching klines for {symbol} with interval {interval} and limit {limit}")
            response = self.restful_service.get(url)
            
            if response.status_code == 200:
                klines_data = response.json()
                self.logger.info(f"Successfully retrieved {len(klines_data)} klines")
                
                result = {
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit,
                    "days_ago": days_ago,
                    "timestamp": self._get_current_timestamp(),
                    "klines": klines_data
                }
                
                self._save_klines_data(result)
                return result
            else:
                self.logger.error(f"Failed to fetch klines: {response.status_code} - {response.text}")
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Error fetching klines: {str(e)}")
            raise
            
    def parse_kline_data(self, klines: List[List[Any]]) -> List[Dict[str, Any]]:
        parsed_data = []
        
        for kline in klines:
            parsed_kline = {
                "open_time": int(kline[0]),
                "open_price": float(kline[1]),
                "high_price": float(kline[2]),
                "low_price": float(kline[3]),
                "close_price": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": int(kline[6]),
                "quote_asset_volume": float(kline[7]),
                "number_of_trades": int(kline[8]),
                "taker_buy_base_volume": float(kline[9]),
                "taker_buy_quote_volume": float(kline[10])
            }
            parsed_data.append(parsed_kline)
            
        return parsed_data
        
    def _get_current_timestamp(self) -> str:
        return datetime.now().isoformat()
        
    def _save_klines_data(self, data: Dict[str, Any]) -> None:
        data_dir = Path("data/kline")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        symbol = data["symbol"].upper()
        crypto_name = symbol
        if crypto_name.endswith("USDT"):
            crypto_name = crypto_name[:-4]
        elif crypto_name.endswith("BUSD"):
            crypto_name = crypto_name[:-4]
        elif crypto_name.endswith("BTC"):
            crypto_name = crypto_name[:-3]
        elif crypto_name.endswith("ETH"):
            crypto_name = crypto_name[:-3]
        
        filename = f"{crypto_name.lower()}.json"
        filepath = data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Data saved to: {filepath}")
