#######################################################################################################

#最简单的开始策略：轮替策略
#当比特币涨幅超过以太坊，则购买比特币
#否则购买以太坊
#优化方案：前一天如果大饼和以太都跌，则今天空仓

#######################################################################################################

import matplotlib.pyplot as plt
import matplotlib
from pandas import DataFrame, read_csv
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
from config import DATA_DIR,BACKTEST_DATA_DIR
import os

font = {'family':'Arial Unicode MS'}
matplotlib.rc('font',**font)

btc_df:DataFrame = pd.read_csv(os.path.join(DATA_DIR,"BTC-USDT.csv"))
eth_df:DataFrame = pd.read_csv(os.path.join(DATA_DIR,"ETH-USDT.csv"))

change_data_file = "btc_eth_price_change.csv"
back_test_file ="back_test_celue1_youhua.csv"
back_test1_file ="back_test_celue1.csv"


#开始分析涨跌
change_data_df:DataFrame = pd.read_csv(os.path.join(BACKTEST_DATA_DIR,change_data_file))

back_test_df:DataFrame = DataFrame()

for index in change_data_df.index:
    time = btc_df['time'][index]
    #首先，需要看前一天谁的涨跌幅大，然后买入涨幅大的
    #比如，前一天btc涨幅大，今天开盘价我买入btc
    #第二天，看btc价格变化，算出净值。继续轮替策略买入新的，卖出旧的
    btc_change = change_data_df['btc_change'][index]
    eth_change = change_data_df['eth_change'][index]
    if(index==0):
        back_test_df = pd.concat([back_test_df,
        DataFrame({'time':[time],'BTC当日涨幅':btc_change,'ETH当日涨幅':eth_change,'买入':'无','开盘收益':0, '持仓U':1000,'持仓净值':1})],ignore_index=True)
        continue
    #看昨天的涨幅
    btc_change_before = change_data_df['btc_change'][index-1]
    eth_change_before = change_data_df['eth_change'][index-1]
    totalU = back_test_df['持仓U'][index-1]
    total =  back_test_df['持仓净值'][index-1]
    #如果大饼和以太都跌，则不买入
    buy_crypto = "BTC"
    if(btc_change_before>eth_change_before):
        buy_crypto = 'BTC'
    else:
        buy_crypto = 'ETH'
    if btc_change_before<0 and eth_change_before<0:
        buy_crypto = "无"

    lastbuy = back_test_df['买入'][index-1]
    if lastbuy=='无':
        back_test_df = pd.concat([back_test_df,
        DataFrame({'time':[time],'BTC当日涨幅':btc_change,'ETH当日涨幅':eth_change,'买入':buy_crypto,'开盘收益':0, '持仓U':totalU,'持仓净值':round(totalU/1000,2)})],ignore_index=True)
        continue
    
    #前一天买入，然后今天看看昨天该币的涨跌幅，计算净值
    earn = 0

    if lastbuy == 'BTC':
        earn = btc_change_before/100 * totalU
    else:
        earn = eth_change_before/100 * totalU
    earn = round(earn,2)
    totalU = round(totalU+earn,2)
    back_test_df = pd.concat([back_test_df,
        DataFrame({'time':[time],'BTC当日涨幅':btc_change,'ETH当日涨幅':eth_change,'买入':buy_crypto,'开盘收益':earn, '持仓U': totalU,'持仓净值':round(totalU/1000,2)})],ignore_index=True)
       
back_test_df.to_csv(os.path.join(BACKTEST_DATA_DIR,back_test_file))


back_test1_df:DataFrame = pd.read_csv(os.path.join(BACKTEST_DATA_DIR,back_test1_file))
eth_price_df:DataFrame = pd.read_csv(os.path.join(DATA_DIR,"ETH-USDT.csv"))


plt.title("持仓净值-ETH/BTC价格轮动策略-优化方案")
plt.xlabel('时间')
plt.ylabel('净值')
plt.grid(True)
plt.grid(color='red',ls='--')

x = back_test_df["time"]
plt.plot(x,back_test_df["持仓净值"],label='优化后持仓净值')
plt.plot(x,back_test1_df['持仓净值'],label='未优化持仓净值')
plt.plot(x,eth_price_df["start"]/eth_price_df["start"][0],label="ETH-USDT")
plt.legend()
plt.xticks(x[::90], rotation=45)
plt.show()