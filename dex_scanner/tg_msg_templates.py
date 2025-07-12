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
    """Generate alert message for Solana tokens in the ETH (first image) style."""
    # Format numbers
    price_formatted = f"${price_usd:.6f}"
    mcap_formatted = f"${mcap_usd:,.0f}" if mcap_usd >= 1000 else f"${mcap_usd:.0f}"
    liquidity_formatted = f"${liquidity_usd:,.0f}" if liquidity_usd >= 1000 else f"${liquidity_usd:.0f}"
    net_flow_formatted = f"{net_token_flow:,.0f}"
    avg_trades_formatted = f"{avg_trades_per_hour:.1f}"
    liq_mcap_ratio = (liquidity_usd / mcap_usd * 100) if mcap_usd > 0 else 0
    liq_ratio_formatted = f"{liq_mcap_ratio:.2f}%"
    token_age = "Unknown"
    if helius_data and "age_info" in helius_data and "age_formatted" in helius_data["age_info"]:
        token_age = helius_data["age_info"]["age_formatted"]

    # Metrics (try to get real values from Moralis if available)
    avg_trades_7d = None
    net_token_flow_7d = None
    active_addrs_24h = None
    active_addrs_t24h = None
    if moralis_data and "token_analytics" in moralis_data:
        analytics = moralis_data["token_analytics"]
        avg_trades_7d = analytics.get("avgTradesPerHour7d")
        net_token_flow_7d = analytics.get("netTokenFlow7d")
        active_addrs_24h = analytics.get("activeAddresses24h")
        active_addrs_t24h = analytics.get("activeAddressesT24h")

    # Build message
    message = f"""
<u>Token Details</u>
├ Chain: <code>SOL</code>
├ Name: <code>{token_name}</code>
├ Symbol: <code>{token_symbol}</code>
├ Total Supply: <code>{total_supply:,}</code>
├ Token Age: <code>{token_age}</code>
├ Holders: <code>{holder_count:,}</code>
├ MCap: <code>{mcap_formatted}</code>
├ Liquidity: <code>{liquidity_formatted}</code>
├ Liq/Mcap Ratio: <code>{liq_ratio_formatted}</code>
└ Dexes: <code>{', '.join(dexes)}</code>

<u>Price:</u> <code>{price_formatted}</code>

<u>Token Address</u>
<code>{token_address}</code>
"""
    # Metrics section
    metrics_lines = []
    if avg_trades_7d is not None:
        metrics_lines.append(f"├ Avg. Trades Per Hour 7D: <code>{avg_trades_7d}</code>")
    if net_token_flow_7d is not None:
        metrics_lines.append(f"├ Net Token Flow 7D: <code>{net_token_flow_7d}</code>")
    if active_addrs_24h is not None:
        metrics_lines.append(f"├ Active Addrs. 24H: <code>{active_addrs_24h}</code>")
    if active_addrs_t24h is not None:
        metrics_lines.append(f"└ Active Addrs. T-24H: <code>{active_addrs_t24h}</code>")
    if metrics_lines:
        message += f"\n<u>Metrics</u>\n" + "\n".join(metrics_lines)

    # Links section
    if links:
        message += f"\n\n<u>Links</u>\n"
        for link in links:
            if link.get('url'):
                message += f"├ <a href='{link['url']}'>{link['name']}</a>\n"
        message = message.rstrip('\n')
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

