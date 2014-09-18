#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      Administrator
#
# Created:     16-09-2014
# Copyright:   (c) Administrator 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re,urllib2
import logging
from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import simplejson
from simplejson import JSONEncoder

HTTP_TIMEOUT=10

class Any:
    pass

class MyJSONEncoder(simplejson.JSONEncoder):
    def default(self, o):
        from types import InstanceType
        import datetime
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, InstanceType):
            return getattr(o,'__dict__', None)
        else:
            return super(MyJSONEncoder, self).default(o)

CHAIWU_MODELS=[
        #市值  -- 市值，已发行股本，流通股
        [
            'shizhi',
            'faxingguben',
            'liutonggu',
        ],
        #每股财务数据 --收益，销售，帐面价值，现金流，现金
        [
            'shouyi',
            'xiaoshou',
            'zhangmian',
            'xianjinliu',
            'xianjin',
        ],
        #估值指标 --市盈率,总市值/销售收入,市帐率 （市价/帐面资产净值）,股价/每股现金
        [
            'shiyinglv',
            'zhongshizhi',
            'shizhanglv',
            'gujia',
        ],
        #管理效率 --权益收益率,资产报酬率,投资回报率
        [
            'qyshouyilv',
            'baochoulv',
            'huibaolv',
        ],
        #盈利能力比率 --毛利,营运利润率,净利率
        [
            'maoli',
            'lirunlv',
            'jinglilv',
        ],
        #分红送配 --股息收益率,每股股利,股息支付率
        [
            'gxshouyilv',
            'guli',
            'zhifulv',
        ],
        #财务实力 --速动比率,流动比率,长期债务率,债务股本比
        [
            'sdbilv',
            'ldbilv',
            'zhaiwulv',
            'zwgubenbi',
        ],
    ]

Table_Stocks=[
    "code",
    "name",
    "zone",
    "industry",
    "subindustry",
    "reporttime",
]

Table_Report=[
    "code",
    "currency",
    "name",
    "price",
    "change",
    "shizhi",
    "faxingguben",
    "liutonggu",
    "shouyi",
    "xiaoshou",
    "zhangmian",
    "xianjinliu",
    "xianjin",
    "shiyinglv",
    "zhongshizhi",
    "shizhanglv",
    "gujia",
    "qyshouyilv",
    "baochoulv",
    "huibaolv",
    "maoli",
    "lirunlv",
    "jinglilv",
    "gxshouyilv",
    "guli",
    "zhifulv",
    "sdbilv",
    "ldbilv",
    "zhaiwulv",
    "zwgubenbi",
    "TotalRevenue",
    "GrossProfit",
    "OperatingIncome",
    "NetIncome",
    "reporttime",
]


MyGlobals = {
    ###在这里加入地区
    'zones': ['ALL','香港', u'b股', u'沪市', u'深市'],
    ###在这里加入行业
    'industrys': ['ALL', u'制造业'],
    ###在这里加入子行业
    'subindustrys': ['ALL', u'加工'],
}

class Any:
    pass

def to_int(s):
    return s.replace(',','').strip()

def parseChaiwu(data, code):
    try:
        doc=urllib2.urlopen( "http://cn.reuters.com/investing/quotes/companyRatios?symbol=%s" %(code) , timeout=HTTP_TIMEOUT).read()
    except Exception as err:
        return
    soup = BeautifulSoup(doc,fromEncoding="GB2312")

    try:
        data.price = soup.find('div', {'id': "priceQuote"}).find('span', {'class':"valueContent"}).text
    except:
        data.price = None
    #print 'price', '=', data.price
    try:
        data.change      = soup.find('div', {'id': "percentChange"}).find('span').find('span').text
    except:
        data.change      = None
    #print 'percentChange', '=', data.change

    try:
        data.name      = soup.find('h5', {'class': "quoteHeader"}).text[:6]
    except:
        data.name      = None
    #print 'name', '=', data.name

    try:
        data.currency      = soup.find('span', {'class': "currencyCode"}).text
    except:
        data.currency      = None
    #print 'currency', '=', data.currency


    tables = soup.findAll('table',{'class':'dataTable'})
    i = 0
    for table in tables:
        #市值  -- 市值，已发行股本，流通股
        #每股财务数据 --收益，销售，帐面价值，现金流，现金
        #估值指标 --市盈率,总市值/销售收入,市帐率 （市价/帐面资产净值）,股价/每股现金
        #管理效率 --权益收益率,资产报酬率,投资回报率
        #盈利能力比率 --毛利,营运利润率,净利率
        #分红送配 --股息收益率,每股股利,股息支付率
        #财务实力 --速动比率,流动比率,长期债务率,债务股本比
        if i < len(CHAIWU_MODELS):
            adata = table.findAll('td',{'class':'data'})
            model =CHAIWU_MODELS[i]
            for j in range(len(model)):
                key =model[j]
                value = adata[j].text.replace(',','').strip()
                setattr(data, key , value )
                #print key, '=', value
        i +=1

def parseShouru(data, code):
    try:
        doc=urllib2.urlopen( "http://www.reuters.com/finance/stocks/incomeStatement?perType=ANN&symbol=%s" %(code) , timeout=HTTP_TIMEOUT).read()
    except Exception as err:
        logging.error("error:%s", err);
        return
    soup = BeautifulSoup(doc,fromEncoding="gb2312")

    datas = soup.findAll('td',{'class':'data plus'})
    for td in datas:
        tdtile = td.findPrevious('td').text
        if  tdtile== "Total Revenue":
            data.TotalRevenue = td.text.replace(',','').strip()
        elif tdtile== "Gross Profit":
            data.GrossProfit = td.text.replace(',','').strip()
        elif tdtile== "Operating Income":
            data.OperatingIncome = td.text.replace(',','').strip()
        elif tdtile== "Net Income":
            data.NetIncome = td.text.replace(',','').strip()
            break
    #print "data.TotalRevenue", "=",data.TotalRevenue
    #print "data.GrossProfit", "=",data.GrossProfit
    #print "data.OperatingIncome", "=",data.OperatingIncome
    #print "data.NetIncome", "=",data.NetIncome

def saveData(db, data, stock = None):
    myvars ={}
    for field in Table_Report:
        if hasattr(data, field):
            myvars[field] = getattr(data, field)

    count = int(db.query("SELECT count(id) as _total FROM report WHERE code= $code", vars={'code': data.code})[0]._total)
    if count <= 0:
        db.insert('report', **myvars)
    else:
        db.update('report', "code = $code", {'code': data.code}, **myvars)

    if stock != None and not stock.name and data.name:
        db.update("stocks", "code = $code", {'code':data.code},  name=data.name)

def doParse(code):
    data = Any()
    data.code = code
    parseChaiwu(data, code)
    parseShouru(data, code)
    return data
