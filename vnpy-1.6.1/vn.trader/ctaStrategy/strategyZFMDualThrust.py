# encoding: UTF-8
from ctaTemplate import CtaTemplate
from ctaBase import *

########################################################################
class ZFMDualThrustStrategy(CtaTemplate):
    """所有策略命名以ZFM起头"""
    className = 'ZFMDualThrustStrategy'
    author = 'zfm'
    
    #交易引擎参数
    orderList = []
    barList = []
    
    #策略参数
    K1 = EMPTY_FLOAT
    K2 = EMPTY_FLOAT
    
    #出入场参数
    ioRange = EMPTY_FLOAT
    ioOpen = EMPTY_FLOAT
    
    #下单参数
    fixedSize = 1
    
    #初始化参数
    days = 1
    
    #需要首先输入参数汇总
    paramList = ['K1',
                 'K2',
                 'fixedSize',
                 'days']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        ##按策略内部设置变量
        #d = self.__dict__
        #for key in self.paramList:
            #d[key] = self.paramList[key]   
        
        #如有setting参数，则按setting设置
        super(ZFMDualThrustStrategy, self).__init__(ctaEngine, setting)

        
    def onInit(self):
        #策略初始化
        self.writeCtaLog(u'%s策略初始化成功' %self.name)
        initData = self.loadBar(self.days)
        #barList初始为空，在达到长度2之前，只会append barList
        for bar in initData:
            self.onBar(bar)
            
        #更新策略状态事件
        self.putEvent()
            
        
    #个人感觉意义不大    
    def onStart(self):
        self.writeCtaLog(u'%s策略启动成功' %self.name)
        self.putEvent()
        
        
    def onBar(self, bar):
        #先取消策略已发的未成交的订单（若没有会有什么影响待测）
        for orderId in self.orderList:
            self.cancelOrder(orderId)
            
        self.orderList = []
        self.barList.append(bar)
        if len(self.barList) <= 2:
            return
        else:
            self.barList.pop(0)
        #用于计算dualThrust上下轨的range
        lastBar = self.barList[-2]    
        lastOpen = lastBar.open
        lastHigh = lastBar.high
        lastLow = lastBar.low
        lastClose = lastBar.close
        
        #用于计算上下轨的值
        open = bar.open
        high = bar.high
        low = bar.low
        close = bar.close
        
        ioRange = max(lastHigh - lastClose, lastClose - lastLow)
        ioOpen = open 
        
        upLimit = ioOpen + self.K1 * ioRange
        lowLimit = ioOpen - self.K2 * ioRange
        
        #未处理有旧仓需要平仓问题
        if self.pos == 0:
            if close >= upLimit:
                vtOrderId = self.short(upLimit, self.fixedSize)
                self.orderList.append(vtOrderId)
            
            if close <= lowLimit:
                vtOrderId = self.buy(lowLimit, self.fixedSize)
                self.orderList.append(vtOrderId)
                
        elif self.pos >0:
            if close >= upLimit:
                vtOrderId = self.sell(upLimit, self.fixedSize)
                self.orderList.append(vtOrderId)
                
            if close <= lowLimit:
                vtOrderId = self.buy(lowLimit, self.fixedSize)
                self.orderList.append(vtOrderId)
                
        else:
            if close >= upLimit:
                vtOrderId = self.short(upLimit, self.fixedSize)
                self.orderList.append(vtOrderId)
                
            if close <= lowLimit:
                vtOrderId = self.cover(lowLimit, self.fixedSize)
                self.orderList.append(vtOrderId)            
            
                
        #发出状态更新事件（具体如何更新有待测试）    
        self.putEvent()
        

        
    def onTrade(self, trade):
        pass
    
    def onOrder(self, order):
        pass
        
if __name__ == '__main__':
    
    from ctaBacktesting import BacktestingEngine
    from PyQt4 import QtCore, QtGui
    
    BE = BacktestingEngine()
    BE.initStrategy(ZFMDualThrustStrategy)
    BE.setBacktestingMode(BE.BAR_MODE)
    BE.setSlippage(0.2)
    BE.setSize(300)
    BE.setRate(0.1/1000)
    BE.setPriceTick(0.2)
    BE.setStartDate(startDate='20161216', initDays=1)
    BE.setDatabase(MINUTE_DB_NAME, 'IF0000')
    BE.runBacktesting()
    BE.showBacktestingResult()
            
        
        
        
        
        
        
        
        
    
    