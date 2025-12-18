import paho.mqtt.client as mqtt

BROKER = "dg.pariautomation.in"   # ya aapka server IP / domain
PORT = 1883
TOPIC = "greenway/rpi3/sub"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected")
        client.subscribe(TOPIC)
    else:
        print("Connection failed", rc)

def on_message(client, userdata, msg):
    print("Topic:", msg.topic)
    print("Message:", msg.payload.decode())

client = mqtt.Client(client_id="RPI3_SUB_001", clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
