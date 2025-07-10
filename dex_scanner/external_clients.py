import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any


class DexScreener:
    BASE_URL = "https://api.dexscreener.com/latest"
    
    def __init__(self, chain_id_by_name: Dict[str, str]):
        self.chain_id_by_name = chain_id_by_name
    
    def get_links(self, pool_address: str) -> List[Dict[str, str]]:
        """Get trading links for a pool address."""
        try:
            response = requests.get(f"{self.BASE_URL}/dex/pairs/solana/{pool_address}")
            response.raise_for_status()
            data = response.json()
            
            links = []
            if "pairs" in data and data["pairs"]:
                pair = data["pairs"][0]
                if "dexId" in pair:
                    links.append({
                        "name": f"{pair['dexId']}",
                        "url": pair.get("url", "")
                    })
            
            return links
        except Exception:
            return []


class MoralisSolana:
    BASE_URL = "https://solana-gateway.moralis.io"
    NETWORK = "mainnet"
    DEEP_INDEX_URL = "https://deep-index.moralis.io/api/v2.2"
    CHAIN = "solana"
    MAX_RETRIES = 5

    def __init__(self, api_key: str) -> None:
        self.headers = {"Accept": "application/json", "X-API-Key": api_key}

    def _get(self, url: str, params: Dict[str, Any] | None = None) -> Any:
        retry = 0
        while True:
            try:
                resp = requests.get(url, headers=self.headers, params=params)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                retry += 1
                if retry > self.MAX_RETRIES:
                    raise e
                time.sleep(2**retry)

    def get_token_metadata(self, address: str) -> Dict[str, Any]:
        return self._get(f"{self.BASE_URL}/token/{self.NETWORK}/{address}/metadata")

    def get_recently_graduated_tokens(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._get(
            f"{self.BASE_URL}/token/{self.NETWORK}/exchange/pumpfun/graduated",
            {"limit": limit},
        )["result"]

    def get_top_token_holders(self, token_address: str, limit: int = 20) -> List[Dict[str, Any]]:
        return self._get(
            f"{self.BASE_URL}/token/{self.NETWORK}/{token_address}/top-holders",
            {"limit": limit},
        )["result"]

    def get_token_analytics(self, token_address: str) -> Dict[str, Any]:
        return self._get(
            f"{self.DEEP_INDEX_URL}/tokens/{token_address}/analytics",
            {"chain": self.CHAIN},
        )

    def get_token_holder_stats(self, token_address: str) -> Dict[str, Any]:
        return self._get(
            f"{self.BASE_URL}/token/{self.NETWORK}/holders/{token_address}"
        )

    def get_token_pairs(self, token_address: str) -> List[Dict[str, Any]]:
        return self._get(f"{self.BASE_URL}/token/{self.NETWORK}/{token_address}/pairs")[
            "pairs"
        ]

    def get_24h_candlestick_data(self, pool_address: str) -> List[Dict[str, Any]]:
        to_date = datetime.now() + timedelta(minutes=30)
        from_date = to_date - timedelta(days=1)
        to_date = to_date.strftime("%Y-%m-%d")
        from_date = from_date.strftime("%Y-%m-%d")
        resp = self._get(
            f"{self.BASE_URL}/token/{self.NETWORK}/pairs/{pool_address}/ohlcv",
            {
                "timeframe": "5min",
                "currency": "usd",
                "fromDate": from_date,
                "toDate": to_date,
                "limit": 288,
            },
        )
        candles = resp["result"][::-1]
        for candle in candles:
            candle["timestamp"] = datetime.fromisoformat(
                candle["timestamp"].replace("Z", "+00:00")
            ).timestamp()
        return candles

    def get_48h_candlestick_data(
        self,
        pool_address: str,
        from_date: datetime,
    ) -> List[Dict[str, Any]]:  # type: ignore
        to_date = from_date + timedelta(days=2)
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        resp = self._get(
            f"{self.BASE_URL}/token/{self.NETWORK}/pairs/{pool_address}/ohlcv",
            {
                "timeframe": "5min",
                "currency": "usd",
                "fromDate": from_date_str,
                "toDate": to_date_str,
                "limit": 576,
            },
        )
        candles = resp["result"][::-1]
        for candle in candles:
            candle["timestamp"] = datetime.fromisoformat(
                candle["timestamp"].replace("Z", "+00:00")
            ).timestamp()
        return candles

    def get_address_token_balances(self, address: str) -> List[Dict[str, Any]]:
        return self._get(f"{self.BASE_URL}/account/{self.NETWORK}/{address}/tokens") 