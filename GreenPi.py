"""
GreePi

Designed to monitor a desktop plant


"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import sys
from xively import XivelyAPIClient
from spidev import SpiDev
from datetime import datetime
from requests import HTTPError
import requests
import RPi.GPIO as GPIO

def getenv(key):
    if(key in os.environ):
        return os.environ[key]
    raise EnvironmentError("Environment variable %s not found" % key)

if("DEBUG" in os.environ):
    DEBUG = os.environ["DEBUG"]
else:
    DEBUG = False

# xyvely API configuration

XIVELY_API_KEY = getenv("XIVELY_API_KEY")
XIVELY_FEED_ID = getenv("XIVELY_FEED_ID")

PUSHOVER_APP_KEY = "ekmEHrj1nmAtMLqGHkP2oyDU2NaHFX"
PUSHOVER_USER_KEY = getenv("PUSHOVER_USER_KEY")

# pins numbers
ADC_LIGHT_PIN = 0
ADC_MOISTURE_PIN = 1
ADC_TMP_PIN = 2
ALERT_PIN = 7 # WARNING: physical number of the pin on rpi

MOISTURE_THRESHOLD = 500 # When should we blink the light ?

UPDATE_DELAY = 60 # 1 minute

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ALERT_PIN, GPIO.OUT)

spi = SpiDev()
spi.open(0, 0)

def send_pushover_msg(msg):
    requests.post("https://api.pushover.net/1/messages.json",
            data = {
                "token": PUSHOVER_APP_KEY,
                "user": PUSHOVER_USER_KEY,
                "message": msg,
                "title": "GreenPi"
                }
            )

def convert_temp(val):
    v = val * (3.3 / 1023.0)
    return v * 100 - 50


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    r = spi.xfer2([1,(8+adcnum)<<4,0])
    adcout = ((r[1]&3) << 8) + r[2]
    return adcout

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed, key):
    try:
        datastream = feed.datastreams.get(key)
        if DEBUG:
            print "Found existing datastream %s" % key
        return datastream
    except:
        if DEBUG:
            print "Creating new datastream %s" % key
        datastream = feed.datastreams.create(key)
        return datastream

def run():
    api = XivelyAPIClient(XIVELY_API_KEY)
    feed = api.feeds.get(XIVELY_FEED_ID)

    moisture = get_datastream(feed, "water")
    light = get_datastream(feed, "light")
    temp = get_datastream(feed, "temp")

    sent_notification = False

    while True:
        moisture.current_value = readadc(ADC_MOISTURE_PIN)
        moisture.at = datetime.utcnow()
        light.current_value = readadc(ADC_LIGHT_PIN)
        light.at = datetime.utcnow()
        temp.current_value = "%.2f" % convert_temp(readadc(ADC_TMP_PIN))
        temp.at = datetime.utcnow()
        if(DEBUG):
            print("Moisture: %d, light: %d, temp: %s" % (
                moisture.current_value,
                light.current_value,
                temp.current_value))
        if(moisture.current_value < MOISTURE_THRESHOLD):
            if(not sent_notification):
                send_pushover_msg(
                        "Please water your plant: %s" % moisture.current_value)
                sent_notification = True
            GPIO.output(ALERT_PIN, GPIO.HIGH)
        else:
            sent_notification = False
            GPIO.output(ALERT_PIN, GPIO.LOW)
        try:
            moisture.update()
            light.update()
            temp.update()
        except Exception as e:
            print("%s" % e.strerror)
        time.sleep(UPDATE_DELAY)


if __name__ == "__main__":
    run()
