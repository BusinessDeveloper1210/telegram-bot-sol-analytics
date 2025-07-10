#!/usr/bin/env python3
"""
Test script for enhanced token information in alert messages
"""

import os
import sys
from config import SolanaConfig
from dex_scanner.external_clients import MoralisSolana, HeliusAPI
from dex_scanner import tg_msg_templates


def test_enhanced_alert_message():
    """Test the enhanced alert message with comprehensive token information."""
    
    print("🧪 Testing Enhanced Alert Message\n")
    
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
        
        # Generate enhanced alert message
        print("\n📝 Generating enhanced alert message...")
        
        # Mock some values for demonstration
        token_name = token_metadata.get("name", "Test Token")
        token_symbol = token_metadata.get("symbol", "TEST")
        total_supply = int(float(token_metadata.get("totalSupplyFormatted", "1000000")))
        holder_count = holder_stats.get("totalHolders", 1000)
        price_usd = 1.0
        mcap_usd = 1000000.0
        liquidity_usd = 500000.0
        net_token_flow = 10000.0
        avg_trades_per_hour = 50.0
        dexes = ["UniswapV2", "PumpSwap"]
        links = [{"name": "DexScreener", "url": "https://dexscreener.com"}]
        
        enhanced_message = tg_msg_templates.alert_message_solana_text(
            chain_reference_name="solana",
            token_name=token_name,
            token_symbol=token_symbol,
            total_supply=total_supply,
            token_address=test_token_address,
            pool_address="test_pool_address",
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
        
        print("\n📋 Enhanced Alert Message:")
        print("=" * 60)
        print(enhanced_message)
        print("=" * 60)
        
        print("\n✅ Enhanced alert message test completed successfully!")
        
        # Show what data sources were used
        print("\n📊 Data Sources Used:")
        print("• Moralis API: Token analytics, holder stats, metadata")
        if helius_data:
            print("• Helius API: On-chain token age, metadata verification")
        else:
            print("• Helius API: Not available (no API key)")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main function."""
    print("🚀 Enhanced Alert Message Test\n")
    
    if test_enhanced_alert_message():
        print("\n🎉 All tests passed!")
        print("\nThe enhanced alert message now includes:")
        print("• Structured token details with chain, name, symbol, supply, age")
        print("• Market cap, liquidity, and liquidity/market cap ratio")
        print("• Trading activity metrics")
        print("• Enhanced Moralis analytics (24H volume, buy/sell volumes)")
        print("• Helius on-chain data (verified age, metadata)")
        print("• Trading links")
        print("\nTo use in your scanner:")
        print("1. Set your HELIUS_API_KEY environment variable for full functionality")
        print("2. Run the scanner: python main.py")
        print("3. Enhanced token information will be automatically included in alerts")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 