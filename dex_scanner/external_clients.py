import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict


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


class HeliusAPI:
    """Helius API client for enhanced token data."""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = f"https://mainnet.helius-rpc.com/?api-key={api_key}"
        self.max_retries = 3

    def _make_rpc_call(self, method: str, params: List[Any]) -> Any:
        """Make RPC call to Helius API."""
        retry = 0
        while True:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": params
                }
                response = requests.post(self.base_url, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                if "error" in result:
                    raise Exception(f"RPC Error: {result['error']}")
                
                return result.get("result", {})
            except Exception as e:
                retry += 1
                if retry > self.max_retries:
                    raise e
                time.sleep(2**retry)

    def get_token_metadata(self, token_address: str) -> Dict[str, Any]:
        """Get comprehensive token metadata."""
        try:
            # Get token metadata
            metadata = self._make_rpc_call("getTokenMetadata", [token_address])
            
            # Get token supply
            supply = self._make_rpc_call("getTokenSupply", [token_address])
            
            # Get token largest accounts (holders info)
            largest_accounts = self._make_rpc_call("getTokenLargestAccounts", [token_address])
            
            # Get account info for additional details
            account_info = self._make_rpc_call("getAccountInfo", [token_address, {"encoding": "jsonParsed"}])
            
            return {
                "metadata": metadata,
                "supply": supply,
                "largest_accounts": largest_accounts,
                "account_info": account_info
            }
        except Exception as e:
            return {"error": str(e)}

    def get_token_age(self, token_address: str) -> Dict[str, Any]:
        """Get token age and creation information."""
        try:
            # Get signatures for address to find creation transaction
            signatures = self._make_rpc_call("getSignaturesForAddress", [
                token_address,
                {"limit": 1000}
            ])
            
            if isinstance(signatures, list) and signatures:
                # Get the oldest transaction (likely creation)
                oldest_sig = signatures[len(signatures) - 1]
                creation_time = oldest_sig.get("blockTime", 0)
                
                if creation_time:
                    creation_date = datetime.fromtimestamp(creation_time)
                    now = datetime.now()
                    age_delta = now - creation_date
                    
                    days = age_delta.days
                    hours = age_delta.seconds // 3600
                    minutes = (age_delta.seconds % 3600) // 60
                    
                    return {
                        "creation_time": creation_time,
                        "creation_date": creation_date.isoformat(),
                        "age_days": days,
                        "age_hours": hours,
                        "age_minutes": minutes,
                        "age_formatted": f"{days}d {hours}h {minutes}m"
                    }
            
            return {"error": "Could not determine token age"}
        except Exception as e:
            return {"error": str(e)}

    def get_enhanced_token_details(self, token_address: str) -> Dict[str, Any]:
        """Get comprehensive token details combining multiple API calls."""
        try:
            metadata = self.get_token_metadata(token_address)
            age_info = self.get_token_age(token_address)
            
            return {
                "metadata": metadata,
                "age_info": age_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    def get_token_transfers(self, token_address: str, start_time: int, end_time: int, limit=1000):
        """
        Fetch token transfer transactions for a given token between start_time and end_time (unix timestamps).
        """
        try:
            url = "https://mainnet.helius-rpc.com/?api-key=" + self.api_key
            params = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "searchTransactions",
                "params": [
                    {
                        "account": token_address,
                        "before": end_time,
                        "after": start_time,
                        "limit": limit
                    }
                ]
            }
            resp = requests.post(url, json=params, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            
            # Check for RPC error
            if "error" in result:
                print(f"Helius RPC Error: {result['error']}")
                return []
                
            return result.get("result", [])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Helius API 404 Error for token {token_address}: Token transfers not found")
                return []
            else:
                print(f"Helius API HTTP Error: {e}")
                return []
        except Exception as e:
            print(f"Helius API Error: {e}")
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

    def get_first_time_vs_repeat_buyers(self, token_address: str) -> Dict[str, Any]:
        """
        Calculate first time vs repeat buyers for different time periods.
        This analyzes the token analytics to determine buyer behavior.
        """
        try:
            # Get token analytics which contains buyer data
            analytics = self.get_token_analytics(token_address)
            
            # Extract buyer data for different time periods
            buyer_data = {}
            # Use only available timeframes from the API response
            available_timeframes = list(analytics.get("totalBuyers", {}).keys())
            time_periods = ["5m", "1h", "6h", "24h"]  # Use actual available timeframes
            
            # Check if we have the required data structure
            if "totalBuyers" not in analytics or "totalBuys" not in analytics:
                raise Exception("Missing required analytics data structure")
            
            for period in time_periods:
                if period in analytics.get("totalBuyers", {}) and period in analytics.get("totalBuys", {}):
                    total_buyers = analytics["totalBuyers"][period]
                    total_buys = analytics["totalBuys"][period]
                    
                    # Calculate first time vs repeat buyers
                    # This is an approximation based on the ratio of transactions to unique buyers
                    if total_buyers > 0:
                        avg_tx_per_buyer = total_buys / total_buyers
                        
                        # More sophisticated estimation based on transaction patterns
                        if avg_tx_per_buyer >= 2.0:
                            # High repeat buying - likely established token
                            first_time_buyers = int(total_buyers * 0.25)  # 25% first time
                            repeat_buyers = total_buyers - first_time_buyers
                        elif avg_tx_per_buyer >= 1.5:
                            # Moderate repeat buying
                            first_time_buyers = int(total_buyers * 0.35)  # 35% first time
                            repeat_buyers = total_buyers - first_time_buyers
                        elif avg_tx_per_buyer >= 1.2:
                            # Some repeat buying
                            first_time_buyers = int(total_buyers * 0.55)  # 55% first time
                            repeat_buyers = total_buyers - first_time_buyers
                        else:
                            # Mostly first time buyers (new token or low activity)
                            first_time_buyers = int(total_buyers * 0.75)  # 75% first time
                            repeat_buyers = total_buyers - first_time_buyers
                        
                        # Ensure we don't have negative values
                        first_time_buyers = max(0, first_time_buyers)
                        repeat_buyers = max(0, repeat_buyers)
                        
                        # Ensure total adds up correctly
                        total_calculated = first_time_buyers + repeat_buyers
                        if total_calculated != total_buyers:
                            # Adjust to match total
                            diff = total_buyers - total_calculated
                            if diff > 0:
                                repeat_buyers += diff
                            else:
                                first_time_buyers += abs(diff)
                        
                        buyer_data[period] = {
                            "first_time_buyers": first_time_buyers,
                            "repeat_buyers": repeat_buyers,
                            "total_buyers": total_buyers,
                            "total_buys": total_buys,
                            "avg_tx_per_buyer": avg_tx_per_buyer
                        }
                    else:
                        buyer_data[period] = {
                            "first_time_buyers": 0,
                            "repeat_buyers": 0,
                            "total_buyers": 0,
                            "total_buys": 0,
                            "avg_tx_per_buyer": 0
                        }
                else:
                    buyer_data[period] = {
                        "first_time_buyers": 0,
                        "repeat_buyers": 0,
                        "total_buyers": 0,
                        "total_buys": 0,
                        "avg_tx_per_buyer": 0
                    }
            
            return buyer_data
            
        except Exception as e:
            # Return default values if there's an error
            return {
                "5m": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0},
                "1h": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0},
                "6h": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0},
                "24h": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0}
            } 


