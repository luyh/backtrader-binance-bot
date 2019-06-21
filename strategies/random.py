#!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from indicators.macd_hist import MACDHistSMA
from indicators.stoch_rsi import StochRSI
from strategies.base import StrategyBase
import random

class Profit(bt.Indicator):
    def __init__(self):
        self.profit = 0

class ATRD(bt.Indicator):
    lines = ('atrd',)

    params = (('direction', 'up'),
              ('yinzi',3)
              )

    plotinfo = dict(

        subplot=False, )

    def __init__(self):
        if self.params.direction == 'up':
            self.lines.atrd = self.data0.close + self.params.yinzi * bt.indicators.AverageTrueRange(self.data0,period = 10)
        else:
            self.lines.atrd = self.data0.close - self.params.yinzi * bt.indicators.AverageTrueRange( self.data0, period=10 )



class BasicRandom(StrategyBase):
    def __init__(self):
        StrategyBase.__init__(self)
        self.log("Using 随机入市 strategy")

        #self.sma_fast = bt.indicators.MovingAverageSimple(self.data0.close, period=20)
        #self.sma_slow = bt.indicators.MovingAverageSimple(self.data0.close, period=200)
        #self.rsi = bt.indicators.RelativeStrengthIndex()

        self.atr = bt.indicators.AverageTrueRange(self.data0,period = 10)

        self.atrh1 = ATRD(direction = 'up',yinzi = 1)
        self.atrl1 = ATRD(direction = 'down',yinzi = 1)
        self.atrh3 = ATRD(direction = 'up',yinzi = 3)
        self.atrl3 = ATRD(direction = 'down',yinzi = 3)


        self.profit = 0
        self.maxprice = 0

        self.is_order_sell = False

        self.count = 0

        self.enable_zuokong = True

        self.atr_yinzi = 3

        self.stop_loss = 0.01
        self.stop_gian = self.stop_loss *3

    def next(self):
        #print('next',round(self.rsi[0],2),round(self.data0.close[0],2))

        #print('positiion',self.position)
        #self.log('position.size:{}'.format(self.position.size))
       # print('atr_h:{},atr_l:{}'.format(self.atrh1[0],self.atrl1[0]))
        if not self.position.size:

            if self.enable_zuokong:
                # 无仓位，随机开仓
                if random.random() > 0.5:
                    self.log( '下多单:{}'.format(self.data0.close[0] ) )
                    self.buy( size=0.1 )
                else:
                    self.log( '下空单:{}'.format(self.data0.close[0]))
                    self.sell( size=0.1 )
            else:
                self.log( '只做多单', self.data0.close[0] )
                self.long( size=0.1 )

            self.maxprice = self.data0.close[0]
            self.trade_price = self.data0.close[0]
            self.log('maxprice:{}'.format(self.maxprice))

            # 重置时钟
            self.count = 0

        else:
            #print(self.stop_loss[0])
            if self.is_order_sell:
                self.maxprice = min( self.maxprice, self.data0.close[0] )
                self.stop_loss = self.maxprice + self.atr[0] * self.atr_yinzi

                if self.data0.close[0]>self.stop_loss:
                    self.log('count:{},空单止损：波动：{},现价：{}'.format( self.count, self.atr[0],
                                                                       self.data0.close[0] ) )
                    self.close()
            else:
                self.maxprice = max( self.maxprice, self.data0.close[0] )
                self.stop_loss = self.maxprice - self.atr[0] * self.atr_yinzi
                if self.data0.close[0]<self.stop_loss:
                    print( self.count,'多单止损：波动：{},现价：{}'.format(  self.atr[0],self.data0.close[0] ) )
                    self.close()

            # self.profit = (self.data0.close[0] - self.trade_price) / self.trade_price
            # if self.is_order_sell:
            #     self.profit = - self.profit
            #
            #
            # #止盈
            # if self.profit < - self.stop_loss:
            #     print('时钟',self.count,'止损',self.data0.close[0],self.profit)
            #     self.close()
            # #止损
            # elif self.profit >self.stop_gian:
            #     print('时钟',self.count,'止盈',self.data0.close[0],self.profit)
            #     self.close()


            # if self.is_order_sell:
            #
            #
            #     self.maxprice = min( self.maxprice, self.data0.close[0] )
            #     self.stop_loss = self.maxprice + self.atr[0] * self.atr_yinzi
            #     if self.data0.close[0] > self.stop_loss:
            #         self.log('count:{},空单止损：最低价：{}，波动：{}，止损价：{},现价：{}'.format( self.count,self.maxprice, self.atr[0], self.stop_loss,
            #                                                            self.data0.close[0] ) )
            #         self.close()
            # else:
            #     self.maxprice = max( self.maxprice, self.data0.close[0] )
            #     self.stop_loss = self.maxprice - self.atr[0] *  self.atr_yinzi
            #     if self.data0.close[0] < self.stop_loss:
            #         print( self.count,
            #                   '多单止损：最高价：{}，波动：{}，止损价：{},现价：{}'.format( self.maxprice, self.atr[0], self.stop_loss,
            #                                                            self.data0.close[0] ) )
            #         self.close()

            self.count = self.count + 1


        if self.status != "LIVE" and ENV == PRODUCTION:
            self.log("%s - $%.2f" % (self.status, self.data0.close[0]))
            return

        if self.order:
            return



