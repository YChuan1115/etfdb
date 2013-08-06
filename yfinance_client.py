#!/usr/bin/env python

from decimal import Decimal
import urllib
import json

ROOT_URL = 'http://query.yahooapis.com/v1/public/yql'

class StockQuote(object):
    def __init__(
        self, original_ticker, ticker, name, last, change,
        day_low, day_high, year_low, year_high,
        volume, average_daily_volume, market_cap
    ):
        self.original_ticker = original_ticker
        self.ticker = ticker
        self.name = name
        self.last = last
        self.change = change
        self.day_low = day_low
        self.day_high = day_high
        self.year_low = year_low
        self.year_high = year_high
        self.volume = volume
        self.average_daily_volume = average_daily_volume
        self.market_cap = market_cap
    
    @property
    def percent_change(self):
        return self.change / (self.last - self.change) * 100
    
    def __repr__(self):
        return "<StockQuote('%s'): %f" % (self.ticker, self.last)

def get_chunks(l, n):
    while True:
        if len(l) < n:
            yield l
            break
        yield l[0:n]
        l = l[n:]

def make_yahoo_ticker(t):
    return t.replace('.', '-')

def get_quotes_iter(tickers):
    ticker_map = dict([(make_yahoo_ticker(x), x) for x in tickers])
    for chunk in get_chunks(ticker_map.keys(), 100):
        url = ROOT_URL + '?' + urllib.urlencode({
            'format': 'json',
            'env': 'store://datatables.org/alltableswithkeys',
            'q': 'select * from yahoo.finance.quote where symbol in (%s)' % (
                ','.join(['"%s"' % x for x in chunk])
            )
        })
        #print(url)
        res = json.load(urllib.urlopen(url))
        for s in res['query']['results']['quote']:
            if s['StockExchange'] is None:
                continue
            yield StockQuote(
                ticker_map[s['symbol']],
                s['symbol'],
                s['Name'],
                Decimal(s['LastTradePriceOnly']),
                Decimal(s['Change']),
                Decimal(s['DaysLow']),
                Decimal(s['DaysHigh']),
                Decimal(s['YearLow']),
                Decimal(s['YearHigh']),
                long(s['Volume']),
                long(s['AverageDailyVolume']),
                s['MarketCapitalization'],
            )

def get_quotes(tickers):
    out = {}
    for x in get_quotes_iter(tickers):
        out[x.original_ticker] = x
    return out

if __name__ == '__main__':
    print(get_quotes(['AAPL', 'VNQ', 'SPY']))
