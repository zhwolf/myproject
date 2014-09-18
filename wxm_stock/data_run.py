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


import logging
import utils
import web
import Queue
import threading
import simplejson
num_worker_threads=10

if __name__ == '__main__':
    db = web.database(dbn = "sqlite",
                  db = "./stock.dat")
    datas = db.select('stocks')
    q = Queue.Queue()

    db_q = Queue.Queue()

    def parse_worker():
        while not q.empty():
            stock = q.get()

            result = utils.doParse( stock.code)

            db_q.put( (result, stock))

            q.task_done()
        logging.info("Thread quit for queue is empty")

    def db_worker():
        while True:
            item, stock = db_q.get()

            utils.saveData(db, item, stock)

            db_q.task_done()

    for item in datas:
        data = utils.Any()
        for k,v in item.items():
            setattr(data, k, v)
        data.id = item.id
        q.put(data)

    for i in range(num_worker_threads):
         t = threading.Thread(target=parse_worker)
         t.daemon = True
         t.start()

    t = threading.Thread(target=db_worker)
    t.daemon = True
    t.start()

    q.join()       # block until all tasks are done
    db_q.join()