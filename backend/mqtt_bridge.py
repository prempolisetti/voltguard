import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voltguard/battery/data"
BACKEND_URL = "http://127.0.0.1:5000"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] ✓ Connected")
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] ✓ Subscribed")
    else:
        print(f"[MQTT] ✗ Failed rc={rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        v = float(data.get("voltage", 0))
        c = float(data.get("current", 0))
        t = float(data.get("temperature", 0))
        print(f"[ESP32] V={v:.2f}V I={c:.2f}A T={t:.1f}°C")
        requests.post(f"{BACKEND_URL}/hardware/data", 
                     json={"voltage": v, "current": c, "temperature": t}, 
                     timeout=5)
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    client = mqtt.Client(client_id="VoltGuard_Bridge")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("[MQTT] Listening...")
    client.loop_forever()

if __name__ == "__main__":
    main()