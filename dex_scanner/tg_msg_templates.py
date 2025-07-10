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
) -> str:
    """Generate alert message for Solana tokens."""
    
    # Format numbers
    price_formatted = f"${price_usd:.6f}"
    mcap_formatted = f"${mcap_usd:,.0f}"
    liquidity_formatted = f"${liquidity_usd:,.0f}"
    net_flow_formatted = f"{net_token_flow:,.0f}"
    avg_trades_formatted = f"{avg_trades_per_hour:.1f}"
    
    # Create message
    message = f"""
🚨 <b>SOLANA TOKEN ALERT</b> 🚨

📊 <b>Token Information</b>
• <b>Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Total Supply:</b> {total_supply:,}
• <b>Price:</b> <code>{price_formatted}</code>
• <b>Market Cap:</b> <code>{mcap_formatted}</code>
• <b>Liquidity:</b> <code>{liquidity_formatted}</code>

👥 <b>Holder Statistics</b>
• <b>Total Holders:</b> {holder_count:,}

📈 <b>Trading Activity</b>
• <b>Net Token Flow:</b> <code>{net_flow_formatted}</code>
• <b>Avg Trades/Hour:</b> <code>{avg_trades_formatted}</code>

🔗 <b>Links</b>
• <b>Token Address:</b> <code>{token_address}</code>
• <b>Pool Address:</b> <code>{pool_address}</code>
"""
    
    # Add DEX links
    if links:
        message += "\n🌐 <b>Trading Links:</b>\n"
        for link in links:
            if link.get('url'):
                message += f"• <a href='{link['url']}'>{link['name']}</a>\n"
    
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