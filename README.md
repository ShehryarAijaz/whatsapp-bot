# Crypto Price WhatsApp Bot

A simple Flask-based WhatsApp bot using Twilio and Dexscreener API to fetch real-time token prices and market cap.

## Features

- Search token data by name, symbol, or contract address
- Returns price and market cap
- Supports predefined and custom tokens

## Setup

1. Clone the repo  
   `git clone https://github.com/yourusername/crypto-price-bot.git`

2. Install dependencies  
   `pip install -r requirements.txt`

3. Run the server  
   `python app.py`

4. Set Twilio WhatsApp sandbox webhook to:  
   `http://your-server.com/webhook`

## Example

- Message: `btc`  
- Response: `BTC price: $65,432.12 USD, Market Cap: $1,234,567,890`

## License

MIT
