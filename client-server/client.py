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
import traceback

lock = threading.Lock()
red = redis.Redis(host='localhost', port=6379, db=0)
red.flushdb()
db = TinyDB('offlineDB.json')
red.set("success_count",0)
red.set("buffer_count",0)
localurl = "http://127.0.0.1:5001/sendData?"

logging.basicConfig(filename="client.log", format="%(asctime)s %(message)s", filemode="a+")
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s %(message)s")
handler = RotatingFileHandler("client.log", mode="a+", maxBytes=100*1024*1024, backupCount=1, encoding=None, delay=0)
handler.setFormatter(log_formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def constructJson():
    data = {}
    data["value"]=str(round(random.uniform(30.5, 39.5),2))
    data["sensor"]="Sensor-"+str(random.randint(1,5))
    return data

def logdata_save(data):
    #global db, red
    db.insert(data)
    red.set('buffer_count',int(red.get("success_count").decode("utf-8"))+1)
    logger.info("saved buffered data:{0}".format(data))
    print("saved buffered data:{0}".format(data))

def logdata_read():
    #global db, localurl, red
    if not (db.all() == []):
        el = db.all()[0]
        ID = el.doc_id
    else:
        return False
    for i in range(0,len(db)):
        element = db.get(doc_id=ID+i)
        encoded = urllib.parse.urlencode(element)
        final=str(localurl+encoded)
        try:
            r=requests.get(final)
            result = [r.text, r.status_code]
            if result[0] == "success":
                red.set('success_count',int(red.get("success_count").decode("utf-8"))+1)
                db.remove(doc_ids=[ID+i])
                red.set('buffer_count',int(red.get("success_count").decode("utf-8"))-1)
                logger.info("sent buffered data:{0}".format(element))
                print("sent buffered data:{0}".format(element))
                time.sleep(5) #SEND BUFFERED DATA EVERY 5 SECONDS.
        except:
            break

def  message_count():
    #global red
    messageCount = {}
    messageCount['Transmitted Messages'] = int(red.get("success_count").decode("utf-8"))
    messageCount['Buffered Messages'] = int(red.get("buffer_count").decode("utf-8"))
    return messageCount

def edge_program():
    #global red, localurl
    params = constructJson()
    encoded = urllib.parse.urlencode(params)
    final=str(localurl+encoded)
    try:
        r=requests.get(final)
        result = [r.text, r.status_code]
        if result[0] == "success":
            red.set('success_count',int(red.get("success_count").decode("utf-8"))+1)
            logger.info("sent live data:{0}".format(params))
            print("sent live data:{0}".format(params))
        else:
            logdata_save(params)
    except:
        logdata_save(params)

def every(task, delay):
    next_time = time.time() + delay
    while True:
        try:
            task()
        except Exception:
            traceback.print_exc()
        time.sleep(max(0, next_time - time.time()))
        next_time += (time.time() - next_time) // delay * delay + delay

def conn_check():
    try:
        if requests.get("http://localhost:5001/healthcheck").status_code == 200:
            print(threading.enumerate())
            logdata_read()
    except:
        pass

def main():
    try:
        main_thread = threading.Thread(target=lambda:every(edge_program,10))
        buffer_thread = threading.Thread(target=lambda:every(conn_check,10))
        main_thread.start()
        buffer_thread.start()
    except KeyboardInterrupt:
        exit(0)
#    main_thread.join()
#    buffer_thread.join()

if __name__=="__main__":
    main()
