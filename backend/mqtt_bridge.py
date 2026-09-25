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
        payload = {
            "voltage": data.get("voltage", data.get("Voltage")),
            "current": data.get("current", data.get("Current")),
            "temperature": data.get("temperature", data.get("Temperature", data.get("temp"))),
        }
        if any(value is None for value in payload.values()):
            raise ValueError("MQTT payload needs voltage, current, and temperature")

        payload = {key: float(value) for key, value in payload.items()}
        soc = data.get("soc", data.get("SOC"))
        if soc is not None:
            payload["soc"] = int(float(soc))

        response = requests.post(f"{BACKEND_URL}/hardware/data", json=payload, timeout=5)
        response.raise_for_status()
        print(
            f"[DASHBOARD] Updated: V={payload['voltage']:.2f}V "
            f"I={payload['current']:.2f}A T={payload['temperature']:.1f}°C"
        )
    except Exception as e:
        print(f"[MQTT ERROR] {e}")

def main():
    client = mqtt.Client(client_id="VoltGuard_Bridge")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("[MQTT] Listening...")
    client.loop_forever()

if __name__ == "__main__":
    main()