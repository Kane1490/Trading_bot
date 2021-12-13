from binance import Client
import requests
from dotenv import load_dotenv
import os
import ta
import pandas as pd
from time import sleep
from binance.exceptions import BinanceAPIException
import time
from datetime import datetime

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")

client = Client(api_key, api_secret)

def getdata(symbol):
    try:
        frame = pd.DataFrame(client.get_historical_klines(symbol, '1m', '10m UTC'))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        frame = pd.DataFrame(client.get_historical_klines(symbol, '1m', '10m UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time','Open', 'High','Low','Close','Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def tradingstrat(symbol, open_position = False):    
    df = getdata(symbol)
    trade_size = None
    buyprice = None     
    if not open_position:

        if ta.trend.macd_diff(df.Close).iloc[-1] > 0 \
        and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
            balance = client.get_asset_balance(asset='BUSD')
            balance= balance['free']
            balance = float(balance)
            trade_size = (balance * .30)/(df.Close).iloc[-1]
            
            order = client.create_order(symbol=symbol,
                                            side='BUY',
                                            type='MARKET',
                                            quantity=trade_size)
            print(order)
            open_position = True
            buyprice = float(order['fills'][0]['price'])
                
                
                
        if open_position:
            
            df = getdata(symbol)
            
            if ta.trend.macd_diff(df.Close).iloc[-1] < 0 \
            and ta.trend.macd_diff(df.Close).iloc[-2] > 0 | df.Close[-1] <= buyprice * 0.90 or df.Close >= 2 * buyprice:
                order = client.create_order(symbol=symbol,
                                            side='BUY',
                                            type='MARKET',
                                            quantity=trade_size) 
                print(order)
                sellprice = float(order['fills'][0]['price'])
                print(f'profit = {(sellprice - buyprice)/buyprice}')
                open_position = False
                
                    
                

while True:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(f'MACD -- No Trade as of:', dt_string)
    sleep(60) 
    tradingstrat('ETHBUSD')