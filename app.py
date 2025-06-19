from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Define tokens with their contract addresses
TOKENS = {
    "rei": "0x6B2504A03ca4D43d0D73776F6aD46dAb2F2a4cFD",  # Replace with actual REI contract address
    "jos": "JosjEXh69RckgSs2AWsN1xN8zmiSHxBuJjHLURJnHhg",  # Example for ETH
    "trump": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "btc": "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf",
    "bios": "0x73Cb479f2ccf77BAd90BcDA91e3987358437240A",
    "tlb": "PEJALXmiYFq6biPkNDuEyFg8B4pwX8hAyesL86qKPwL"
}

def get_token_data(contract_address):
    """Fetch the token price and market cap from Dexscreener API using the contract address."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        response = requests.get(url, timeout=5)  # 5-second timeout
        if response.status_code == 200:
            data = response.json()
            if data['pairs'] and len(data['pairs']) > 0:
                # Select pair with highest liquidity
                sorted_pairs = sorted(data['pairs'], key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
                price = sorted_pairs[0]['priceUsd']
                market_cap = sorted_pairs[0]['marketCap']
                return price, market_cap
            return None, None
        return None, None
    except Exception:
        return None, None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in TOKENS:
        contract_address = TOKENS[incoming_msg]
        price, market_cap = get_token_data(contract_address)
        if price and market_cap:
            # Directly use the exact price and market cap without formatting
            msg.body(f"The current price of {incoming_msg.upper()} is ${price} USD, Market Cap is ${int(market_cap):,} USD.")
        else:
            msg.body(f"Sorry, I couldn't fetch the price or market cap for {incoming_msg.upper()}. Try again later.")
    else:
        msg.body("Hey, we currently only support 'rei, jos, trump' tokens. :)")

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)
