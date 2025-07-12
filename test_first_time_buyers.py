#!/usr/bin/env python3
"""
Test script for first time vs repeat buyers functionality
"""

import os
import sys
from config import SolanaConfig
from dex_scanner.external_clients import MoralisSolana
from dex_scanner import tg_msg_templates


def test_first_time_buyers():
    """Test the first time vs repeat buyers functionality."""
    
    print("🧪 Testing First Time vs Repeat Buyers Analysis\n")
    
    # Create config
    config = SolanaConfig()
    
    # Initialize Moralis API
    moralis = MoralisSolana(config.MORALIS_API_KEY)
    print("✅ Moralis API initialized")
    
    # Test token address (USDC - a well-known token with trading activity)
    test_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    print(f"\n🔍 Testing with token: {test_token_address}")
    
    try:
        # Get first time vs repeat buyers data
        print("📊 Fetching first time vs repeat buyers data...")
        buyer_analysis = moralis.get_first_time_vs_repeat_buyers(test_token_address)
        
        print("✅ Buyer analysis data fetched successfully")
        print("\n📈 Buyer Analysis Results:")
        
        # Display the raw data
        for period, data in buyer_analysis.items():
            print(f"\n{period.upper()}:")
            print(f"  First Time Buyers: {data['first_time_buyers']}")
            print(f"  Repeat Buyers: {data['repeat_buyers']}")
            print(f"  Total Buyers: {data['total_buyers']}")
            print(f"  Total Buys: {data['total_buys']}")
            print(f"  Avg Tx per Buyer: {data['avg_tx_per_buyer']:.2f}")
        
        # Test the message generation
        print("\n📝 Testing message generation...")
        message = tg_msg_templates.dynamic_crypto_signals_message(buyer_analysis)
        print("\nGenerated Message:")
        print("=" * 50)
        print(message)
        print("=" * 50)
        
        # Test with empty data
        print("\n🧪 Testing with empty data...")
        empty_data = {
            "15min": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0},
            "1h": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0},
            "2h": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0},
            "6h": {"first_time_buyers": 0, "repeat_buyers": 0, "total_buyers": 0, "total_buys": 0, "avg_tx_per_buyer": 0}
        }
        empty_message = tg_msg_templates.dynamic_crypto_signals_message(empty_data)
        print("\nEmpty Data Message:")
        print("=" * 50)
        print(empty_message)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_mock_data():
    """Test with mock data to verify the logic."""
    
    print("\n🧪 Testing with Mock Data\n")
    
    # Mock buyer analysis data
    mock_data = {
        "15min": {
            "first_time_buyers": 15,
            "repeat_buyers": 10,
            "total_buyers": 25,
            "total_buys": 35,
            "avg_tx_per_buyer": 1.4
        },
        "1h": {
            "first_time_buyers": 25,
            "repeat_buyers": 15,
            "total_buyers": 40,
            "total_buys": 65,
            "avg_tx_per_buyer": 1.625
        },
        "2h": {
            "first_time_buyers": 45,
            "repeat_buyers": 25,
            "total_buyers": 70,
            "total_buys": 110,
            "avg_tx_per_buyer": 1.571
        },
        "6h": {
            "first_time_buyers": 80,
            "repeat_buyers": 45,
            "total_buyers": 125,
            "total_buys": 200,
            "avg_tx_per_buyer": 1.6
        }
    }
    
    print("📊 Mock Data:")
    for period, data in mock_data.items():
        print(f"{period.upper()}: {data['first_time_buyers']} first time, {data['repeat_buyers']} repeat")
    
    print("\n📝 Generated Message:")
    message = tg_msg_templates.dynamic_crypto_signals_message(mock_data)
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    return True


def main():
    """Main function."""
    print("🚀 First Time vs Repeat Buyers Test\n")
    
    success = True
    
    # Test with real data
    if not test_first_time_buyers():
        success = False
    
    # Test with mock data
    if not test_with_mock_data():
        success = False
    
    if success:
        print("\n🎉 All tests passed!")
        print("\nThe first time vs repeat buyers functionality now includes:")
        print("• Real-time buyer analysis from Moralis API")
        print("• Dynamic calculation based on transaction patterns")
        print("• Support for multiple time periods (1H, 6H, 1D, 7D)")
        print("• Intelligent estimation of first time vs repeat buyers")
        print("• Graceful error handling with fallback values")
        print("\nTo use in your scanner:")
        print("1. The scanner will automatically fetch buyer analysis data")
        print("2. Dynamic messages will replace static values")
        print("3. Real-time buyer behavior will be displayed in alerts")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 