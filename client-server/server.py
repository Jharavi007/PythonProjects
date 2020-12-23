import requests
import sys
import os
import warnings
from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import time
#import paho.mqtt.client as mqtt
import time as ts
import random
import datetime
import json
import csv
from healthcheck import HealthCheck

app = Flask(__name__)
warnings.filterwarnings('ignore')
health = HealthCheck()


logging.basicConfig(filename="server.log", format="%(asctime)s %(message)s", filemode="a+")
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s %(message)s")
handler = RotatingFileHandler("server.log", mode="a+", maxBytes=100*1024*1024, backupCount=1, encoding=None, delay=0)
handler.setFormatter(log_formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

#COMMENTED CODEBLOCK BELOW CAN BE UNCOMMENTED,
#TO SEND DATA FROM THIS MIDDLEWARE SOFTWARE TO CLOUD FINALLY.
'''
def on_connect(mqttc, userdata, flags, rc):
    print('connected to MQTT server')
    logger.debug("connected to MQTT server")

def on_disconnect(mqttc, userdata, rc):
    print('Disconnected From MQTT server')
    logger.debug("Disconnected to MQTT server")

def on_publish(mqttc,userdata,result):
    print("data published and result is", result)
    logger.debug("data published")

def sendData(jsonVal,deviceID,deviceKey,endpoint,channel):
    try:
        mqttc=mqtt.Client('test001')
        mqttc.on_connect = on_connect
        mqttc.on_disconnect  = on_disconnect
        mqttc.on_publish = on_publish
        mqttc.username_pw_set(username=deviceID,password=deviceKey)
        mqttc.connect(endpoint,1883,60)
        mqttc.loop_start()
        ts.sleep(5)
        messageval= json.dumps(jsonVal)
        (result,mid)= mqttc.publish(channel,messageval,2)
        print(result,mid)
        print("Sent Data: %s"%messageval)
        logger.debug("Sent Data: %s"%messageval)
        mqttc.loop_stop()
        mqttc.disconnect()

    except KeyboardInterrupt:
            pass
    except Exception as e:
            print('Exception occured while sending data')
            logger.error(e,exc_info=True)
'''

def constructJson(timestampval):
    data = {}
    data["Timestamp"] = timestampval
    data["Value"]=str(request.args.get("value"))
    data["Sensor"]=str(request.args.get("sensor"))
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
        timestampval=ts.strftime('%Y-%m-%dT%H:%M:%S+05:30')
        jsonToSend=constructJson(timestampval)
        csvSaver(jsonToSend)
        #SEND DATA TO CLOUD, FUNCTION CALL. INACTIVE FOR NOW.
        '''sendData(jsonToSend,"user","pass","broker.mqttdashboard.com","testing123") '''
        return 'success'
    except Exception as e:
        logger.debug("Exception occured in server as:",e)
        return 'faliure'

app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())

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