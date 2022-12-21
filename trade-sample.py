import os
from env import APIKEY,SECRET
import ccxt

binance = ccxt.binance(
    {
        "proxies": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        },
        'apiKey': APIKEY,
        'secret': SECRET,
    }
)

def open_margin(_symbol,_direction,_amount):
    # _symbol = "BTCUSDT"
    # _direction = "BUY"
    # _direction = "SELL"
    # _amount=0.001

    order_res = binance.fapiPrivatePostOrder({
        "symbol": _symbol,
        "side": _direction,
        "type": "MARKET",
        "positionSide":"LONG",
        "quantity": _amount
    })
    orderid = order_res['orderId']
    print(order_res)

open_margin("BTCUSDT","BUY",0.001)

# result = binance.fapiPrivateGetAccount()
# result = binance.fapiPrivateV2GetAccount()
# assets = result['assets']
# positions = result['positions']

# for position in positions:
#     if(abs(float( position['positionAmt']))>0.00001):
#         print(position)
    

