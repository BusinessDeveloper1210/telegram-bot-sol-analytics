import os
from dataclasses import dataclass


@dataclass
class SolanaConfig:
    # API Keys
    MORALIS_API_KEY: str = os.getenv("MORALIS_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImZhOTBhMmIxLTEyOGUtNGZkMS05NjMzLTFlOGFhODhkYTBlMCIsIm9yZ0lkIjoiNDUzNTA2IiwidXNlcklkIjoiNDY2NTk1IiwidHlwZUlkIjoiN2JlMDE3Y2EtZDk5Yy00YjMyLWJjOTEtMDhiYWUyNmUzZTNhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDk3MDM2NzksImV4cCI6NDkwNTQ2MzY3OX0.01A0xGL-upQUDtu37GrsO1_jEMJ9c2rpGgBOM628fDA")
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "a3581119-3185-4c36-b698-e281526f4200")
    TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN", "7066246808:AAEAvJULF5ZIhPtg6JJ3ZY_9a3ZeTp-7Jg8")
    

    # Telegram Configuration
    TG_SIGNALS_CHANNEL_ID: str = os.getenv("TG_SIGNALS_CHANNEL_ID", "-1002550238152")
    
    # Chain Configuration
    REFERENCE_NAME: str = "solana"
    CHAIN_ID_BY_NAME: dict = None  # type: ignore
    
    # Directory Configuration
    LOGS_DIR: str = "logs"
    TEMP_DIR: str = "temp"
    TOKENS_ALERTED_DIR: str = "alerted_tokens"
    INDIVIDUAL_SCAN_REPORTS_DIR: str = "scan_reports"
    
    # Timing Configuration
    SECONDS_BETWEEN_SCANS: int = 30
    SECONDS_TO_IGNORE_TOKEN_OR_POOL_AFTER_SIGNAL: int = 60
    
    def __post_init__(self):
        if self.CHAIN_ID_BY_NAME is None:
            self.CHAIN_ID_BY_NAME = {"solana": "solana"}
        
        # Create directories if they don't exist
        for directory in [self.LOGS_DIR, self.TEMP_DIR, self.TOKENS_ALERTED_DIR, self.INDIVIDUAL_SCAN_REPORTS_DIR]:
            os.makedirs(directory, exist_ok=True) 