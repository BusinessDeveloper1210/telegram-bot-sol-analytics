from typing import List, Dict, Any


def alert_message_solana_text(
    chain_reference_name: str,
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
    dexes: List[str],
    links: List[Dict[str, str]],
    moralis_data: Dict[str, Any] | None = None,
    helius_data: Dict[str, Any] | None = None,
) -> str:
    """Generate alert message for Solana tokens with enhanced information."""
    
    # Format numbers
    price_formatted = f"${price_usd:.6f}"
    mcap_formatted = f"${mcap_usd:,.0f}" if mcap_usd >= 1000 else f"${mcap_usd:.0f}"
    liquidity_formatted = f"${liquidity_usd:,.0f}" if liquidity_usd >= 1000 else f"${liquidity_usd:.0f}"
    net_flow_formatted = f"{net_token_flow:,.0f}"
    avg_trades_formatted = f"{avg_trades_per_hour:.1f}"
    
    # Calculate liquidity to market cap ratio
    liq_mcap_ratio = (liquidity_usd / mcap_usd * 100) if mcap_usd > 0 else 0
    liq_ratio_formatted = f"{liq_mcap_ratio:.2f}%"
    
    # Get token age from Helius data
    token_age = "Unknown"
    if helius_data and "age_info" in helius_data and "age_formatted" in helius_data["age_info"]:
        token_age = helius_data["age_info"]["age_formatted"]
    
    # Create enhanced token information section
    message = f"""
🚨 <b>SOLANA TOKEN ALERT</b> 🚨

📋 <b>Token Details</b>
├ <b>Chain:</b> <code>SOL</code>
├ <b>Name:</b> <code>{token_name}</code>
├ <b>Symbol:</b> <code>{token_symbol}</code>
├ <b>Total Supply:</b> <code>{total_supply:,}</code>
├ <b>Token Age:</b> <code>{token_age}</code>
├ <b>Holders:</b> <code>{holder_count:,}</code>
├ <b>Price:</b> <code>{price_formatted}</code>
├ <b>MCap:</b> <code>{mcap_formatted}</code>
├ <b>Liquidity:</b> <code>{liquidity_formatted}</code>
├ <b>Liq/Mcap Ratio:</b> <code>{liq_ratio_formatted}</code>
└ <b>Dexes:</b> <code>{', '.join(dexes)}</code>

📈 <b>Trading Activity</b>
• <b>Net Token Flow:</b> <code>{net_flow_formatted}</code>
• <b>Avg Trades/Hour:</b> <code>{avg_trades_formatted}</code>

🔗 <b>Links</b>
• <b>Token Address:</b> <code>{token_address}</code>
• <b>Pool Address:</b> <code>{pool_address}</code>
"""
    
    # Add enhanced Moralis data if available
    if moralis_data:
        message += "\n🔍 <b>Moralis Analytics</b>\n"
        if "token_analytics" in moralis_data:
            analytics = moralis_data["token_analytics"]
            if "totalBuyVolume" in analytics and "totalSellVolume" in analytics:
                buy_24h = analytics["totalBuyVolume"].get("24h", 0)
                sell_24h = analytics["totalSellVolume"].get("24h", 0)
                total_volume = buy_24h + sell_24h
                message += f"• <b>24H Volume:</b> <code>${total_volume:,.0f}</code>\n"
                message += f"• <b>Buy Volume:</b> <code>${buy_24h:,.0f}</code>\n"
                message += f"• <b>Sell Volume:</b> <code>${sell_24h:,.0f}</code>\n"
        
        if "holder_stats" in moralis_data:
            holder_stats = moralis_data["holder_stats"]
            message += f"• <b>Verified Holders:</b> <code>{holder_stats.get('totalHolders', 'N/A')}</code>\n"
    
    # Add enhanced Helius data if available
    if helius_data:
        message += "\n🌐 <b>Helius On-Chain Data</b>\n"
        if "age_info" in helius_data and "age_formatted" in helius_data["age_info"]:
            age = helius_data["age_info"]["age_formatted"]
            message += f"• <b>Verified Age:</b> <code>{age}</code>\n"
        
        if "metadata" in helius_data and "metadata" in helius_data["metadata"]:
            metadata = helius_data["metadata"]["metadata"]
            if metadata and "name" in metadata:
                message += f"• <b>On-chain Name:</b> <code>{metadata['name']}</code>\n"
            if metadata and "symbol" in metadata:
                message += f"• <b>On-chain Symbol:</b> <code>{metadata['symbol']}</code>\n"
    
    # Add DEX links
    if links:
        message += "\n🌐 <b>Trading Links:</b>\n"
        for link in links:
            if link.get('url'):
                message += f"• <a href='{link['url']}'>{link['name']}</a>\n"
    
    return message.strip()


