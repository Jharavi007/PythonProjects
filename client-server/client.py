import json
import os
import time
import urllib.parse
import requests
import random
import schedule
import logging
from logging.handlers import RotatingFileHandler
from tinydb import TinyDB, Query

db = TinyDB('offlineDB.json')
success_count = 0
buffer_count = 0
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
    global db, buffer_count
    db.insert(data)
    buffer_count += 1
    logger.info("saved buffered data:{0} and the transmitted message count is:{1} and the buffered message count is:{2}".format(data,success_count,buffer_count))
    print("saved buffered data:{0} and the transmitted message count is:{1} and the buffered message count is:{2}".format(data,success_count,buffer_count))
    

def logdata_read():
    global db, localurl, success_count, buffer_count
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
                success_count +=1
                db.remove(doc_ids=[ID+i])
                buffer_count -=1
                logger.info("sent buffered data:{0} and the transmitted message count is:{1} and the buffered message count is:{2}".format(element,success_count,buffer_count))
                print("sent buffered data:{0} and the transmitted message count is:{1} and the buffered message count is:{2}".format(element,success_count,buffer_count))
                time.sleep(5) #SEND BUFFERED DATA EVERY 5 SECONDS.
        except:
            break

def edge_program():
    global success_count, localurl, buffer_count
    params = constructJson()
    encoded = urllib.parse.urlencode(params)
    final=str(localurl+encoded)
    try:
        r=requests.get(final)
        result = [r.text, r.status_code]
        if result[0] == "success":
            flag = 0
            success_count += 1
            logger.info("sent live data:{0} and the transmitted message count is:{1} and the buffered message count is:{2}".format(params,success_count, buffer_count))
            print("sent live data:{0} and the transmitted message count is:{1} and the buffered message count is:{2}".format(params,success_count,buffer_count))
        else:
            flag = 1
    except:
        flag = 1

    if (flag == 0):
        if os.path.exists('offlineDB.json') == True:
            logdata_read()
    if (flag == 1):
        logdata_save(params)

schedule.every(60).seconds.do(edge_program) #WILL RUN EVERY ONE MINUTE IRRESPECTIVE OF ANYTHING.

while 1:
    schedule.run_pending()
    time.sleep(1)