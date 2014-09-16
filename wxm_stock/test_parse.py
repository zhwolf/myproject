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

class Any:
    pass

def main():
    try:
        doc=urllib2.urlopen("http://cn.reuters.com/investing/quotes/companyRatios?symbol=0001.HK", timeout=1)
    except:
        f = open("test.txt")
        doc = f.read()
        f.close()
    soup = BeautifulSoup(doc,fromEncoding="GB2312")

    MODELS=[
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

    data = Any()
    data.price = soup.find('div', {'id': "priceQuote"}).find('span', {'class':"valueContent"}).text
    print 'price', '=', data.price
    data.percentChange = soup.find('div', {'id': "percentChange"}).find('span').find('span').text
    print 'percentChange', '=', data.percentChange


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
        if i < len(MODELS):
            data = table.findAll('td',{'class':'data'})
            model =MODELS[i]
            for j in range(len(model)):
                key =model[j]
                value = data[j].text
                setattr(data, key , value )
                print key, '=', value
        i +=1


if __name__ == '__main__':
    main()
