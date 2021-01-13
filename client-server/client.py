import json
import os,sys
import time, traceback
import urllib.parse
import requests
import random
import schedule
import logging
import redis
from logging.handlers import RotatingFileHandler
from tinydb import TinyDB, Query
import threading
import traceback, signal

class EdgeFunctions:
    def __init__(self):
        CONSTANT_DICTIONARY = {}
        CONSTANT_DICTIONARY['LAST_AVERAGE'] = 30
        CONSTANT_DICTIONARY['AVERAGE_DATA_COUNT'] = 7
        CONSTANT_DICTIONARY['SEND_URL'] = "http://127.0.0.1:5001/sendData?"
        CONSTANT_DICTIONARY['LOCAL_DB'] = TinyDB('offlineDB.json')
        self.CONSTANT_DICTIONARY = CONSTANT_DICTIONARY
        self.red = redis.Redis(host='localhost', port=6379, db=0)
        self.red.set("success_count",0)
        self.logger = logging_enable()

    def calculate_average(self,current_value):
        try:
            last_average = float(self.red.get('last_average').decode("utf-8"))
        except:
            last_average = self.CONSTANT_DICTIONARY.get('LAST_AVERAGE')
        n = self.CONSTANT_DICTIONARY.get('AVERAGE_DATA_COUNT')
        current_average = ((n-1)*last_average + current_value)/n
        return current_average

    def bufferData_save(self,data):
        self.CONSTANT_DICTIONARY['LOCAL_DB'].insert(data)
        self.logger.info("saving data %s to buffer"%data)
        return

    def stimulate_data(self):
        data = {}
        data["value"]=float(round(random.uniform(30.5, 39.5),2))
        return data
    
    def data_send(self, data):
        try:
            data_encoded = urllib.parse.urlencode(data)
            final_url = str(self.CONSTANT_DICTIONARY.get('SEND_URL')+ data_encoded)
            r=requests.get(final_url)
            result = str(r.text)
        except:
            result = 'faliure'
        return result
    
    def live_thread(self):
        print("running live thread")
        self.logger.info("running live thread")
        data = self.stimulate_data()
        new_average = self.calculate_average(data["value"])
        data['average'] = new_average
        self.red.set('last_average', new_average)
        self.CONSTANT_DICTIONARY['LAST_AVERAGE'] = new_average
        result = self.data_send(data)
        if result == 'success':
            self.red.set('success_count',int(self.red.get("success_count").decode("utf-8"))+1)
            self.logger.info("sent live data: %s to server"%data)
        else:
            self.logger.info("failed to send live data")
            self.bufferData_save(data)

    def buffer_thread(self):
        print("running buffer thread")
        self.logger.info("running buffer thread")
        db = self.CONSTANT_DICTIONARY['LOCAL_DB']
        if not (db.all() == []):
            ID = db.all()[0].doc_id
            data = db.get(doc_id=ID)
            result = self.data_send(data)
            if result == 'success':
                db.remove(doc_ids=[ID])
                self.red.set('success_count',int(self.red.get("success_count").decode("utf-8"))+1)
                self.logger.info("sent buffer data: %s to server"%data)
            else:
                self.logger.info("failed to send buffer data")
        else:
            self.logger.info("no buffer data found")

def every(delay=0,task=None, run_event=None):
    next_time = time.time() + delay
    while run_event.is_set():
        task()
        time.sleep(max(0, next_time - time.time()))
        next_time += (time.time() - next_time) // delay * delay + delay 

def logging_enable():
    logging.basicConfig(filename="client.log", format="%(asctime)s %(message)s", filemode="a+")
    logger=logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter("%(asctime)s %(message)s")
    handler = RotatingFileHandler("client.log", mode="a+", maxBytes=100*1024*1024, backupCount=1, encoding=None, delay=0)
    handler.setFormatter(log_formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

def main():
    run_event = threading.Event()
    run_event.set()
    d1=6
    t1 = threading.Thread(name='LiveThread60', target= every, kwargs = dict(delay=d1, task=EdgeFunctions().live_thread, run_event=run_event))
    d2=3
    t2 = threading.Thread(name='BufferData30', target= every, kwargs= dict(delay=d2, task=EdgeFunctions().buffer_thread, run_event=run_event))
    t1.start()
    time.sleep(0.5)
    t2.start()
    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        EdgeFunctions().red.flushdb()    #if only you want to reset last average and message count values.
        try:
            print ("attempting to close threads. Max wait =",max(d1,d2))
            run_event.clear()
            t1.join()
            t2.join()
            print ("threads successfully closed")
        except:
            sys.exit(0)

if __name__=='__main__':
    main()