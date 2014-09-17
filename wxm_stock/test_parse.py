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

import re,urllib2
from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import logging

class Any:
    pass


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

def parseChaiwu(data, code):
    try:
        doc=urllib2.urlopen( "http://cn.reuters.com/investing/quotes/companyRatios?symbol=%s" %(code) , timeout=4).read()
    except Exception as err:
        logging.root().ERROR("error:%s", err);
        f = open("test.txt")
        doc = f.read()
        f.close()
    soup = BeautifulSoup(doc,fromEncoding="GB2312")

    try:
        data.price = soup.find('div', {'id': "priceQuote"}).find('span', {'class':"valueContent"}).text
    except:
        data.price = None
    print 'price', '=', data.price
    try:
        data.change      = soup.find('div', {'id': "percentChange"}).find('span').find('span').text
    except:
        data.change      = None
    print 'percentChange', '=', data.change

    try:
        data.name      = soup.find('h5', {'class': "quoteHeader"}).text
    except:
        data.name      = None
    print 'name', '=', data.name

    try:
        data.currency      = soup.find('span', {'class': "currencyCode"}).text
    except:
        data.currency      = None
    print 'currency', '=', data.currency


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
            data = table.findAll('td',{'class':'data'})
            model =CHAIWU_MODELS[i]
            for j in range(len(model)):
                key =model[j]
                value = data[j].text
                setattr(data, key , value )
                print key, '=', value
        i +=1

def parseShouru(data, code):
    try:
        doc=urllib2.urlopen( "http://www.reuters.com/finance/stocks/incomeStatement?perType=ANN&symbol=%s" %(code) , timeout=5).read()
    except Exception as err:
        logging.ERROR("error:%s", err);
        f = open("test1.txt")
        doc = f.read()
        f.close()
    soup = BeautifulSoup(doc,fromEncoding="gb2312")

    datas = soup.findAll('td',{'class':'data plus'})
    data.TotalRevenue = datas[2].text
    data.GrossProfit = datas[4].text
    data.OperatingIncome = datas[12].text
    data.NetIncome = datas[28].text
    print "data.TotalRevenue", "=",data.TotalRevenue
    print "data.GrossProfit", "=",data.GrossProfit
    print "data.OperatingIncome", "=",data.OperatingIncome
    print "data.NetIncome", "=",data.NetIncome


if __name__ == '__main__':
    data = Any()
    data.code ='0001.HK'
    parseChaiwu(data, data.code)
    parseShouru(data, data.code)
