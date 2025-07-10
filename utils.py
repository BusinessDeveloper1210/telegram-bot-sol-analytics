import json
import os
from typing import Any, Dict


def load_chain_parameter_config(reference_name: str) -> Dict[str, Any]:
    """Load chain parameter configuration from JSON file."""
    config_path = f"chain_parameters/{reference_name}.json"
    
    # Default configuration if file doesn't exist
    default_config = {
        "min_liquidity_in_usd": 10000,
        "min_mcap_in_usd": 100000,
        "max_mcap_in_usd": 10000000,
        "max_holding_percentage_top_5_holders": 50.0,
        "min_holder_count": 100,
        "min_24h_usd_volume_as_percentage_of_mcap": 5.0,
        "std_multiple_for_outlier": 2.0
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            return default_config
    
    # Create directory and save default config
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    save_json(default_config, config_path)
    return default_config


def save_json(data: Any, file_path: str) -> None:
    """Save data to JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2) 