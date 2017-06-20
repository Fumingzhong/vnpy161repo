#encoding:utf-8

from datetime import datetime, timedelta
from ctaTemplate import *
import sys
sys.path.append(r'd:\pythonworkspace\pythoncode')
from ContinuousGeometricOption import *

##############################################
class GammaTradingStrategy(CtaTemplate):    
    """通过BS模型进行delta调仓，实现gamma收益"""
    className = "GammaTradingStrategy"
    author = u'牙刷哥'
    
    #期货合约
    futureList=[]
    
    #期权合约
    optionList=[]
    
    #策略参数
    execisePrice = EMPTY_FLOAT #执行价 X
    riskfreeRate = 0.035 #无风险利率 r
    expiraryDate = EMPTY_STRING #合约到期日期 t
    historicalVol = EMPTY_FLOAT #标的期货合约历史波动率 v
    
    initDays = 1 #用来初始化策略，如delta等
    
    #策略变量
    bar = None #K线对象
    barMinute = EMPTY_STRING #K线的时间（第几分钟）
    currentPrice = 0 #现价 S
    optionPrice = 0 #期权现价 C 或 P
    impliedVol = 0
    gamma = 0
    delta = 0
    vega = 0
    
    #参数列表，保存参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'execisePrice',
                 'riskfreeRate',
                 'expiraryDate',
                 'historicalVol']
    
    #变量列表，保存变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'currentPrice',
               'optionPrice',
               'impliedVol',
               'gamma',
               'delta',
               'vega']
    
    
    
    def __init__(self, ctaEngine, setting):
        super(GammaTradingStrategy, self).__init__(ctaEngine, setting)
        
        
        
    def onInit(self):
        """初始化策略（必须由用户继承实现），因为CtaTemplate中onInit为空函数"""
        self.writeCtaLog(u'%s策略初始化' % self.name)
        
        #载入历史数据，并采用回放计算的方式初始化策略数值，用来获取旧的delta等值
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)
            
        self.putEvent()
         
         
         
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略启动' %self.name)
        self.putEvent()
        
        
    def onStop(self):
        """停止策略（必须由用户集成实现）"""
        self.writeCtaLog(u'%s策略停止' %self.name)
        self.putEvent()
        
        
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        #计算K线
        tickMinute = tick.datetime.minute
        
        if tickMinute != self.barMinute:
            if self.bar:
                self.onBar(self.bar)#说明之前那根bar已经完结及时推送到策略计算中去
                
            bar = CtaBarData()
            bar.vtSymbol = tick.vtSymbol
            bar.symbol = tick.symbol 
            bar.exchange = tick.exchange
            
            bar.open = tick.lastPrice
            bar.high = tick.lastPrice
            bar.low = tick.lastPrice
            bar.close = tick.lastPrice
            
            bar.date = tick.date
            bar.time = tick.time
            bar.datetime = tick.datetime #K线的时间设为第一个Tick的时间
            
            self.bar = bar 
            self.barMinute = tickMinute
            
        else:
            bar = self.bar
            
            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)
            bar.close = tick.lastPrice
            
            
    def onBar(self, bar):
        """收到Bar推送，然后进行策略计算（必须由用户集成实现），
        接收期权的bar行情，以bar的开盘价做计算"""
        if not self.currentPrice:
            self.optionPrice = bar.close
            startDate = datetime.today()
            #当expiraryDate是datetime格式时，运行try,否则将expiraryDate先转化成datetime格式
            #例如：expiraryDate为datetime(2017,06,05)或者[5,6,2017]
            try:
                daysTimedelta = self.expiraryDate-startDate()
                daysLeft = daysTimedelta.days
            except:
                expiraryDateDatetime = datetime(self.expiraryDate[2],self.expiraryDate[1],self.expiraryDate[0])
                daysTimedelta = expiraryDateDatetime-startDate()
                daysLeft = daysTimedelta.days                
            args = [self.optionPrice, self.execisePrice, self.riskfreeRate,
                    startDate, daysLeft, self.historicalVol,0]
        
        