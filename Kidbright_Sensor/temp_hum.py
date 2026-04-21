from machine import Pin
import time
import network
import json
import dht

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


dht_sensor = dht.DHT11(Pin(27, Pin.IN, Pin.PULL_UP))

print("Starting Temp & Humidity Sensor...")

while True:
    try:
        air_temp = 0
        humidity = 0
        for i in range(5):
            dht_sensor.measure()
            air_temp = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
            
            if air_temp > 0 and humidity > 0:
                break
            time.sleep(2)

        if air_temp > 0 and humidity > 0:
            data = {'temp': air_temp, 'humidity': humidity}
            mqtt.publish('b6710545512/temphumidity', json.dumps(data))
            print("Sent Success:", data)
        else:
            print("Skipping: Sensor returned 0")

    except OSError as e:
        print("Sensor error")
        
    time.sleep(600)
