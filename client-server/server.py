import requests
import sys
import os
import warnings
from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import time
import random
import datetime
import json
import csv

app = Flask(__name__)
warnings.filterwarnings('ignore')

logging.basicConfig(filename="server.log", format="%(asctime)s %(message)s", filemode="a+")
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s %(message)s")
handler = RotatingFileHandler("server.log", mode="a+", maxBytes=100*1024*1024, backupCount=1, encoding=None, delay=0)
handler.setFormatter(log_formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def constructJson(timestampval):
    data = {}
    data["Timestamp"] = timestampval
    data["CurrentValue"]=str(request.args.get("value"))
    data["AverageValue"]=str(request.args.get("average"))
    return data

def csvSaver(jsondata):
    if os.path.exists('dataset.csv') == True:
        output_file = open('dataset.csv', 'r+')
        reader_file = csv.reader(output_file)
        count = len(list(reader_file))
        output_file.close()
        if count >= 1:
            logger.debug("Appending values %s to CSV"%jsondata)
            with open('dataset.csv',mode='a',newline='') as output_file:
                csv_writer = csv.writer(output_file, delimiter=',')
                csv_writer.writerow(jsondata.values())
                output_file.close()
        else:
            logger.debug("No headers found in CSV, So writing headers too.")
            with open('dataset.csv',mode='w',newline='') as output_file:
                csv_writer = csv.writer(output_file, delimiter=',')
                csv_writer.writerow(jsondata.keys())
                csv_writer.writerow(jsondata.values())
                output_file.close()
    else:
        logger.debug("Creating CSV Output file for first time.")
        with open('dataset.csv',mode='w',newline='') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',')
            csv_writer.writerow(jsondata.keys())
            csv_writer.writerow(jsondata.values())
            output_file.close()
                

@app.route("/sendData", methods=["GET"])
def upload():
    try:
        logger.debug("RECEIVED REQUEST")
        logger.debug(request.args.get)
        timestampval=time.strftime('%Y-%m-%dT%H:%M:%S+05:30')
        jsonToSend=constructJson(timestampval)
        csvSaver(jsonToSend)
        return 'success'
    except Exception as e:
        logger.debug("Exception occured in server as:{}".format(e))
        return 'faliure'

@app.errorhandler(404)
def not_found(error):
    utc_datetime = datetime.datetime.utcnow()
    utc_datetime = utc_datetime.strftime("%Y-%m-%d %H:%M:%SZ")
    error_404 = json.dumps({
        'timestamp': utc_datetime,
        'error': error.code,
        'error status': repr(error),
        'Message': 'Given URL may be invalid Please check and try again',
        'path': '/sendData'
    })
    logger.error(error_404)
    return 'faliure'

  
if __name__ == "__main__":
    app.run(port=5001, debug=True ,host ="0.0.0.0",threaded=True)