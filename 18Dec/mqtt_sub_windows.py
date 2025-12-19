import paho.mqtt.client as mqtt
import json
import time

# ================= MQTT CONFIG =================
MQTT_BROKER = "broker.hivemq.com"   # same broker as Raspberry Pi
MQTT_PORT = 1883
MQTT_TOPIC = "greenway/rpi/pzem/data"
CLIENT_ID = "WIN_SUB_001"
# ==============================================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        print("❌ Connection failed, code:", rc)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        print("\n📥 Data Received")
        print("---------------------------")
        print(f"Device ID        : {data.get('deviceId')}")
        print(f"Voltage (V)      : {data.get('voltage')}")
        print(f"Current (A)      : {data.get('current')}")
        print(f"Power (W)        : {data.get('active_power')}")
        print(f"Energy (kWh)     : {data.get('energy_kwh')}")
        print(f"Frequency (Hz)   : {data.get('frequency')}")
        print(f"Power Factor     : {data.get('power_factor')}")
        print(f"Timestamp        : {data.get('timestamp')}")
    except Exception as e:
        print("⚠️ Invalid data:", e)

client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
