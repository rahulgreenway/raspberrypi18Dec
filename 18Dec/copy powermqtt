import serial
import time
import math
import json
import paho.mqtt.client as mqtt

# ================= SERIAL CONFIG =================
PORT = "/dev/ttyUSB0"     # 🔴 Raspberry Pi serial port
BAUD = 9600
ADDR = 0x01
# ================================================

# ================= MQTT CONFIG ===================
MQTT_BROKER = "broker.hivemq.com"   # or your server IP
MQTT_PORT = 1883
MQTT_TOPIC = "greenway/rpi/pzem/data"
CLIENT_ID = "GreenwayInduction1"
# ================================================

# ================= CRC ===========================
def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc
# ================================================

def read_pzem(ser):
    cmd = bytes([ADDR, 0x04, 0x00, 0x00, 0x00, 0x0A])
    crc = crc16(cmd)
    cmd += bytes([crc & 0xFF, crc >> 8])

    ser.write(cmd)
    time.sleep(0.1)
    resp = ser.read(40)

    if len(resp) < 25:
        return None

    voltage = ((resp[3] << 8) | resp[4]) / 10.0

    current_raw = (
        (resp[7] << 24) |
        (resp[8] << 16) |
        (resp[5] << 8) |
        resp[6]
    )
    current = current_raw / 1000.0

    power_raw = (
        (resp[11] << 24) |
        (resp[12] << 16) |
        (resp[9] << 8) |
        resp[10]
    )
    power = power_raw / 10.0

    energy = (
        (resp[15] << 24) |
        (resp[16] << 16) |
        (resp[13] << 8) |
        resp[14]
    ) / 1000.0

    frequency = ((resp[17] << 8) | resp[18]) / 10.0
    pf = ((resp[19] << 8) | resp[20]) / 100.0

    apparent_power = voltage * current
    reactive_power = math.sqrt(max(apparent_power**2 - power**2, 0))

    return {
        "deviceId": CLIENT_ID,
        "voltage": round(voltage, 2),
        "current": round(current, 3),
        "active_power": round(power, 2),
        "energy_kwh": round(energy, 3),
        "frequency": round(frequency, 2),
        "power_factor": round(pf, 2),
        "apparent_power": round(apparent_power, 2),
        "reactive_power": round(reactive_power, 2),
        "timestamp": int(time.time())
    }

# ================= MQTT ==========================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT Connected")
    else:
        print("❌ MQTT Connection failed:", rc)

mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()
# ================================================

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("✅ Connected to PZEM-004T on", PORT)
    except Exception as e:
        print("❌ Serial Error:", e)
        return

    while True:
        data = read_pzem(ser)
        if data:
            payload = json.dumps(data)
            mqtt_client.publish(MQTT_TOPIC, payload, qos=1)
            print("📤 Published:", payload)
        else:
            print("⚠️ No data received")

        time.sleep(2)

if __name__ == "__main__":
    main()
