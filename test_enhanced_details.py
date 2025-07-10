#!/usr/bin/env python3
"""
Test script for enhanced token details functionality
"""

import os
import sys
from config import SolanaConfig
from dex_scanner.external_clients import MoralisSolana, HeliusAPI
from dex_scanner import tg_msg_templates


def test_enhanced_token_details():
    """Test the enhanced token details functionality."""
    
    print("🧪 Testing Enhanced Token Details\n")
    
    # Create config
    config = SolanaConfig()
    
    # Initialize APIs
    moralis = MoralisSolana(config.MORALIS_API_KEY)
    helius = None
    if config.HELIUS_API_KEY:
        helius = HeliusAPI(config.HELIUS_API_KEY)
        print("✅ Helius API initialized")
    else:
        print("⚠️  Helius API not available (no API key)")
    
    print("✅ Moralis API initialized")
    
    # Test token address (you can replace this with any Solana token)
    test_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    
    print(f"\n🔍 Testing with token: {test_token_address}")
    
    try:
        # Get Moralis data
        print("📊 Fetching Moralis data...")
        token_metadata = moralis.get_token_metadata(test_token_address)
        token_analytics = moralis.get_token_analytics(test_token_address)
        holder_stats = moralis.get_token_holder_stats(test_token_address)
        
        moralis_data = {
            "token_analytics": token_analytics,
            "holder_stats": holder_stats,
            "token_metadata": token_metadata
        }
        
        print("✅ Moralis data fetched successfully")
        
        # Get Helius data if available
        helius_data = None
        if helius:
            print("🌐 Fetching Helius data...")
            helius_data = helius.get_enhanced_token_details(test_token_address)
            print("✅ Helius data fetched successfully")
        
        # Generate enhanced message
        print("\n📝 Generating enhanced token details message...")
        
        # Mock some values for demonstration
        token_name = token_metadata.get("name", "Test Token")
        token_symbol = token_metadata.get("symbol", "TEST")
        total_supply = token_metadata.get("totalSupplyFormatted", "1,000,000")
        token_age = "388d 21h 31m"  # Mock age
        holder_count = holder_stats.get("totalHolders", 1000)
        mcap_usd = 1000000.0  # Mock market cap
        liquidity_usd = 500000.0  # Mock liquidity
        liq_mcap_ratio = (liquidity_usd / mcap_usd * 100) if mcap_usd > 0 else 0
        dexes = ["UniswapV2", "PumpSwap"]
        
        enhanced_message = tg_msg_templates.enhanced_token_details_text(
            token_name=token_name,
            token_symbol=token_symbol,
            total_supply=total_supply,
            token_age=token_age,
            holder_count=holder_count,
            mcap_usd=mcap_usd,
            liquidity_usd=liquidity_usd,
            liq_mcap_ratio=liq_mcap_ratio,
            dexes=dexes,
            moralis_data=moralis_data,
            helius_data=helius_data,
        )
        
        print("\n📋 Enhanced Token Details Message:")
        print("=" * 50)
        print(enhanced_message)
        print("=" * 50)
        
        print("\n✅ Enhanced token details test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main function."""
    print("🚀 Enhanced Token Details Test\n")
    
    if test_enhanced_token_details():
        print("\n🎉 All tests passed!")
        print("\nTo use enhanced token details in your scanner:")
        print("1. Set your HELIUS_API_KEY environment variable")
        print("2. Run the scanner: python main.py")
        print("3. Enhanced token details will be automatically included in alerts")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 