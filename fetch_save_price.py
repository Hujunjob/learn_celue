import ccxt
import matplotlib.pyplot as plt
from pandas import DataFrame, read_csv
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
from config import DATA_DIR
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


# 时间戳
time2019 = 1546272000000
time2022 = 1640966400000


#由于从交易所单次获取数据是有限制的，手动每次获取1000条数据，然后拼接
btcFrame01:DataFrame = fetch_price("BTC/USDT",'1d',time2019,1000)
btcFrame02:DataFrame = fetch_price("BTC/USDT",'1d',time2019+1000*86400*1000,1000)
btcFrame:DataFrame = pd.concat([btcFrame01,btcFrame02],ignore_index=True)


ethFrame01:DataFrame = fetch_price("ETH/USDT",'1d',time2019,1000)
ethFrame02:DataFrame = fetch_price("ETH/USDT",'1d',time2019+1000*86400*1000,1000)
ethFrame:DataFrame = pd.concat([ethFrame01,ethFrame02],ignore_index=True)


btcFrame.to_csv(os.path.join(DATA_DIR,"BTC-USDT.csv"))
ethFrame.to_csv(os.path.join(DATA_DIR,"ETH-USDT.csv"))


# plt.xlabel('time')
# plt.ylabel('price')
# plt.plot(btcFrame["Time"],btcFrame["Price"])
# plt.show()

