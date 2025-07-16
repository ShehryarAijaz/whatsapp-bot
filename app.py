from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Define tokens with their contract addresses
TOKENS = {
    "rei": "0x6B2504A03ca4D43d0D73776F6aD46dAb2F2a4cFD",
    "jos": "JosjEXh69RckgSs2AWsN1xN8zmiSHxBuJjHLURJnHhg",
    "trump": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "btc": "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf",
    "bios": "0x73Cb479f2ccf77BAd90BcDA91e3987358437240A",
    "tlb": "PEJALXmiYFq6biPkNDuEyFg8B4pwX8hAyesL86qKPwL"
}

def get_token_data_by_contract(contract_address):
    """Fetch token data from Dexscreener by contract address."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['pairs']:
                sorted_pairs = sorted(data['pairs'], key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
                token = sorted_pairs[0]
                return token['baseToken']['symbol'], token['priceUsd'], token.get('marketCap')
    except Exception:
        pass
    return None, None, None

def search_token_by_name(query):
    """Search for token by ticker/symbol or name using Dexscreener's search endpoint."""
    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['pairs']:
                # Take top result with highest liquidity
                sorted_pairs = sorted(data['pairs'], key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
                token = sorted_pairs[0]
                return token['baseToken']['symbol'], token['priceUsd'], token.get('marketCap')
    except Exception:
        pass
    return None, None, None

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in TOKENS:
        symbol, price, market_cap = get_token_data_by_contract(TOKENS[incoming_msg])
    else:
        # Treat it as a custom query to search
        symbol, price, market_cap = search_token_by_name(incoming_msg)

    if price and market_cap:
        msg.body(f"📊 {symbol.upper()} price: ${price} USD\nMarket Cap: ${int(market_cap):,} USD")
    elif price:
        msg.body(f"📊 {symbol.upper()} price: ${price} USD\nMarket Cap: Not available")
    else:
        msg.body(f"❌ Could not find data for '{incoming_msg.upper()}'. Try another token or symbol.")

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)
