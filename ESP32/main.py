from machine import Pin, ADC, PWM
import network
import dht
import time
from umqtt.simple import MQTTClient
import ujson

SSID = "Wokwi-GUEST"
PASSWORD = ""

BROKER = "broker.hivemq.com"
CLIENT_ID = "ESP32_IntelliMine_Node"
TOPIC = b"Abdelrahman_IntelliMine/Data"

dht_sensor = dht.DHT22(Pin(4))

gas_sensor = ADC(Pin(35))
gas_sensor.atten(ADC.ATTN_11DB)

buzzer = PWM(Pin(25))
buzzer.duty(0)

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    print("Connecting to WiFi...")
    
    while not wifi.isconnected():
        time.sleep(0.5)
        print(".", end="")
        
    print("\nWiFi Connected!")
    print("IP Address:", wifi.ifconfig()[0])

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER)
    client.connect()
    print("Connected to MQTT Broker!")
    return client

try:
    connect_wifi()
    client = connect_mqtt()
    
    while True:
        try:
            dht_sensor.measure()
            temperature = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
        except OSError:
            print("Failed to read DHT sensor!")
            temperature = 0
            humidity = 0

        gas = gas_sensor.read()

        if gas > 3000:
            status = "DANGER"
            buzzer.freq(1000)
            buzzer.duty(512)
        else:
            status = "SAFE"
            buzzer.duty(0)

        data = {
            "temperature": temperature,
            "humidity": humidity,
            "gas": gas,
            "status": status
        }
        
        payload = ujson.dumps(data)
        client.publish(TOPIC, payload)

        print("----------------------------")
        print("Temperature :", temperature, "°C")
        print("Humidity    :", humidity, "%")
        print("Gas Level   :", gas)
        print("Status      :", status)
        print("----------------------------")        

        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped manually.")
except Exception as e:
    print("An error occurred:", e)
