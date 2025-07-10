# Solana Token Scanner

A comprehensive Solana token scanner that monitors recently graduated tokens on PumpSwap and sends alerts via Telegram when they meet specific criteria.

## Features

- 🔍 **Token Monitoring**: Scans recently graduated tokens on PumpSwap
- 📊 **Multi-Criteria Analysis**: Checks liquidity, market cap, holder distribution, and trading activity
- 📈 **Chart Generation**: Creates candlestick charts with volume data
- 📱 **Telegram Alerts**: Sends formatted alerts with token information and charts
- 🔄 **Continuous Scanning**: Runs continuously with configurable intervals
- 📝 **Logging**: Comprehensive logging with file and console output

## Requirements

- Python 3.9+
- Moralis API key
- Telegram Bot Token
- Telegram Channel ID
- Helius API key (optional, for enhanced token details)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd solana-scanner
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export MORALIS_API_KEY="your_moralis_api_key"
   export TG_BOT_TOKEN="your_telegram_bot_token"
   export TG_SIGNALS_CHANNEL_ID="your_telegram_channel_id"
   export HELIUS_API_KEY="your_helius_api_key"  # Optional, for enhanced token details
   ```

## Configuration

The scanner uses a configuration system with the following parameters:

### Chain Parameters (`chain_parameters/solana.json`)
```json
{
  "min_liquidity_in_usd": 10000,
  "min_mcap_in_usd": 100000,
  "max_mcap_in_usd": 10000000,
  "max_holding_percentage_top_5_holders": 50.0,
  "min_holder_count": 100,
  "min_24h_usd_volume_as_percentage_of_mcap": 5.0,
  "std_multiple_for_outlier": 2.0
}
```

### Scanner Configuration (`config.py`)
- `SECONDS_BETWEEN_SCANS`: Time between scan cycles (default: 60)
- `SECONDS_TO_IGNORE_TOKEN_OR_POOL_AFTER_SIGNAL`: Ignore tokens after alert (default: 3600)

## Usage

### Running the Scanner

```bash
python main.py
```

### Testing Enhanced Token Details

To test the enhanced token details functionality:

```bash
python test_enhanced_details.py
```

This will demonstrate the enhanced token details format and verify API connectivity.

### Manual Execution

```python
from solana_scanner import SolanaScanner
from config import SolanaConfig

config = SolanaConfig()
scanner = SolanaScanner(config)
scanner.run()
```

## Token Analysis Criteria

The scanner evaluates tokens based on the following criteria:

1. **Liquidity Check**: Minimum USD liquidity requirement
2. **Market Cap Range**: Token must be within specified market cap range
3. **Holder Distribution**: Top 5 holders must not exceed threshold percentage
4. **Minimum Holders**: Token must have minimum number of holders
5. **24H Volume**: Must meet minimum 24-hour USD volume as percentage of market cap
6. **Buy Outlier**: Must show significant buy activity in the last hour

## Alert Format

Alerts include:
- **Enhanced Token Details**: Comprehensive token information with structured layout
- Token basic information (name, symbol, price, market cap)
- Holder statistics
- Trading activity metrics
- Candlestick chart with volume
- Transaction analysis breakdown
- Trading links

### Enhanced Token Details Format

The scanner now provides enhanced token details in a structured format:

```
📋 Token Details
├ Chain: SOL
├ Name: TokenName
├ Symbol: SYMBOL
├ Total Supply: 1,000,000
├ Token Age: 388d 21h 31m
├ Holders: 679
├ MCap: $388K
├ Liquidity: $70.4K
├ Liq/Mcap Ratio: 18.13%
└ Dexes: UniswapV2, PumpSwap
```

This enhanced format includes:
- **Moralis Data**: 24H volume, buy/sell volumes, holder statistics
- **Helius Data**: On-chain token age, metadata verification
- **Real-time Values**: All values are fetched from APIs, not static

## File Structure

```
solana-scanner/
├── main.py                 # Main execution file
├── solana_scanner.py       # Main scanner class
├── moralis_solana.py       # Moralis API client
├── config.py              # Configuration management
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── dex_scanner/          # Scanner package
│   ├── __init__.py
│   ├── chart.py          # Chart generation
│   ├── data_types.py     # Data structures
│   ├── external_clients.py # API clients
│   ├── logger.py         # Logging functionality
│   ├── scan_responses.py # Response enums
│   └── tg_msg_templates.py # Telegram templates
├── logs/                 # Log files
├── temp/                 # Temporary files (charts)
├── tokens_alerted/       # Alerted token data
├── scan_reports/         # Scan reports
└── chain_parameters/     # Chain configuration files
```

## API Dependencies

### Moralis API
- Token metadata
- Token analytics
- Holder statistics
- Candlestick data
- Token pairs

### Helius API
- Enhanced token metadata
- Token age calculation
- On-chain data verification
- Token supply information

### DexScreener API
- Trading links
- Pool information

### Telegram Bot API
- Message sending
- Photo uploads

## Error Handling

The scanner includes comprehensive error handling:
- API rate limiting with exponential backoff
- Network error retries
- Graceful degradation for missing data
- Detailed logging of errors and exceptions

## Monitoring

The scanner provides:
- Real-time console output
- Detailed log files with timestamps
- Scan reports with statistics
- Alerted token data storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the repository. 