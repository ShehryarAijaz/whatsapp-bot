from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import traceback
import os

app = Flask(__name__)

# Define tokens with their contract addresses
TOKENS = {
    "rei": "0x6B2504A03ca4D43d0D73776F6aD46dAb2F2a4cFD",  
    "jos": "JosjEXh69RckgSs2AWsN1xN8zmiSHxBuJjHLURJnHhg",  
    "trump": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "btc": "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf"
}

def get_token_data(contract_address):
    """Fetch the token price and market cap from Dexscreener API using the contract address."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    print(f"[DEBUG] Fetching token data from URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)  # 5-second timeout
        print(f"[DEBUG] Received response with status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Response JSON keys: {list(data.keys())}")

            if data.get('pairs'):
                sorted_pairs = sorted(data['pairs'], key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
                price = sorted_pairs[0]['priceUsd']
                market_cap = sorted_pairs[0]['marketCap']
                print(f"[DEBUG] Selected Pair - Price: {price}, Market Cap: {market_cap}")
                return price, market_cap
            else:
                print("[WARN] No 'pairs' found in API response.")
                return None, None
        else:
            print(f"[ERROR] Non-200 response: {response.text}")
            return None, None

    except Exception as e:
        print(f"[EXCEPTION] Error fetching token data: {str(e)}")
        traceback.print_exc()
        return None, None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip().lower()
    print(f"[DEBUG] Incoming message: '{incoming_msg}'")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in TOKENS:
        contract_address = TOKENS[incoming_msg]
        print(f"[DEBUG] Token matched: {incoming_msg.upper()}, Address: {contract_address}")

        price, market_cap = get_token_data(contract_address)

        if price and market_cap:
            reply_text = (f"The current price of {incoming_msg.upper()} is ${price} USD, "
                          f"Market Cap is ${int(market_cap):,} USD.")
            print(f"[DEBUG] Reply: {reply_text}")
            msg.body(reply_text)
        else:
            error_text = f"Sorry, I couldn't fetch the price or market cap for {incoming_msg.upper()}."
            print(f"[ERROR] {error_text}")
            msg.body(error_text)
    else:
        error_text = "Hey, we currently only support 'rei, jos, trump' tokens. :)"
        print(f"[WARN] Unknown token: {incoming_msg}")
        msg.body(error_text)

    return str(resp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)