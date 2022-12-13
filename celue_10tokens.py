#######################################################################################################

#最简单的开始策略：轮替策略
#当比特币涨幅超过以太坊，则购买比特币
#否则购买以太坊

#######################################################################################################

import matplotlib.pyplot as plt
import matplotlib
from pandas import DataFrame, read_csv
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
from config import DATA_DIR,BACKTEST_DATA_DIR,FETCH_TOKENS
import os

font = {'family':'Arial Unicode MS'}
matplotlib.rc('font',**font)

all_tokens_file_name = "all_tokens_change.csv"
back_test_file="back_test_10tokens.csv"

#从币里面选取每天涨幅最大的3个
max_size = 3

def cal_all_token_change():
    dataFrames:dict = dict()
    for token in FETCH_TOKENS:
        symbol = token.replace("/","-")
        df:DataFrame = pd.read_csv(os.path.join(DATA_DIR,f"{symbol}.csv"))
        dataFrames[token] = df
    
    all_token_change_df:DataFrame = DataFrame()
    for index in dataFrames[FETCH_TOKENS[0]].index:
        time = dataFrames[FETCH_TOKENS[0]]['time'][index]
        frameData:dict = dict()
        frameData['time'] = [time]
        for token in FETCH_TOKENS:
            frameData[f"{token}_change"] = dataFrames[token]['change/%'][index]
        all_token_change_df = pd.concat([all_token_change_df,DataFrame(frameData)],ignore_index=True)
    all_token_change_df.to_csv(os.path.join(BACKTEST_DATA_DIR,all_tokens_file_name))

#只需要保存一次
# cal_all_token_change()



#开始分析涨跌
change_data_df:DataFrame = pd.read_csv(os.path.join(BACKTEST_DATA_DIR,all_tokens_file_name))

back_test_df:DataFrame = DataFrame()

for index in change_data_df.index:
    time = change_data_df['time'][index]

    #首先，需要看前一天谁的涨跌幅大，然后买入涨幅大的
    #比如，前一天btc涨幅大，今天开盘价我买入btc
    #第二天，看btc价格变化，算出净值。继续轮替策略买入新的，卖出旧的
    if(index==0):
        back_test_df = pd.concat([back_test_df,
        DataFrame({'time':[time],
        '今天买入Rank1':'无','Rank1涨幅':0,'卖出Rank1涨幅':0,
        '今天买入Rank2':'无','Rank2涨幅':0,'卖出Rank2涨幅':0,
        '今天买入Rank3':'无','Rank3涨幅':0,'卖出Rank3涨幅':0,
        '开盘收益':0, '持仓U':1000,'持仓净值':1})],ignore_index=True)
        continue
    #看昨天前三的涨幅
    #根据今天这3个币的涨幅，计算收益

    alltokenchange:dict = dict()
    for token in FETCH_TOKENS:
        token_change = change_data_df[token+'_change'][index-1]
        alltokenchange[token] = token_change

    ranked = sorted(alltokenchange.items(),key=lambda s:-s[1])

    
    # #前一天买入，然后今天看看昨天该币的涨跌幅，计算净值
    totalU = back_test_df['持仓U'][index-1]
    total =  back_test_df['持仓净值'][index-1]

    next_total_u = totalU
    change_before:list = [0,0,0]
    if back_test_df[f'今天买入Rank1'][index-1] !='无':
        for i in range(0,max_size):
            #昨天开盘买的币
            hold_token_before = back_test_df[f'今天买入Rank{i+1}'][index-1]
            #今天看昨天结束的涨幅
            change_before[i] = change_data_df[hold_token_before+'_change'][index-1]
            #计算收益
            profit = totalU/max_size * change_before[i]/100
            next_total_u += profit
            

    earn = round(next_total_u - totalU,2)
    next_total_u = round(next_total_u,2)
    
    back_test_df = pd.concat([back_test_df,
        DataFrame({'time':[time],
        '今天买入Rank1':ranked[0][0],'Rank1涨幅':ranked[0][1],'卖出Rank1涨幅':change_before[0],
        '今天买入Rank2':ranked[1][0],'Rank2涨幅':ranked[1][1],'卖出Rank2涨幅':change_before[1],
        '今天买入Rank3':ranked[2][0],'Rank3涨幅':ranked[2][1],'卖出Rank3涨幅':change_before[2],
        '开盘收益':earn, '持仓U':next_total_u,'持仓净值':round(next_total_u/1000,2)})],ignore_index=True)
    # back_test_df = pd.concat([back_test_df,
    #     DataFrame({'time':[time],'BTC当日涨幅':btc_change,'ETH当日涨幅':eth_change,'买入':buy_crypto,'开盘收益':earn, '持仓U': totalU,'持仓净值':round(totalU/1000,2)})],ignore_index=True)
       
back_test_df.to_csv(os.path.join(BACKTEST_DATA_DIR,back_test_file))

# plt.rcParams['font.sans-serif'] = ['Arial Black'] # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
# 
eth_price_df:DataFrame = pd.read_csv(os.path.join(DATA_DIR,"ETH-USDT.csv"))
doge_price_df:DataFrame = pd.read_csv(os.path.join(DATA_DIR,"DOGE-USDT.csv"))


font = {'family':'Arial Unicode MS'}
matplotlib.rc('font',**font)
plt.title("持仓净值-10选3策略")
plt.xlabel('时间')
plt.ylabel('净值')
plt.grid(True)
plt.grid(color='red',ls='--')
x = back_test_df["time"]
plt.plot(x,back_test_df["持仓净值"],label="持仓净值")
plt.plot(x,eth_price_df["start"]/eth_price_df["start"][0],label="ETH-USDT")
plt.plot(x,doge_price_df["start"]/doge_price_df["start"][0],label="DOGE-USDT")
plt.xticks(x[::90], rotation=45)
plt.legend()
plt.show()

