# coding=utf-8

import datetime
import os
import sys
import traceback
from xmlrpc.client import ServerProxy

import easytrader as et
import numpy as np
import pandas as pd
import pandas.io.json as json


def int2str(ints):
    sb = '000000'
    if isinstance(ints, list) or isinstance(ints, np.ndarray):
        lst = []
        for i in ints:
            lst.append(sb[0:6 - len(str(int(i)))] + str(i))
        return lst
    else:
        return sb[0:6 - len(str(int(ints)))] + str(int(ints))


def adjust_position(config, stocks):
    # if len(stocks) ==0: return
    user = et.use('xq')
    user.prepare(config)

    j = 0

    try:
        for s in user.position:
            try:
                if s['stock_code'] not in stocks.code:
                    user.adjust_weight(s['stock_code'], 0)
                    pass
                else:
                    stocks = stocks.drop([stocks['code'] == s['stock_code']], axis=0)
                    j = j + 1
            except:
                traceback.print_exc()
                continue

        vol = (user.balance[0]['enable_balance'] - 100) / max(10 - j, len(stocks) - j)

        stocks = np.array(stocks)
        for s in stocks:
            try:
                user.buy(int2str(s[0]), volume=vol)
                pass
            except:
                traceback.print_exc()
    except:
        traceback.print_exc()


def trade():
    map = {
           # '''MR_T2_B256_C2_E1000_Lclose_K5_XSGD': 'S2016-01-01.20181009.11.29.52.run','''
        'MR_T10_B256_C2_E2000_Lclose_K5_XSGD':'S2015-01-03.20181119.17.27.09.run',
        'MR_T5_B256_C2_E2000_Lclose_K5_XSGD': 'S2015-01-03.20181114.11.21.34.run'}
    file = os.path.realpath(__file__)
    os.chdir(os.path.dirname(file))
    s = ServerProxy("http://127.0.0.1:8080")
    data_str = s.predict_today_rpc2(json.dumps(map), False)

    dataset = pd.read_json(data_str,orient='records')
    for model in map.keys():
        stocks = dataset[dataset['model'] == model]

        if not os.path.exists(model): os.makedirs(model)
        datapath = datetime.datetime.now().strftime(model + '/T%Y%m%d.txt')
        stocks.to_csv(datapath)

        # stocks = pd.read_csv(datapath,index_col=0).sort_values('proba',ascending=False)

        adjust_position(model + '.json', stocks[stocks.proba > 0.5][:10])


if __name__ == '__main__':
    trade()
