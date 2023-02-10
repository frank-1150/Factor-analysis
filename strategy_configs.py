import re, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sb

# query from binance_client.futures_ticker() on 2023-02-09, sort in quote volume DESC
with open('./FUTURE_PAIR_UNIVERSE.json') as f:
    read = json.load(f)
    FUTURE_PAIR_UNIVERSE = read['data']
    NOT_IN_15M_PAIRS = read['not_in_15m_pairs']

# BLOOMBERG_GALAXY_CRYPTO_INDEX_WEIGHTS = [0.35, 0.35, 0.0614, 0.0483, 0.039, 0.0336, 0.0277, 0.0268, 0.0247, 0.0205, 0.0181]
# NOT_IN_15M_PAIRS = ["RNDRUSDT", "HIGHUSDT", "MINAUSDT", "TUSDT"]

def get_usdt_pair(pairList=FUTURE_PAIR_UNIVERSE):
    '''return a list of pairs with quote currency in USDT'''
    result = []
    for pair in pairList:
        x = re.search(r"USDT$", pair)
        if x:
            result.append(pair)
#             print(pair)
    return result

def get_busd_pair(pairList=FUTURE_PAIR_UNIVERSE):
    '''return a list of pairs with quote currency in BUSD'''
    result = []
    for pair in pairList:
        x = re.search(r"BUSD$", pair)
        if x:
            result.append(pair)
    return result

def get_coins_universe(pairList=FUTURE_PAIR_UNIVERSE):
    '''return a list of unique name of coins'''
    result = set()
    for pair in pairList:
        if '1000' in pair:
#             print(f'before={pair}')
            pair = pair.replace('1000', '')
#             print(f'after={pair}')
        x = re.search(r"BUSD$", pair)
        y = re.search(r"USDT$", pair)
        if x:
            # replace BUSD with empty string
            x = re.sub("BUSD$", "", pair)
            result.add(x)
        elif y:
            # replace USDT with empty string
            y = re.sub("USDT$", "", pair)
            result.add(y)
#         print(x or y, pair)
    return list(result)

def get_not_in_15m_pairs():
    return NOT_IN_15M_PAIRS

def get_close_price_agg_df(symbol_list, data_dic):
    res = {}
    for sym in symbol_list:
        future_series = data_dic[sym].rename(columns={'Close': sym})[sym]
        res[sym] = future_series
    return pd.DataFrame(res)

def get_single_logreturn_series(aggPrice_df, assetName:str):
    return pd.DataFrame(np.log((aggPrice_df[assetName]/aggPrice_df[assetName].shift(1)) )).rename(columns={assetName: assetName+'_logreturn'})

def get_index_logreturn_from_agg_price_df(aggPrice_df, indexAssetName_list:list, index_name:str, weights=None):
#     columnNames_list = [name+"_logreturn" for name in indexAssetName_list]
    columnNames_list = ['index_logreturn_' + str(len(indexAssetName_list))]
    selected_df = aggPrice_df[indexAssetName_list]
    if weights:
        logreturn_df = pd.DataFrame((np.log((selected_df/selected_df.shift(1))) * weights).sum(axis=1), columns=[index_name])
    else:
        logreturn_df = pd.DataFrame(np.log((selected_df/selected_df.shift(1)).mean(axis=1) ), 
                                columns= [index_name])
    return logreturn_df

def get_alpha(index_return_df, asset_return_df):
    result_df = pd.concat([index_return_df, asset_return_df], axis=1)
    indexName = index_return_df.columns[0]
    assetName = asset_return_df.columns[0]
    result_df[assetName + '_alpha'] = result_df[assetName] - result_df[indexName]
    return result_df
def plot_alpha(index_return_df, aggPrice_df, assetName):
    fig, ax = plt.subplots(figsize=(9, 5), dpi=110)
    rose_return_df = get_single_logreturn_series(all_coins_price_agg_df, assetName)
    get_alpha(index_return_df, rose_return_df).cumsum().plot(ax=plt.gca(), title='Alpha of '+assetName)
def get_all_alpha(index_return_df, assetName_list):
    result_df = pd.DataFrame()
    for assetName in assetName_list:
        asset_return_df = get_single_logreturn_series(all_coins_price_agg_df, assetName)
        result_df = pd.concat([result_df, get_alpha(index_return_df, asset_return_df)[assetName + '_logreturn_alpha']], axis=1)
    return result_df
if __name__=='__main__':
    print(NOT_IN_15M_PAIRS)