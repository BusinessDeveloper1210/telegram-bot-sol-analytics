#!/usr/bin/env python3
"""
Test script to verify the Solana scanner setup
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        import requests
        print("✅ requests")
        
        from telebot import TeleBot
        print("✅ pyTelegramBotAPI")
        
        import matplotlib.pyplot as plt
        print("✅ matplotlib")
        
        import numpy as np
        print("✅ numpy")
        
        import pandas as pd
        print("✅ pandas")
        
        # Test local imports
        import utils
        print("✅ utils")
        
        import config
        print("✅ config")
        
        from dex_scanner import chart, tg_msg_templates
        print("✅ dex_scanner.chart")
        print("✅ dex_scanner.tg_msg_templates")
        
        from dex_scanner.data_types import SolanaChainParameterConfig
        print("✅ dex_scanner.data_types")
        
        from dex_scanner.external_clients import DexScreener, MoralisSolana
        print("✅ dex_scanner.external_clients")
        
        from dex_scanner.logger import Logger
        print("✅ dex_scanner.logger")
        
        from dex_scanner.scan_responses import HandlePoolResponse
        print("✅ dex_scanner.scan_responses")
        
        from solana_scanner import SolanaScanner
        print("✅ solana_scanner")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration creation."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import SolanaConfig
        
        config = SolanaConfig()
        print(f"✅ Configuration created successfully")
        print(f"   - Reference name: {config.REFERENCE_NAME}")
        print(f"   - Logs directory: {config.LOGS_DIR}")
        print(f"   - Temp directory: {config.TEMP_DIR}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_scanner_creation():
    """Test scanner creation (without running)."""
    print("\n🤖 Testing scanner creation...")
    
    try:
        from config import SolanaConfig
        from solana_scanner import SolanaScanner
        
        # Create config with test values
        config = SolanaConfig()
        config.MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImZhOTBhMmIxLTEyOGUtNGZkMS05NjMzLTFlOGFhODhkYTBlMCIsIm9yZ0lkIjoiNDUzNTA2IiwidXNlcklkIjoiNDY2NTk1IiwidHlwZUlkIjoiN2JlMDE3Y2EtZDk5Yy00YjMyLWJjOTEtMDhiYWUyNmUzZTNhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDk3MDM2NzksImV4cCI6NDkwNTQ2MzY3OX0.01A0xGL-upQUDtu37GrsO1_jEMJ9c2rpGgBOM628fDA"
        config.TG_BOT_TOKEN = "7068725354:AAGkDVanKkglVoXIcZofDeQLKCfhxve275g"
        config.TG_SIGNALS_CHANNEL_ID = "-1002803549988"
        
        # Create scanner
        scanner = SolanaScanner(config)
        print("✅ Scanner created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Scanner creation error: {e}")
        return False

def test_utils():
    """Test utility functions."""
    print("\n🛠️  Testing utilities...")
    
    try:
        import utils
        import tempfile
        import os
        
        # Test save_json
        test_data = {"test": "data", "number": 123}
        test_file = os.path.join(tempfile.gettempdir(), "test_config.json")
        
        utils.save_json(test_data, test_file)
        print("✅ save_json function works")
        
        # Test load_chain_parameter_config
        config = utils.load_chain_parameter_config("solana")
        print("✅ load_chain_parameter_config function works")
        print(f"   - Loaded {len(config)} parameters")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Utilities error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Solana Scanner Setup Test\n")
    
    tests = [
        test_imports,
        test_config,
        test_scanner_creation,
        test_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scanner is ready to run.")
        print("\nTo run the scanner:")
        print("1. Set your environment variables:")
        print("   export MORALIS_API_KEY='your_key'")
        print("   export TG_BOT_TOKEN='your_token'")
        print("   export TG_SIGNALS_CHANNEL_ID='your_channel'")
        print("2. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 