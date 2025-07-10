from dataclasses import dataclass


@dataclass
class SolanaChainParameterConfig:
    min_liquidity_in_usd: float
    min_mcap_in_usd: float
    max_mcap_in_usd: float
    max_holding_percentage_top_5_holders: float
    min_holder_count: int
    min_24h_usd_volume_as_percentage_of_mcap: float
    std_multiple_for_outlier: float 