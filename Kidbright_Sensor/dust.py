from machine import UART, Pin
import time
import network
import json

from umqtt.robust import MQTTClient
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS
)

# WIFI connected
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)
print("Network connected")

# Broker connected
mqtt = MQTTClient(client_id="",
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)
mqtt.connect()
print("MQTT broker connected")

uart = UART(1, baudrate=9600, rx=19, tx=18)

print("Starting Dust Sensor...")

def read_dust():
    if uart.any():
        if uart.read(1) == b'\x42':
            if uart.read(1) == b'\x4D':
                data = uart.read(30)
                if data and len(data) == 30:
                    pm1_0 = (data[8] << 8) | data[9]
                    pm2_5 = (data[10] << 8) | data[11]
                    pm10 = (data[12] << 8) | data[13]
                    return pm1_0, pm2_5, pm10
    return None

while True:
    while uart.any():
        uart.read() 
    
    dust_data = None
    retry = 0
    while dust_data is None and retry < 20:
        dust_data = read_dust()
        time.sleep(0.1)
        retry += 1

    if dust_data:
        pm2_5 = dust_data[1]
        data = {'dust' : pm2_5}
        print(data)
        mqtt.publish('b6710545512/dust', json.dumps(data))
    else:
        print("Read failed: No data from sensor")

    time.sleep(600)