def detailed_tx_analysis_solana_text(tx_analysis: dict) -> str:
    """Return a detailed Solana transaction analysis message using real values from tx_analysis, with Buy/Sell Wallets in italic. Only include 6H and 24H timeframes."""
    message = "🔄 <b><u>Transaction Analysis</u></b> 🔄\n\n"
    for timeframe in ["6H", "24H"]:
        if timeframe in tx_analysis:
            data = tx_analysis[timeframe]
            buy_data = data.get('buy', {})
            sell_data = data.get('sell', {})
            message += f"<b>{timeframe} Transaction Analysis</b>\n"
            message += f"├ BUY Outlier: <b>{buy_data.get('outlier', 'N/A')}</b>\n"
            message += f"├ BUY Avg: <b>{buy_data.get('avg', 'N/A')}</b>\n"
            message += f"├ BUY StDev: <b>{buy_data.get('stdev', 'N/A')}</b>\n"
            message += f"├ <i>BUY Wallets:</i> <b><i>{buy_data.get('wallets', 'N/A')}</i></b>\n"
            message += f"├ SELL Outlier: <b>{sell_data.get('outlier', 'N/A')}</b>\n"
            message += f"├ SELL Avg: <b>{sell_data.get('avg', 'N/A')}</b>\n"
            message += f"├ SELL StDev: <b>{sell_data.get('stdev', 'N/A')}</b>\n"
            message += f"└ <i>SELL Wallets:</i> <b><i>{sell_data.get('wallets', 'N/A')}</i></b>\n\n"
    return message.strip()

def static_smart_money_message(*, first_repeat: dict | None = None, smart_money: dict | None = None) -> str:
    """Return a Smart Money message with top wallets data (3D/14D), dynamic if provided, else static."""
    if smart_money is not None:
        def format_wallets(wallets):
            lines = []
            for i, (wallet, stats) in enumerate(wallets, 1):
                lines.append(f"├ #{i} Buy txs: {stats['buy']}  || Sell txs: {stats.get('sell', 0)}")
            if lines:
                lines[-1] = lines[-1].replace('├', '└', 1)
            return '\n'.join(lines)
        msg = "🧠 Smart Money 🧠\n\n"
        for period in ["3D", "14D"]:
            msg += f"<b>Top Wallets {period}</b>\n"
            wallets = smart_money.get(period, [])
            msg += format_wallets(wallets) + "\n\n"
        return msg.strip()
    # fallback to static
    return (
        "🧠 Smart Money 🧠\n\n"
        "<b>Top Wallets 3D</b>\n"
        "├ #1 Buy txs: 1  || Sell txs: 2\n"
        "├ #2 Buy txs: 3  || Sell txs: 0\n"
        "├ #3 Buy txs: 3  || Sell txs: 1\n"
        "├ #4 Buy txs: 4  || Sell txs: 0\n"
        "└ #5 Buy txs: 3  || Sell txs: 0\n\n"
        "<b>Top Wallets 14D</b>\n"
        "├ #1 Buy txs: 1  || Sell txs: 2\n"
        "├ #2 Buy txs: 3  || Sell txs: 0\n"
        "├ #3 Buy txs: 3  || Sell txs: 1\n"
        "├ #4 Buy txs: 4  || Sell txs: 0\n"
        "└ #5 Buy txs: 3  || Sell txs: 0\n"
    )


def dynamic_crypto_signals_message(buyer_analysis: dict) -> str:
    """Return a dynamic Crypto Signals message with real first time vs repeat buyers data."""
    
    # Helper function to format time periods
    def format_period(period: str) -> str:
        if period == "5m":
            return "5M"
        elif period == "1h":
            return "1H"
        elif period == "6h":
            return "6H"
        elif period == "24h":
            return "24H"
        else:
            return period.upper()
    
    # Build the message
    message = "🚨 Crypto Signals 🚨\n💰 <b>First Time Vs Repeat Buyers</b> 💰\n\n"
    
    # Add data for each time period
    time_periods = ["5m", "1h", "6h", "24h"]
    
    for period in time_periods:
        if period in buyer_analysis:
            data = buyer_analysis[period]
            first_time = data.get("first_time_buyers", 0)
            repeat = data.get("repeat_buyers", 0)
            
            message += f"<b>{format_period(period)}</b>\n├ First Time Buyers: {first_time}\n└ Repeat Buyers: {repeat}\n\n"
        else:
            message += f"<b>{format_period(period)}</b>\n├ First Time Buyers: 0\n└ Repeat Buyers: 0\n\n"
    
    return message 

