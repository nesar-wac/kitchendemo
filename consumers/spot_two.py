import json
from time import sleep
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")
    print(f"Connected successfully with broker")
    client.subscribe("Kitchen_1/In/Cooking_Station/WAC990", 2)


def on_message(client, userdata, msg):
    # convert binary data to python dictionary
    data = json.loads(msg.payload.decode("utf-8"))
    print(data)
    res_data = json.dumps({"Spot_Id": data["Spot_Id"], "Status": "success"})
    sleep(data["Duration"])  # put on sleep mode
    # return spot number and status of the process
    topic = f"Kitchen_1/Out/Cooking_Station/WAC990"
    client.publish(topic=topic, payload=res_data, qos=2)


client = mqtt.Client("SpotTwoAction", clean_session=False)

# Specify callback functions
client.on_connect = on_connect
client.on_message = on_message

# Establish a connection with broker using username and password
client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    exit(0)
