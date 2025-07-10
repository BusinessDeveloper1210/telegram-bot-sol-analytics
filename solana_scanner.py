import os
import time
from telebot import TeleBot

import utils
from dex_scanner import chart, tg_msg_templates
from dex_scanner.data_types import SolanaChainParameterConfig
from dex_scanner.external_clients import DexScreener, MoralisSolana, HeliusAPI
from dex_scanner.logger import Logger
from dex_scanner.scan_responses import HandlePoolResponse

from config import SolanaConfig


class SolanaScanner:
    SECONDS_TO_SLEEP_ON_ERROR = 60

    def __init__(self, chain_config: SolanaConfig) -> None:
        self.chain_config = chain_config

        self.tg_bot = TeleBot(
            token=self.chain_config.TG_BOT_TOKEN,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        self.moralis = MoralisSolana(self.chain_config.MORALIS_API_KEY)
        self.dex_screener = DexScreener(self.chain_config.CHAIN_ID_BY_NAME)
        
        # Initialize Helius API if key is provided
        self.helius = None
        if self.chain_config.HELIUS_API_KEY:
            self.helius = HeliusAPI(self.chain_config.HELIUS_API_KEY)

        _chain_parameter_config = utils.load_chain_parameter_config(
            self.chain_config.REFERENCE_NAME
        )
        self.chain_parameter_config = SolanaChainParameterConfig(
            **_chain_parameter_config
        )

        self.logger = Logger(
            f"scanner_{self.chain_config.REFERENCE_NAME}",
            self.chain_config.LOGS_DIR,
        )

        # State
        self._ignorable_tokens = {}

    def _add_token_to_ignore(self, pool: str, ignore_till_timestamp: int) -> None:
        self._ignorable_tokens[pool] = ignore_till_timestamp

    def _token_is_ignorable(self, token: str, timestamp: int) -> bool:
        if token in self._ignorable_tokens:
            return self._ignorable_tokens[token] >= timestamp
        return False

    def _handle_token_of_interest(
        self,
        token_data: dict,
        timestamp: int,
    ) -> HandlePoolResponse:
        token_address = token_data["tokenAddress"]

        if self._token_is_ignorable(token_address, timestamp):
            self.logger.info(f"Token {token_address} is ignorable")
            return HandlePoolResponse.IGNORABLE

        # Check min liquidity requirement
        if (
            float(token_data["liquidity"])
            < self.chain_parameter_config.min_liquidity_in_usd
        ):
            self.logger.info(
                f"Token {token_address} doesn't meet min liquidity: {token_data['liquidity']}"
            )
            return HandlePoolResponse.MIN_LIQUIDITY

        # Check market cap range requirement
        mcap_usd = float(token_data["fullyDilutedValuation"])
        if (
            mcap_usd < self.chain_parameter_config.min_mcap_in_usd
            or mcap_usd > self.chain_parameter_config.max_mcap_in_usd
        ):
            self.logger.info(
                f"Token {token_address} doesn't meet mcap range: {mcap_usd}"
            )
            return HandlePoolResponse.MCAP_RANGE

        # Get token holder data
        top_token_holders = self.moralis.get_top_token_holders(token_address, limit=10)
        top_5_holders = []
        for holder in top_token_holders:
            if holder["isContract"]:
                continue
            top_5_holders.append(holder)
            if len(top_5_holders) == 5:
                break

        # Check conditions
        top_5_holders_percentage_holding = 0
        for holder in top_5_holders:
            top_5_holders_percentage_holding += holder[
                "percentageRelativeToTotalSupply"
            ]
        if (
            top_5_holders_percentage_holding
            > self.chain_parameter_config.max_holding_percentage_top_5_holders
        ):
            self.logger.info(
                f"Top 5 holders holding for token {token_address} above threshold, top 5: {top_5_holders_percentage_holding} %"
            )
            return HandlePoolResponse.TOP_5_HOLDERS_ABOVE_TH

        # Check min holders
        token_holder_stats = self.moralis.get_token_holder_stats(token_address)
        if (
            token_holder_stats["totalHolders"]
            < self.chain_parameter_config.min_holder_count
        ):
            self.logger.info(
                f"Min holder count {token_address} not met. Count: {token_holder_stats['totalHolders']}"
            )
            return HandlePoolResponse.LOW_HOLDER_COUNT

        # Get token analytics
        token_analytics = self.moralis.get_token_analytics(token_address)

        # Verify 24H usd Volume
        _24h_usd_volume = (
            token_analytics["totalBuyVolume"]["24h"]
            + token_analytics["totalBuyVolume"]["24h"]
        )
        if _24h_usd_volume < (
            mcap_usd
            * self.chain_parameter_config.min_24h_usd_volume_as_percentage_of_mcap
            / 100
        ):
            self.logger.info(
                f"Token {token_address} does not meet min 24H USD Volume: {_24h_usd_volume}"
            )
            return HandlePoolResponse.MIN_24H_VOLUME

        # Check if it passes tx_analysis condition
        h1_threshold = (
            token_analytics["totalBuyVolume"]["24h"]
            * self.chain_parameter_config.std_multiple_for_outlier
        ) / 24
        if token_analytics["totalBuyVolume"]["1h"] <= h1_threshold:
            self.logger.info(
                f"Token's {token_address} txs does not meet the outlier requirement: (outlier {token_analytics['totalBuyVolume']['1h']:.2f}), (th {h1_threshold:.2f})"
            )
            return HandlePoolResponse.NO_BUY_OUTLIER

        # Get additional data for alert message
        token_metadata = self.moralis.get_token_metadata(token_address)
        token_pairs = self.moralis.get_token_pairs(token_address)
        pool_address = ""
        for pair in token_pairs:
            if pair["exchangeName"] == "PumpSwap":
                pool_address = pair["pairAddress"]
                break
        dexes = ["PumpSwap"]
        net_token_flow = (
            token_analytics["totalBuyVolume"]["24h"]
            - token_analytics["totalSellVolume"]["24h"]
        ) / float(token_data["priceUsd"])
        avg_trades_per_hour = (
            token_analytics["totalBuys"]["24h"] + token_analytics["totalSells"]["24h"]
        ) / 24
        candlestick_data = self.moralis.get_24h_candlestick_data(pool_address)
        tx_analysis = self._get_tx_analysis(token_analytics)
        try:
            links = self.dex_screener.get_links(pool_address)
        except Exception as e:
            # NOTE: Adding this here while we try out DexScreener
            self.logger.error(f"DexScreener for pool {pool_address} failed due to: {e}")
            links = []

        # Fetch enhanced token details from Helius if available
        helius_data = None
        if self.helius:
            try:
                helius_data = self.helius.get_enhanced_token_details(token_address)
                self.logger.info(f"Fetched Helius data for token: {token_address}")
            except Exception as e:
                self.logger.error(f"Failed to fetch Helius data for token {token_address}: {e}")

        # Prepare Moralis data for enhanced display
        moralis_data = {
            "token_analytics": token_analytics,
            "holder_stats": token_holder_stats,
            "token_metadata": token_metadata
        }

        # Send Enhanced Alert
        self.logger.info(f"Sending enhanced alert for token: {token_address}")
        self._send_alert(
            token_name=token_metadata["name"],
            token_symbol=token_metadata["symbol"],
            total_supply=int(float(token_metadata["totalSupplyFormatted"])),
            token_address=token_address,
            pool_address=pool_address,
            holder_count=token_holder_stats["totalHolders"],
            price_usd=float(token_data["priceUsd"]),
            mcap_usd=mcap_usd,
            liquidity_usd=float(token_data["liquidity"]),
            net_token_flow=net_token_flow,
            avg_trades_per_hour=avg_trades_per_hour,
            tx_analysis=tx_analysis,
            dexes=dexes,
            candlestick_data=candlestick_data,
            links=links,
            moralis_data=moralis_data,
            helius_data=helius_data,
        )

        self._add_token_to_ignore(
            token_address,
            timestamp + self.chain_config.SECONDS_TO_IGNORE_TOKEN_OR_POOL_AFTER_SIGNAL,
        )
        self._store_alerted_token_data(
            token_address,
            pool_address,
            token_metadata["name"],
            token_metadata["symbol"],
            timestamp,
            top_5_holders,
        )

        return HandlePoolResponse.PASSED

    def _get_tx_analysis(self, token_analytics: dict) -> dict:
        tws = ["5M", "1H", "6H", "24H"]
        analysis = {}
        for tw in tws:
            _tw_lower = tw.lower()
            analysis[tw] = {
                "buy": {
                    "avg": token_analytics["totalBuyVolume"][_tw_lower]
                    / token_analytics["totalBuyers"][_tw_lower]
                    if token_analytics["totalBuyers"][_tw_lower] > 0
                    else token_analytics["totalBuyVolume"][_tw_lower],
                    "txs": token_analytics["totalBuys"][_tw_lower],
                    "wallets": token_analytics["totalBuyers"][_tw_lower],
                },
                "sell": {
                    "avg": token_analytics["totalSellVolume"][_tw_lower]
                    / token_analytics["totalSellers"][_tw_lower]
                    if token_analytics["totalSellers"][_tw_lower] > 0
                    else token_analytics["totalSellVolume"][_tw_lower],
                    "txs": token_analytics["totalSells"][_tw_lower],
                    "wallets": token_analytics["totalSellers"][_tw_lower],
                },
            }
        return analysis

    def _send_alert(
        self,
        token_name: str,
        token_symbol: str,
        total_supply: int,
        token_address: str,
        pool_address: str,
        holder_count: int,
        price_usd: float,
        mcap_usd: float,
        liquidity_usd: float,
        net_token_flow: float,
        avg_trades_per_hour: float,
        tx_analysis: dict,
        dexes: list[str],
        candlestick_data: list[dict],
        links: list[dict],
        moralis_data: dict | None = None,
        helius_data: dict | None = None,
    ) -> None:
        # Send Alert Token Info Message
        text = tg_msg_templates.alert_message_solana_text(
            chain_reference_name=self.chain_config.REFERENCE_NAME,
            token_name=token_name,
            token_symbol=token_symbol,
            total_supply=total_supply,
            token_address=token_address,
            pool_address=pool_address,
            holder_count=holder_count,
            price_usd=price_usd,
            mcap_usd=mcap_usd,
            liquidity_usd=liquidity_usd,
            net_token_flow=net_token_flow,
            avg_trades_per_hour=avg_trades_per_hour,
            dexes=dexes,
            links=links,
            moralis_data=moralis_data,
            helius_data=helius_data,
        )
        chart_path = os.path.join(
            self.chain_config.TEMP_DIR,
            f"{token_address}_price_chart.png",
        )
        hours = (
            candlestick_data[-1]["timestamp"] - candlestick_data[0]["timestamp"]
        ) / 3600
        chart_title = f"Price Chart for {token_symbol} <b>(Last {hours:.1f}H)</b>"
        chart.create_candlestick_chart(
            chart_title,
            chart_path,
            candlestick_data,
        )
        with open(chart_path, "rb") as image:
            self.tg_bot.send_photo(
                self.chain_config.TG_SIGNALS_CHANNEL_ID,
                image,
                text,
            )

        # Send TX Analysis message
        self.tg_bot.send_message(
            self.chain_config.TG_SIGNALS_CHANNEL_ID,
            tg_msg_templates.tx_analysis_solana_text(tx_analysis),
        )



    def _store_alerted_token_data(
        self,
        token_address: str,
        pool_address: str,
        name: str,
        symbol: str,
        timestamp: int,
        top_holders: list[dict],
    ) -> None:
        top_holder_data = [
            {
                "address": holder["ownerAddress"],
                "balance": float(holder["balanceFormatted"]),
            }
            for holder in top_holders
        ]
        data = {
            "address": token_address,
            "pool_address": pool_address,
            "name": name,
            "symbol": symbol,
            "timestamp_alerted": timestamp,
            "top_holders": top_holder_data,
        }
        utils.save_json(
            data,
            os.path.join(self.chain_config.TOKENS_ALERTED_DIR, f"{token_address}.json"),
        )

    def run(self) -> None:
        self.logger.info("Started")

        while True:
            start_time = time.time()

            _chain_parameter_config = utils.load_chain_parameter_config(
                self.chain_config.REFERENCE_NAME
            )
            self.chain_parameter_config = SolanaChainParameterConfig(
                **_chain_parameter_config
            )

            try:
                timestamp = int(time.time())
                tokens = self.moralis.get_recently_graduated_tokens()

                scan_report = {}
                for token_data in tokens:
                    try:
                        resp = self._handle_token_of_interest(token_data, timestamp)
                    except Exception as e:
                        self.logger.error(
                            f"Failed to handle token of interest {token_data['tokenAddress']} due to {e}"
                        )
                        self.logger.log_exception_stack_trace(e)
                        resp = HandlePoolResponse.ERROR

                    # Convert enum to string for JSON serialization
                    resp_key = resp.value
                    if resp_key not in scan_report:
                        scan_report[resp_key] = 0
                    scan_report[resp_key] += 1

                # Store scan report
                utils.save_json(
                    scan_report,
                    os.path.join(
                        self.chain_config.INDIVIDUAL_SCAN_REPORTS_DIR,
                        f"{int(time.time())}.json",
                    ),
                )

            except Exception as e:
                self.logger.error(
                    f"Ran into the following error while executing scan: {e}"
                )
                self.logger.log_exception_stack_trace(e)
                time.sleep(self.SECONDS_TO_SLEEP_ON_ERROR)
                continue

            # Sleep till next execution
            exec_secs = time.time() - start_time
            secs_to_sleep = self.chain_config.SECONDS_BETWEEN_SCANS - exec_secs
            self.logger.info(f"Finished cycle scan, sleeping for: {secs_to_sleep:.2f}")
            if secs_to_sleep > 0:
                time.sleep(secs_to_sleep)