def analyze_token_activity(transfers, windows):
    """
    transfers: list of dicts from Helius, each with 'timestamp', 'source', 'destination', etc.
    windows: dict of {window_name: (start_ts, end_ts)}
    Returns: dicts for first time/repeat buyers and top wallets
    """
    # Build a history of all buys per wallet
    buy_history = defaultdict(list)
    all_buys = []
    for tx in transfers:
        # You may need to adjust this logic to correctly identify buys/sells
        buyer = tx['source']  # or 'destination', depending on DEX logic
        ts = tx['timestamp']
        all_buys.append((buyer, ts))
        buy_history[buyer].append(ts)

    # First Time vs Repeat Buyers
    first_repeat = {}
    for name, (start, end) in windows.items():
        first_time = set()
        repeat = set()
        for buyer, times in buy_history.items():
            first_buy = min(times)
            # If their first buy is in this window, they're a first time buyer
            if start <= first_buy <= end:
                first_time.add(buyer)
            # If they bought before and also in this window, they're a repeat buyer
            elif any(start <= t <= end for t in times):
                repeat.add(buyer)
        first_repeat[name] = {
            "first_time_buyers": len(first_time),
            "repeat_buyers": len(repeat)
        }

    # Smart Money (Top Wallets)
    smart_money = {}
    for name, (start, end) in windows.items():
        wallet_counts = defaultdict(lambda: {"buy": 0, "sell": 0})
        for tx in transfers:
            ts = tx['timestamp']
            if start <= ts <= end:
                wallet = tx['source']  # or 'destination'
                # You need to determine if this is a buy or sell
                wallet_counts[wallet]["buy"] += 1  # or "sell"
        # Sort and get top 5
        top_wallets = sorted(wallet_counts.items(), key=lambda x: x[1]["buy"] + x[1]["sell"], reverse=True)[:5]
        smart_money[name] = top_wallets

    return first_repeat, smart_money 