def enhanced_token_details_text(
    token_name: str,
    token_symbol: str,
    total_supply: str,
    token_age: str,
    holder_count: int,
    mcap_usd: float,
    liquidity_usd: float,
    liq_mcap_ratio: float,
    dexes: List[str],
    moralis_data: Dict[str, Any] | None = None,
    helius_data: Dict[str, Any] | None = None,
) -> str:
    """Generate enhanced token details message with comprehensive information."""
    
    # Format numbers
    mcap_formatted = f"${mcap_usd:,.0f}" if mcap_usd >= 1000 else f"${mcap_usd:.0f}"
    liquidity_formatted = f"${liquidity_usd:,.0f}" if liquidity_usd >= 1000 else f"${liquidity_usd:.0f}"
    liq_ratio_formatted = f"{liq_mcap_ratio:.2f}%"
    
    # Create the main token details section
    message = f"""
📋 <b>Token Details</b>
├ <b>Chain:</b> <code>SOL</code>
├ <b>Name:</b> <code>{token_name}</code>
├ <b>Symbol:</b> <code>{token_symbol}</code>
├ <b>Total Supply:</b> <code>{total_supply}</code>
├ <b>Token Age:</b> <code>{token_age}</code>
├ <b>Holders:</b> <code>{holder_count:,}</code>
├ <b>MCap:</b> <code>{mcap_formatted}</code>
├ <b>Liquidity:</b> <code>{liquidity_formatted}</code>
├ <b>Liq/Mcap Ratio:</b> <code>{liq_ratio_formatted}</code>
└ <b>Dexes:</b> <code>{', '.join(dexes)}</code>
"""
    
    # Add Moralis data if available
    if moralis_data:
        message += "\n🔍 <b>Moralis Data</b>\n"
        if "token_analytics" in moralis_data:
            analytics = moralis_data["token_analytics"]
            if "totalBuyVolume" in analytics and "totalSellVolume" in analytics:
                buy_24h = analytics["totalBuyVolume"].get("24h", 0)
                sell_24h = analytics["totalSellVolume"].get("24h", 0)
                total_volume = buy_24h + sell_24h
                message += f"├ <b>24H Volume:</b> <code>${total_volume:,.0f}</code>\n"
                message += f"├ <b>Buy Volume:</b> <code>${buy_24h:,.0f}</code>\n"
                message += f"└ <b>Sell Volume:</b> <code>${sell_24h:,.0f}</code>\n"
        
        if "holder_stats" in moralis_data:
            holder_stats = moralis_data["holder_stats"]
            message += f"├ <b>Total Holders:</b> <code>{holder_stats.get('totalHolders', 'N/A')}</code>\n"
    
    # Add Helius data if available
    if helius_data:
        message += "\n🌐 <b>Helius Data</b>\n"
        if "age_info" in helius_data and "age_formatted" in helius_data["age_info"]:
            age = helius_data["age_info"]["age_formatted"]
            message += f"├ <b>Token Age:</b> <code>{age}</code>\n"
        
        if "metadata" in helius_data and "metadata" in helius_data["metadata"]:
            metadata = helius_data["metadata"]["metadata"]
            if metadata and "name" in metadata:
                message += f"├ <b>On-chain Name:</b> <code>{metadata['name']}</code>\n"
            if metadata and "symbol" in metadata:
                message += f"└ <b>On-chain Symbol:</b> <code>{metadata['symbol']}</code>\n"
    
    return message.strip()


def tx_analysis_solana_text(tx_analysis: Dict[str, Dict[str, Dict[str, Any]]]) -> str:
    """Generate transaction analysis message."""
    
    message = "📊 <b>Transaction Analysis</b>\n\n"
    
    for timeframe, data in tx_analysis.items():
        buy_data = data['buy']
        sell_data = data['sell']
        
        message += f"⏰ <b>{timeframe}</b>\n"
        message += f"🟢 <b>Buys:</b> {buy_data['txs']} txs, {buy_data['wallets']} wallets, avg ${buy_data['avg']:.2f}\n"
        message += f"🔴 <b>Sells:</b> {sell_data['txs']} txs, {sell_data['wallets']} wallets, avg ${sell_data['avg']:.2f}\n\n"
    
    return message.strip() 