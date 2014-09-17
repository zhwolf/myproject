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

