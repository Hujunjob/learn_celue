import os
from env import APIKEY,SECRET
import ccxt

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': APIKEY,
    'secret': SECRET,
})

exchange.fapiPrivateGetAccount()
     
