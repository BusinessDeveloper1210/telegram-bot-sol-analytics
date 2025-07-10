#!/usr/bin/env python3
"""
Main execution file for Solana Scanner
"""

import os
import sys
from solana_scanner import SolanaScanner
from config import SolanaConfig


def main():
    """Main function to run the Solana scanner."""
    
    # Create configuration first
    config = SolanaConfig()
    
    # Check if required values are available (either from env vars or defaults)
    required_values = [
        ("MORALIS_API_KEY", config.MORALIS_API_KEY),
        ("TG_BOT_TOKEN", config.TG_BOT_TOKEN), 
        ("TG_SIGNALS_CHANNEL_ID", config.TG_SIGNALS_CHANNEL_ID)
    ]
    
    missing_values = []
    for name, value in required_values:
        if not value:
            missing_values.append(name)
    
    if missing_values:
        print("❌ Missing required configuration values:")
        for var in missing_values:
            print(f"   - {var}")
        print("\nPlease set these environment variables or update the default values in config.py")
        sys.exit(1)
    
    # Create and run scanner
    scanner = SolanaScanner(config)
    
    try:
        print("🚀 Starting Solana Scanner...")
        scanner.run()
    except KeyboardInterrupt:
        print("\n⏹️  Scanner stopped by user")
    except Exception as e:
        print(f"❌ Scanner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 