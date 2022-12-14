import ccxt
import matplotlib.pyplot as plt
from pandas import DataFrame, read_csv
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
from config import DATA_DIR,FETCH_TOKENS
import os


#######################################################################################################

#从币安获取价格数据，然后存储在文件里，供之后研究策略使用

#######################################################################################################

binance = ccxt.binance(
    {
        "proxies": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        },
    }
)

#从binance获取价格
#输入交易对，k线间隔，开始时间戳
def fetch_price(
    symbol:str,    
    timeframe:str,
    since:int,
    limit:int
) -> DataFrame:
    kline = binance.fetchOHLCV(symbol=symbol, timeframe=timeframe,since=since,limit=limit)

    df:DataFrame = DataFrame()

    for data in kline:
        readable_time: datetime = datetime.fromtimestamp(  # type: ignore
                                data[0] / 1000, tz=ZoneInfo("Asia/Shanghai")
                                )
        # readable_time = readable_time.strftime('%Y-%m-%d %H:%M:%S')
        readable_time = readable_time.strftime('%Y-%m-%d')
        start_price = data[1]
        end_price = data[4]
        change = (end_price - start_price)/start_price
        change = round(change*100,2)
        df = pd.concat([df,DataFrame({"time":[readable_time],"start":start_price,'end':end_price,'change/%':change})],ignore_index=True)
        #下面的方法将被废弃
        # df = df.append(
        #         DataFrame({"Time":[readable_time],"Price":price}),ignore_index=True
            # )
    return df



def fetch_all_price(
    symbol:str,    
    timeframe:str,
    start:int
) ->DataFrame:
    # 时间戳

    #由于从交易所单次获取数据是有限制的，手动每次获取1000条数据，然后拼接
    frame01:DataFrame = fetch_price(symbol,timeframe,start,1000)
    frame02:DataFrame = fetch_price(symbol,timeframe,start+1000*86400*1000,1000)
    frame:DataFrame = pd.concat([frame01,frame02],ignore_index=True)
    return frame


def fetch_and_save(
    symbol:str,    
    timeframe:str,
    start:int
):
    frame:DataFrame = fetch_all_price(symbol,timeframe,start)
    symbol = symbol.replace("/","-")
    file = os.path.join(DATA_DIR,f"{symbol}.csv")
    print(f"save file {file}")
    frame.to_csv(file)


time2019 = 1546272000000
time2022 = 1640966400000

for token in FETCH_TOKENS:
    fetch_and_save(token,'1d',time2019)