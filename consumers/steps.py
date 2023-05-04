import paho.mqtt.client as mqtt


# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("In/Cooking_Station/+")


# The callback function for received message
def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))


client = mqtt.Client()

# Specify callback functions
client.on_connect = on_connect
client.on_message = on_message

# Establish a connection with broker
client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

client.loop_forever()
