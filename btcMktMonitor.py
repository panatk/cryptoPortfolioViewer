
import pandas as pd
import numpy as np
from btcmarkets import BTCMarkets
import pprint
import datetime

import pyalgotrade


def main():

    btcmAPI = BTCMarkets()
    accountInfo = btcmAPI.get_accounts()

    portfolioPL = {

        'LTC': {'PL': getPL('LTC', 'AUD')},
        'BTC': {'PL': getPL('BTC', 'AUD')},
        'XRP': {'PL': getPL('XRP', 'AUD')},
        'ETH': {'PL': getPL('ETH', 'AUD')}

    }

    print(getPosition())
    pprint.pprint(portfolioPL)

    pprint.pprint(getTradingVolume('01/12/2017'))


def getPL(ticker, currency):  # include fees from liquidation

    btcmAPI = BTCMarkets()

    spot = getSpot(ticker, currency)

    tradeHist = pd.DataFrame(btcmAPI.get_trade_history(
        instrument=ticker, currency=currency))

    buyHist = tradeHist[tradeHist.side == 'Bid']

    feeRate = 0.008

    if ticker != 'ETH':
        wac = sum(buyHist['volume']*buyHist['price'])/sum(buyHist['volume'])
        buyVol = sum(buyHist['volume'])
        buyFees = sum(buyHist['fee']/100000000)

        sellFees = feeRate*spot*buyVol

        pl = (spot - wac)*buyVol - buyFees - sellFees

    else:

        wac = 525
        buyVol = 0.9
        buyFees = 0
        sellFees = feeRate*spot*buyVol
        pl = (spot - wac)*buyVol - buyFees - sellFees

    return pl


def getPosition():

    btcmAPI = BTCMarkets()
    accountBalances = pd.DataFrame(btcmAPI.get_accounts())

    accountBalances = accountBalances[(accountBalances.currency != 'AUD') & (
        accountBalances.currency != 'USD')]
    accountBalances['spot'] = accountBalances.apply(
        lambda row: getSpot(row.currency, 'AUD'), axis=1)

    accountBalances['AUDvalue'] = accountBalances['balance'] * \
        accountBalances['spot']

    return accountBalances


def getSpot(ticker, currency):

    btcmAPI = BTCMarkets()
    spot = pd.DataFrame(btcmAPI.get_market_trades(
        instrument=ticker, currency=currency))['price'][0] * 100000000

    return spot


def getTradingVolume(sinceDate):

    btcmAPI = BTCMarkets()

    accountBalances = pd.DataFrame(btcmAPI.get_accounts())
    accountBalances = accountBalances[(accountBalances.currency != 'AUD') & (
        accountBalances.currency != 'USD')]
    accountBalances.rename(columns={'currency': 'ticker'}, inplace=True)
    completeTradeHist = pd.DataFrame()

    for ticker in accountBalances['ticker']:

        tradeHist = pd.DataFrame(btcmAPI.get_trade_history(
            instrument=ticker, currency='AUD', since=datetime(sinceDate)))
        completeTradeHist.append(tradeHist)

    return completeTradeHist


if __name__ == "__main__":
    main()

