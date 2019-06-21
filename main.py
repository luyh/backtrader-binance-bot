#!/usr/bin/env python3

import time
import backtrader as bt
import datetime as dt

from ccxtbt import CCXTStore
from config import BINANCE, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG

from dataset.dataset import CustomDataset,OneTokenDataset
from sizer.percent import FullMoney
from strategies.random import BasicRandom
from utils import print_trade_analysis, print_sqn, send_telegram_message
import os

def main():
    cerebro = bt.Cerebro(quicknotify=True)

    if ENV == PRODUCTION:  # Live trading with Binance
        broker_config = {
            'apiKey': os.environ.get('okex_key'),
            'secret': os.environ.get('okex__secret'),
            'nonce': lambda: str( int( time.time() * 1000 ) ),
            'enableRateLimit': True,
        }

        store = CCXTStore( exchange='okex', currency='USDT', config=broker_config, retries=5, debug=DEBUG )

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'status',
                    'value': 'canceled'
                }
            }
        }

        okex = store.getbroker(broker_mapping=broker_mapping)
        print( okex.getcash(),okex.getvalue() )

        #cerebro.setbroker(okex)

        broker = cerebro.getbroker()
        broker.setcommission( commission=0.001, name=COIN_TARGET )
        broker.setcash( 100000.0 )
        cerebro.addsizer( FullMoney )

        initial_value = cerebro.broker.getvalue()
        print( 'Starting Portfolio Value: %.2f' % initial_value )



        hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=30000)
        data = store.getdata(
            dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
            name='%s%s' % (COIN_TARGET, COIN_REFER),
            timeframe=bt.TimeFrame.Minutes,
            #fromdate=hist_start_date,
            fromdate=dt.datetime( 2018, 1, 1 ),
            todate=dt.datetime( 2018, 12, 31 ),
            compression=15,
            ohlcv_limit=None
        )

        # Add the feed
        #cerebro.adddata(data)
        cerebro.resampledata( data, timeframe=bt.TimeFrame.Minutes, compression=30 )

    else:  # Backtesting with CSV file
        data = OneTokenDataset(
            name='btc',
            dataname="dataset/candles_okef_btc.usd.t_2018-11-11_2018-12-12_5m.csv",
            timeframe=bt.TimeFrame.Minutes,
            #fromdate=dt.datetime(2018, 11, 11,11,11),
            #todate=dt.datetime(2018, 11, 10,11,11),
            compression = 5,
            nullvalue=0.0,
            dtformat = 1,
        )

        cerebro.adddata(data)
        #cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5)

        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001, name=COIN_TARGET)
        broker.setcash(10000.0)
        cerebro.addsizer(FullMoney)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) x SquareRoot( number of trades )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Include Strategy
    cerebro.addstrategy(BasicRandom)

    # Print analyzers - results
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)

    #exit()
    result = cerebro.run()
    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)
    print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))

    #exit()
    print_trade_analysis(result[0].analyzers.ta.get_analysis())
    print_sqn(result[0].analyzers.sqn.get_analysis())

    if True:  #DEBUG:
        cerebro.plot()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        #send_telegram_message("Bot finished by user at %s" % time)
    except Exception as err:
        send_telegram_message("Bot finished with error: %s" % err)
        print("Finished with error: ", err)
        raise
