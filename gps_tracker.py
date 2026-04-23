import json
import time
from timeloop import Timeloop
from datetime import timedelta
from sim76xx import *

from time import time

from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

file_path = "/home/UbiqCM4/access_token.json"
access_token = ""
GPS_failed_count=0

def Reset_GPS():
    """
    this function resets the gps when gps error occurs more the 5 times consecutively
    """
    global GPS_failed_count

    GPS_failed_count=0
    send_at('AT+CVAUX=3050','',1)
    #time.sleep(0.1)
    send_at('AT+CVAUXs=1','',1)
    #time.sleep(5)


t1 = Timeloop()

try:
    with open(file_path, 'r') as file:
        data = json.load(file)
        access_token = data['token']
        #uncomment for debug
        #print("access token reasd successfully : ",access_token)
except FileNotFoundError:
    print(f"JSON file not found: {file_path}")
except KeyError:
    print("Token key not found in the JSON file.")
except json.JSONDecodeError:
    print("Invalid JSON format in the file.")


try:
    client = TBDeviceMqttClient("samasth.io",username=access_token) #access token to be added
    client.connect()
except Exception as e:
    print("connection error",e)


def Publish(telemetry_with_ts):
    """
    publish data
    """
    try:
       # client = TBDeviceMqttClient("samasth.io",username=access_token)
        client.connect()
        client.send_telemetry(telemetry_with_ts)
    except Exception as e:
        print("connection error",e)
        print("Saving Unpublish data")
        client.disconnect()

@t1.job(interval=timedelta(seconds=30))
def read_gps_every_30s():
    """
    This function returns gps coordinate every 30 seconds
    """
    global GPS_failed_count

    try:
        print(">>>>>>>>>>>>>>")

        lat,long,gps_status = get_gps_position()
        if gps_status:
            GPS_failed_count=0
            telemetry_with_ts = {"ts": int(round(time() * 1000)), "values": {"Latitude":lat,"Longitude":long}}
        else:
            telemetry_with_ts = {"ts": int(round(time() * 1000)), "values": {"GPS_Error":-1}}
            GPS_failed_count+=1
            if GPS_failed_count > 5 :
                Reset_GPS()

        Publish(telemetry_with_ts)
    except Exception as e:
        print("Exception occured ", e)


t1.start(block=True)